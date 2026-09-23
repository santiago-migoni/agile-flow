# Product, design and delivery document operations

The current writer uses schema 4 with the editorial-v2 codec. Plugin versions, document schemas and codecs are distinct; see the [compatibility and migration table](migration.md). Always select the actual product root. Do not initialize a temporary directory as the product or modify installed plugin code.

## CLI and concurrency

Run `python3 <plugin>/scripts/agile_flow.py --root <product> inspect`. For mutations pass `--request <file.json> mutate` or JSON on stdin. Include operation, unique operation_id, purpose, and the latest expected_revision/expected_fingerprint. Initialize needs project.name and project.purpose but no previous revision. `validate` and `inspect` are read-only. `render` refreshes the two indexes; `render --force` first preserves manually edited indexes. `recover` completes a pending transaction only when affected bytes agree with its journal.

## Authored layout

```text
.agile-flow/
  constitution.md
  product-design.md                  # optional, meaningful design content only
  architecture.md                    # optional, independent of iterations
  roadmap.md
  summary.md                         # generated
  backlog/
    product-backlog.md                # generated
    BL-0001.md
  release/
    v0.1.0/
      release-0.1.0.md
      ITER-001/
        sprint-planning.md
        verification.md
        review.md
        retrospective.md
        user-stories/
          US-0001.md
        evidence/                    # only actual supporting artifacts
  .internal/                         # metadata, journals and preserved backups
```

BL records are product needs. Each US record is concrete iteration work with type US, NFR, BUG, TCH or SPK. US identity is unique across the product, regardless of type/release/iteration. Each story has one BL parent, one iteration and its own acceptance criteria and Definition of Done. There is no parent DoD file. A BL may produce several stories across releases. A release may contain several iterations. Do not silently move a baselined story; create linked follow-up scope and preserve its original identity.

Roadmap versions describe strategic evolution and may identify an intended MVP milestone. The release owns the detailed MVP hypothesis, early users, usable scope, feedback and learning decision. Release plans and delivered outcomes are separate fields. A plan is not authorization; a release description is not proof that it was published.

## Product and planning mutations

| Operation | Payload |
| --- | --- |
| initialize | project with name, purpose and known context; preserve original source quotations. No global quality_policy. |
| update-project | project with changed purpose/vision/mission, users, stakeholders, objectives, scope, exclusions, constraints, agreements, confirmed_facts, assumptions, proposals, open_questions, references or next_step. |
| update-product-design | document with purpose on creation; partial updates support status, scope, exclusions, journeys, screens, states, accessibility, alternatives, decisions, open_questions and references. |
| update-architecture | document with purpose on creation; partial updates support status, scope, exclusions, constraints, components, data, integrations, operations, alternatives, decisions, open_questions and references. |
| update-backlog | item with purpose; optional existing BL id, value, users, outcome, scope, exclusions, success_indicators, dependencies (BL IDs), assumptions, open_questions, priority, order, provenance, references, target_release. |
| reorder-backlog | item_ids containing every BL exactly once. |
| retire-backlog / complete-backlog | item_id (BL), reason; records the actual decision without deleting its history. |
| update-roadmap | document with direction, versions (rows with version such as v0.1.0, stage, intended outcome, capabilities, dependencies, status), milestones, assumptions, uncertainties, adaptation_criteria, release_references and changes as useful. No detailed mvp. |
| update-release | release with version id, objective, optional users, value, item_ids (BL), scope, exclusions, mvp, dependencies, risks, open_questions, exit_conditions, delivered_outcome, learning, upgrade_notes and publication. New status defaults to draft. Published status requires delivered_outcome and publication references; publishing is never performed by this operation. |
| plan-iteration | iteration with release_id, goal and scope; optional existing id, item_ids, exclusions, technical_plan, tasks, verification_plan, dependencies, risks, open_decisions, timeframe. A draft may begin without stories; update-story selects its new story in that draft. |
| update-story | story with purpose, parent_id (BL), iteration_id and type for new work; existing US id for refinement. Include criteria, dod, scope, exclusions, value, priority/order, estimate/basis, dependencies (US), open_questions and provenance as useful. |

Story-specific fields follow the approved type: US uses story; NFR quality_attribute/applicability/verification_method; BUG reproduction/observed/expected/impact; TCH approach/components; SPK question/work_limit/findings/recommendation. Do not force technical or defect records into a fictional user-story sentence.

Criteria accept text or rows `{id: AC-01, condition: ..., result: ...}`. DoD accepts text or rows `{id: DOD-01, requirement: ..., evidence: ...}`. Text is normalized to numbered rows; keep existing IDs when refining or reordering structured conditions. Drafts may have unresolved criteria/DoD, but execution preparation requires both. No arbitrary point estimate is required.

## Delivery operations

Record sourced authorization with record-decision: decision.kind=authorization, author=user, reason, source, actual quote where available, and scope covering US IDs, increment IDs or the project. BL scope does not automatically authorize its future stories.

