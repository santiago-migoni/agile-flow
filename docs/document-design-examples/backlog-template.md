# Backlog document contract

**Status:** Proposed common editorial template, not yet implemented in the parser or renderer.

Every backlog record uses the same section order. Its type changes the need-specific fields, not the document family. Filenames use a type prefix and four digits: US-0001.md, NFR-0001.md, BUG-0001.md, TCH-0001.md and SPK-0001.md. Proposed numbering is independent within each type; identifiers remain stable after creation. Prefix migration from TECH/SPIKE is future implementation work, not performed by these examples.

## Shared template

```markdown
# <TYPE>-<0001> — <Concise title>

**Type:** <US | NFR | BUG | TCH | SPK> · **Status:** <actual status>
**Order:** <position and decision/proposal> · **Estimate:** <relative estimate and basis, or not assigned>
**Target release:** <version or unassigned> · **Iteration:** <linked iteration or unassigned>

## Need and value
<Who benefits, what is needed and why.>

## Scope
<Included and excluded work.>

## Type-specific detail
<Use the appropriate fields from the type guide below.>

## Acceptance criteria
| ID | Condition | Observable result |
| --- | --- | --- |
<Number criteria locally: AC-01, AC-02…>

## Definition of Done
| ID | Completion requirement | Required evidence |
| --- | --- | --- |
<Number completion requirements locally: DOD-01, DOD-02…>

## Dependencies and open questions
<Actual dependencies, material unknowns and impact on readiness.>

## Source and changes
<Sourced need, priority rationale, dated revisions and relevant decisions.>
```

## Type guide

| Type | Nature | Detail inside the common structure |
| --- | --- | --- |
| US | User story | As a <person>, I want <capability>, so that <value>; user context and journey. |
| NFR | Non-functional requirement | Quality attribute, applicability, measurable conditions and verification method. |
| BUG | Defect | Reproduction, observed versus expected behavior, environment, affected revision and impact. Unknown observations remain unknown. |
| TCH | Technical work | Technical problem, benefit, proposed approach, affected components and operational limits. |
| SPK | Bounded investigation | Question, work boundary, sources/findings and recommendation or resulting decision. |

Acceptance criteria define the result; the embedded DoD defines what evidence and quality work are required to regard that particular item as done. Each item owns its DoD; there is no parent definition-of-done.md and no hidden inherited checklist. Similar conditions may recur deliberately, but changes must be considered for each affected item rather than applied retrospectively.

Iteration plans reference item-local AC/DOD IDs and preserve selected versions. User acceptance remains a separate sourced review. Types share a structure without forcing bugs or technical work into a fictional user-story sentence. Create useful detail progressively and omit optional empty fields; an item approaching execution must have meaningful acceptance criteria and DoD.
