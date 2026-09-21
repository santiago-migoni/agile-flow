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

Version 0.4.0 implements schema 3: authored constitution and version roadmap; concrete releases with optional MVP definition; product needs in backlog/BL-nnnn.md; and US-nnnn.md work records under release/<version>/ITER-nnn/user-stories/. A story’s type is US, NFR, BUG, TCH or SPK and its DoD is embedded. Iteration records use sprint-planning.md, verification.md, review.md and retrospective.md. No empty ceremony documents are scaffolded.

Only backlog/product-backlog.md and summary.md are generated. templates/documents.json drives the actual editorial layout. Functional values remain in visible Markdown with typed markers; technical metadata stays under .internal/.

See [document operations](references/document-operations.md) and [migration from older layouts](references/migration-release-layout.md). The previously published 0.3.0 uses schema 2; upgrading the plugin does not automatically migrate existing products. Deterministic tests and independent agent exercises are different forms of evidence.
