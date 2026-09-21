---
name: advance
description: Prepare a reviewable agile-flow proposal, or implement, verify, and continue an authorized increment while preserving evidence boundaries.
---

# Advance an increment

Read `../../references/collaboration-flow.md`, `../../references/session-protocol.md`, `../../references/authorization.md`, `../../references/readiness-and-quality.md`, and `../../references/record-contracts.md` before writing records.

Inspect the project, authorization, active increment, blockers, relevant instructions, and repository state. Documentation-only or analysis-only requests retain that scope. For definition or planning requests, use `plan-iteration` to draft `release/<version>/ITER-*/sprint-planning.md` as a non-executable proposal before implementation authorization. The `prepare` operation remains reserved for an authorized increment. Select only an executable increment covered by current authorization; do not start a different backlog item.

Prepare missing objective, scope, exclusions, criteria, checks, uncertainty, and technical plan. Record an authorization decision if it is actually present in the request/source. When ready, start at most one unsuspended increment. Implement with normal repository safeguards, preserving unrelated changes. Record blockers and available checks. Record each check with its delivery scope, result, limitations, and observable fingerprints.

Before reusing evidence, inspect recorded file hashes and `effective_verification`. Record `mark-delivery-change` for behavior- or dependency-affecting work before new verification, which invalidates affected current evidence and acceptance. For a non-behavioral covered-file edit within the same delivery, document the impact and reason on each affected `record-evidence` rerun, then obtain fresh explicit acceptance of the current result. Never infer acceptance from a passing rerun. For user-requested changes, an observed failed check, or a documented defect within existing scope, use `prepare-correction` with the true basis on the same increment, then start it again. If its authorization was replaced, record the sourced replacement and use `rebind-authorization` before resuming or correcting. Stop at a real blocker, necessary product decision, or a delivery ready for review.

Report change summary, development/verification/acceptance separately, evidence, limitations, blockers, and exact user review needed.

## Document-centered workflow

Read `../../references/document-operations.md`. Authored Markdown owns functional content; `.internal/state.json` is bookkeeping. Preserve authored edits and refresh only `backlog/product-backlog.md` and `summary.md`. Resolve the product root; never patch installed plugin code or tests. Legacy projects require an explicit dry-run and authorized migration. Present readable outcomes, not temporary request files.

Plan within an iteration. Check the roadmap direction, concrete release/MVP scope and each selected US record’s criteria and DoD. Draft planning requires no implementation permission; prepare/start does. Preserve selected item/DoD baselines and keep one active increment. New scope gets a new plan; corrections preserve revision-specific evidence.

Use the schema-3 release/BL/US contract in the shared document operations reference. Old global DoD and direct iteration layouts require explicit migration. Preserve product context and authorization when decomposing a BL; a need is not itself an executable story.
