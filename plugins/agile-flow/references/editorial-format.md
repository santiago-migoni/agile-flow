# Editorial Markdown integration

See [compatibility and migration](migration.md) to identify the source format. The schema remains 4; the document codec changes from clean-markdown-v1 to editorial-v2. Plugin version 0.6.0 includes this codec; installing it does not migrate existing product records.

## Current behavior

All eleven [templates](../templates/README.md) are executable presentation contracts. Roadmap rows retain list-valued capabilities and dependencies inside their cells. Constitution tables keep actors, objectives, decisions and uncertainty distinct. Each work document retains exactly its own US/NFR/BUG/TCH/SPK block and local DoD. Iteration records retain frozen baselines, actual evidence attempts and sourced reviews. Additional context preserves fields that do not fit the standard columns.

Markdown remains the functional authority. The registry records structural bindings, not a duplicate current product state. Older codecs remain read-compatible. New projects use editorial-v2 immediately. Read operations do not rewrite existing documents.

## Convert an existing project

Run against the actual product checkout using the source or installed plugin selected for that project. Do not modify an installed cache or replace product documents with a temporary fixture.

```bash
python3 "$PLUGIN_ROOT/scripts/agile_flow.py" --root /path/to/product migrate --dry-run
```

Review `changes`, `blocking`, `unresolved`, `preserved_files` and `source_fingerprint`. Save the returned fingerprint in a request file:

```json
{
  "expected_source_fingerprint": "COPY_THE_REVIEWED_SOURCE_FINGERPRINT"
}
```

Then apply that reviewed conversion:

```bash
python3 "$PLUGIN_ROOT/scripts/agile_flow.py" --root /path/to/product --request migration-request.json migrate --apply
python3 "$PLUGIN_ROOT/scripts/agile_flow.py" --root /path/to/product validate
```

A changed source invalidates the preview. Original bytes are verified and backed up under `.internal/local/backups/migration-*`; the normal write-ahead journal makes interrupted application recoverable. Read the returned backup path. The migration retains prior acceptance/evidence records and valid draft planning baselines. A plan already stale before conversion still needs replanning. Subsequent migration returns `already_applied`.

Review the Markdown diff and commit the documents together with their portable metadata using the established Git policy. Local backups and journals remain ignored. Conversion does not commit, push, publish or install anything.

## Edit and refresh

Use the [editing contract](../templates/README.md#editing-contract). Preserve managed labels, use explicit operations for new structural fields, and place free commentary under a separate Notes heading. Ambiguous structural edits fail without overwriting the source. Repeated identities and scoped acceptance remain consistent across tables and detail blocks.

`render` refreshes only the generated product-backlog and summary documents. It does not silently upgrade an older codec or replace authored document bytes. Generated-index edits still require explicit backup/reconciliation with `--force`.

## Evidence boundaries

Automated tests exercise semantic round-trips, layout contracts, lifecycle boundaries, portability, migration, recovery and Git. Synthetic rendered examples demonstrate composition; they are not proof of a real Codex conversation or user acceptance of an actual product.
