# Agile Flow repository guidance

This repository develops and distributes the Agile Flow Codex plugin. Read [the plugin workflow map](plugins/agile-flow/AGENTS.md) to understand the behavior being maintained. Its macro flow complements the skills and shared references; it does not automatically initialize Agile Flow records in this repository.

## Repository boundaries

- `.agents/plugins/marketplace.json` is the marketplace catalog.
- `plugins/agile-flow/` is the self-contained, distributable plugin.
- `docs/` contains the vision, functional specification, design, and validation records.
- Preserve unrelated working-tree changes and existing product documents.
- Write plugin-owned instructions, code, documents, and generated prose in English. Converse in the user's preferred language and preserve original quotations.
- Do not use spec-flow.

## Maintaining the plugin

Keep the macro workflow, skills, shared references, and observable runtime behavior consistent. Put stage ordering and outcome boundaries in the plugin workflow map; keep operation schemas and implementation details in their existing references and code. A successful state mutation does not establish product understanding or user acceptance.

For runtime changes, run the relevant tests from `plugins/agile-flow/`:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -q
```

For instruction changes, check referenced paths and evaluate realistic conversational outcomes proportionally. Report automated checks separately from actual agent exercises. GitHub Releases is the plugin changelog. Commit, publish, install, or deploy only within the user's authorization.
