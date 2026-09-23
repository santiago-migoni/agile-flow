# Consultative refinement implementation

Status: implemented in the source checkout; not published or installed by this change.

## Result

Consultation now has an explicit continuity contract: understand the message, identify the changed claim, consolidate its principal document and continue within the existing mandate. Explicit definitions are settled; examples and conditional journeys do not become universal requirements. A return to strategy changes the conversation focus without inventing delivery planning.

The shared collaboration protocol and discover/define/design/status skills describe synthesis at meaningful topic boundaries, reuse of supplied background, progressive unassigned BL capture, and partial corrections that preserve compatible agreements. The writer provides structural controls; the agent remains responsible for faithful interpretation and source support.

## Runtime and documents

- `refine-design-records` applies ID-addressed add, identify, update, resolve, defer, adopt, reject and supersede edits atomically across existing product-design and architecture documents. Unknown IDs, ambiguous legacy identification, invalid transitions and stale requests fail without partial document writes.
- Existing `update-backlog` refines a single BL by ID. It remains independent of releases and iterations.
- `update-collaboration` persists current focus, strategic/functional/technical level and authorized independent work in the constitution.
- Product design has separate rules, examples and conditional journeys. Active decisions, proposed decisions and decision history are separate editorial tables over the original record list. Stored row indexes preserve correct reconstruction.
- Resolved questions retain their answer and source. Reconciliation rows expose affected documents until actual content reconciliation is recorded. A batch emits one change entry per affected document, naming edited IDs and preserving provenance.
- Summary derives agreements, proposals, user questions, investigation, deferred topics and reconciliation separately. It includes constitutional agreements as well as design decisions; technical blockers are not automatically labeled user decisions. Dates come from available recorded source changes. Empty delivery sections are omitted.
- Plain or structured constitutional agreements render in the agreement column. Example explanation and source have explicit columns. Legacy extra fields remain visible rather than being silently discarded.

See [operation payloads](../plugins/agile-flow/references/document-operations.md), [ownership](../plugins/agile-flow/references/document-ownership.md) and [collaboration protocol](../plugins/agile-flow/references/collaboration-protocol.md).

## Verification

The complete source suite passes 157 tests, including 13 new refinement regressions. Coverage includes preservation of independent preproduction validation when mandatory staging is superseded, retained decision references, question resolution/deferral, proposal dispositions without implementation authority, atomic multi-document failure, optimistic concurrency, explicit legacy identity adoption, filtered-table reconstruction, compact batch history and old unfiltered design bindings.

The four changed skills pass the skill-creator validator. Package validation runs within the complete test suite.

An independent agent ran a six-message synthetic consultation through the actual CLI, producing 12 successful mutations. Fresh reconstruction and validation confirmed meaningful constitution content, three unassigned BL needs, optional dev/staging/production examples, a production-only topology, preserved validation requirements, resolved/deferred questions and continued strategic focus. It created no releases, iterations, stories, increments or execution authorization.

That evaluation found three concrete presentation issues: agreement strings occupying the ID column, example explanation vocabulary not being discoverable, and repeated batch-history entries. All were fixed and independently retested in a new temporary fixture through actual CLI writes, Markdown inspection and exact readback. Test fixtures were isolated; no live project data was added to this repository.

## Compatibility and limits

Existing schema-4/editorial-v2 records remain readable through their stored bindings. Read-only inspection does not rewrite documents. New record operations and fields require the updated writer; this is not a promise of downgrade compatibility. Historical schema and migration tests remain in the suite.

Full-list document updates remain available for compatibility. Prefer targeted operations for existing collections. The runtime validates identity, structure, references, provenance presence and atomicity; it cannot determine whether a user source supports a claim or whether reconciliation evidence is truthful. The independent exercise tests a simulated conversation using source runtime, not live installed skill selection or real product execution.

## Optional app-odoo reconciliation

No live files were changed. A subsequent requested reconciliation should inspect the current checkout and prepare explicit edits for:

1. Supplied product problem/background and objectives missing from the constitution.
2. Concrete needs suitable for unassigned BL records, without invented scheduling.
3. Optional topology examples that were generalized into requirements.
4. Any supersession that unintentionally revoked compatible preproduction validation.
5. Proposed alternatives and investigable/deferred questions omitted from the summary.

Use actual current sources, preserve authored notes and decision history, show the affected documents, then apply only the requested reconciliation scope. Updating or publishing the plugin does not trigger this product migration.
