# Record contracts

## Document authority

Authored `.agile-flow/constitution.md`, `roadmap.md`, `definition-of-done.md`, `backlog/*.md`, and `iterations/ITER-*/{sprint_planning,verification,review,retrospective}.md` own product meaning. `backlog.md` and `summary.md` are generated. `.internal/state.json` holds schema 2, revision, hashes, idempotency and migration metadata only. Transaction snapshots are historical recovery evidence, never another editable source.

[Document operations](document-operations.md) defines the CLI and field contract. Hidden `af` markers describe a field's key/type; its value lives in visible Markdown. Edit the prose inside a field without removing markers. Free notes survive targeted updates but do not automatically become criteria, decisions, or authorization. The parser validates field nesting and identity. Preserve history; retire work with a reason instead of deleting its file.

Stable IDs distinguish typed needs, iterations, delivery increments, decisions, checks, reviews and improvements. Backlog order belongs to each item's `order`; ties or missing orders are reported, not silently prioritized. Estimates are optional. Planning does not create execution permission. An increment retains its own acceptance criteria, required-check baseline and document hashes as historical delivered scope; later item or DoD edits do not rewrite it. Transaction source snapshots preserve the corresponding bytes.

## Lifecycle and evidence

At most one open, unsuspended `in_progress` increment may be active, in an open iteration and project. Closing or pausing preserves unfinished development; reopening checks authorization and the active-work boundary. Several draft iterations are allowed.

Keep development, verification and user acceptance independent. The latest attempt per check determines current verification. Earlier attempts and delivery revisions remain available. Reviews bind to actual delivery parts, revision, evidence and file fingerprints. Another successful check on an unchanged accepted result preserves acceptance. Changed reviewed files require reassessment.

Use `mark-delivery-change` before checks for behavior/dependency changes. Same-delivery non-behavioral changes require `change_impact: non_behavioral` and an honest `impact_reason` on reruns. The engine validates declarations, not semantic truth. `prepare-correction` needs requested changes, a failed current check or a documented defect; `rebind-authorization` uses a sourced replacement. Neither creates approval.

## Preservation and recovery

Cooperating writers lock `.internal/.lock`. Requests compare revision and current document hashes. A write-ahead journal contains before/after bytes and source snapshots; `.internal/state.json` commits last. `recover` completes an interrupted transaction only when each affected file matches its before or after bytes. Unrelated edits produce a conflict and remain intact. Completed journals stay in `.internal/transactions/`; previous technical metadata stays in `state.backup.json`. Never restore only the metadata over mismatched documents.

Migration defaults to read-only preview. Authorized application requires the preview fingerprint, preserves a complete legacy backup and leaves old files as inactive history. Unknown types, roadmap/MVP, missing quality policy and uncertain learning attribution remain explicit. Do not run the legacy writer against a migrated product.
