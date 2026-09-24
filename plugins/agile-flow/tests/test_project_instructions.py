import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

PLUGIN = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('project_instructions', PLUGIN / 'scripts/project_instructions.py')
instructions = importlib.util.module_from_spec(spec)
spec.loader.exec_module(instructions)


class ProjectInstructionsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def request(self):
        result, _, _ = instructions.preview(self.root)
        return dict(expected_source_fingerprint=result['expected_source_fingerprint'], authorization_source='User requested project instructions.')

    def apply(self):
        return instructions.apply(self.root, self.request())

    def test_preview_is_read_only_and_apply_is_idempotent(self):
        result, _, _ = instructions.preview(self.root)
        self.assertEqual(result['instruction_status'], 'missing')
        self.assertEqual(list(self.root.iterdir()), [])
        applied = self.apply()
        self.assertEqual(applied['status'], 'applied')
        snapshot = {str(p): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertFalse(json.loads((Path(applied['backup']) / 'source.json').read_text())['existed'])
        self.assertEqual(self.apply()['status'], 'unchanged')
        self.assertEqual(snapshot, {str(p): p.read_bytes() for p in self.root.rglob('*') if p.is_file()})

    def test_preserves_original_bytes_permissions_and_backup(self):
        original = b'# Team\r\n\r\nKeep our Spanish notes: caf\xc3\xa9.\r\n'
        agents = self.root / 'AGENTS.md'
        agents.write_bytes(original)
        agents.chmod(0o640)
        applied = self.apply()
        self.assertTrue(agents.read_bytes().startswith(original))
        self.assertEqual((Path(applied['backup']) / 'AGENTS.md').read_bytes(), original)
        self.assertEqual(agents.stat().st_mode & 0o777, 0o640)

    def test_upgrade_preserves_external_notes(self):
        self.apply()
        agents = self.root / 'AGENTS.md'
        agents.write_bytes(b'User prefix\n' + agents.read_bytes() + b'\nUser suffix\n')
        template = self.root / 'new-template.md'
        template.write_text('New collaboration instructions\n')
        preview, _, _ = instructions.preview(self.root, template)
        with patch.object(instructions, 'TEMPLATE_VERSION', instructions.TEMPLATE_VERSION + 1):
            preview, _, _ = instructions.preview(self.root, template)
            result = instructions.apply(self.root, dict(expected_source_fingerprint=preview['expected_source_fingerprint'], authorization_source='Upgrade instructions.'), template)
        self.assertEqual(result['status'], 'applied')
        content = agents.read_text()
        self.assertTrue(content.startswith('User prefix\n'))
        self.assertTrue(content.endswith('\nUser suffix\n'))
        self.assertIn('New collaboration instructions', content)
        self.assertEqual(instructions.preview(self.root)[0]['status'], 'conflict')

    def test_manual_edits_and_ambiguous_markers_are_preserved(self):
        self.apply()
        agents = self.root / 'AGENTS.md'
        clean = agents.read_bytes()
        for content in (clean.replace(b'## Agile Flow', b'## My Agile Flow'), clean + clean,
                        clean.replace(instructions.END, b'<!-- broken -->')):
            agents.write_bytes(content)
            self.assertEqual(self.apply()['status'], 'conflict')
            self.assertEqual(agents.read_bytes(), content)

    def test_stale_fingerprint_or_missing_authorization_cannot_write(self):
        request = self.request()
        (self.root / 'AGENTS.md').write_text('Concurrent user edit')
        self.assertEqual(instructions.apply(self.root, request)['status'], 'conflict')
        with self.assertRaises(ValueError):
            instructions.apply(self.root, {})
        self.assertEqual((self.root / 'AGENTS.md').read_text(), 'Concurrent user edit')
        self.assertFalse((self.root / '.agile-flow').exists())

    def test_overrides_and_symlinks_do_not_escape_root(self):
        override = self.root / 'AGENTS.override.md'
        override.write_text('User override')
        self.assertEqual(self.apply()['status'], 'conflict')
        self.assertFalse((self.root / 'AGENTS.md').exists())
        override.unlink()
        with tempfile.TemporaryDirectory() as other:
            external = Path(other) / 'rules'
            external.write_text('External')
            (self.root / 'AGENTS.md').symlink_to(external)
            with self.assertRaises(ValueError):
                self.apply()
            (self.root / 'AGENTS.md').unlink()
            (self.root / '.agile-flow').symlink_to(other, target_is_directory=True)
            with self.assertRaises(ValueError):
                self.apply()
            self.assertEqual(external.read_text(), 'External')
            self.assertFalse((Path(other) / '.internal').exists())

    def test_interrupted_replace_preserves_original_and_backup(self):
        (self.root / 'AGENTS.md').write_text('Original rules')
        with patch.object(instructions.os, 'replace', side_effect=OSError('Interrupted')):
            with self.assertRaises(OSError):
                self.apply()
        self.assertEqual((self.root / 'AGENTS.md').read_text(), 'Original rules')
        backups = list(self.root.glob('.agile-flow/.internal/local/backups/instructions/*/AGENTS.md'))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), 'Original rules')
        self.assertFalse(list(self.root.glob('.agile-flow-agents-*')))

    def test_existing_records_and_git_are_not_mutated_by_setup(self):
        from scripts.clean_store import CleanStore
        store = CleanStore(self.root)
        store.transaction(dict(operation='initialize', operation_id='init', purpose='Fixture', project={'name':'Workshop','purpose':'Book repairs'}))
        before = {str(p):p.read_bytes() for p in (self.root / '.agile-flow').rglob('*') if p.is_file()}
        self.assertEqual(self.apply()['status'], 'applied')
        self.assertEqual(before, {name:Path(name).read_bytes() for name in before})
        self.assertEqual(store.inspect()['project']['name'], 'Workshop')
        self.assertFalse((self.root / '.git').exists())

    def test_edit_during_apply_is_preserved(self):
        original_preview = instructions.preview
        calls = 0
        def concurrent_preview(root, template=None):
            nonlocal calls
            calls += 1
            if calls == 2:
                (self.root / 'AGENTS.md').write_text('Late external edit')
            return original_preview(root, template)
        request = self.request()
        with patch.object(instructions, 'preview', side_effect=concurrent_preview):
            result = instructions.apply(self.root, request)
        self.assertEqual(result['status'], 'conflict')
        self.assertEqual((self.root / 'AGENTS.md').read_text(), 'Late external edit')
        self.assertFalse(list(self.root.glob('.agile-flow-agents-*')))

    def test_template_and_override_changes_invalidate_preview(self):
        template = self.root / 'template.md'
        template.write_text('First template')
        initial, _, _ = instructions.preview(self.root, template)
        request = dict(expected_source_fingerprint=initial['expected_source_fingerprint'], authorization_source='Update')
        template.write_text('Changed template')
        self.assertEqual(instructions.apply(self.root, request, template)['status'], 'conflict')
        (self.root / 'AGENTS.override.md').write_text('New override')
        self.assertEqual(instructions.apply(self.root, self.request())['status'], 'conflict')
        self.assertFalse((self.root / 'AGENTS.md').exists())

    def test_cli_preview_apply_and_current_from_unrelated_cwd(self):
        cli = [sys.executable, str(PLUGIN / 'scripts/agile_flow.py'), '--root', str(self.root), 'instructions']
        result = subprocess.run(cli, cwd='/', capture_output=True, text=True, check=True)
        request = json.loads(result.stdout)
        request['authorization_source'] = 'Initialize project with Agile Flow.'
        applied = subprocess.run(cli + ['--apply'], input=json.dumps(request), cwd='/', capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(applied.stdout)['status'], 'applied')
        current = subprocess.run(cli, cwd='/', capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(current.stdout)['instruction_status'], 'current')


if __name__ == '__main__':
    unittest.main()
