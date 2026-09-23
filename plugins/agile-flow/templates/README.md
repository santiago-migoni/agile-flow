# Document presentation contracts

The thirteen Markdown files below are complete editorial templates: visible metadata, prose composition, table columns, repeatable rows and conditional blocks. They define the target presentation for every product document. Plugin-owned output is English; actual source quotations retain their original language.

## Catalog

| Template | Product document | Responsibility |
| --- | --- | --- |
| [Constitution](markdown/constitution.md) | constitution.md | Shared purpose, people, objectives, boundaries and agreements. |
| [Roadmap](markdown/roadmap.md) | roadmap.md | Strategic version stages and adaptation. |
| [Product backlog](markdown/product_backlog.md) | backlog/product-backlog.md | Generated ordered index of BL needs. |
| [Product need](markdown/product_item.md) | backlog/BL-nnnn.md | Need, value, boundaries and story breakdown. |
| [Release](markdown/release.md) | release/<version>/release-<version-without-v>.md | Concrete scope, optional MVP learning, delivered outcome and publication. |
| [Sprint planning](markdown/planning.md) | release/<version>/ITER-nnn/sprint-planning.md | Iteration goal, stories, tasks, verification and sourced authorization. |
| [Typed work record](markdown/story.md) | release/<version>/ITER-nnn/user-stories/US-nnnn.md | One common record with US/NFR/BUG/TCH/SPK detail, criteria and its own DoD. |
| [Verification](markdown/verification.md) | release/<version>/ITER-nnn/verification.md | Actual checks, evidence and limitations. |
| [User review](markdown/review.md) | release/<version>/ITER-nnn/review.md | Real user feedback and scoped acceptance. |
| [Retrospective](markdown/retrospective.md) | release/<version>/ITER-nnn/retrospective.md | Collaboration learning and improvement follow-up. |
| [Summary](markdown/summary.md) | summary.md | Generated current situation and next action. |

## Presentation rules

- Braced placeholders identify semantic content, not literal output or approved decisions. Replace them from actual records. Never invent a date, owner, estimate, target, approval or evidence to populate a cell.
- Repeat table rows for records. Nested lists stay within their defined cells using concise semicolon-separated items or line breaks. Do not switch an entire table into Entry/Field heading trees because one field contains a list.
- Keep prose for purpose, explanation, scope and tradeoffs. Use tables for comparisons, status, requirements and traceability. Do not duplicate a heading as a field subtitle.
- Keep comparable rows concise without discarding qualifications or source meaning. Put substantial procedures, quotes and explanations in the named detail block and link from their table row. Do not compress different sources into a fabricated common decision.
- Retain required sections. If their information is missing, write a short explicit sentence such as "No decisions recorded." or "Not yet defined." instead of an empty heading or empty table.
- Omit optional sections when inapplicable. Distinguish unknown (Not recorded), not applicable and actually pending. A dash must not conceal missing evidence.
- Tables have stable semantic columns. Source-only lists may lack impact, owner or measurement data: record that absence, rather than inventing relationships between separate lists.
- Extra author Notes sections survive later updates. No af markers, raw JSON, local filesystem roots, UUIDs or hash dumps appear in the readable output. Useful BL/US/ITER/INC/evidence/decision references remain visible.
- Preserve distinct planning, authorization, development, verification, acceptance and publication states. A template never supplies approval.
- Dates refer to actual observations or document changes. A document may link a prior relevant commit; never insert the SHA of the commit that must contain that same reference.
- Links in template bodies are relative to the product document's intended location. Only link existing targets; use a plain unassigned reference when the target does not yet exist.

## Conditional content

| Document | Required composition | Conditional content |
| --- | --- | --- |
| Constitution | Purpose; people; objectives; boundaries; agreements; facts and uncertainty. | Git agreement only when sourced; sources and changes when recorded. Omit unpopulated optional sections; preserve genuinely unresolved choices as scoped questions. |
| Roadmap | Strategic direction and version table. | Milestones, uncertainty, adaptation, release links and changes as available. An MVP milestone may appear; its detailed definition belongs to a release. |
| Product backlog | Ordered active-needs table or "No product needs recorded." | Priority explanation and completed/retired needs. Never invent ranking. |
| Product need | Problem, value, outcome, boundaries and priority rationale. | Indicators, dependencies, breakdown, sources and changes. Do not add story criteria or shared DoD here. |
| Release | Objective, target value, planned scope and exit conditions. | MVP definition only for an explicitly planned MVP; delivered results, learning and publication only when recorded. This is not only a changelog. |
| Sprint planning | Goal, selected work, scope, approach, tasks, verification plan and authorization state. | Risks, plan changes and actual prepared increments. Repeat each delivery baseline block only when a frozen baseline exists. |
| Typed work record | Metadata, need, scope, acceptance criteria and embedded DoD. | Keep exactly ONE type-specific subsection. US uses the user-story sentence; NFR a measurable quality table; BUG reproduction and impact; TCH technical objective and approach; SPK bounded inquiry and findings. All five use US-nnnn IDs. |
| Verification | Actual scope, check results and honest conclusion. | Repeat an evidence detail block per recorded attempt; blockers when present. Historical attempts remain distinguishable from the current result. |
| User review | Presented result, source and actual acceptance state. | Repeat detail blocks for real feedback; resulting work and unresolved feedback. No invented quotation if only a message reference exists. |
| Retrospective | Sourced observations and proposed or agreed improvements. | Retained practices and follow-up. Do not fabricate ownership or successful effects. |
| Summary | Product position, current delivery state and one useful next action. | Releases/iterations, blockers and Git snapshot when available. Observe Git when refreshing; summary is not live monitoring. |

