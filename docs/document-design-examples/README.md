# Document design examples

> Historical presentation exhibit. Keep these files for comparison with their original design stage. The [current editorial examples](../examples/editorial/README.md) and [executable template contracts](../../plugins/agile-flow/templates/README.md) define the current source presentation. Product version directories in this exhibit identify the synthetic product, not the plugin release.

> Historical intermediate design examples. For the v0.4.0 structure, use [the rendered release-layout example](../release-layout-example/README.md).

Status: Proposed reading format for review. Not implemented in the renderer.

These documents illustrate Bookly, a fictional appointment-booking product. They are editorial examples, not active Agile Flow records, approved product requirements, or completed work. All sources, requirements, identifiers and candidate decisions below belong to this demonstration only.

## Agreed direction after design feedback

- Preserve the approved constitution example unchanged.
- Organize roadmap stages by target product version, with scope, dependencies and exit conditions.
- Embed Definition of Done inside every backlog item; remove the parent quality-policy document.
- Place iteration records under `release/<version>/iterations/<iteration-id>/`. This nesting is the working interpretation of release grouping and remains reviewable.
- Use one common backlog template, specialized by US, NFR, BUG, TCH and SPK, with four-digit identifiers and filenames such as `US-0001.md`.

## Example structure

```text
.agile-flow/
  constitution.md
  roadmap.md
  backlog.md
  summary.md
  backlog/
    US-0001.md
    NFR-0001.md
    BUG-0001.md
    TCH-0001.md
    SPK-0001.md
  release/
    v0.1.0/
      iterations/
        ITER-001/
          sprint_planning.md
          verification.md
          review.md
          retrospective.md
```

Future version directories are created when actual plans or records exist. The roadmap can describe versions without creating empty folders. `backlog-template.md` is a design reference here, not an additional required project record. Technical `.internal/` bookkeeping is outside this editorial tree.

## Document catalog

| Document | Reading purpose |
| --- | --- |
| [Constitution](constitution.md) | Approved presentation of purpose, vision, mission, objectives and agreements. |
| [Roadmap](roadmap.md) | Version stages and MVP placement. |
| [Common backlog template](backlog-template.md) | Shared sections, embedded DoD and type-specific fields. |
| [Backlog index](backlog.md) | Priority and proposed version/iteration assignments. |
| [US-0001](backlog/US-0001.md) | User story. |
| [NFR-0001](backlog/NFR-0001.md) | Non-functional requirement. |
| [BUG-0001](backlog/BUG-0001.md) | Hypothetical defect, pending reproduction. |
| [TCH-0001](backlog/TCH-0001.md) | Technical work. |
| [SPK-0001](backlog/SPK-0001.md) | Bounded investigation. |
| [Sprint planning](release/v0.1.0/iterations/ITER-001/sprint_planning.md) | Release-specific selected work and item-local completion baselines. |
| [Verification](release/v0.1.0/iterations/ITER-001/verification.md) | Planned evidence coverage and actual status, currently not run. |
| [Review](release/v0.1.0/iterations/ITER-001/review.md) | User evaluation, currently not requested. |
| [Retrospective](release/v0.1.0/iterations/ITER-001/retrospective.md) | Collaboration improvement proposals and follow-up. |
| [Summary](summary.md) | Current target release, iteration and next action. |

All documents describe one draft scenario. No implementation, verification or acceptance has occurred. Iteration reports are editorial previews; they would not be created merely to fill folders in a real project.

## Example brief

**S1 — Fictional scenario brief.** A self-employed professional wants customers to select an available appointment online instead of arranging every booking through messages. For this example, appointments last 30 minutes and use one professional's calendar and one clearly displayed business time zone. The first development slice may use prepared availability and test data. A real pilot would additionally need usable availability administration, a professional's booking view and agreed handling of customer information. Payments and automatic reminders are outside the initial proposal.

**S2 — Editorial design proposals.** The document author proposes the horizons, trial design, detailed criteria and technical approach to illustrate the format. They are not stakeholder decisions or validated research.

## Presentation rules to review

- Start with the document's purpose and a short status line. Include only useful metadata.
- Use prose for the problem, value and reasoning; lists for parallel scope items; tables for decisions, comparisons, criteria and traceability.
- Keep headings at two or three levels. Avoid one heading per machine field, raw hashes, absolute checkout paths and large nested record dumps in the primary reading flow.
- Give each detail one authoritative home. The roadmap references needs; planning references criteria instead of copying their full definitions. Historical baselines remain explicit.
- Label proposals, assumptions, observed evidence and real approvals distinctly. Do not manufacture approval, estimates, dates or passed checks to fill a layout.
- Omit empty optional sections. Include an unresolved item when its absence materially changes the next action.
- Preserve original quotations when actual source material exists. This fictional brief supplies no customer interview or approval quote.

## Implementation boundary

The filenames model the intended product layout, but these are ordinary reviewable Markdown examples. They deliberately omit the v0.3.0 parser's field markers. They cannot replace live documents directly. After format review, the renderer/parser must preserve stable identities, authored edits, links, baselines, source evidence and recovery semantics while producing the agreed presentation.

This revised proposal supersedes the previous example layout and parent DoD. The catalog covers each functional document and all five backlog types. The backlog index and summary are hand-authored mockups of generated outputs; the remaining documents model authored sources. Optional evidence attachments are absent because no checks have run. Technical recovery files under .internal/ are not editorial documents and are not fabricated here. Git behavior is unchanged.

## Runtime compatibility

These changes revise the design examples only. Released v0.3.0 still uses its earlier shared DoD, iteration paths and TECH/SPIKE identifiers. Applying this revised design requires a later implementation and explicit migration; do not rename files or remove the DoD in a live v0.3.0 project based on these mockups.
