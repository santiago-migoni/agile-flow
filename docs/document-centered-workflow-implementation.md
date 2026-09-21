# Document-centered workflow implementation

Date: 2026-09-21
Status: Implemented and validated for release v0.3.0; installation and live migration not performed.
Baseline: document-centered-workflow-specification.md. Upgrade baseline: 0.2.0.

## Result

Product meaning now lives in authored Markdown. The current entry point, `plugins/agile-flow/scripts/agile_flow.py`, uses schema 2 and writes technical metadata under `.agile-flow/.internal/`. The preserved legacy engine supplies established lifecycle/evidence transitions and explicit schema-1 migration support; it is not the current product writer. Its writer refuses migrated projects.

The six skills, distributed AGENTS.md, README and shared contracts now route the collaboration through constitution, roadmap/MVP, refined backlog, iteration planning, development/verification, review and learning. They distinguish the product checkout, plugin source and installed cache.

## Delivered structure and ownership

| Artifact | Purpose and creation boundary |
| --- | --- |
| constitution.md | Authored context, vision, mission, objectives, scope, facts, assumptions, agreements, sourced decisions and dated amendments. Existing external documents remain referenced. |
| roadmap.md | Authored horizons, milestone links and MVP learning definition; created when meaningful planning exists. |
| definition-of-done.md | Authored shared criteria plus optional criteria scoped to work types. Delivery preparation preserves the applicable baseline. |
| backlog/*.md | Typed needs with stable identities, purpose, criteria, order, estimates when useful, sources and specific story/NFR/bug/technical/investigation details. |
| backlog.md | Generated ordered index; retired work is separated from current selection. |
| iterations/ITER-*/sprint_planning.md | Draft goal and scope, linked item criteria, selected-version hashes, dated changes and independently authorized delivery increments. |
| verification.md | Observed attempts, delivery revisions, fingerprints and blockers. |
| review.md | Actual user feedback, scoped acceptance and explicit supersession. |
| retrospective.md | Process observations, adjustments and follow-up evidence. |
| summary.md | Generated current situation, iteration links and observed development/verification/acceptance. |
| .internal/ | Technical revision, identity registry, fingerprints, idempotency, locks, migration mapping and historical recovery snapshots. |

Initialization creates a meaningful constitution and the two indexes. It does not scaffold empty review, roadmap or retrospective documents. No new global preparation.md, presentation.md or vision.md is introduced.

## Persistence contract

One shared codec stores values as visible Markdown with hidden field-name/type markers. Text lists use bullets. Structured decisions and agreements use tables, including exact source quotations and supersession fields. There is no competing current functional JSON record. Manual notes survive targeted updates; agents read the relevant full documents as well as structured inspection results.

Every generated authored document is parsed and compared with its intended content before commit. Cross-references, types, identity retention and active development are validated. Requests use an operation ID and the current revision/document fingerprint. Record deletion is surfaced; explicit retirement preserves history.

Writes use a lock and a before/after journal. Metadata commits last. Inspection refuses pending transactions. Recovery completes an interrupted write only when affected bytes match the journal; unrelated edits remain intact and cause a conflict. Completed journals preserve dated operation context and document snapshots. `render --force` backs up manually edited indexes before replacement; it does not interpret their intended meaning.

Draft plans record selected source hashes and criterion links. Changed draft baselines must be refined before preparing execution. Later backlog/DoD changes do not rewrite a delivered increment's accepted criteria, applicable checks or historical baseline. Planning, authorization, implementation, verification and user acceptance remain independent.

## Migration

`migrate --dry-run` inventories legacy files without writing. Its fingerprint covers the source inventory, so changed views also invalidate a preview. It reports manual view edits, explicit type mapping, target conflicts and missing/ambiguous context.

Authorized application requires that fingerprint, backs up the complete legacy inventory, verifies copied bytes and preserves originals as inactive history. Existing increments map to separate iterations. Existing revisions, evidence, scoped reviews and authorizations remain linked. Unknown classifications remain unresolved until `classify-backlog`; explicit reclassification updates typed references and the identity map while preserving quotations and history. Repeating migration does not duplicate records.

Missing roadmap/MVP or DoD content remains missing. Project-level legacy learning has explicitly unverified iteration attribution; legacy source/baseline limitations are recorded rather than invented. A pending transaction is recovered explicitly. No live project was migrated during this work.

## Validation

Final automated command, run from `plugins/agile-flow/`:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -q
```

Result: **77 tests passed**: the 51 existing domain, recovery, collaboration-view and packaging regressions, plus 26 new document-workflow tests. Legacy fixtures deliberately continue exercising `legacy_records.py`; new integration tests exercise DocumentStore and the current CLI. These are different evidence boundaries, not a claim that the old view tests validate the new renderer.

New tests cover authored edits, generated-index preservation, mixed types and order, draft planning without authorization, required permission, scoped DoD, historical baselines, evidence/acceptance validity, several iterations, pause/reopen/cancellation, retrospective follow-up, identity preservation, conflicts, process-interruption recovery, migration of accepted deliveries, manual-view preview conflicts, classification, table quote round-tripping and actual CLI exit behavior.

The plugin manifest validator and all six skill validators passed. Packaging tests checked standalone references, entry-point loading and exclusions. Git whitespace validation passed.

## Independent agent exercise

An independent agent used the changed instructions and CLI in isolated product fixtures. It interpreted a personal single-server Odoo platform request, distinguished confirmed constraints from assumptions, created a constitution, typed backlog, roadmap/MVP and a draft iteration, and confirmed no execution authorization was manufactured. It also checked read-only status, preservation of a manual note, unauthorized preparation, draft closure/reopening and copied-legacy migration.

The first pass found an outdated vision-view instruction, noisy list headings and missing navigable criteria/baseline/authorization context in the draft plan. These were corrected. A second fresh-fixture pass confirmed all three fixes and rejected preparation after a selected criterion changed. It reported no further material findings within that bounded exercise.

This is a real but bounded agent workflow exercise, separate from deterministic assertions. It is not production acceptance, an installed-plugin end-to-end evaluation of every conversation, or a live migration of app-odoo.

## Operational boundaries

- Markdown field markers are part of the documented contract. Preserve them; use operations to add decision-table rows/columns. Free notes are legitimate context but do not silently become approval.
- The engine validates structure, scope declarations and observed fingerprints. It cannot authenticate a user quote or infer behavioral impact solely from file bytes; the agent must preserve actual sources.
- Recovery tests simulate process interruption and conflicting edits, not hardware power-loss durability or distributed writers.
- Release/version changes, commit, push, installation and live migration remain separate from this source implementation. Installed 0.2.0 behavior is unchanged until an authorized upgrade.