Prepare with iteration_id and increment containing selected US item_ids, objective, scope and authorization decision ID; optional required_checks, technical_plan and exclusions. Criteria and mandatory checks are taken from the selected stories and preserved as delivery baselines. Check identifiers include the story and condition ID. Newly selected stories receive a planning baseline. After refining a selected story, update plan-iteration to review and refresh the draft baseline before preparation. Preparing does not execute software changes.

Use start, mark-implemented, record-evidence, record-review, prepare-correction, mark-delivery-change, rebind-authorization and resume for actual work under the preserved lifecycle engine. Read the relevant domain payload in scripts/legacy_records.py when needed. Evidence carries increment_id, check, result, scope, paths and actual procedure/environment/limitations. Review carries increment_id, a real user_quote or message_reference, decision and scoped parts; never infer acceptance from tests.

record-blocker uses blocker with increment_id, condition, resolution_requirement; resolve-blocker needs blocker_id and resolution. record-improvement needs iteration_id and improvement with observation, adjustment, target_cycle; follow-up-improvement needs improvement_id, state and effect_evidence. pause/close/reopen accepts target=iteration plus iteration_id, or the existing project/increment targets. Closure does not establish completion.

## Markdown contract and templates

The current writer emits clean Markdown with no af markers. Executable editorial templates in [templates/markdown/](../templates/README.md) drive prose, tables, repeatable records and conditional blocks. The reader uses portable reversible bindings. templates/legacy/clean-markdown-v1/ and templates/legacy/documents.json remain legacy compatibility inputs only. Portable document schemas store keys and types, not functional content. Read [clean Markdown and Git](clean-markdown-and-git.md) for editing, concurrency, migration and versioning contracts.

Use operations to add new structured fields or complex records. Existing text and homogeneous table rows can be edited manually. Preserve structured headings; ambiguous or duplicate headings require reconciliation. Additional Notes sections remain authored context and do not grant authorization. Root DoD and old iteration layouts remain historical.

## Report context

Use `update-report` with `iteration_id`, `document` and `fields` to maintain readable context without changing evidence or acceptance. Supported fields: verification — `scope`, `conclusion`; review — `presented_result`, `resulting_work`, `unresolved_feedback`; retrospective — `retain`, `follow_up`. Use the existing record-evidence, record-review and improvement operations for sourced events. Narrative context never grants authorization or acceptance.


Existing schema-4 clean-markdown-v1 projects remain inspectable, but mutation and index rendering require the explicit [editorial format conversion](editorial-format.md). The migration preview identifies `target_codec: editorial-v2` and the exact changed document text; its source fingerprint is required for application.

## Optional design document operations

Follow [document ownership](document-ownership.md). `update-product-design` and `update-architecture` create or merge top-level fields. Omitted fields remain unchanged; a supplied list replaces that list, so preserve previous decisions, IDs and unresolved rows. The writer manages `updated_at` and `changes`; do not send these fields. Each change uses the request purpose and optional provenance. Creation requires a meaningful purpose; no release, iteration or implementation authorization is inferred. `inspect` exposes `product_design` and `architecture` only when present.

Document status is draft (default), in-review, agreed or superseded. `agreed` must reflect actual agreement; it never grants implementation permission. Each knowledge row may use proposed, confirmed, decided, superseded or rejected. These labels must reflect the actual conversation, not an assumption.

| Field | Row vocabulary |
| --- | --- |
| journeys | id, actor, trigger, steps (text list), outcome, status |
| screens | id, journey, screen, information, actions, status |
| states | context, state, behavior, recovery, status |
| accessibility | need, behavior, verification, status |
| alternatives | topic, option, benefits, costs, recommendation, status |
| components | component, responsibility, interfaces, boundary, status |
| data | data, owner, persistence, lifecycle, status |
| integrations | system, contract, failure, trust_boundary, status |
| operations | concern, approach, cost, verification, status |
| decisions | id, decision, scope, basis, source, rationale, status, supersedes (optional local decision ID) |
| open_questions | question, impact, timing (now/later/investigate), revisit_when |

Settled decision rows require a source and basis: user-definition, user-confirmation, delegated or technical-discretion. Cite the actual instruction for delegation, or the agreed boundary and technical evidence for routine discretion. An explicit user definition needs no second confirmation. Proposed decisions have no execution effect. These local IDs do not substitute for DEC authorization records. IDs are local to the design document; preserve old rows when superseding. The update operation rejects deletion of existing decision IDs and replacement of settled decision text, scope, basis or source. Add a new sourced row with supersedes and retain the earlier row as superseded. Later questions require a revisit point. The summary separates immediate questions, investigable questions and deferred topics. Existing plain project questions remain unclassified pending questions until deliberately refined; do not guess their timing.

Example request after inspecting current revision and fingerprint (replace transport values with actual values):

