# Executive reading and principal agreement references

Implemented in source. This change does not publish or install a plugin version or rewrite a live product.

## Observable result

The agent writes a concise executive synthesis and selected highlights in the constitution using update-collaboration. The generated summary projects that selection, immediate questions, next action and unresolved reconciliation. It groups proposed records by document and collection with counts and links, rather than copying every agreement or proposal. Investigation, deferral and proposal inventories are expandable. Pending user choices and blockers are not truncated or silently hidden.

Design tables now expose record IDs directly. Rejected/superseded alternatives, components and operations have separate expandable history sections. Change history retains a short purpose and separate edited-record details. Existing verbose history remains intact. Standard Markdown readers without expandable HTML still have the complete source text available.

Optional absent constitution paragraphs/header clauses are omitted. Available amendment/decision timestamps provide its display date. An absent vision is not invented, and a material missing definition must be raised by the agent as a scoped question. Explicit existing values and notes remain preserved. Backlog needs show Unranked/Unassigned when appropriate and display their value in the main body.

Agreement pointers identify the principal wording by document and ID. Dependent rules, journeys and states use agreement_refs; BL and highlight references accept pointers alongside ordinary sources. Generated links target the owning section and show the exact ID. The writer rejects unknown pointers, preserves identity during round-trip and flags references to superseded/rejected agreements for applicability review. It never substitutes a replacement's meaning automatically.

## Examples

[Complete generated documents](examples/executive/README.md) use a synthetic product with 21 settled design decisions, 14 proposed states and two additional architecture proposals. Its [summary](examples/executive/summary.md) is 1,973 bytes and 59 source lines, including expandable sections. This is a controlled volume example, not a universal size guarantee when many genuine blockers need attention.

The example generator performs actual transactions in a temporary product and copies only Markdown to its output. No app-odoo content was copied into these examples.

## Validation

- Complete automated suite: 165 tests, including eight new executive-reading regressions.
- Four changed skills pass the skill-creator validator.
- Regression coverage: summary volume with full underlying records; lossless folded history and ID tables; optional absences and dates; principal-reference identity and stale-reference warnings; unknown-reference rejection without partial writes; editable synthesis, notes and portability; published unfolded bindings; ordinary source text containing double colons.
- Published v0.8.0 codec output and bindings are frozen in a synthetic fixture. The current reader reconstructs them without rewriting and can subsequently render the same data into the new presentation.
- Independent agent exercise: 20 settled decisions and 14 technical proposals, actual source CLI mutations, scoped correction, journey/BL/highlight reconciliation and fresh reconstruction. Final validation succeeded at revision 11. Detailed records survived; no releases, iterations, increments or implementation authorization were created.

The independent exercise exposed a generic no-question message, which was corrected, and a request missing update-backlog's already-required purpose, which was documented explicitly. It did not validate installed skill selection or real product execution.

## Boundaries and next use

The renderer does not determine semantic relevance, infer missing definitions or prove that a citation supports a claim. The agent must maintain the synthesis and interpret historical-reference warnings. A stale highlight can remain visible alongside a warning until explicitly reconciled; no semantic text is rewritten automatically.

Schema 4/editorial-v2 stored bindings remain readable. New source fields and operations need this writer; downgrading is not guaranteed. Existing duplicated prose is preserved until a requested reconciliation compares scopes and replaces only actual duplication with references. Live app-odoo reconciliation, installation, commits and publication are separate from this source implementation.
