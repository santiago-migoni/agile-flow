# Document-centered product and iteration workflow

Date: 2026-09-21
Status: Consolidated functional baseline for implementation. The user endorsed the document model and requested this consolidation; implementation, migration, and release are not claimed complete.
Product: Agile Flow
Current published baseline: 0.2.0

## 1. Purpose and authority

Help a user and a Codex agent maintain shared product understanding, progressively plan useful deliveries, verify results, and adapt based on feedback. Human-readable documents carry the functional meaning. Technical bookkeeping supports these documents rather than replacing them.

This specification consolidates the conversation agreements about the project constitution, roadmap, MVP, DEEP backlog, INVEST stories, Definition of Done, and iteration-specific sprint planning. It supersedes the JSON-as-sole-functional-authority and global preparation-view model for the next implementation. Unchanged authorization, evidence, preservation, and language requirements remain applicable. Earlier design documents describe the released implementation until this change is delivered.

All plugin-authored documents, names, templates, and code use English. Conversation follows the user's language. Preserve original user quotations and external source text. Do not use spec-flow or introduce its document chain.

## 2. Product records layout

Example: Bookly, an appointment booking application.

```text
bookly/
  .agile-flow/
    constitution.md
    roadmap.md
    backlog.md
    definition-of-done.md
    summary.md
    backlog/
      US-001-book-appointment.md
      US-002-cancel-appointment.md
      NFR-001-accessibility.md
      BUG-001-duplicate-booking.md
      TECH-001-database-migrations.md
      SPIKE-001-calendar-integration.md
    iterations/
      ITER-001/
        sprint_planning.md
        verification.md
        review.md
        retrospective.md
        evidence/                 # Only when useful supporting evidence exists
      ITER-002/
        sprint_planning.md
    .internal/
      state.json
      state.backup.json
      .lock
```

This is a populated example, not a mandatory initialization scaffold. Create documents when meaningful content exists; label unresolved information rather than inventing it. Do not create empty review or retrospective files merely to satisfy a directory template. Additional technical recovery files may exist under `.internal/`; they are not product deliverables.

The spelling is `sprint_planning.md`. There is no new global `preparation.md`, `presentation.md`, or mandatory separate `vision.md`. Existing authored vision documents are preserved and referenced. MVP definition belongs in the roadmap rather than requiring another file.

## 3. Sources of truth and ownership

| Artifact | Authority | Editing behavior |
| --- | --- | --- |
| Constitution, roadmap, Definition of Done | Authored product documents | Updated by the agent within the request; user edits are legitimate input. |
| Backlog item files | Canonical definition and planning metadata for each need | Update the item once, then refresh the generated index. |
| Iteration planning, verification, review, retrospective | Canonical iteration scope, evidence, decisions, and learning | Preserve dated changes and provenance; do not overwrite historical acceptance. |
| `backlog.md` | Generated index | Derived from item files; never a competing editable item definition. |
| `summary.md` | Generated current-state summary | Derived from authoritative documents and observed evidence. |
| `.internal/state.json` | Technical metadata only | IDs, schema versions, document fingerprints, transaction/recovery metadata, and reconstructible indexes. |

Do not keep full editable product content in both Markdown and JSON. Cached values must be labeled derived and refreshable. Technical snapshots or backups may contain document bytes for recovery, but must not be treated as an alternate functional authority.

Use minimal machine-readable metadata where reliable identity, ordering, links, or state require it. Define one documented metadata contract during implementation; keep prose human-readable. Prefer a shared renderer/parser contract to unrelated per-command assumptions.

A manual edit to an authored document is a change to understand and validate, not corruption by definition. Preserve it, reconcile affected links and derived indexes, and never silently overwrite it. An edit to a generated index must be preserved and its intended change reconciled into the source item; it must not be silently promoted into authorization.

## 4. Project documents

### 4.1 constitution.md — shared project agreement

Include:

- Background and problem.
- Vision: desired future and value.
- Mission: how the product intends to create that value.
- Intended users and actual stakeholders.
- Objectives and observable success factors.
- High-level scope, exclusions, constraints, and assumptions.
- Real collaboration and external stakeholder agreements.
- Sources, unresolved material decisions, and dated amendments.

For Bookly: help a professional and customers arrange appointments without coordinating every booking through messages. Do not invent a team, external stakeholders, interviews, approvals, or budget. Distinguish confirmed facts from hypotheses and proposals. Present decisions and agreements in compact tables with source, status, and supersession where useful.

### 4.2 roadmap.md — anticipated evolution

Organize anticipated outcomes and capabilities into ordered horizons or milestones. Each entry identifies value, linked backlog scope, dependencies, assumptions, uncertainty, and evidence that would justify progression.

