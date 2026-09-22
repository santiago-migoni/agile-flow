# Editorial reader and renderer integration

The approved eleven Markdown templates now drive rendering and reading. This replaces heading-only compatibility layouts for newly initialized projects and explicitly migrated records. This integration is included in plugin v0.6.0. Validation described here covers the source implementation, not installation or migration of a live product.

## Implemented behavior

- Template-defined table columns, concise prose, optional sections and type-specific US/NFR/BUG/TCH/SPK blocks.
- Reversible bindings for scalar values, nested cells, source lists, repeated evidence/review details and frozen delivery baselines.
- Readable preservation of extra source fields and separate author Notes sections.
- Generated product-backlog and summary indexes using the same editorial templates, with observed effective delivery states and optional Git context.
- Relative identity links only to known product documents; no guessed links to missing roadmap/review records.
- Explicit clean-markdown-v1 to editorial-v2 conversion within schema 4, including reviewed fingerprints, verified original-byte backups, recoverable writes and preservation of valid versus stale planning baselines.
- Compatibility reading for the published v0.5.0 format; mutation and index rendering request explicit conversion instead of silently replacing that format.

## Validation

Run from `plugins/agile-flow`:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -q
```

The automated suite includes fourteen editorial-specific scenarios in addition to existing workflow, migration, recovery, package and Git coverage. These verify all eleven sparse formats, populated tables, five story types, repeated evidence, partial acceptance, template-driven columns, meaningful special characters, manual rows and notes, source-only lists, explicit v0.5.0 migration, preserved acceptance history and stale-baseline behavior.

The [rendered example collection](examples/editorial/README.md) demonstrates all formats through actual isolated domain operations. The package validator and Git whitespace check are separate from the Python tests.

The two user-supplied constitution/roadmap documents were also decoded with their legacy composition, converted on copies and read back with equality of functional content. The supplied constitution changes from 111 to 74 lines; the roadmap from 130 to 41. List-valued capabilities remain inside version-table cells, and separate objectives/success lists are not joined into invented relationships. Original Downloads files were not changed. These two private-product previews are outside this repository.

## Practical limits

This is automated and direct renderer validation, not an independent conversational agent evaluation or a live app-odoo migration. Missing source relationships remain explicit. New structural fields and heterogeneous row changes use record operations; free commentary belongs in a separate Notes section. Derived headers and cross-document link projections are refreshed context, not independent approval or evidence. See the [editing contract](../plugins/agile-flow/templates/README.md#editing-contract) and [migration guide](../plugins/agile-flow/references/editorial-format.md).
