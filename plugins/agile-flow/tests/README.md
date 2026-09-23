# Test organization

Run from the plugin directory:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -q
```

Lifecycle tests are grouped by behavior: authorization, correction workflow, review acceptance, evidence/acceptance validity, review compatibility, record history, transitions and recovery. `record_scenarios.py` contains the shared delivered-record fixture; `test_records.py` supplies the existing isolated CLI harness. Test names describe the invariant, without audit-round or finding-number prefixes.

The workflow suites retain their distinct coverage: `test_document_workflow.py` covers the schema-2 document layer, `test_release_workflow.py` the schema-3 release/story layer, `test_clean_workflow.py` schema-4 portability and Git, and `test_editorial.py` editorial rendering/reading and codec conversion. These are separate compatibility and integration surfaces, not obsolete duplicates.

`legacy_records.py` still supplies shared lifecycle/evidence behavior as well as the historical JSON writer. The document and release stores are reused layers of the current clean store. Their code remains in place; separating the shared engine from its historical writer is outside this organization change.

Fixture releases such as v0.1.0 belong to the synthetic product. Preserve persistent schema/codec identifiers and fixture identities. Renaming tests does not authorize rewriting snapshots, weakening assertions or retiring compatibility coverage.

`test_design_documents.py` covers optional consultative records without delivery scheduling, sourced decision preservation, manual edits, portability, timing of open questions and absence of implied authorization. `scenarios/consultative-workflows.md` defines separate behavioral exercises.

Project instruction preservation is covered by test_project_instructions.py. Conversational evaluation is specified in [project collaboration scenarios](scenarios/project-collaboration.md); deterministic tests alone do not establish instruction loading or agent behavior.
