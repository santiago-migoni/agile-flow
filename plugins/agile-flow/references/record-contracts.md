# Record contracts

Schema 4 uses authored Markdown for functional authority. The constitution defines product context; the roadmap describes version stages; release documents define concrete scope and optional MVP learning. Product BL needs live under backlog/, and US work records of type US/NFR/BUG/TCH/SPK live inside release/<version>/<iteration>/user-stories/. Each US owns its acceptance criteria and DoD. Only backlog/product-backlog.md and summary.md are generated indexes.

Read [document operations](document-operations.md) for payloads, templates and paths. No global DoD, global preparation document or direct iterations/ directory exists in new projects. Existing schemas require [explicit migration](migration.md), never silent file renaming.

The technical registry holds schema/revision, identities, hashes and operation IDs. Journals preserve before/after bytes and provenance for recoverable writes; no current functional JSON competes with Markdown. Locks coordinate cooperating writers. Requests check revision and actual document fingerprints. Missing authored identities, stale requests and conflicting edits are surfaced. Read-only status never rewrites documents. Manual generated-index edits are backed up before an explicit forced refresh.

At most one open, unsuspended in_progress increment may be active, in an open iteration and project. Administrative closure preserves unfinished history. Reopening rechecks authorization and active-work limits. Planning itself grants no permission; reuse actual permission without ceremony.

Delivery preparation freezes selected story criteria, their DoD and source hashes. Later refinement does not reinterpret prior delivery acceptance. The latest attempt per check determines current verification; previous attempts remain historical. Reviews bind actual user decisions to delivery revision, parts and evidence fingerprints. Another check on unchanged accepted work preserves acceptance. Changed covered behavior requires reassessment through delivery-change/correction operations.

The engine validates declared structure and observed bytes, not the authenticity of a quote or semantic truth of a non-behavioral change declaration. The agent must use actual sources and evidence. Release publication references record an observed publication; this local record program never publishes software.

The registry now lives at .internal/registry.json with clean document schemas. Manifest and baseline references are portable; locks, transaction journals and backups live under ignored .internal/local/. Review [clean Markdown and Git](clean-markdown-and-git.md) for checkout reconciliation and authorized commits.
