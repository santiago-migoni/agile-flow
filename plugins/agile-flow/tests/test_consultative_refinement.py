"""Targeted consultation edits preserve intent boundaries, records and atomicity."""
import copy
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch
import unittest
from scripts import editorial_codec
from scripts.release_store import Error
import test_clean_workflow as workflow


class ConsultativeRefinementTests(unittest.TestCase):
    setUp = workflow.CleanWorkflow.setUp
    op = workflow.CleanWorkflow.op

    def start(self):
        self.op('initialize', project={'name': 'Owner platform', 'purpose': 'Understand environments'})
        self.op('update-product-design', document={'purpose': 'Define environment behavior', 'decisions': [
            self.decision('PD-1', 'Require staging for all projects'),
            self.decision('PD-2', 'Validate every change before production')],
            'open_questions': [{'question': 'Recovery target?', 'impact': 'Recovery', 'timing': 'now'}]})

    def decision(self, ident, text):
        return {'id': ident, 'decision': text, 'scope': 'Environments', 'status': 'decided',
                'basis': 'user-definition', 'source': 'Synthetic original statement'}

    def refine(self, *edits):
        return self.op('refine-design-records', provenance='Synthetic later user statement', edits=list(edits))

    def edit(self, action, ident, record=None, collection='decisions', **kw):
        edit = dict(document='product_design', collection=collection, action=action, id=ident, **kw)
        if record is not None: edit['record'] = record
        return edit

    def test_partial_correction_preserves_independent_validation_and_history(self):
        self.start()
        before = copy.deepcopy(self.store.inspect()['product_design']['decisions'][1])
        replacement = self.decision('PD-3', 'Production-only projects are allowed; staging is optional')
        replacement.update(source='Synthetic correction', retained_ids=['PD-2'])
        self.refine(self.edit('supersede', 'PD-1', replacement),
                    self.edit('add', 'RC-1', {'document': 'architecture.md', 'reason': 'Check topology assumptions', 'status': 'open'}, 'reconciliation'))
        result = self.store.inspect()
        decisions = result['product_design']['decisions']
        self.assertEqual(decisions[1], before)
        self.assertEqual(decisions[0]['status'], 'superseded')
        self.assertEqual(decisions[2]['supersedes'], 'PD-1')
        text = (self.store.directory/'product-design.md').read_text()
        current = text.split('## Design decisions')[1].split('## ')[0]
        self.assertIn('Production-only', current); self.assertIn('Validate every change', current)
        self.assertNotIn('Require staging', current)
        self.assertIn('Require staging', text.split('## Decision history')[1])
        summary = (self.store.directory/'summary.md').read_text()
        self.assertIn('Check topology assumptions', summary)
        self.assertNotIn('Require staging', summary)
        for group in ('releases', 'iterations', 'stories', 'increments', 'decisions'):
            self.assertEqual(result[group], [])

    def test_resolve_and_defer_keep_other_questions_and_legacy_identity(self):
        self.start()
        row = self.store.inspect()['product_design']['open_questions'][0]
        self.refine(self.edit('identify', 'Q-1', collection='open_questions', match=row),
                    self.edit('add', 'Q-2', {'question': 'Brand colors?', 'timing': 'now'}, 'open_questions'))
        self.refine(self.edit('resolve', 'Q-1', {'resolution': 'One hour'}, 'open_questions'),
                    self.edit('defer', 'Q-2', {'revisit_when': 'When designing screens'}, 'open_questions'))
        rows = self.store.inspect()['product_design']['open_questions']
        self.assertEqual(len(rows), 2); self.assertEqual(rows[0]['question'], row['question'])
        self.assertEqual(rows[0]['source'], 'Synthetic later user statement')
        summary = (self.store.directory/'summary.md').read_text()
        self.assertNotIn('Recovery target?', summary)
        self.assertIn('Brand colors?', summary.split('## Deferred topics')[1])
        self.assertIn('No immediate user decision recorded', summary)

    def test_atomic_failure_leaves_every_document_unchanged(self):
        self.start()
        before = self.store.inventory()
        with self.assertRaises(Error):
            self.refine(self.edit('add', 'Q-2', {'question': 'Unknown?', 'timing': 'now'}, 'open_questions'),
                        self.edit('resolve', 'missing', {'resolution': 'No'}, 'open_questions'))
        self.assertEqual(self.store.inventory(), before)

    def test_ambiguous_identity_and_unknown_payload_are_rejected(self):
        self.start(); row = self.store.inspect()['product_design']['open_questions'][0]
        self.op('update-product-design', document={'open_questions': [row, row]})
        with self.assertRaisesRegex(Error, 'exact unnamed'):
            self.refine(self.edit('identify', 'Q-1', collection='open_questions', match=row))
        with self.assertRaisesRegex(Error, 'Unsupported'):
            self.refine(self.edit('update', 'PD-1', authorization='yes'))

    def test_proposal_adoption_and_rejection_are_explicit_and_not_authorization(self):
        self.start()
        self.refine(self.edit('add', 'PD-3', {'decision': 'Use containers', 'scope': 'Runtime', 'status': 'proposed'}),
                    self.edit('add', 'PD-4', {'decision': 'Use VMs', 'scope': 'Runtime', 'status': 'proposed'}))
        with self.assertRaisesRegex(Error, 'basis'):
            self.refine(self.edit('adopt', 'PD-3'))
        self.refine(self.edit('adopt', 'PD-3', {'basis': 'user-confirmation'}), self.edit('reject', 'PD-4'))
        result = self.store.inspect()
        self.assertEqual(result['product_design']['decisions'][2]['status'], 'decided')
        self.assertEqual(result['product_design']['decisions'][3]['status'], 'rejected')
        self.assertEqual(result['decisions'], [])
        self.assertNotIn('Use VMs', (self.store.directory/'summary.md').read_text())

    def test_filtered_editorial_rows_keep_original_indexes_and_notes(self):
        rows = [self.decision('D-1', 'First'), self.decision('D-2', 'Second'), self.decision('D-3', 'Third')]
        rows[0]['status'] = 'superseded'; rows[2]['status'] = 'proposed'
        data = {'purpose': 'Compare options', 'decisions': rows}
        text, schema = editorial_codec.render('product_design', 'Design', data)
        self.assertEqual(editorial_codec.unpack(text, schema), data)
        edited = text.replace('Second', 'Second refined')
        observed = editorial_codec.unpack(edited, schema)
        self.assertEqual(observed['decisions'][1]['decision'], 'Second refined')
        self.assertEqual(observed['decisions'][0], rows[0]); self.assertEqual(observed['decisions'][2], rows[2])
        with self.assertRaises(ValueError):
            editorial_codec.unpack(text.replace('| D-2 |', '| D-9 |')+'\n## Design decisions\n\nDuplicate\n', schema)

    def test_focus_and_proposals_visible_without_delivery_scaffolding(self):
        self.start()
        self.op('update-collaboration', context={'focus': 'Define product value', 'level': 'strategic', 'can_continue': 'Consolidate already supplied needs'})
        self.refine(self.edit('add', 'J-1', {'actor': 'Owner', 'steps': ['dev', 'staging', 'production'], 'outcome': 'Publish change', 'applicability': 'Optional example', 'status': 'proposed'}, 'journeys'))
        summary = (self.store.directory/'summary.md').read_text()
        self.assertIn('Define product value', summary); self.assertIn('strategic', summary)
        self.assertIn('Publish change', summary.split('## Pending proposals')[1])
        self.assertNotIn('## Current release and iteration', summary)
        self.assertNotIn('**Updated:** Not recorded', summary)
        self.assertEqual(self.store.inspect()['project']['collaboration']['level'], 'strategic')

    def test_invalid_reconciliation_and_cycle_are_rejected(self):
        self.start()
        with self.assertRaises(Error):
            self.refine(self.edit('add', 'RC-1', {'document': 'constitution.md', 'reason': 'Clarify', 'status': 'resolved'}, 'reconciliation'))
        decisions = copy.deepcopy(self.store.inspect()['product_design']['decisions'])
        decisions[0]['supersedes'] = 'PD-2'; decisions[1]['supersedes'] = 'PD-1'
        with self.assertRaisesRegex(Error, 'cycles'):
            self.op('update-product-design', document={'decisions': decisions})

    def test_cross_document_batch_and_reconciliation_resolution(self):
        self.start(); self.op('update-architecture', document={'purpose': 'Bound runtime'})
        self.refine(self.edit('add', 'RC-1', {'document': 'architecture.md', 'reason': 'Align topology', 'status': 'open'}, 'reconciliation'))
        self.refine({'document': 'architecture', 'collection': 'decisions', 'action': 'add', 'id': 'A-1', 'record': self.decision('A-1', 'Support production alone')},
                    self.edit('resolve', 'RC-1', {'resolution': 'Architecture A-1 records the same topology'}, 'reconciliation'))
        self.assertNotIn('## Reconciliation pending', (self.store.directory/'summary.md').read_text())
        self.assertEqual(self.store.inspect()['product_design']['reconciliation'][0]['status'], 'resolved')

    def test_plain_and_structured_constitution_agreements_use_content_column(self):
        for agreement in ('Keep consultation first', {'id': 'A-1', 'decision': 'Keep consultation first', 'scope': 'Collaboration', 'source': 'Synthetic user'}):
            body = {'project': {'name': 'Example', 'purpose': 'Definition', 'agreements': [agreement]}, 'decisions': []}
            text, schema = editorial_codec.render('constitution', 'Example', body)
            self.assertEqual(editorial_codec.unpack(text, schema), body)
            self.assertNotIn('Additional context', text)
            line = next(line for line in text.splitlines() if 'Keep consultation first' in line)
            self.assertEqual(line.split('|')[2].strip(), 'Keep consultation first')

    def test_batch_history_has_one_entry_with_each_changed_identity(self):
        self.start(); before = len(self.store.inspect()['product_design']['changes'])
        self.refine(self.edit('add', 'Q-2', {'question': 'Colors?', 'timing': 'now'}, 'open_questions'),
                    self.edit('add', 'Q-3', {'question': 'Name?', 'timing': 'now'}, 'open_questions'))
        history = self.store.inspect()['product_design']['changes']
        self.assertEqual(len(history), before + 1)
        self.assertIn('Q-2', history[-1]['change']); self.assertIn('Q-3', history[-1]['change'])

    def test_unfiltered_design_bindings_remain_readable_without_rewrite(self):
        # Published unfiltered template: emulate its original binding descriptors.
        template = (Path(__file__).parent/'fixtures/design-unfiltered-decisions.md').read_text()
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            for source in editorial_codec.ROOT.glob('*.md'):
                shutil.copyfile(source, target/source.name)
            (target/'product_design.md').write_text(template)
            old_tables = {
                'Design decisions': [('decisions','id','decision','scope','basis','source','rationale','status','supersedes')],
                'Questions and revisit points': [('open_questions','question','impact','timing','revisit_when')],
                'User journeys': [('journeys','id','actor','trigger','steps','outcome','status')],
            }
            with patch.object(editorial_codec, 'ROOT', target), patch.object(editorial_codec, 'FILTERS', {}), patch.dict(editorial_codec.TABLES, old_tables):
                self.start()
        before = self.store.inventory()
        observed = self.store.inspect()
        self.assertEqual(len(observed['product_design']['decisions']), 2)
        self.assertEqual(self.store.inventory(), before)
        self.refine(self.edit('add', 'EX-1', {'example': 'One environment', 'illustrates': 'Optional topology', 'status': 'proposed'}, 'examples'))
        self.assertEqual(self.store.inspect()['product_design']['decisions'], observed['product_design']['decisions'])

    def test_stale_refinement_is_a_conflict_and_does_not_apply(self):
        self.start(); observed = self.store.inspect()
        self.op('update-project', project={'next_step': 'Discuss product value'})
        before = self.store.inventory()
        result = self.store.transaction({'operation': 'refine-design-records', 'operation_id': 'stale-refinement',
            'purpose': 'Outdated change', 'provenance': 'Synthetic source',
            'expected_revision': observed['revision'], 'expected_fingerprint': observed['fingerprint'],
            'edits': [self.edit('add', 'Q-2', {'question': 'Colors?', 'timing': 'now'}, 'open_questions')]})
        self.assertEqual(result['status'], 'conflict'); self.assertEqual(self.store.inventory(), before)