## Runtime integration

`markdown/` drives the current editorial-v2 renderer: paragraph composition, table headers, section order, conditional work-type blocks and repeated evidence/review/baseline details. `scripts/editorial_codec.py` binds domain fields to these presentation slots and reads the same composition back. Unmapped source fields remain visible in Additional context; no functional information is moved to a hidden JSON authority.

Portable registry schemas contain source paths, types, literal presentation structure and record identities. They do not contain a second copy of functional values. Read-only header context (for example, the release identified by the document path and the effective verification/acceptance snapshot) is recomputed during writes; edit the underlying records rather than those header snapshots. Generated indexes use the same editorial templates.

`legacy/clean-markdown-v1/` and `legacy/documents.json` are retained only for legacy clean-markdown-v1 compatibility and migration tests. Existing v0.5.0 records remain readable. Their first editorial conversion requires an explicit `migrate --dry-run` followed by `migrate --apply` with the reviewed source fingerprint. The conversion backs up original bytes, preserves meaningful notes and acceptance history, and refreshes only draft planning hashes that still matched the source. Already stale plans remain stale.

## Editing contract

- Edit bound prose and existing table values without changing their labels. Table spacing is flexible. Flat list cells use `<br>`; escape a literal vertical bar as `&#124;`.
- Add homogeneous criterion/DoD rows using the existing columns. Changes to mixed row structures, columns or record identity require a record operation. Rows with separately bound details cannot be reordered independently.
- A `Not recorded` cell without an existing source field is explicitly unknown; populate that field through a record operation. Do not interpret a missing relationship as an empty approval.
- Add free author commentary under a separate level-two Notes heading. Unknown sections survive later updates; ambiguous or duplicate managed headings fail before a write.
- Structured project users require `actor` (with optional `need` and `value`); structured facts/proposals require `statement`. Existing text-only lists remain supported and never acquire invented associations.
- Headers are observations, not independent evidence or user decisions. The authoritative review source and scoped decision remain in the review records. Summary is a refreshed Git/domain snapshot, not monitoring.

## Validation for renderer integration

Exercise every document with populated and sparse data. Include multiple versions with list-valued capabilities/dependencies, all five work types, partial acceptance, repeated evidence attempts, superseded decisions and manual notes. Compare rendered structure with these templates as well as round-trip meaning. Check relative links, readable unknown states, omission of inapplicable blocks and absence of leftover placeholders. Automated storage tests alone do not establish presentation fidelity.

## Consultative design documents

- [Product design](markdown/product_design.md): purpose, boundaries, user journeys, screens, states, accessibility, alternatives, decisions and questions.
- [Architecture](markdown/architecture.md): constraints, alternatives, components, data ownership, integrations, operation, decisions and questions.

Both are optional authored documents created by their update operations when content is meaningful. They do not require releases or iterations. Repeated tables use the row vocabulary in [document operations](../references/document-operations.md#optional-design-document-operations). Decision status and source preserve the distinction between proposed and settled choices; execution authority remains separate.

## Consultative documents and continuity

Product design separates rules, illustrative examples and conditional journeys. Product design and architecture show active decisions near the top, proposals separately, and superseded/rejected decisions as history. All are views of the same authored records; the codec stores source row indexes to read the separated tables without changing record order. Existing unfiltered bindings remain readable.

The constitution may include current collaboration focus, level and independent work. Summary derives agreements, proposals, current questions, investigations, deferred topics and outstanding document reconciliation. Its date comes from recorded source changes, not the clock at view time. Empty release/delivery sections are omitted before delivery planning. A resolved question remains in its source document with its answer and provenance but leaves the pending summary.
