"""Executive reading contracts without loss of authored meaning or old bindings."""
import copy
import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts.clean_store import CleanStore
from scripts.release_store import Error
from scripts import editorial_codec as codec
import test_clean_workflow as workflow


class ExecutiveDocumentTests(unittest.TestCase):
    setUp = workflow.CleanWorkflow.setUp
    op = workflow.CleanWorkflow.op

    def start(self):
        self.op('initialize', project={'name': 'Workshop', 'purpose': 'Replace manual workspace setup', 'next_step': 'Choose the first owner outcome'})
        self.op('update-product-design', document={'purpose': 'Define workspaces', 'decisions': [
            {'id': 'PD-1', 'decision': 'Workspace types are independent', 'scope': 'Creation', 'status': 'decided', 'basis': 'user-definition', 'source': 'Synthetic user'}]})

    def test_volume_does_not_turn_summary_into_agreement_inventory(self):
        self.start()
        decisions = self.store.inspect()['product_design']['decisions']
        decisions += [{'id': 'PD-'+str(n), 'decision': 'Detailed settled agreement '+str(n), 'scope': 'Creation', 'status': 'decided', 'basis': 'user-definition', 'source': 'Synthetic user'} for n in range(2, 22)]
        self.op('update-product-design', document={'decisions': decisions,
            'states': [{'id': 'S-'+str(n), 'state': str(n), 'behavior': 'Detailed technical proposal '+str(n), 'status': 'proposed'} for n in range(14)],
            'open_questions': [{'id': 'Q-1', 'question': 'Which task should be replaced first?', 'impact': 'Initial value', 'timing': 'now'}]})
        self.op('update-collaboration', context={'focus': 'First owner outcome', 'level': 'strategic', 'synthesis': 'Independent workspaces are defined. The initial useful outcome remains open.',
            'highlights': [{'text': 'Workspace types are optional', 'references': ['product-design.md::PD-1']}], 'can_continue': 'Compare existing needs'})
        summary = (self.store.directory/'summary.md').read_text()
        self.assertLess(len(summary), 5000)
        self.assertIn('14 pending', summary)
        self.assertIn('Which task should be replaced first?', summary)
        self.assertNotIn('Detailed technical proposal', summary)
        self.assertNotIn('Detailed settled agreement', summary)
        self.assertIn('Independent workspaces are defined', summary)
        self.assertIn('[product-design.md::PD-1](product-design.md#design-decisions)', summary)
        self.assertEqual(len(self.store.inspect()['product_design']['decisions']), 21)
        for key in ('releases', 'iterations', 'stories', 'increments', 'decisions'):
            self.assertEqual(self.store.inspect()[key], [])

    def test_ids_and_historical_rows_have_complete_lossless_tables(self):
        data = {'purpose': 'Compare hosting', 'components': [
            {'id': 'C-1', 'component': 'Old edge', 'status': 'rejected'},
            {'id': 'C-2', 'component': 'New edge', 'status': 'decided'}],
            'operations': [{'id': 'O-1', 'concern': 'Old flow', 'status': 'superseded'}, {'id': 'O-2', 'concern': 'Current flow', 'status': 'decided'}],
            'alternatives': [{'id': 'A-1', 'option': 'Past choice', 'status': 'rejected'}],
            'data': [{'id': 'D-1', 'data': 'Workspace', 'status': 'proposed'}],
            'changes': [{'at': '2026-01-01', 'change': 'Clarify edge', 'records': ['components/C-1: update'], 'source': 'Synthetic'}]}
        text, schema = codec.render('architecture', 'Architecture', data)
        self.assertEqual(codec.unpack(text, schema), data)
        self.assertNotIn('Additional context', text)
        active = text.split('## Components and responsibilities\n')[1].split('## ')[0]
        self.assertNotIn('Old edge', active); self.assertIn('New edge', active)
        history = text.split('## Components and responsibilities history')[1].split('## ')[0]
        self.assertIn('<details>', history); self.assertIn('Old edge', history)
        edited = text.replace('Past choice', 'Past choice explained')
        self.assertEqual(codec.unpack(edited, schema)['alternatives'][0]['option'], 'Past choice explained')
        with self.assertRaises(ValueError): codec.unpack(text.replace('</details>', '', 1), schema)

    def test_optional_absences_do_not_generate_fake_definitions(self):
        data = {'project': {'name': 'Workshop', 'purpose': 'Simplify setup',
                'amendments': [{'at': '2026-02-03T00:00:00Z', 'reason': 'Clarify purpose'}]}, 'decisions': []}
        text, schema = codec.render('constitution', 'Workshop', data)
        self.assertIn('2026-02-03T00:00:00Z', text)
        self.assertNotIn('**Vision.**', text); self.assertNotIn('**Owner:**', text)
        self.assertEqual(codec.unpack(text, schema), data)
        self.assertEqual(codec.unpack(text+'\n## Owner notes\n\nPreserve me.\n', schema), data)

    def test_references_preserve_identity_and_warn_after_supersession(self):
        self.start()
        self.op('update-product-design', document={'rules': [{'id': 'R-1', 'rule': 'Applies to creation controls', 'status': 'confirmed', 'agreement_refs': ['product-design.md::PD-1']}]})
        self.op('update-backlog', item={'purpose': 'Choose workspace types', 'references': ['product-design.md::PD-1']})
        source_before = copy.deepcopy(self.store.inspect()['product_design']['rules'])
        self.op('refine-design-records', provenance='Synthetic correction', edits=[{'document': 'product_design', 'collection': 'decisions', 'action': 'supersede', 'id': 'PD-1', 'record': {'id': 'PD-2', 'decision': 'Workspace types have a bounded constraint', 'scope': 'Creation', 'status': 'decided', 'basis': 'user-definition', 'source': 'Synthetic correction'}}])
        self.assertEqual(self.store.inspect()['product_design']['rules'], source_before)
        summary = (self.store.directory/'summary.md').read_text()
        self.assertIn('References a historical agreement', summary)
        self.assertIn('backlog/BL-0001.md', summary)
        text = (self.store.directory/'backlog/BL-0001.md').read_text()
        self.assertIn('../product-design.md#decision-history', text)
        self.assertNotIn('Workspace types have a bounded constraint', text)

    def test_unknown_reference_does_not_partially_write(self):
        self.start(); before = self.store.inventory()
        with self.assertRaisesRegex(Error, 'Unknown agreement'):
            self.op('update-product-design', document={'rules': [{'id': 'R-1', 'rule': 'Applies', 'agreement_refs': ['product-design.md::MISSING']}]})
        self.assertEqual(self.store.inventory(), before)
        with self.assertRaisesRegex(Error, 'Unknown agreement'):
            self.op('update-backlog', item={'purpose': 'Invalid dependency', 'references': ['architecture.md::MISSING']})
        self.assertEqual(self.store.inventory(), before)

    def test_synthesis_roundtrip_portability_and_selection_bounds(self):
        self.start()
        context = {'synthesis': 'The user outcome is the current focus.', 'highlights': [{'text': 'Types clarified', 'references': ['product-design.md::PD-1']}]}
        self.op('update-collaboration', context=context)
        path = self.store.directory/'constitution.md'
        path.write_text(path.read_text().replace('The user outcome is the current focus.', 'The owner outcome is now the focus.')+'\n## Owner notes\n\nPreserve this note.\n')
        self.op('update-project', project={'next_step': 'Compare needs'})
        self.assertIn('Preserve this note.', path.read_text())
        self.assertIn('The owner outcome is now the focus.', (self.store.directory/'summary.md').read_text())
        with tempfile.TemporaryDirectory() as tmp:
            shutil.copytree(self.store.directory, Path(tmp)/'.agile-flow', ignore=shutil.ignore_patterns('local'))
            self.assertEqual(CleanStore(tmp).inspect()['project']['collaboration'], self.store.inspect()['project']['collaboration'])
        with self.assertRaises(Error):
            self.op('update-collaboration', context={'highlights': [{'text': 'Too many'}]*6})

    def test_published_unfolded_document_is_read_without_mutation(self):
        fixture = json.loads((Path(__file__).parent/'fixtures/editorial-unfolded-bindings.json').read_text())
        self.assertEqual(codec.unpack(fixture['text'], fixture['schema']), fixture['data'])
        text, schema = codec.render('architecture', 'Updated architecture', fixture['data'])
        self.assertIn('<details>', text)
        self.assertEqual(codec.unpack(text, schema), fixture['data'])

    def test_ordinary_source_text_is_not_reinterpreted_as_an_agreement(self):
        self.start()
        self.op('update-backlog', item={'purpose': 'Keep the source', 'references': ['Meeting::notes and examples']})
        self.assertEqual(self.store.inspect()['backlog'][0]['references'], ['Meeting::notes and examples'])
        self.assertIn('No immediate user decision recorded', (self.store.directory/'summary.md').read_text())
