# Compatibility and migration

Identify the actual product records before selecting migration instructions. Plugin release numbers, persistent document schemas and Markdown codecs describe different things. An installed plugin manifest alone cannot identify a product's stored format.

| Published plugin or source | Record format | Recognition | Current-writer handling |
| --- | --- | --- | --- |
| 0.2.0 | Schema 1: functional JSON with generated views | `.agile-flow/state.json` | Explicit preview and migration; preserve original records and views. |
| 0.3.0 | Schema 2: authored typed Markdown | `.agile-flow/.internal/state.json`, schema 2 | Explicit preview and migration; supply missing release assignments. |
| 0.4.0 | Schema 3: release-owned iterations and stories | `.agile-flow/.internal/state.json`, schema 3 | Explicit conversion to clean editorial Markdown. |
| 0.5.0 | Schema 4, clean-markdown-v1 codec | `.agile-flow/.internal/registry.json` and `manifest.json` | Read-compatible; explicit format conversion before mutation or index rendering. |
| 0.6.0 | Schema 4, editorial-v2 codec | Same registry location; manifest identifies editorial-v2 | Read and write directly with the current writer; no conversion required. |
| 0.7.0 | Schema 4, editorial-v2 with optional design documents | Optional product-design.md and architecture.md with registered bindings | Existing editorial-v2 records remain compatible. Earlier writers cannot handle the new optional paths. |
| 0.8.0 | Schema 4, editorial-v2 with targeted consultation records | Separate active/proposed/historical decisions, resolved questions and reconciliation records | Existing stored bindings remain readable without rewriting. New operations and fields require the updated writer; no automatic product reconciliation or downgrade guarantee. |
| 0.9.0 | Schema 4, editorial-v2 with executive synthesis and agreement pointers | Selected highlights, grouped proposal inventories, identity columns and expandable history | Existing stored bindings remain readable. Use current operations for explicit editorial reconciliation; render refreshes generated indexes only. New pointers and synthesis fields require this writer. |

## Current conversion procedure

Use the current selected plugin against the actual product checkout. Do not initialize a substitute project or patch an installed cache. Run `migrate --dry-run` and inspect the returned source format, changed documents, blocking issues and unresolved mappings.

- For schema 1 or 2, preserve the [release assignment and story mapping requirements](migration-release-layout.md). Do not invent releases, story types or an MVP destination to satisfy the migration.
- Follow the [current clean Markdown preservation and Git contract](clean-markdown-and-git.md#migration).
- Follow the [editorial conversion procedure](editorial-format.md#convert-an-existing-project) for reviewed fingerprints, application, backup and validation. The current migration composes older conversions; do not assume each historical plugin must be installed in sequence.

Apply only a reviewed, still-current source fingerprint. Preserve backup inventories, scoped user acceptance, evidence, identities and unresolved work. Installation, migration, commits and publication remain separate actions.

## Historical target-specific procedures

These guides document older target layouts, not the default current workflow:

- [JSON to authored Markdown](migration-json-to-authored-markdown.md): schema 1 → 2, using the explicitly required historical plugin version.
- [Release-owned story layout](migration-release-layout.md): schema 1/2 → 3 and the release mapping semantics still needed by current conversion.

Version checks inside a historical guide are intentional compatibility requirements. Do not remove them when renaming documentation. Persistent schema numbers, codec identifiers, operation names and product release directories are not renamed by a source-tree cleanup.
