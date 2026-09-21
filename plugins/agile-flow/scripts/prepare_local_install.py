#!/usr/bin/env python3
"""Prepare a local marketplace without replacing existing catalog entries."""
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

from package_plugin import EXCLUDED_NAMES, EXCLUDED_PARTS, PROJECT_ONLY_FILES


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare an agile-flow entry in a chosen local marketplace.")
    parser.add_argument("marketplace_root", type=Path, help="Directory containing marketplace.json and plugins/.")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    destination = args.marketplace_root.expanduser().resolve()
    catalog_path = destination / "marketplace.json"
    plugin = destination / "plugins" / "agile-flow"
    if catalog_path.exists():
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        if not isinstance(catalog, dict) or not isinstance(catalog.get("plugins"), list):
            raise SystemExit("Existing marketplace must contain a plugins array.")
    else:
        catalog = {"name": "agile-flow-local", "interface": {"displayName": "Local plugins"}, "plugins": []}
    entry = {"name": "agile-flow", "source": {"source": "local", "path": "./plugins/agile-flow"},
             "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}, "category": "Productivity"}
    matches = [item for item in catalog["plugins"] if item.get("name") == "agile-flow"]
    if matches and matches[0] != entry:
        raise SystemExit("An agile-flow entry already exists with different settings; review it before updating.")
    if not matches:
        catalog["plugins"].append(entry)
    destination.mkdir(parents=True, exist_ok=True)
    if plugin.exists():
        raise SystemExit(f"Plugin destination already exists: {plugin}. Review it before replacing it.")
    plugin.mkdir(parents=True)
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if not path.is_file() or relative.as_posix() in PROJECT_ONLY_FILES or path.name in EXCLUDED_NAMES or any(part in EXCLUDED_PARTS for part in relative.parts):
            continue
        target = plugin / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=destination, delete=False) as handle:
        json.dump(catalog, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        temp = Path(handle.name)
    temp.replace(catalog_path)
    print(f"Prepared {plugin} and preserved marketplace entries in {catalog_path}")


if __name__ == "__main__":
    main()