Dates are optional and distinguish forecasts from commitments. Preliminary budget or effort ranges may be added when useful and grounded in explicit assumptions. Never invent amounts to complete a template.

Bookly example: validate booking first; add cancellation next; consider reminders after feedback. Roadmap items remain revisable hypotheses and do not authorize implementation.

#### MVP

Define the intended early users, hypothesis to test, smallest usable end-to-end outcome, included/excluded capabilities, feedback approach, and decision criteria for the next step. Link the contributing backlog items. An MVP can span several iterations; the first increment is not automatically the MVP. Minimum scope does not waive quality conditions necessary for that use.

### 4.3 backlog.md — generated prioritized index

Provide one row per current item with relative order, stable ID/link, type, short title, estimate when present, state, and iteration assignment when useful. Historical or retired items remain available without cluttering the current selection.

The detailed item owns these values, including its relative ordering metadata. Reordering updates authoritative metadata consistently, then regenerates the index. Define deterministic handling of missing or duplicate ranks; never silently manufacture a user priority decision.

### 4.4 definition-of-done.md — shared quality conditions

Define observable conditions common to deliveries: relevant criteria verified, appropriate checks, necessary documentation, known defects and limitations, and required operational evidence. Scope each rule to the kinds of deliverable it applies to; a bounded investigation does not require deployment checks.

Keep three concepts separate:

- Acceptance criteria specify the behavior of an individual need.
- Definition of Done specifies shared quality requirements.
- User acceptance records an actual decision about a presented result.

Passing checks is not user acceptance. User acceptance with outstanding checks does not make those checks pass. Iterations reference the applicable version or fingerprint of the Definition of Done; later changes do not silently reinterpret earlier results.

### 4.5 summary.md — generated current situation

Show current product objective, active iteration and goal, development/verification/acceptance separately, blockers, material pending decisions, and next useful action. Link detailed documents. Do not reproduce the complete constitution or introduce new decisions. Read-only status may report stale summaries without rewriting them.

## 5. Backlog items

Every item has a stable identifier, type, concise title, purpose/value, state, relative priority/order and rationale, source, and appropriate detail. Keep estimates, dependencies, uncertainty, acceptance criteria, and iteration links as they become useful. Renaming a title or changing scope must not silently create a new identity.

| Type | Prefix | Specific information |
| --- | --- | --- |
| User story | US | As a <user>, I want <capability>, so that <value>; acceptance criteria and scope. |
| Non-functional requirement | NFR | Quality attribute, measurable condition, applicability, and verification method. |
| Bug | BUG | Reproduction, observed and expected behavior, impact, and regression check. |
| Technical work | TECH | Technical need, benefit, scope, and evidence of completion. |
| Bounded investigation | SPIKE | Question, work boundary, findings, and resulting recommendation or decision. |

Do not force all work into a user-story sentence. Preserve replaced or removed work with a reason; removal from the current backlog must not erase its provenance.

### Story format

```markdown
# US-001 — Book an appointment

## Story
As a customer, I want to book an available appointment,
so that I can secure a time without contacting the professional.

## Value
## Acceptance criteria
## Included and excluded scope
## Dependencies and open questions
## Relative estimate and basis
## Planning metadata
## Source and changes
```

The headings are a guide, not a requirement to fill distant work with empty boilerplate. Implementation must choose one metadata location for fields used by the generated index, without repeating editable copies in prose.

### DEEP — quality of the backlog as a whole

- Detailed appropriately: near-term work is sufficiently understood; distant work remains lightweight.
- Estimated: use relative estimates when they help compare or plan. Show uncertainty and the basis. Do not confuse estimability with an actual estimate.
- Emergent: needs can be added, changed, split, reordered, or retired with provenance.
- Prioritized: preserve useful relative ordering; avoid labeling everything merely high priority.

Story points are optional and never automatically equated with hours. Use a consistent declared scale when estimates are introduced. Lack of an arbitrary point value must not block otherwise ready work.

### INVEST — quality of individual stories

- Independent: understandable in isolation and designed to minimize delivery dependencies; disclose remaining dependencies.
- Negotiable: capture the need without prematurely prescribing every solution. Changes during an iteration require visible impact handling.
- Valuable: identify the user and expected benefit.
- Estimable: sufficient knowledge exists for a relative estimate; investigate consequential unknowns when needed.
- Small: fits a useful iteration-sized result. Split oversized work along user-value boundaries.
- Testable: observable acceptance criteria support verification and user review.

Use INVEST to reason about deficiencies and refinements, not to automatically stamp six passed checkboxes.

## 6. Iterations

### Identity and relationship to delivery

