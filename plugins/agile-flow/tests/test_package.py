from __future__ import annotations

import json
import unittest
import zipfile
from pathlib import Path
import tempfile
import re
import subprocess
import sys


ROOT = Path(__file__).parents[1]


class PackageTests(unittest.TestCase):
    def test_repository_marketplace_resolves_plugin(self) -> None:
        repository = ROOT.parents[1]
        catalog = json.loads((repository / ".agents/plugins/marketplace.json").read_text())
        self.assertEqual(catalog["name"], "agile-flow")
        entry = next(item for item in catalog["plugins"] if item["name"] == "agile-flow")
        source = (repository / entry["source"]["path"]).resolve()
        self.assertEqual(source, ROOT.resolve())
        manifest = json.loads((source / ".codex-plugin/plugin.json").read_text())
        self.assertEqual(manifest["name"], entry["name"])
        self.assertEqual(entry["policy"]["installation"], "AVAILABLE")

    def test_manifest_and_skill_layout_are_complete(self) -> None:
        manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "agile-flow")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertNotIn("mcpServers", manifest)
        self.assertNotIn("apps", manifest)
        for name in ("initialize", "backlog", "advance", "review", "status", "close"):
            content = (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
            self.assertTrue(content.startswith(f"---\nname: {name}\n"))
            self.assertIn("../../references/", content)

    def test_package_excludes_source_book(self) -> None:
        output = Path("/private/tmp/agile-flow-package-test.zip")
        subprocess.run([sys.executable, str(ROOT / "scripts" / "package_plugin.py"), "--output", str(output)], cwd=ROOT, check=True)
        with zipfile.ZipFile(output) as archive:
            names = archive.namelist()
        self.assertNotIn("docs/agile-lledo.pdf", names)
        self.assertNotIn("docs/implementation-reaudit.md", names)
        self.assertNotIn("docs/reaudit-remediation.md", names)
        self.assertNotIn("docs/implementation-audit-round-3.md", names)
        self.assertNotIn("docs/audit-round-3-remediation.md", names)
        self.assertFalse(any(name.startswith(".agile-flow/") for name in names))
        self.assertIn("scripts/agile_flow.py", names)

    def test_every_skill_reference_resolves_from_installed_layout(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            archive = Path(temporary) / "plugin.zip"
            subprocess.run([sys.executable, str(ROOT / "scripts" / "package_plugin.py"), "--output", str(archive)], cwd="/private/tmp", check=True)
            installed = Path(temporary) / "installed"
            with zipfile.ZipFile(archive) as package:
                package.extractall(installed)
            for skill in (installed / "skills").glob("*/SKILL.md"):
                text = skill.read_text()
                references = re.findall(r"\.\./\.\./references/[a-z-]+\.md", text)
                self.assertTrue(references, skill)
                for reference in references:
                    self.assertTrue((skill.parent / reference).is_file(), (skill, reference))
            command = subprocess.run([sys.executable, str(installed / "scripts" / "agile_flow.py"), "--help"], cwd="/private/tmp", capture_output=True, text=True)
            self.assertEqual(command.returncode, 0, command.stderr)

    def test_marketplace_preparation_preserves_existing_entries(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            marketplace = Path(temporary) / "marketplace"
            marketplace.mkdir()
            catalog = {"name": "existing", "plugins": [{"name": "another-plugin", "source": {"source": "local", "path": "./plugins/another-plugin"}}]}
            (marketplace / "marketplace.json").write_text(json.dumps(catalog))
            result = subprocess.run([sys.executable, str(ROOT / "scripts" / "prepare_local_install.py"), str(marketplace)], cwd="/private/tmp", capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            updated = json.loads((marketplace / "marketplace.json").read_text())
            self.assertEqual([entry["name"] for entry in updated["plugins"]], ["another-plugin", "agile-flow"])
            self.assertFalse((marketplace / "plugins" / "agile-flow" / "docs" / "agile-lledo.pdf").exists())
