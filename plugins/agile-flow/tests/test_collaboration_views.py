from __future__ import annotations

import unittest

from test_records import RecordsHarness


class CollaborationViews(RecordsHarness, unittest.TestCase):
    def test_definition_produces_reviewable_proposal_without_execution_permission(self):
        self.initialize()
        self.backlog()
        result = self.mutate(dict(operation='update-project', operation_id='synthesis', purpose='Consolidate owner decisions', project={
            'purpose': 'Host Odoo on the same server as the platform.',
            'users': ['The owner'], 'confirmed_facts': ['Owner selected Community 19.0 and Docker.'],
            'assumptions': ['Image pin requires investigation.'], 'proposals': ['Use separate persistent storage per environment.'],
            'constraints': ['No remote-server registration.'], 'open_questions': [],
            'preparation': {'objective': 'Create and open one development environment.', 'item_ids': ['ITEM-0001'],
                'scope': 'Project, environment, deployment URL, status, logs and lifecycle actions.',
                'exclusions': ['Production and Git deployment automation'], 'criteria': ['Open the deployed Odoo URL.'],
                'required_checks': ['Deploy and stop/start without data loss.'], 'technical_plan': 'Investigate the image and local routing.', 'open_decisions': []}}))
        self.assertEqual(result['status'], 'applied')
        current = self.inspect()
        self.assertEqual(current['increments'], [])
        self.assertEqual(current['decisions'], [])
        vision = (self.root / '.agile-flow/views/vision.md').read_text()
        self.assertIn('Owner selected Community 19.0 and Docker.', vision)
        self.assertIn('No remote-server registration.', vision)
        proposal = (self.root / '.agile-flow/views/preparation.md').read_text()
        self.assertIn('Production and Git deployment automation', proposal)
        self.assertIn('Deploy and stop/start without data loss.', proposal)
        denied = self.mutate(dict(operation='prepare', operation_id='unauthorized', purpose='Attempt execution preparation', increment={
            'objective': 'Deploy', 'scope': 'One environment', 'criteria': ['Opens'], 'required_checks': ['Smoke']}))
        self.assertEqual(denied['status'], 'failed')
        self.assertEqual(self.inspect()['increments'], [])

    def test_correction_updates_views_and_preserves_history_and_manual_edits(self):
        self.initialize()
        self.mutate(dict(operation='update-project', operation_id='hypothesis', purpose='Record hypothesis', project={'assumptions': ['Remote SSH may be needed.']}))
        self.mutate(dict(operation='update-project', operation_id='correction', purpose='Owner clarified local hosting', project={'assumptions': [], 'confirmed_facts': ['Same-server hosting only.']}))
        view = self.root / '.agile-flow/views/vision.md'
        self.assertNotIn('Remote SSH may be needed.', view.read_text())
        self.assertIn('Remote SSH may be needed.', str(self.inspect()['history']))
        view.write_text(view.read_text() + '\nUser note\n')
        result = self.mutate(dict(operation='update-project', operation_id='must-preserve', purpose='Update', project={'next_step': 'Prepare'}))
        self.assertEqual(result['status'], 'failed')
        self.assertIn('User note', view.read_text())

    def test_proposal_cannot_embed_authorization_and_invalid_types_are_rejected(self):
        self.initialize()
        for number, project in enumerate([{'preparation': {'authorization': 'approved'}}, {'preparation': {'item_ids': ['ITEM-9999']}}, {'confirmed_facts': 'unsupported'}]):
            revision = self.inspect()['revision']
            result = self.mutate(dict(operation='update-project', operation_id=f'invalid-{number}', purpose='Invalid proposal', project=project))
            self.assertEqual(result['status'], 'failed')
            self.assertEqual(self.inspect()['revision'], revision)

    def test_existing_unmanaged_vision_is_preserved_during_upgrade(self):
        self.initialize()
        import json
        manifest_path = self.root / '.agile-flow/views/.manifest.json'
        manifest = json.loads(manifest_path.read_text())
        manifest['files'].pop('vision.md')
        manifest_path.write_text(json.dumps(manifest))
        vision = self.root / '.agile-flow/views/vision.md'
        vision.write_text('Existing authored vision')
        result = self.mutate(dict(operation='update-project', operation_id='upgrade', purpose='Update context', project={'next_step': 'Review'}))
        self.assertEqual(result['status'], 'applied')
        self.assertEqual(result['views'], 'failed')
        self.assertEqual(vision.read_text(), 'Existing authored vision')
        code, result = self.call('render', extra=['--force'])
        self.assertEqual(code, 0)
        backups = list(vision.parent.glob('vision.md.manual-*.backup'))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), 'Existing authored vision')
