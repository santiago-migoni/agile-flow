# Release and story workflow implementation

> Historical implementation or validation record. Its statements and results apply to the stage documented below; they do not describe every aspect of the current writer. Preserve the original decisions and evidence. See [current documentation](README.md) for maintained contracts and examples.

## Implemented contract

Plugin 0.4.0 implements schema 3; plugin 0.3.0 uses schema 2.

Authored constitution and strategic version roadmap remain at .agile-flow/ root. BL product needs live in backlog/, alongside the generated product-backlog.md index. Concrete release scope, detailed MVP definition, delivered outcomes and publication references live in release/<version>/release-<version-without-v>.md. Iterations inside each release contain sprint-planning.md, verification.md, review.md and retrospective.md when substantive content exists.

All work records use globally unique US-nnnn.md identities inside iteration/user-stories/, with type US, NFR, BUG, TCH or SPK, a BL parent, acceptance criteria and their own DoD. No root DoD or preparation document is created. Technical metadata, recovery journals and preserved backups remain in .internal/.

## Rendering and collaboration

At this release, executable editorial layouts lived in plugins/agile-flow/templates/documents.json. That preserved compatibility asset is now [templates/legacy/documents.json](../plugins/agile-flow/templates/legacy/documents.json). Functional content remains in visible typed Markdown; hidden markers contain keys and types. Overview and simple record tables support scanning; complex events use stacked sections. Targeted updates preserve free notes. Only the product backlog index and summary are generated. Their edits require reconciliation; force regeneration saves originals.

All six skills and macro instructions describe the same model. Narrative report context cannot inject evidence or acceptance. Preparation freezes story criteria, DoD and hashes. Newly selected stories receive a planning baseline; refining them requires explicit plan refresh. Authorization, implementation, verification and user acceptance remain distinct.

## Migration

Schemas 1 and 2 require explicit preview and application, release assignments for existing iterations, and an explicit destination for any legacy MVP definition. Verified original-byte backups, fingerprints and recoverable transactions protect source records. Existing accepted deliveries and evidence remain historical. Unstructured prose is preserved in original backups for deliberate reconciliation, not silently interpreted.

See [migration instructions](../plugins/agile-flow/references/migration-release-layout.md). No live app-odoo data was migrated.

## Verification

The full deterministic suite passed: 95 tests, including 18 current-layout tests and 77 retained lifecycle, storage, migration and packaging tests. Plugin validation and all six skill validations passed; git diff --check passed.

An independent agent exercised synthetic booking planning, authorization, not_run evidence and deferred review. It found missing baseline coverage when adding stories to an initially empty plan. This was corrected, protected by a regression test, and independently rechecked. A second pass confirmed rejection after story refinement and successful synthetic lifecycle behavior. It also confirmed readable stacked review records. This bounded exercise is not real product acceptance.

See [rendered examples](release-layout-example/README.md). Earlier document-design-examples remain historical and may show intermediate layouts.

## Delivery boundary

This implementation is included in release v0.4.0. Publication does not install the plugin, modify installed caches or migrate live products.
