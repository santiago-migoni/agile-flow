# ITER-001 — First booking slice

**Release:** v0.1.0 — Architecture and booking core · **Status:** Draft
**Execution:** Not authorized · **Timeframe:** Not agreed

Prove a reliable customer booking journey in an isolated environment with prepared slots and synthetic data. The iteration contributes to the release; it is not the entire MVP.

## Selected work and baselines

| Item | Planned version | Contribution | Completion requirements |
| --- | --- | --- | --- |
| [US-0001](../../../../backlog/US-0001.md) | Example revision 2. | Booking behavior. | Item-local AC-01–05 and DOD-01–03. |
| [NFR-0001](../../../../backlog/NFR-0001.md) | Example revision 2. | Keyboard access and feedback. | Item-local AC-01–03 and DOD-01–03. |
| [TCH-0001](../../../../backlog/TCH-0001.md) | Example revision 2. | Repeatable isolated setup. | Item-local AC-01–03 and DOD-01–03. |

Each selected document owns its acceptance criteria and DoD. The plan references them without creating a global quality policy or copying their full definitions. An implemented renderer must preserve the selected versions; this editorial example has no execution baseline.

## Scope and approach

Include persistence, booking UI, reliable conflict/retry handling, applicable keyboard behavior and test fixtures. Exclude professional administration, real customer data, payments and reminders.

| Task | Proposed work | Reviewable outcome |
| --- | --- | --- |
| T-01 | Inspect existing architecture and test tooling; resolve material scope questions. | Repository-grounded implementation approach. |
| T-02 | Build isolated setup and reset fixtures. | TCH-0001 evidence. |
| T-03 | Implement booking allocation and repeat-submission handling. | US-0001 behavior with regression checks. |
| T-04 | Implement customer UI states and keyboard interaction. | US-0001 and NFR-0001 behavior. |
| T-05 | Verify item criteria/DoD and present the actual result. | Evidence and limitations, independently from user acceptance. |

This is a proposal, not evidence of an inspected codebase or an executed task.

## Verification plan

Use the criterion-linked [check register](verification.md). Record actual procedures, environment, delivered revision and results when executed. One observation may support several explicitly linked conditions without pretending they were independently tested.

## Decisions required before execution

- Confirm or revise the synthetic-data boundary and selected item scope.
- Agree each selected item's acceptance criteria and DoD.
- Establish actual implementation authorization; none exists in this example.

## Presentation and follow-up

Present a test-only slice against the selected criteria. Keep development, verification and [user review](review.md) separate. New needs return to the backlog; collaboration improvements belong in [retrospective](retrospective.md).

**2026-09-21 — plan revision 2:** placed the iteration within v0.1.0 and replaced the shared DoD reference with each selected item's own requirements. Source: [S1 and S2](../../../../README.md#example-brief).
