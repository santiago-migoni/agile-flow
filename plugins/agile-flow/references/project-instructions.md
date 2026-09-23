# Project instructions

The plugin's own AGENTS.md is its workflow map, not a project installation. The distributable `templates/project-agents.md` supplies a concise project-level collaboration contract. Product data stays in `.agile-flow`; the template contains no product decisions or installed-cache paths.

## Setup and adoption

For a newly initialized product, include instruction setup in the authorized Agile Flow initialization workflow and explain that AGENTS.md will receive a managed section. Initialization of records itself does not silently write this file. For an existing project, apply setup/update only when the user's request covers adopting or updating project instructions. A read-only status request, plugin installation, or unrelated record mutation never applies it. The source repository is not itself a product to initialize.

Use the installed CLI with an explicit absolute product root:

```sh
python3 <installed-plugin>/scripts/agile_flow.py --root <product-root> instructions --dry-run
python3 <installed-plugin>/scripts/agile_flow.py --root <product-root> --request <request.json> instructions --apply
```

Default `instructions` is a read-only preview, including status, diff, issues and `expected_source_fingerprint`. For apply, provide a JSON object with that exact fingerprint and `authorization_source` quoting or identifying the existing user request. This is evidence of the mandate, not a new approval ceremony. Review the diff and relevant repository rules before applying. Repeating a current setup makes no changes or backups.

## Preservation and recovery

The writer manages only the single delimited Agile Flow block. Its checksum detects manual changes, its template version prevents downgrades, and all bytes outside the block are preserved. Preview refuses ambiguous markers, manual block edits, symlink targets and an effective root AGENTS.override.md. Resolve the actual instructions with the user where necessary; never delete or overwrite an override to make setup succeed. Semantically conflicting repository rules require agent review; the writer cannot establish their compatibility.

No force option discards manual edits. To reconcile, first preserve the edited file, review the difference, retain user-specific instructions outside the managed block, and remove only the old managed block under the applicable editing mandate. Preview and apply again. Do not recompute a checksum to hide a conflict.

Apply checks the entire source and template fingerprint, uses a cooperative directory lock, preserves existing permissions, and atomically replaces AGENTS.md. It checks again before replacement to detect concurrent external edits; unrelated editors do not honor the lock, so coordinate editing during apply. Backups under `.agile-flow/.internal/local/backups/instructions/<id>/` contain original AGENTS.md bytes when present and source.json describing prior existence and authorization. If applying fails, inspect AGENTS.md and the backup before retrying. Restore only the reviewed file under the existing recovery mandate; do not roll back later unrelated edits.

Codex discovers instructions at run start. Read the resulting AGENTS.md explicitly in the current task, and verify automatic discovery in a fresh run at the product root and relevant subdirectories. A root override can replace AGENTS.md, nested instructions can override broader guidance, and instruction size limits can truncate it. Report these conditions; do not change global configuration or nested rules automatically. Official reference: https://learn.chatgpt.com/docs/agent-configuration/agents-md.

Instruction template versioning is independent of plugin release versions and document schema 4. Setup does not migrate records, change authorization, initialize Git, commit, publish or install the plugin. Include AGENTS.md in scoped Git previews only when the existing Git agreement covers the instruction change; backups remain local.
