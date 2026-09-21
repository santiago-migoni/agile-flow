# Bookly — Product backlog

**Editorial example of a generated index.** Item documents own their requirements and DoD. Ranks and release assignments below are proposed, not owner approvals.

| Order | Item | Type | Status | Estimate | Target release | Iteration |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | [US-0001 — Book an appointment](backlog/US-0001.md) | US | Draft | Not assigned | v0.1.0 | ITER-001, draft. |
| 2 | [NFR-0001 — Keyboard access](backlog/NFR-0001.md) | NFR | Draft | Not assigned | v0.1.0 | ITER-001, draft. |
| 3 | [BUG-0001 — Selection after conflict](backlog/BUG-0001.md) | BUG | Hypothetical; reproduction pending | Not assigned | Unassigned | Unassigned. |
| 4 | [TCH-0001 — Test fixtures](backlog/TCH-0001.md) | TCH | Draft | Not assigned | v0.1.0 | ITER-001, draft. |
| 5 | [SPK-0001 — Time-zone display](backlog/SPK-0001.md) | SPK | Proposed | Not assigned | Unassigned | Unassigned. |

The five types use the [same document structure](backlog-template.md), with type-specific detail. US-0001 references NFR-0001 without duplicating its quality definition. TCH-0001 is explicitly selected as supporting technical work; do not count it again as an unrelated feature.

Prioritization and release assignment are different: an unconfirmed defect needs triage before a target version is assigned. Later [roadmap stages](roadmap.md#version-plan) remain lightweight until refined into actual items.
