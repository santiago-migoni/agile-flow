# agile-flow

`agile-flow` is a local Codex skills plugin for delivering small, verifiable software increments while preserving decisions, evidence, and review across sessions.

It stores product records in `<product-root>/.agile-flow/`; it never stores product state in the plugin installation, creates commits, publishes, deploys, or installs itself.

## Use

Version 0.12.0 connects strategy and iterative delivery through specialized skills, explicit release and sprint commitments, scoped findings, progress observations and traceable closure. Existing projects adopt the iterative lifecycle explicitly; updating the plugin alone does not migrate them.

Invoke the skill matching the current intent:

| Skill | Responsibility |
| --- | --- |
| discover | Product manager: understand the problem, users and context. |
| define | Product manager: define journeys, behavior, scope and priorities. |
| design | Product engineer in consultative mode: interface and architecture alternatives. |
| roadmap | Product manager: possible version outcomes. |
| release | Bounded release commitment and fulfillment, separate from publication. |
| sprint | Bounded iteration commitment, stories and owner review access. |
| backlog | Capture and prioritize needs and findings without automatic scheduling. |
| retrospective | Observed process learning and follow-up. |
| implement | Product engineer: execute and verify authorized work. |
| review | Both roles: evaluate delivery, corrections and learning. |
| status | Read-only situation and next useful action. |
| close | Explicit pause, closure or reopening. |

Compatibility entries remain: initialize → discover, plan → roadmap/release/sprint, advance → routing by current intent. Explicit user definitions settle their scope without redundant confirmation; a definition does not automatically create an iteration. See [the collaboration protocol](references/collaboration-protocol.md) and [document ownership](references/document-ownership.md).

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

Version 0.12.0 implements schema 4 with the editorial-v2 codec: clean authored Markdown, release-owned iterations, BL product needs and US work records with type US/NFR/BUG/TCH/SPK. Each story owns its acceptance criteria and DoD. Only product-backlog.md and summary.md are generated indexes.

Executable Markdown templates and portable structural schemas support partial updates without af markers. Technical metadata and baselines are versioned; local caches, journals and backups are ignored. Git preview and commit operations follow explicit authorization or an agreed outcome policy and preserve unrelated changes.

See [document operations](references/document-operations.md), [clean Markdown and Git](references/clean-markdown-and-git.md), and the [compatibility and migration table](references/migration.md). Installing 0.12.0 does not migrate existing products. Automated tests and independent agent exercises are different forms of evidence.

## Document presentation

The [complete template catalog](templates/README.md) drives all thirteen document formats, including real tables, prose and conditional content. The editorial-v2 reader reconstructs their functional records, preserves Notes sections and rejects ambiguous edits. Existing v0.5.0 records require a previewed format migration; the schema remains 4. See the [editorial integration guide](references/editorial-format.md).

## Project collaboration instructions

New product setup includes a concise managed section in project-root AGENTS.md under the initialization mandate. Existing projects adopt or update it explicitly. Preview with `scripts/agile_flow.py --root <absolute-product-root> instructions`; apply with a reviewed fingerprint and existing authorization source as described in [project instructions](references/project-instructions.md). Installation and status never update a project automatically. Manual rules outside the block are preserved and edits inside it are surfaced for reconciliation. The template coordinates the skills without duplicating changing product facts.

## Strategic and operational cycle

Strategy and operations continuously inform each other through the backlog. Read [the iterative lifecycle contract](references/iterative-lifecycle.md) for scoped commitments, discovery handling, progress, closure and explicit adoption. Existing records remain readable; upgrading the plugin alone never migrates product records.
