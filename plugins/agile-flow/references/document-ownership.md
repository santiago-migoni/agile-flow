# Document ownership

All product records live in .agile-flow. Authored Markdown owns functional content; only summary.md and backlog/product-backlog.md are generated indexes. Technical registry data is not a second product specification.

| Document | Principal content | Responsibility |
| --- | --- | --- |
| constitution.md | Purpose, users, objectives, boundaries and general agreements | Product manager |
| product-design.md | Journeys, expected behavior and information; progressively screens, interactions, states, accessibility and recovery | Product manager defines behavior; product engineer refines the solution |
| architecture.md | Constraints, alternatives, component/data/integration/operation design, technical decisions and consequences | Product engineer |
| roadmap.md | Strategic version stages and intended outcomes | Product manager |
| release/<version>/release-<version>.md | Concrete delivery scope, MVP hypothesis and learning, planned versus delivered outcome | Product manager with engineering input |
| backlog/BL-*.md | Product needs and priority rationale, unassigned until a release is actually proposed or agreed | Product manager |
| release/<version>/ITER-*/user-stories/US-*.md | Typed work, acceptance criteria and own DoD | Product engineer |
| sprint-planning.md | Selected delivery work, tasks, checks and references to pertinent design decisions | Product engineer |
| verification.md / review.md / retrospective.md | Actual checks, user evaluation and learning | Product engineer / both roles |
| summary.md | Current situation, immediate questions, deferred topics and next action, linking to sources | Generated |

Create product-design.md and architecture.md through their update operations only when useful content exists. Neither requires a release or iteration. Do not create empty documents to complete a process. Preserve existing authored documents and reference them rather than copying them.

Keep one principal home for each fact. Put detailed technical alternatives in architecture, not the constitution or a sprint plan. A plan references the relevant design instead of becoming the product's architecture specification. Record pending versus settled decisions locally with source and scope; only actual authorization uses the lifecycle decision operation. Adoption of a proposal must be supported by the user statement or delegated decision, not inferred from its presence in a document.

Existing projects are read in place. Do not automatically relocate legacy prose from Additional context or reinterpret old proposals as agreement. A requested reorganization identifies the source content and destination, preserves notes and history, and previews any migration. The new optional documents are additive to schema 4 / editorial-v2; creating them requires the current writer. Earlier plugins cannot manage these new paths.

Product design distinguishes rules (`rules`), conditional journeys (`journeys.applicability`) and examples (`examples`). An example is not evidence of a required sequence. Active decisions, proposed decisions and decision history are separate tables over the same records. Questions retain their resolution and source; resolved questions do not appear as pending in the summary.

The constitution owns durable collaboration focus and conversation level when useful. The summary derives its date from recorded changes and presents an agent-authored executive synthesis, selected recent changes, immediate questions and reconciliation; proposal inventories, investigation and deferral are supplementary. Empty release and delivery sections are omitted before delivery planning. Generated indexes never invent a mandate.

For an existing project, inspect current records first. Optional reconciliation should identify missing supported constitution content, candidate BL needs, wrongly generalized examples, overly broad supersessions and unresolved proposals. Present source/destination and exact changes before any requested bulk reorganization. No live project migration is triggered by a plugin update.

## Executive reading and principal agreements

The agent owns relevance selection. Use `update-collaboration` to maintain a short `synthesis` of the present situation and at most five `highlights` with `text` and `references` when something material changes. Both live in the constitution; summary.md projects them. Do not recopy every settled agreement into the synthesis or treat a synthesis as new approval. At a strategic focus, summarize technical proposals by topic and link their detail. Unselected records remain fully available in their principal documents.

Give each agreement one principal wording in a design decision or product rule with a stable ID. A dependent rule, journey or state may carry `agreement_refs`, for example `product-design.md::PD-001`, and explain only its local application. BL `references` and highlight `references` accept the same pointers alongside ordinary sources. Unknown pointers fail validation; references to rejected or superseded agreements surface as reconciliation pending. Historical references remain valid and are never silently redirected. A reference is neither adoption nor execution authorization.

Do not rewrite existing duplicated prose automatically. During requested reconciliation, compare its scope, retain meaningful local differences and replace only demonstrably duplicated agreement wording with a pointer. Keep ID namespaces distinct between rules and decisions in each design document.

Unpopulated optional constitution fields are omitted. A material missing definition belongs in a scoped open question; the renderer cannot invent the question or its answer. History and rejected/superseded alternatives, components and operations are available in folded sections. A new change records a short purpose and separate edited-record details. Existing verbose history is preserved verbatim.

Project-root AGENTS.md owns stable collaboration guidance only; see [project instructions](project-instructions.md). It is not rendered from product state. An unnumbered release outline may be consolidated in product-design.md while identity is unresolved; once a version is established, the release owns delivery scope and references the underlying agreements. Do not maintain competing editable copies.