An iteration is a planning and review container with one goal and selected backlog items. It can contain multiple technical changes; evidence and acceptance remain tied to specific delivered scope and revision. Do not conflate the iteration, a backlog item, a commit, and a delivered increment.

Retain the existing single-active-development boundary: at most one iteration has active development, and one delivery increment is actively developed at a time within it. Closed or suspended unfinished work does not occupy that slot. Several candidate plans may exist without starting work.

Fixed sprint duration is not required by the filename. Record an agreed timeframe when one exists; otherwise state that the iteration ends around its bounded outcome. Do not invent dates or impose full Scrum ceremonies.

### sprint_planning.md — iteration-specific preparation

Include:

1. Iteration ID, status, and agreed timeframe or outcome boundary.
2. Goal and expected usable result or bounded learning outcome.
3. Selected backlog IDs with the baseline/version used for planning.
4. Included and excluded scope.
5. Technical approach and proportional implementation tasks.
6. Dependencies, risks, assumptions, and material open decisions.
7. Verification approach and applicable Definition of Done baseline.
8. Actual authorization and agreements, or an explicit statement that execution is not authorized.
9. Dated plan changes and effects on the goal.

Reference detailed item criteria rather than maintaining a second editable copy. Preserve the selected baseline so later backlog edits cannot silently rewrite what a previous iteration agreed or verified.

Planning may proceed under a definition request without implementation permission. No authorization field is created merely because a document exists or because the user accepts an outline. Reuse valid execution permission already present rather than requiring a new ceremony.

### verification.md — observed checks

Record each check's criterion/quality-condition links, delivery scope and revision, environment, command or procedure, observed result, evidence links/fingerprints, and limitations. Required checks unavailable for lack of resources remain visibly not run; do not omit them and declare verification complete.

Preserve failed and superseded attempts. Additional successful checks on an unchanged accepted delivery do not invalidate acceptance. Relevant product changes require reassessment. Supporting logs under `evidence/` are optional, scoped, and stripped of secrets.

### review.md — user evaluation of the delivery

Record what was presented, delivery revision and parts, observed user feedback, acceptance or requested changes, source/quote, unresolved verification, and resulting work. Preserve multiple dated reviews, partial acceptance, and explicit supersession. New needs return to the backlog; corrections to existing criteria stay linked to the original work.

### retrospective.md — improvement of the collaboration

Record concrete observations, useful adjustments, intended application, and follow-up evidence. This evaluates how the work was performed, whereas review evaluates the delivered product. Do not invent lessons or require a meeting. Create the document when a retrospective occurs; if no adjustment is justified, say so.

## 7. Progressive planning and skill routing

The flow is: shared constitution → roadmap and MVP → refined backlog → iteration planning → development and verification → review → learning and adaptation.

Progressive wave planning is a behavior across these artifacts: keep distant work general, refine work approaching execution, and revise plans as information improves. It is not another mandatory file.

| Skill | Responsibilities in this model |
| --- | --- |
| initialize | Understand/adopt the product; create or reference a meaningful constitution; propose roadmap/MVP and initial needs proportionally. |
| backlog | Maintain item files and their generated index; apply DEEP and INVEST where relevant; preserve order and provenance. |
| advance | Prepare a candidate iteration plan or execute its authorized scope; maintain delivery evidence. |
| review | Record product feedback and, when applicable, a brief retrospective and follow-up. |
| status | Reconstruct context from documents and relevant repository observations without mutating by default. |
| close | Apply explicit administrative transitions and preserve unfinished work, reviews, and resumption conditions. |

The distributed AGENTS.md provides this macro map. Skills and references supply details. Do not require a new product-root AGENTS.md to use the plugin or overwrite an existing one. A user request for an explanation remains an explanation; do not start a cycle automatically.

Correct misunderstandings across affected documents, not merely the latest answer. Distinguish user statements from interpretations, especially when borrowing ideas from benchmarks. Do not introduce blocking decisions about optional future expansion. Produce a reviewable outcome rather than ending with a storage confirmation.

## 8. Plugin and project boundaries

The managed product, plugin source repository, and installed cache are different workspaces. A request to change product documentation does not authorize editing installed plugin code or tests. Never patch the plugin cache as a development workflow.

If a generated format prevents satisfying a product request, identify the source limitation and route the improvement to the actual plugin source under the relevant authorization. Publish/install through the normal workflow when authorized. Temporary request files are transport, never the sole location of product content or accepted plans.

## 9. Persistence and migration from 0.2.0

The implementation must support validated Markdown updates, safe derived-index regeneration, conflict detection, atomic or recoverable multi-document writes, and idempotent operations. A lock coordinates cooperating writers but does not excuse ignoring user edits. Technical recovery never establishes acceptance or permission.

