# Implementation Audit Remediation

**Date:** September 20, 2026.  
**Basis:** The approved `vision.md`, `functional-specification.md`, and `plugin-design.md`, plus the preserved `implementation-audit.md`.

The audit findings were checked against the pre-remediation record program at commit `80ee0bf`. The audit had already executed seven isolated reproductions; code inspection confirmed each reported branch and missing operation. This remediation added isolated regression fixtures and exercised the corrected outcomes. Static package findings were verified against the original skill paths and README command. The original audit is unchanged.

| Finding | Correction | Verification |
| --- | --- | --- |
| A01 | Review revision and named criterion parts are validated. Current acceptance is recomputed only from current-delivery reviews. Historical reviews remain available. Partial acceptance retains `accepted_parts` without accepting unidentified work. | `test_a01_stale_review_cannot_accept_current_delivery_and_partial_parts_accumulate`; `test_partial_acceptance_identifies_parts_without_accepting_whole` |
| A02 | `prepare-correction` reopens the same implemented increment after requested changes, increments delivery revision, and requires applicable authorization. `start` enforces the active slot. | `test_a02_correction_cycle_and_a05_lifecycle` |
| A03 | Decisions now have kind, author, source, structured scope, and supersession. Only a sourced user authorization covering the increment or linked items permits preparation/start. | `test_a03_technical_and_superseded_decisions_do_not_authorize` |
| A04 | Each mutation history entry stores affected before/after records, purpose, provenance, and operation receipt. | `test_a04_history_keeps_multiple_prior_values_and_provenance` |
| A05 | Added `resolve-blocker`, `follow-up-improvement`, `update-project`, `complete-backlog`, `resume`, and cancellation via `close` action. Inspect returns resolved and open records. | Full cycle in `test_a02_correction_cycle_and_a05_lifecycle`; transition tests |
| A06 | State fingerprints exclude stored receipt fingerprints, removing the circular hash. Legacy integrity fingerprints remain readable. Initialization and replay return consistent committed metadata. | `test_a06_replay_metadata_matches_committed_state` |
| A07 | Recovery locks the record, validates backup integrity, and preserves each damaged canonical file under a unique name before restoring. | `test_a07_invalid_backup_is_rejected_and_snapshots_are_unique`; `test_backup_and_recovery_are_explicit` |
| A08 | Every skill names each shared reference with its explicit plugin-relative path. | `test_every_skill_reference_resolves_from_installed_layout` from an extracted package and different working directory; six skill validators |
| A09 | README uses a chosen local marketplace directory and `prepare_local_install.py`, which preserves existing entries and refuses conflicting replacements. | `test_marketplace_preparation_preserves_existing_entries` |

## Additional gaps

- `inspect` now returns evidence, reviews, full blockers, improvements, and history. It computes read-only `stale_evidence`, `effective_verification`, and `effective_acceptance` against recorded product file hashes.
- `reconcile-manual` requires a reviewed raw-file hash, reviewer, reason, and operation ID. It preserves the exact edited file as a unique snapshot before sealing structurally valid state. The agent must review the contents; the program cannot authenticate the reviewer or infer intended changes.
- `record-evidence` hashes declared relative product paths. Changing a covered file makes the evidence stale in `inspect` without changing canonical revision; affected checks need rerun. External services and unlisted dependencies remain declared limits for agent judgment.
- A correction, renewed checks, final acceptance, backlog completion, blocker resolution, and improvement follow-up were exercised in one isolated product fixture.
- A first ephemeral Codex CLI attempt failed before skill loading because sandbox access blocked its state database and app-server client. An authorized retry then completed an explicit `initialize` scenario in `/private/tmp/agile-flow-agent-fixture`: it recorded context and one backlog item, proposed the first increment, and did not implement product code. A fresh ephemeral session explicitly invoked `status`, reconstructed the objective, work states, decisions, next step, and repository limits; SHA-256 of canonical state was identical before and after. Intent-based skill selection, existing-repository adoption, and agent-led correction/review/learning scenarios remain unexecuted. Static skill validation and record tests do not prove those agent behaviors.

## Capability reassessment

| Capability | Current implementation evidence | Limit |
| --- | --- | --- |
| F01 | Initialization and idempotent retrieval, project context updates; explicit agent initialization in a temporary product | Intent-based skill selection unexecuted |
| F02 | Existing-repository inspection instructions and references | Agent-led adoption scenario unexecuted |
| F03 | Stable backlog IDs, duplicate detection, priority/history, completion | Semantic duplicate matching relies on the agent |
| F04 | Readiness fields and scoped authorization checks | Source truth cannot be authenticated by the program |
| F05 | Active limit, correction cycle, blockers and resolution, pause/resume | Product edits remain agent actions |
| F06 | Required-check aggregation, delivered revision, file-hash reassessment | External dependencies require declared limitations |
| F07 | Revision and part-specific review, correction linkage | User intent interpretation remains an agent responsibility |
| F08 | Improvement creation and follow-up | Real agent learning scenario unexecuted |
| F09 | Read-only complete inspection and repository hash comparison; fresh-session explicit agent status kept state bytes unchanged | Intent-based selection and richer history-free resumption unexecuted |
| F10 | Pause, resume, administrative close, cancel, reopen | Agent-led priority interruption unexecuted |

## Validation record

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v` passed 28 tests. The plugin validator and all six skill validators passed using PyYAML installed only under `/private/tmp/agile-flow-validator-deps`. The extracted package resolved every skill reference and ran the record script from `/private/tmp`. The distributable ZIP excluded `docs/agile-lledo.pdf`, `.agile-flow/`, canonical state, backups, and project-only audit and superseded documents. Two explicit ephemeral Codex skill scenarios succeeded as described above. No local or global plugin installation was performed.
