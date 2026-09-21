# Migrate to release-owned stories (schema 3)

This is an explicit data-layout migration, separate from installing or publishing the plugin. Work in the actual product checkout using the new source entry point. Do not modify the installed cache or automatically migrate live projects during plugin development.

## Preview

Run `agile_flow.py --root <product> migrate --dry-run`. Schema-1 conversion is inspected in an isolated temporary fixture; source records are unchanged. Schema-2 authored fields are read directly. Review source_fingerprint, product_mapping, story_mapping, blocking, unresolved, manual_edits and preserved_files.

Every old item becomes a BL need retaining its legacy detail. Only items already assigned to an iteration become US stories. Items without an iteration stay product needs; the tool does not invent a release or implementation plan. Existing increments, evidence, reviews and authorization sources retain their identity and delivery scope.

For each existing iteration, provide an explicit target release and a sourced or clearly proposed objective. For example, use --request with:

```json
{
  "iteration_releases": {"ITER-001": "v0.1.0"},
  "releases": {"v0.1.0": {"objective": "The agreed first booking outcome"}}
}
```

These values are examples, not defaults. Multiple iterations may target one release. Optional item_types maps legacy item IDs to US/NFR/BUG/TCH/SPK when the source supports classification. Unknown types remain unresolved. If the old roadmap contains detailed MVP content, supply mvp_release matching one mapped release. Otherwise migration blocks rather than discarding or arbitrarily relocating that definition.

## Apply and verify

Repeat the preview with the intended mappings. Resolve all blocking entries. Add expected_source_fingerprint from that preview to the same request and run `migrate --apply`. Before replacing documents, the tool copies and verifies original files, technical state, history, projections and manual prose under `.internal/migration-backups/schema-<n>-<fingerprint>/`.

Run validate and inspect. Compare counts, identities, delivery revisions, acceptance, evidence and original user-authored text. The migration response returns mappings and unresolved work. Repeating migration is idempotent. Source changes invalidate the preview.

The old shared quality rules are copied into the applicable migrated stories' DoD; there is no new parent quality-policy file. If no stories exist, old quality context remains in the backup for deliberate refinement. Old delivery criteria/checks and source hashes remain historical; they are not rewritten as though new story definitions had been previously accepted. Cross-iteration dependencies and unclassified work require explicit review. Legacy authorizations with no mapped story do not grant permission to future US records.

Unstructured manual prose is preserved byte-for-byte in original backup files and surfaced for reconciliation. Read those files and incorporate meaningful notes into the new authored sections before claiming context is fully consolidated. Migration is structural, not an automatic interpretation of free prose.

## Recovery

Pending transactions block ordinary reads/writes. Run recover to finish a partial commit only when affected bytes still match the journal. Unrelated edits cause a conflict and remain intact. A complete verified source backup remains available; do not restore technical metadata alone over a different document set. Never use an old writer against migrated records.
