---
name: advance
description: Prepare, implement, verify, or continue one authorized agile-flow increment while preserving evidence boundaries.
---

# Advance an increment

Read `../../references/session-protocol.md`, `../../references/authorization.md`, `../../references/readiness-and-quality.md`, and `../../references/record-contracts.md` before writing records.

Inspect the project, authorization, active increment, blockers, relevant instructions, and repository state. Documentation-only or analysis-only requests retain that scope. Select only an increment covered by current authorization; do not start a different backlog item.

Prepare missing objective, scope, exclusions, criteria, checks, uncertainty, and technical plan. Record an authorization decision if it is actually present in the request/source. When ready, start at most one unsuspended increment. Implement with normal repository safeguards, preserving unrelated changes. Record blockers and available checks. Record each check with its delivery scope, result, limitations, and observable fingerprints.

Before reusing evidence, inspect recorded file hashes and `effective_verification`. Record `mark-delivery-change` for behavior- or dependency-affecting work before new verification, which invalidates affected current evidence and acceptance. For user-requested changes, an observed failed check, or a documented defect within existing scope, use `prepare-correction` with the true basis on the same increment, then start it again. If its authorization was replaced, record the sourced replacement and use `rebind-authorization` before resuming or correcting. Stop at a real blocker, necessary product decision, or a delivery ready for review.

Report change summary, development/verification/acceptance separately, evidence, limitations, blockers, and exact user review needed.
