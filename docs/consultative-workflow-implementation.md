# Consultative workflow implementation

## Outcome and scope

The approved workflow separates product management from product engineering while retaining one collaborator and shared context. Explicit user definitions settle their stated scope; the agent continues the current responsibility without redundant confirmation. Document completion does not trigger a stage transition. Existing authorization remains reusable.

This implementation is included in v0.7.0. Validation covers source behavior and isolated fixtures; no installation, server edit or live app-odoo migration was performed.

## Skill contracts

Eight primary entries are available: discover, define, design, plan, implement, review, status and close. Product management owns discovery, product behavior, journeys and priorities. Product engineering handles consultative interface/architecture design, requested planning and authorized execution. Review combines delivery evidence with actual user evaluation.

Compatibility entries remain: initialize → discover, backlog → define, advance → intent-based discovery/definition/design/planning/implementation. AGENTS.md routes intent; role references, collaboration-protocol.md and document-ownership.md define shared behavior. The protocol distinguishes explicit definitions, preferences, exploration, delegation, scoped confirmation, correction and execution requests.

Questions are limited to one or two material topics at a time, with useful context and recommendations. Necessary unresolved choices stop only dependent work; investigable questions and deferred topics receive distinct treatment. A requested multi-stage mandate can continue without ceremonial approvals.

## Runtime and document changes

- Optional authored product-design.md and architecture.md have complete executable templates and reversible editorial readers.
- update-product-design and update-architecture merge supplied top-level fields. They need useful content, not a release or iteration. Lists replace their prior values; decision updates preserve earlier identities and settled source text, using sourced superseding rows for replacements.
- Inspect reconstructs both documents from Markdown. Index rendering preserves authored bytes; transactions retain notes, concurrency checks and portable registry behavior.
- Design decisions have local IDs and explicit proposed/settled states. Settled rows require a basis and source. They cannot substitute for lifecycle authorization records.
- Summary separates immediate questions, agent investigation and deferred topics with revisit points.
- Constitution decision tables expose scope, source, quotation, author and timestamp. Change tables display the recorded change reason instead of leaving the change column empty.
- A legacy unsupported-project-field diagnostic no longer suggests iteration planning. Operation documentation names actual payload fields, including scope, exclusions and constraints.

The writer can validate structure and provenance presence, but cannot prove that a claimed source accurately represents the conversation. That remains an agent responsibility assessed through forward testing.

## Compatibility

Schema 4 and editorial-v2 remain unchanged. Existing stored document bindings are read without rewriting on inspect. Adding design documents does not require migrating an existing editorial-v2 project. Older writers cannot handle the new optional paths. Earlier layouts/codecs retain their explicit previewed migration process.

Existing constitution or sprint-planning prose is not automatically relocated. Any requested reorganization must preserve meaning, provenance, notes and history. Compatibility templates and historical lifecycle behavior remain covered by the existing suite.

## Validation

The automated suite covers optional-document creation without scheduling, authored round-trips, notes and manual edits, portable reconstruction, timing-separated summaries, stale requests, invalid edits, decision source/history preservation, absence of implied execution authority and reading published compact constitution bindings. Package tests cover the new skills, templates and module.

All eleven skill entrypoints pass the skill validator. Plugin manifest/structure validation and local documentation-link checks pass. The full automated suite passed: 144 tests. Local link validation checked 125 plugin and example references with no missing targets.

An independent agent first simulated five discovery/design messages, then performed six actual CLI mutations in an isolated synthetic Workshop fixture: initialize, update-project, three update-architecture operations and update-project. Every subsequent mutation used a fresh revision/fingerprint. Final validate returned status ok at revision 6 with no document changes; fresh inspect recovered three design decisions and six questions. No releases, iterations, stories, increments, lifecycle decisions or authorization were created.

The exercise exposed and led to corrections for missing design-operation documentation, missing discovery routing in advance, list-preservation guidance and the misleading project-field diagnostic. Technical dependency suitability was explicitly unverified; the exercise did not claim to implement or deploy the fictional product.

Transient raw evidence was produced at /tmp/agile-flow-consultative-forward-j9cv5ykz/test-transcript.json and fresh-inspect.json. These are local test artifacts, not durable product records. [Rendered consultative examples](examples/consultative/README.md) provide a separate reproducible-shape illustration of product design and architecture before delivery scheduling. [Behavioral scenarios](../plugins/agile-flow/tests/scenarios/consultative-workflows.md) describe wider follow-up exercises; not every listed scenario was independently executed in this change.
