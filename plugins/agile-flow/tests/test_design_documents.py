"""Consultative records work without delivery scheduling or implied authority."""
import copy
import json
import shutil
from unittest.mock import patch
import tempfile
import unittest
from pathlib import Path
from scripts.clean_store import CleanStore
from scripts.release_store import Error
from scripts import editorial_codec
import test_clean_workflow as workflow


class DesignDocumentTests(unittest.TestCase):
    setUp = workflow.CleanWorkflow.setUp
    op = workflow.CleanWorkflow.op

    def initialize(self):
        self.op('initialize', project={'name': 'Workshop', 'purpose': 'Manage personal environments', 'next_step': 'Discuss the current workflow'})

    def architecture(self):
        return {'purpose': 'Compare a control-plane solution',
                'alternatives': [{'topic': 'Backend', 'option': 'Django', 'benefits': 'Integrated domain tools', 'costs': 'Python deployment', 'recommendation': 'Candidate', 'status': 'proposed'}],
                'decisions': [{'id': 'ARCH-001', 'decision': 'Use Django', 'scope': 'Backend', 'basis': 'user-definition', 'source': 'User: El backend será Django.', 'rationale': 'Explicit choice', 'status': 'decided'}],
                'open_questions': [{'question': 'Separate frontend?', 'impact': 'Build and operation cost', 'timing': 'now'},
                                   {'question': 'Production backups?', 'impact': 'Recovery guarantee', 'timing': 'later', 'revisit_when': 'Before defining production'},
                                   {'question': 'Which job runner?', 'impact': 'Operations', 'timing': 'investigate'}]}

    def test_discovery_creates_no_delivery_or_empty_design(self):
        self.initialize(); result = self.store.inspect()
        self.assertEqual(result['documents'], ['backlog/product-backlog.md', 'constitution.md', 'summary.md'])
        for group in ['releases', 'iterations', 'stories', 'increments', 'decisions']:
            self.assertEqual(result[group], [])
        self.op('update-backlog', item={'purpose': 'Understand environment state'})
        self.assertNotIn('target_release', self.store.inspect()['backlog'][0])

    def test_design_without_iteration_roundtrip_notes_and_portability(self):
        self.initialize()
        self.op('update-product-design', document={'purpose': 'Understand the owner journey', 'journeys': [{'id': 'J-001', 'actor': 'Owner', 'trigger': 'New project', 'steps': ['Name it', 'Choose environment'], 'outcome': 'Known environment state', 'status': 'proposed'}]})
        self.op('update-architecture', document=self.architecture())
        result = self.store.inspect()
        self.assertEqual(result['architecture']['decisions'][0]['decision'], 'Use Django')
        for group in ['releases', 'iterations', 'stories', 'increments', 'decisions']:
            self.assertEqual(result[group], [])
        path = self.store.directory/'architecture.md'
        text = path.read_text().replace('Integrated domain tools', 'Integrated relational tools')+'\n## Operator notes\n\nKeep setup small.\n'
        path.write_text(text)
        self.store.render(); self.assertEqual(path.read_text(), text)
        self.op('update-architecture', document={'constraints': ['One operator']})
        self.assertIn('Keep setup small.', path.read_text())
        self.assertEqual(self.store.inspect()['architecture']['alternatives'][0]['benefits'], 'Integrated relational tools')
        self.assertNotIn('Use Django', self.store.path.read_text())
        with tempfile.TemporaryDirectory() as tmp:
            shutil.copytree(self.store.directory, Path(tmp)/'.agile-flow', ignore=shutil.ignore_patterns('local'))
            clone = CleanStore(tmp)
            self.assertEqual(clone.inspect()['architecture'], self.store.inspect()['architecture'])
            self.assertEqual(clone.inspect()['product_design'], result['product_design'])

    def test_pending_and_deferred_topics_stay_separate(self):
        self.initialize(); self.op('update-architecture', document=self.architecture())
        text = (self.store.directory/'summary.md').read_text()
        pending = text.split('## Blockers and pending decisions')[1].split('## Questions to investigate')[0]
        deferred = text.split('## Deferred topics')[1].split('## Next useful action')[0]
        self.assertIn('Separate frontend?', pending)
        self.assertNotIn('Production backups?', pending)
        self.assertIn('Production backups?', deferred)
        self.assertIn('Before defining production', deferred)
        self.assertIn('](architecture.md)', text)
        self.assertNotIn('](product-design.md)', text)

    def test_settled_decision_needs_source_and_never_grants_execution(self):
        self.initialize()
        bad = self.architecture(); del bad['decisions'][0]['source']
        with self.assertRaisesRegex(Error, 'actual source'):
            self.op('update-architecture', document=bad)
        self.assertFalse((self.store.directory/'architecture.md').exists())
        self.op('update-architecture', document=self.architecture())
        with self.assertRaises(Error):
            self.op('prepare', iteration_id='ITER-001', increment={'item_ids': [], 'objective': 'Build', 'scope': 'Backend', 'authorization': 'ARCH-001'})
        self.assertEqual(self.store.inspect()['increments'], [])

    def test_invalid_empty_document_and_stale_request_do_not_write(self):
        self.initialize()
        with self.assertRaises(Error): self.op('update-product-design', document={})
        with self.assertRaises(Error): self.op('update-architecture', document={'purpose': ' '})
        before = self.store.inspect()
        self.op('update-project', project={'next_step': 'Discuss interfaces'})
        result = self.store.transaction({'operation': 'update-architecture', 'operation_id': 'stale', 'purpose': 'Design', 'expected_revision': before['revision'], 'expected_fingerprint': before['fingerprint'], 'document': self.architecture()})
        self.assertEqual(result['status'], 'conflict')
        self.assertFalse((self.store.directory/'architecture.md').exists())

    def test_unsupported_fields_and_ambiguous_manual_edits_fail_safely(self):
        self.initialize()
        with self.assertRaises(Error): self.op('update-architecture', document={'purpose': 'Design', 'authorization': 'Approved'})
        self.op('update-architecture', document=self.architecture())
        path = self.store.directory/'architecture.md'
        path.write_text(path.read_text()+'\n## Architecture decisions\n\nConflicting choices.\n')
        before = path.read_bytes()
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            self.store.inspect()
        self.assertEqual(path.read_bytes(), before)

    def test_populated_templates_preserve_all_domain_fields(self):
        records = {
            'product_design': {'purpose': 'Independent booking', 'scope': ['Booking'], 'exclusions': ['Billing'],
                'journeys': [{'id': 'J-1', 'actor': 'Customer', 'trigger': 'Need a slot', 'steps': ['Choose', 'Confirm'], 'outcome': 'Booking', 'status': 'confirmed'}],
                'screens': [{'id': 'S-1', 'journey': 'J-1', 'screen': 'Calendar', 'information': ['Availability'], 'actions': ['Select slot'], 'status': 'proposed'}],
                'states': [{'context': 'Calendar', 'state': 'Empty', 'behavior': 'Explain availability', 'recovery': 'Choose another day', 'status': 'proposed'}],
                'accessibility': [{'need': 'Keyboard access', 'behavior': 'Visible focus', 'verification': 'Keyboard journey', 'status': 'proposed'}]},
            'architecture': {**self.architecture(), 'constraints': ['Single host'],
                'components': [{'component': 'API', 'responsibility': 'Domain rules', 'interfaces': ['HTTP'], 'boundary': 'No Docker socket', 'status': 'proposed'}],
                'data': [{'data': 'Projects', 'owner': 'API', 'persistence': 'Relational store', 'lifecycle': 'Archive explicitly', 'status': 'proposed'}],
                'integrations': [{'system': 'Docker', 'contract': 'Bounded operations', 'failure': 'Visible failure', 'trust_boundary': 'Worker only', 'status': 'proposed'}],
                'operations': [{'concern': 'Recovery', 'approach': 'Reconcile observed state', 'cost': 'Operator workflow', 'verification': 'Fault scenario', 'status': 'proposed'}]}}
        for kind, data in records.items():
            text, schema = editorial_codec.render(kind, 'Workshop', data, display={'project_name': 'Workshop'})
            self.assertEqual(editorial_codec.unpack(text, schema), data)
            self.assertNotIn('Additional context', text)
            self.assertNotIn('{{', text)
            self.assertNotIn('<!-- af:', text)

    def test_decision_quote_and_change_reason_have_named_columns(self):
        self.initialize()
        self.op('record-decision', decision={'kind': 'product', 'author': 'user', 'reason': 'Use one host', 'scope': 'Topology', 'source': 'Synthetic user message', 'quote': 'One host.'})
        self.op('update-project', project={'next_step': 'Discuss the owner workflow'})
        text = (self.store.directory/'constitution.md').read_text()
        table = text.split('## Decisions and collaboration agreements')[1].split('## ')[0]
        self.assertIn('One host.', table)
        self.assertIn('Topology', table)
        self.assertIn('Synthetic user message', table)
        changes = text.split('## Changes')[1].split('## ')[0]
        self.assertIn('Test actual requested scope', changes)
        self.assertNotIn('Decisions / 1 / Quote', text)

    def test_decision_updates_preserve_prior_agreements(self):
        self.initialize(); self.op('update-architecture', document=self.architecture())
        with self.assertRaisesRegex(Error, 'Preserve existing'):
            self.op('update-architecture', document={'decisions': []})
        rows = copy.deepcopy(self.store.inspect()['architecture']['decisions'])
        rows[0]['decision'] = 'Use a different backend'
        with self.assertRaisesRegex(Error, 'sourced replacement'):
            self.op('update-architecture', document={'decisions': rows})
        rows = copy.deepcopy(self.store.inspect()['architecture']['decisions'])
        rows[0]['status'] = 'superseded'
        rows.append({'id': 'ARCH-002', 'decision': 'Use another backend', 'scope': 'Backend', 'basis': 'user-definition', 'source': 'Later synthetic user correction', 'status': 'decided', 'supersedes': 'ARCH-001'})
        self.op('update-architecture', document={'decisions': rows})
        self.assertEqual(len(self.store.inspect()['architecture']['decisions']), 2)
        self.assertEqual(self.store.inspect()['decisions'], [])

    def test_existing_editorial_document_bindings_remain_readable(self):
        # Use the published constitution template to create its older bindings.
        template = (Path(__file__).parent/'fixtures/constitution-compact-decisions.md').read_text()
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            for source in editorial_codec.ROOT.glob('*.md'):
                shutil.copyfile(source, target/source.name)
            (target/'constitution.md').write_text(template)
            with patch.object(editorial_codec, 'ROOT', target):
                self.initialize()
                self.op('record-decision', decision={'kind': 'product', 'author': 'user', 'reason': 'Use one host', 'scope': 'Topology', 'source': 'Synthetic original user', 'quote': 'One host.'})
        before = {str(f.relative_to(self.store.directory)): f.read_bytes() for f in self.store.directory.rglob('*') if f.is_file()}
        observed = CleanStore(self.root).inspect()
        self.assertEqual(observed['decisions'][0]['quote'], 'One host.')
        self.assertEqual(before, {str(f.relative_to(self.store.directory)): f.read_bytes() for f in self.store.directory.rglob('*') if f.is_file()})
        self.op('update-architecture', document=self.architecture())
        self.assertEqual(self.store.inspect()['decisions'], observed['decisions'])
        self.assertEqual(self.store.inspect()['iterations'], [])
