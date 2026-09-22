---
name: close
description: Explicitly pause, cancel, close, or reopen agile-flow work while preserving unfinished records.
---

# Close or pause work

Read [the collaboration protocol](../../references/collaboration-protocol.md) and [document ownership](../../references/document-ownership.md). Reuse settled decisions and the current mandate; do not infer stage transitions from document completion.

Read `../../references/collaboration-flow.md`, `../../references/session-protocol.md`, `../../references/authorization.md`, and `../../references/record-contracts.md` before writing records.

Apply only an explicit administrative instruction. A status question does not pause or close anything. Pause preserves a resumption point and stops new development actions; it does not erase blockers or evidence. Closing reports implemented state, verification, acceptance, and outstanding work without manufacturing completion. Project cancellation or closure never deletes files.

Closing unfinished in-progress work preserves its development state and history but frees the active slot. Reopening it requires current applicable authorization and an available slot if it would become active; if suspended, reopening alone does not resume development. Report these distinctions explicitly.

When urgent reprioritization clearly suspends active work, record the reason and resumption point. If the request is unclear about replace versus supplement, explain the impact and wait before dependent work.

Report the administrative result, preserved outstanding work, evidence needing reassessment, and resumption path.

## Document-centered workflow

Read `../../references/document-operations.md`. Authored Markdown owns functional content; `.internal/registry.json` holds portable technical structure; `.internal/local/` is disposable local control. Preserve authored edits and refresh only `backlog/product-backlog.md` and `summary.md`. Resolve the product root; never patch installed plugin code or tests. Legacy projects require an explicit dry-run and authorized migration. Present readable outcomes, not temporary request files.

Explicit iteration transitions use target=iteration and iteration_id. Preserve unfinished item links and all historical delivery states; closure is not acceptance or verification.

Use the schema-4 release/BL/US contract in the shared document operations reference. Old global DoD and direct iteration layouts require explicit migration. Preserve product context and authorization when decomposing a BL; a need is not itself an executable story.

Read [clean Markdown and Git](../../references/clean-markdown-and-git.md) before writing or versioning records. Use the agreed commit policy at coherent outcomes, review explicit paths, and preserve unrelated changes. Status remains read-only. Never infer push, branch, tag or release permission from commit permission.
