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