```json
{
  "operation": "update-architecture",
  "operation_id": "architecture-backend-choice-1",
  "purpose": "Record the user's backend definition and continue interface design",
  "expected_revision": 3,
  "expected_fingerprint": "fingerprint-from-inspect",
  "provenance": "User message identifying the backend",
  "document": {
    "purpose": "Design the control plane for the agreed owner workflow",
    "decisions": [{
      "id": "ARCH-001",
      "decision": "Use Django for the backend",
      "scope": "Backend framework only",
      "basis": "user-definition",
      "source": "User: El backend será Django.",
      "rationale": "Explicit user choice",
      "status": "decided"
    }],
    "open_questions": [{
      "question": "Does the owner need a separate interactive frontend?",
      "impact": "Build complexity and operation",
      "timing": "now"
    }]
  }
}
```

These operations are additive to schema 4 / editorial-v2. Existing document schemas remain readable without rewriting or migrating records at installation. Earlier writers cannot handle the new optional paths. Older codec/layout conversions still require the explicit previewed migration process. No automatic relocation of existing constitution or sprint-plan prose occurs.

## Targeted consultation updates (schema 4 / editorial-v2)

All operations use the standard operation_id, purpose, expected_revision and expected_fingerprint envelope. These operations confer no execution authorization.

`update-collaboration` accepts `context` with any of `focus`, `level` (strategic, functional, technical), `can_continue`. It merges supplied fields into the constitution. Use actual authorized independent work, not a proposed stage transition.

`refine-design-records` requires actual `provenance` and a nonempty `edits` list. All edits are atomic. Each edit has `document` (`product_design` or `architecture`), `collection`, `action`, stable `id`, and optionally `record`. Collections are the structured row collections of the selected document, including `rules`, `examples` in product design and `reconciliation` in either document. Initialize a meaningful document through its existing update operation first.

| Action | Contract |
| --- | --- |
| add | Add `record` under a new ID. |
| identify | Assign an ID to one legacy unnamed row using `match` equal to the entire current row; ambiguous matches fail. No record payload. |
| update | Merge supplied record fields, preserving other rows and fields. Settled decisions require supersede. |
| resolve | Question or reconciliation only; provide resolution, retain history, attach provenance. |
| defer | Question or reconciliation only; provide revisit_when. Questions receive timing=later. |
| adopt / reject | Pending proposal only. Adoption requires basis: user-definition, user-confirmation, delegated or technical-discretion. Provenance records the disposition source. |
| supersede | Settled decision only; record supplies a new ID and sourced settled replacement. The old record remains superseded. Optional retained_ids names compatible decisions retained at that point. |

Questions use question, impact, timing (now/later/investigate), optional status (open/resolved/deferred), resolution and source. Legacy questions without IDs or status remain readable. Reconciliation rows use id, document (project-relative path), reason, status (open/resolved/deferred), optional resolution, revisit_when and source. Resolved rows require resolution and source; deferred rows require a revisit point. The caller must inspect the affected document before claiming resolution.

Example edit inside a standard refinement envelope:

```json
{
  "document": "product_design",
  "collection": "decisions",
  "action": "supersede",
  "id": "PD-001",
  "record": {
    "id": "PD-003",
    "decision": "A project may have production alone; staging is optional",
    "scope": "Environment topology",
    "status": "decided",
    "basis": "user-definition",
    "source": "Actual user correction reference",
    "retained_ids": ["PD-002"]
  }
}
```

Here PD-002 is the separately recorded preproduction validation agreement. It remains unchanged. If the prior claim bundled topology and validation in a single decision, retain validation explicitly in the replacement instead. Source interpretation and completeness are semantic responsibilities, not guarantees of the storage validator.

For needs, keep using update-backlog with item.id to refine a single existing BL; omit id only when creating a new need. Full document update operations remain available for compatibility. Prefer targeted edits for existing collections to avoid inadvertently replacing unrelated entries. Inspect and reconcile old Markdown bindings before changing editorial format; read-only inspection does not rewrite existing documents.

Product-design content rows use these preferred fields (optional IDs allow targeted refinement):

| Collection | Principal fields |
| --- | --- |
| rules | id, rule, scope, status, source |
| examples | id, example, illustrates, status, source |
| journeys | id, actor, trigger, steps, outcome, applicability, status |

Use applicability to state when a journey applies; absence does not make it mandatory. Keep a rule's wording in one home and reference its ID from a decision rationale rather than maintaining two independently phrased requirements. Batch refinement records one change entry per affected document, naming each edited collection/ID. Unknown legacy row fields remain readable in Additional context; do not silently remove them during reconciliation.

Constitution project.agreements accepts text entries or structured rows with id, agreement, scope, source and optional kind, quote, author, at, supersedes. A text entry occupies the agreement column, not the ID. Prefer sourced structured entries for material agreements. Existing summary/decision wording aliases remain readable.
