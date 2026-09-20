from __future__ import annotations

import json
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).parents[1]


class PackageTests(unittest.TestCase):
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
        import subprocess
        import sys
        output = Path("/private/tmp/agile-flow-package-test.zip")
        subprocess.run([sys.executable, str(ROOT / "scripts" / "package_plugin.py"), "--output", str(output)], cwd=ROOT, check=True)
        with zipfile.ZipFile(output) as archive:
            names = archive.namelist()
        self.assertNotIn("docs/agile-lledo.pdf", names)
        self.assertIn("scripts/agile_flow.py", names)
