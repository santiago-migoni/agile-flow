# Bookly — Product roadmap

**Status:** Proposed version plan · **Revision:** 2 · **Direction:** [Constitution](constitution.md)

Organize product development into versions with a clear purpose, bounded scope and observable exit conditions. A version can contain several iterations. Target versions describe a plan; they are not published tags, delivery dates or permission to implement.

## Version plan

| Version | Stage and intended outcome | Planned scope | Dependencies | Exit conditions | Status |
| --- | --- | --- | --- | --- | --- |
| v0.1.0 | Architecture and booking core: prove the first end-to-end journey in an isolated environment. | [US-0001](backlog/US-0001.md), [NFR-0001](backlog/NFR-0001.md), [TCH-0001](backlog/TCH-0001.md). Persistence, repeatable fixtures and the customer UI. | Inspect the repository and resolve selected-item questions. | Selected criteria and each item's DoD satisfied; working test-only slice demonstrated with limitations. | Proposed; [ITER-001](release/v0.1.0/iterations/ITER-001/sprint_planning.md) is a draft. |
| v0.2.0 | Security and professional operation: make controlled operation possible. | Professional access, availability administration, booking visibility and customer-data handling. Candidate needs await refinement. | Booking core established; real-data and access decisions resolved. | Applicable item criteria/DoD met; permitted access and data boundaries verified. | Proposed; no iterations created. |
| v0.3.0 | MVP pilot: test usefulness with one professional and early customers. | Usable booking service, operational setup and feedback collection. | v0.1.0 and v0.2.0 outcomes; pilot scope and participants agreed. | Applicable item criteria/DoD met and pilot evidence collected for a continue/change decision. | Proposed; no iterations created. |
| v0.4.0 | Adaptation after feedback: reduce demonstrated follow-up work. | Candidate cancellation workflow; reminders only if evidence supports them. | MVP findings. | Future item criteria and DoD defined from observed needs, then verified. | Tentative; scope not committed. |

The detailed backlog owns item requirements. [BUG-0001](backlog/BUG-0001.md) has no target version until reproduced. [SPK-0001](backlog/SPK-0001.md) is unscheduled until time-zone uncertainty becomes material. Neither silently expands a release.

## MVP at v0.3.0

**Hypothesis:** customers can arrange appointments independently and the professional can manage them with less coordination than a message-based process.

**Minimum usable scope:** maintained availability, customer booking and confirmation, professional visibility and appropriate access/data handling. Payments, multiple professionals, reminders and calendar integrations remain excluded.

**Proposed learning:** observe five trial booking sessions, inspect schedule reliability and collect specific examples of coordination avoided or still needed. Five sessions are an illustrative trial proposal, not statistical evidence. Use actual findings to decide whether to expand, revise or stop.

The v0.1.0 test slice contributes to the MVP; synthetic data and prepared slots do not make it pilot-ready.

## Adaptive planning

Refine near-term versions more deeply than distant versions. Move or split pending items with a recorded reason and assess affected dependencies. Preserve baselines of work already delivered. Do not silently reinterpret published versions or prior acceptance.

Dates, budget and capacity remain unagreed. This product roadmap is independent of the Agile Flow plugin's own version numbers.

**Revision 2:** replaced time horizons with version-based stages following the document-design feedback. Product scope and release contents remain fictional proposals from [S1 and S2](README.md#example-brief).