Migration requirements:

1. Detect the legacy layout and inventory current state, views, manual edits, evidence, and existing authored documents.
2. Produce a dry-run mapping and report ambiguities without modifying source data.
3. Preserve a complete recoverable backup before any authorized migration write.
4. Map project synthesis into a constitution draft; keep sourced facts, assumptions, decisions, and unresolved context distinct.
5. Map legacy ITEM records to typed files using evidence for classification, retaining an explicit old-to-new ID map. Unknown classifications remain unresolved; do not fabricate a user story.
6. Map a preparation proposal to a draft iteration plan, not authorized or completed work. Preserve existing delivery revisions, checks, scoped acceptance, and permissions when mapping implemented increments; do not collapse multiple historical increments without an explicit mapping rule.
7. Preserve historical states and provenance; absent roadmap, MVP, DoD, or retrospective content is missing information, not permission to invent it.
8. Regenerate indexes and validate cross-references, record counts, applicable acceptance, and file preservation.
9. Report migrated, preserved, and unresolved content plus recovery instructions. Repeating migration must not duplicate records.

Do not delete old records or overwrite authored documents to force a migration. Do not automatically run migration on live projects while developing this feature. Archived legacy content is historical evidence, not a second active authority. Define and test the new schema version and compatibility behavior before release.

## 10. Acceptance scenarios

| ID | Scenario | Required result |
| --- | --- | --- |
| AC01 | New product with limited context | Meaningful draft constitution, explicit assumptions, and a useful next outcome; no invented stakeholder agreements or empty ceremony files. |
| AC02 | Existing product documents | Existing vision/instructions preserved and referenced; no competing editable full copy. |
| AC03 | Ambiguous CRUD or benchmark reference | No inferred business-record CRUD or remote-server requirement becomes confirmed fact without support. |
| AC04 | Backlog refinement/reorder | Item files remain authoritative; index matches their details and ordering; history and identities survive updates. |
| AC05 | Mixed work types | Stories, NFRs, bugs, technical work, and investigations use appropriate formats. |
| AC06 | Large or uncertain story | INVEST analysis drives a useful split or bounded investigation, not fabricated estimates or automatic compliance labels. |
| AC07 | Plan without execution authorization | Iteration planning is readable and useful; no implementation or false permission is created. |
| AC08 | Authorized iteration | Relevant scope executes without repeated approval; single-active-development boundary holds. |
| AC09 | Missing required verification resources | Check remains not run and completion is qualified; user acceptance stays independent. |
| AC10 | New check versus changed product | An unchanged accepted delivery stays accepted after another check; relevant product changes require reassessment. |
| AC11 | Review and learning | Partial acceptance, corrections, new needs, and retrospective actions remain distinct and traceable. |
| AC12 | Fresh-session status | Agent recovers purpose, active plan, evidence, blockers, and next step from documents without rewriting them. |
| AC13 | Manual edits or interrupted write | User content survives; conflicts are surfaced; recovery is deterministic and does not duplicate work. |
| AC14 | Legacy migration and repeat | Dry-run is read-only; authorized migration preserves provenance and remains idempotent. |
| AC15 | Generated-format request | Product work does not modify installed plugin code/tests or masquerade as a released plugin change. |
| AC16 | Multiple iterations | Earlier plans, DoD baselines, evidence and reviews remain understandable after later backlog changes. |

Automated tests must cover parser/record behavior, index consistency, recovery, migrations, and authorization/evidence regressions. Agent exercises must independently test comprehension, useful synthesis, routing, and actual readable documents. Report the two forms of evidence separately; green persistence tests alone do not establish correct collaboration.

## 11. Implementation sequence and completion boundary

1. Define typed document metadata, parsers, IDs, status rules, and ownership; preserve prose and user edits.
2. Implement document operations, indexes, recovery, and compatibility detection with isolated fixtures.
3. Implement project documents and typed backlog with DEEP/INVEST refinement guidance.
4. Implement iteration planning, delivery evidence, review, and retrospective relationships.
5. Implement and verify dry-run/authorized migration from 0.2.0.
6. Align AGENTS.md, skills, shared references, examples, and package structure.
7. Run acceptance scenarios and regression tests; inspect actual Markdown outputs and record limitations.
8. Version, commit, publish, and install only under the corresponding user authorization. GitHub Releases remains the changelog.

This consolidation authorizes no live-project migration or cache modification. It defines the agreed product direction and implementation constraints. The detailed persistence design must resolve multi-document transaction boundaries, metadata parsing, and legacy identity mapping without weakening the functional contracts above.
