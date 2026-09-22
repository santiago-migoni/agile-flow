# Migrate JSON records to authored Markdown (schema 1 → 2)

> Historical guide for the published 0.3.0 schema-2 layout. For the current writer, start with [compatibility and migration](migration.md). The version checks and commands below apply only to the historical target.

Updating the plugin and migrating a product are separate operations. Run migration with the released 0.3.0 program against the real product root. Do not reinitialize the product, edit the installed cache, delete old views or move product records to a temporary directory. Stop other agents from writing these records during preview and migration.

## 1. Select and verify the program

Use the 0.3.0 installed plugin directory, or a checkout of the repository at tag `v0.3.0`. For a source checkout the plugin directory is `plugins/agile-flow/`. The migration program does not require the Codex CLI to be available on PATH. The installed skills must also be upgraded before continuing agent work; do not continue with 0.2.0 instructions against migrated records.

Run on the machine that owns the product. Set the two absolute paths below to actual directories:

```sh
AF_PLUGIN=/absolute/path/to/agile-flow/plugins/agile-flow
AF_PRODUCT=/absolute/path/to/product
export AF_PLUGIN AF_PRODUCT
python3 - <<'PY'
import json, os
from pathlib import Path
p=Path(os.environ['AF_PLUGIN'])/'.codex-plugin/plugin.json'
assert json.loads(p.read_text())['version']=='0.3.0', 'Select the released 0.3.0 plugin'
assert (Path(os.environ['AF_PRODUCT'])/'.agile-flow/state.json').is_file(), 'Select the legacy product root'
print('Version and legacy root verified')
PY
```

## 2. Preview without changing records

```sh
python3 "$AF_PLUGIN/scripts/agile_flow.py" --root "$AF_PRODUCT" migrate --dry-run
```

Review `item_mapping`, `manual_view_edits`, `conflicts`, `preserved_files` and `unresolved`. Keep the returned `source_fingerprint`. The preview does not migrate or repair anything.

Legacy `feature` does not establish that an item is a user story. Unknown types retain their ITEM identities and require refinement. If source evidence supports classification, supply an `item_types` object mapping old IDs to story, nfr, bug, technical or research through a JSON request file, and use that same mapping for both preview and application. Do not guess a type solely to complete migration.

## 3. Apply the reviewed migration

Create a request file outside `.agile-flow/`, replacing the placeholder with the exact preview fingerprint:

```json
{
  "expected_source_fingerprint": "COPY_THE_PREVIEW_FINGERPRINT_HERE"
}
```

Preserve any `item_types` mapping used for preview. Then run:

```sh
AF_REQUEST=/absolute/path/to/migration-request.json
python3 "$AF_PLUGIN/scripts/agile_flow.py" --root "$AF_PRODUCT" --request "$AF_REQUEST" migrate --apply
python3 "$AF_PLUGIN/scripts/agile_flow.py" --root "$AF_PRODUCT" validate
python3 "$AF_PLUGIN/scripts/agile_flow.py" --root "$AF_PRODUCT" inspect
```

The program verifies the preview fingerprint, copies and verifies the complete legacy inventory under `.agile-flow/.internal/legacy-backup/`, and writes the new documents through a recoverable transaction. Target conflicts stop migration. Original state and views remain as inactive history. Repeating migration does not duplicate work.

## 4. Review and refine the migrated product

| Legacy material | New meaning |
| --- | --- |
| Project context and decisions in state.json | Authored constitution.md, with sourced facts distinct from assumptions/proposals. |
| Backlog records | Authored backlog item files and generated backlog.md index; unresolved classifications remain explicit. |
| Project preparation proposal | Draft iteration sprint_planning.md. No execution permission is inferred. |
| Historical increments | Separate iterations retaining delivery revisions, evidence and review scope. |
| Quality policy, if present | definition-of-done.md; missing policy remains missing. |
| Legacy views | Preserved originals/backup for comparison. Manually written details are not silently promoted to approval. |

Compare the constitution and item documents against the old vision/backlog/preparation views. A matching view manifest does not prove the installed renderer was unmodified. Review relevant wording and formatting, particularly if the installed 0.2.0 scripts had local patches. Bring meaningful old manual details into the authored documents with their actual source; do not copy old approvals to unrelated scope.

Refine unresolved types with `classify-backlog`, using the normal operation ID, purpose, revision/fingerprint, item_id, type and reason contract. This updates references and preserves the legacy identity mapping. Define a roadmap/MVP and applicable Definition of Done from actual product decisions. Migration cannot invent them. New iteration review, verification and retrospective files appear only when meaningful records exist.

After migration, use the 0.3.0 skills in a fresh Codex task. Status is read-only by default. The current functional authority is authored Markdown; only backlog.md and summary.md are generated. Preserve the structured field markers when editing Markdown.

## Recovery

If a write is interrupted, the program reports a pending transaction. Run the same 0.3.0 entry point with `recover`, then `validate` and `inspect`. Recovery stops if a file contains unrelated changes; preserve and reconcile those changes rather than forcing a restore.

Do not restore only state.backup.json over a different document set. The legacy backup and transaction journals are retained for complete recovery. Do not switch back to the legacy writer after migration or delete preserved records as routine cleanup.
