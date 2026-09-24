---
name: review
description: Record delivery-specific user acceptance, requested changes, or learning without inventing approval.
---

# Review a delivery

Read [the collaboration protocol](../../references/collaboration-protocol.md) and [document ownership](../../references/document-ownership.md). Reuse settled decisions and the current mandate; do not infer stage transitions from document completion.

Read `../../references/collaboration-flow.md`, `../../references/session-protocol.md`, `../../references/authorization.md`, and `../../references/review-and-learning.md` before writing records.

Identify the increment, current or historical delivery revision, and criterion parts the user actually evaluated. Record ordinary-language acceptance only when it clearly covers those parts of that delivery. For partial acceptance, name each `accepted_parts` entry. Ask for clarification if the accepted scope is ambiguous. Preserve the actual quote or message reference verbatim. Acceptance with outstanding verification remains acceptance only; it does not change a check to passed.

Compare the result the user reviewed with current check attempts and covered files. Additional or repeated checks preserve acceptance of an unchanged delivery. A change to reviewed files requires reassessment; a passing check alone does not renew acceptance. After a non-behavioral same-delivery reassessment, record a new explicit user review; after a behavior change, review the new delivery revision. The record program binds new reviews to the observable evidence at review time.

Keep requested corrections tied to existing criteria. Capture a new need in the backlog and explain its scope impact. When a concrete fact supports an improvement, record its adjustment, target cycle, authorization boundary, and how its effect will be observed.

If the user withdraws or replaces an earlier change request on the same delivery, name the earlier review and exact parts in `supersedes`. Never infer supersession from a later acceptance of another part. Preserve both reviews and their original quotes.

Report the review decision, current independent states, follow-up work, and next step.

## Document-centered workflow

Read `../../references/document-operations.md`. Authored Markdown owns functional content; `.internal/registry.json` holds portable technical structure; `.internal/local/` is disposable local control. Preserve authored edits and refresh only `backlog/product-backlog.md` and `summary.md`. Resolve the product root; never patch installed plugin code or tests. Legacy projects require an explicit dry-run and authorized migration. Present readable outcomes, not temporary request files.

Product feedback belongs in iteration review; process learning belongs in retrospective. New needs return to backlog, corrections remain linked to the delivered criteria. Create a retrospective only for actual observations or adjustments, with follow-up evidence.

Use the schema-4 release/BL/US contract in the shared document operations reference. Old global DoD and direct iteration layouts require explicit migration. Preserve product context and authorization when decomposing a BL; a need is not itself an executable story.

Read [clean Markdown and Git](../../references/clean-markdown-and-git.md) before writing or versioning records. Use the agreed commit policy at coherent outcomes, review explicit paths, and preserve unrelated changes. Status remains read-only. Never infer push, branch, tag or release permission from commit permission.

At a sprint boundary, follow [iterative lifecycle](../../references/iterative-lifecycle.md): review the usable result, route process learning to retrospective, then conclude the sprint. An incomplete release returns to sprint planning under the current mandate; a completed release feeds strategic reassessment.
