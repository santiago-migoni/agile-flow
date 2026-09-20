#!/usr/bin/env python3
"""Build a local distributable ZIP without source-reference material."""
from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

EXCLUDED_NAMES = {".DS_Store", "agile-lledo.pdf", "state.json", "state.backup.json"}
EXCLUDED_PARTS = {".git", ".agile-flow", "__pycache__", "dist"}
PROJECT_ONLY_FILES = {"functional-specification.md", "docs/implementation-audit.md", "docs/audit-remediation.md", "docs/implementation-reaudit.md", "docs/reaudit-remediation.md"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Package agile-flow without product records or source PDFs.")
    parser.add_argument("--output", default="dist/agile-flow-0.1.0.zip")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    output = (root / args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in root.rglob("*"):
            relative = path.relative_to(root)
            if not path.is_file() or path.resolve() == output:
                continue
            if relative.as_posix() in PROJECT_ONLY_FILES:
                continue
            if path.name in EXCLUDED_NAMES or any(part in EXCLUDED_PARTS for part in relative.parts):
                continue
            archive.write(path, relative.as_posix())
    print(f"Created package: {output}")


if __name__ == "__main__":
    main()
