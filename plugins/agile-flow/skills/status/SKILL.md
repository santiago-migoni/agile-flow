---
name: status
description: Read agile-flow records and compare relevant repository state without mutating records by default.
---

# Inspect status

Read [the collaboration protocol](../../references/collaboration-protocol.md) and [document ownership](../../references/document-ownership.md). Reuse settled decisions and the current mandate; do not infer stage transitions from document completion.

Read `../../references/collaboration-flow.md`, `../../references/session-protocol.md` and `../../references/readiness-and-quality.md`.

Use `inspect` and relevant read-only repository inspection. Recover the objective, `active_increment`, three work states, blockers, pending decisions, reviews, learning, next step, and any delivery evidence requiring reassessment. Closed unfinished increments retain their development label but are not active. Use `stale_evidence`, `current_stale_evidence`, `effective_verification`, and `effective_acceptance` when files changed; distinguish historical stale attempts from stale current checks. Compare recorded references and relevant repository fingerprints; label discrepancies and unknowns without rewriting decisions or claiming acceptance. Treat a document's recorded historical state as historical, not current validity.

Do not mutate state for a status question. If generated indexes are stale or manually edited, report that fact. Regenerate indexes only on an explicit request; preserve manual content when forced regeneration is requested.

Report known facts, unknowns, discrepancies, and the safest next action.

## Document-centered workflow

Read `../../references/document-operations.md`. Authored Markdown owns functional content; `.internal/registry.json` holds portable technical structure; `.internal/local/` is disposable local control. Preserve authored edits and refresh only `backlog/product-backlog.md` and `summary.md`. Resolve the product root; never patch installed plugin code or tests. Legacy projects require an explicit dry-run and authorized migration. Present readable outcomes, not temporary request files.

Use the schema-4 release/BL/US contract in the shared document operations reference. Old global DoD and direct iteration layouts require explicit migration. Preserve product context and authorization when decomposing a BL; a need is not itself an executable story.

Read [clean Markdown and Git](../../references/clean-markdown-and-git.md) before writing or versioning records. Use the agreed commit policy at coherent outcomes, review explicit paths, and preserve unrelated changes. Status remains read-only. Never infer push, branch, tag or release permission from commit permission.

Include pending proposals, investigable questions and deferred topics without conflating them with blocking user decisions. Report any outstanding document reconciliation and the source of the current focus.

When reporting status, use the executive synthesis and identify stale claims against actual source records. Link detail instead of enumerating every agreement; remain read-only.

Use the read-only instructions preview described in [project instructions](../../references/project-instructions.md) when reporting project guidance status. Report missing, outdated or conflicting guidance without applying it. Check whether recorded prerequisites still match the current mandate; distinguish a stale question from a real user blocker.
