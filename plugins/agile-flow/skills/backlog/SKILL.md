---
name: backlog
description: Capture, refine, deduplicate, or reprioritize agile-flow product needs without starting development.
---

# Maintain the backlog

Read `../../references/collaboration-flow.md`, `../../references/session-protocol.md`, `../../references/authorization.md`, and `../../references/adaptive-method.md` before writing records.

Inspect the managed project and compare the request with existing backlog purposes. Record a new item only when it is not an unambiguous match; update a match with the reason and preserve provenance. If matching is ambiguous, disclose it and ask only if it changes the result.

Keep purpose, type, state, priority, criteria, dependencies, uncertainty, and provenance. Separate value, risk, dependencies, and effort when proposing priority. A user priority decision prevails; explain if dependencies prevent its immediate order. If reprioritizing active work, explain whether it suspends or supplements it; do not assume.

Adding or refining a backlog item never starts implementation. Report the affected item, priority rationale, active-work impact, and next step.

## Document-centered workflow

Read `../../references/document-operations.md`. Authored Markdown owns functional content; `.internal/registry.json` holds portable technical structure; `.internal/local/` is disposable local control. Preserve authored edits and refresh only `backlog/product-backlog.md` and `summary.md`. Resolve the product root; never patch installed plugin code or tests. Legacy projects require an explicit dry-run and authorized migration. Present readable outcomes, not temporary request files.

Maintain BL product needs and the generated product-backlog index. Define concrete US work only in its release iteration, using type US/NFR/BUG/TCH/SPK and an embedded DoD. Apply DEEP to the collection and INVEST to stories. Refine nearby work, split oversized stories, use optional relative estimates, explain order and retire with provenance. Do not force bugs, NFRs, technical work or investigations into story sentences.

Use the schema-4 release/BL/US contract in the shared document operations reference. Old global DoD and direct iteration layouts require explicit migration. Preserve product context and authorization when decomposing a BL; a need is not itself an executable story.

Read [clean Markdown and Git](../../references/clean-markdown-and-git.md) before writing or versioning records. Use the agreed commit policy at coherent outcomes, review explicit paths, and preserve unrelated changes. Status remains read-only. Never infer push, branch, tag or release permission from commit permission.
