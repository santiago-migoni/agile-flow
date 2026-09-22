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

Version 0.6.0 implements schema 4 with the editorial-v2 codec: clean authored Markdown, release-owned iterations, BL product needs and US work records with type US/NFR/BUG/TCH/SPK. Each story owns its acceptance criteria and DoD. Only product-backlog.md and summary.md are generated indexes.

Executable Markdown templates and portable structural schemas support partial updates without af markers. Technical metadata and baselines are versioned; local caches, journals and backups are ignored. Git preview and commit operations follow explicit authorization or an agreed outcome policy and preserve unrelated changes.

See [document operations](references/document-operations.md), [clean Markdown and Git](references/clean-markdown-and-git.md), and the [compatibility and migration table](references/migration.md). Installing 0.6.0 does not migrate existing products. Automated tests and independent agent exercises are different forms of evidence.

## Document presentation

The [complete template catalog](templates/README.md) drives all eleven document formats, including real tables, prose and conditional content. The editorial-v2 reader reconstructs their functional records, preserves Notes sections and rejects ambiguous edits. Existing v0.5.0 records require a previewed format migration; the schema remains 4. See the [editorial integration guide](references/editorial-format.md).
