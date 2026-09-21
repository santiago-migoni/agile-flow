# agile-flow

`agile-flow` is a local Codex skills plugin for delivering small, verifiable software increments while preserving decisions, evidence, and review across sessions.

It stores product records in `<product-root>/.agile-flow/`; it never stores product state in the plugin installation, creates commits, publishes, deploys, or installs itself.

## Use

Invoke one of the six skills in a Codex conversation:

- `initialize`: start a managed product or adopt an existing repository.
- `backlog`: capture, refine, deduplicate, or reprioritize needs.
- `advance`: prepare, implement, verify, or continue an authorized increment.
- `review`: record delivery-specific user feedback, acceptance, and learning.
- `status`: inspect records and repository differences without writing by default.
- `close`: pause, cancel, close, or reopen an increment or project.

The skills call `scripts/agile_flow.py` with JSON requests. The CLI is an internal interface, but can be inspected with `python3 scripts/agile_flow.py --help`.

## Local installation

Codex installs local plugins through a marketplace. Choose a directory for a local marketplace, then prepare a copy of this package there. The helper merges the agile-flow entry into an existing catalog and refuses to replace an existing plugin copy or conflicting entry:

```bash
python3 scripts/prepare_local_install.py /path/to/local-marketplace
codex plugin marketplace add /path/to/local-marketplace
```

Restart Codex Desktop, open the Plugin Directory, select the local marketplace, and install **agile-flow**. Keep `.agile-flow/` in each product separate from the plugin installation. These instructions are not executed by this repository.

## Validation

```bash
python3 -m unittest discover -s tests -v
python3 $CODEX_HOME/skills/.system/plugin-creator/scripts/validate_plugin.py .
python3 $CODEX_HOME/skills/.system/skill-creator/scripts/quick_validate.py skills/initialize
```

`scripts/package_plugin.py` creates a ZIP from the current directory and explicitly excludes `docs/agile-lledo.pdf`, product record folders, caches, and temporary files.

## Reviewable collaboration

All six skills use a shared outcome-based flow. Read `.agile-flow/views/vision.md` for product context and `.agile-flow/views/preparation.md` for the current planning proposal. A proposal does not authorize implementation. The detailed backlog and increment views expose criteria, uncertainty, and technical plans. These views are generated from state.json; ask the agent to update the records rather than editing generated Markdown. Existing authored product documents stay in place. No project AGENTS.md is required.
