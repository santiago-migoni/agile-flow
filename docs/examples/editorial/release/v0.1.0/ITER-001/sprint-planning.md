# ITER-001 — Sprint planning

**Release:** [v0.1.0](../release-0.1.0.md) · **Status:** open · **Timeframe:** Not recorded

## Iteration goal and expected result

**Goal.** One complete booking

**Expected result.** Not recorded

## Selected stories and baselines

| Story | Type | Contribution | Estimate | Planning baseline |
| --- | --- | --- | --- | --- |
| [US-0001](user-stories/US-0001.md) | US | US bounded booking work | 2 | Current selected document |
| [US-0002](user-stories/US-0002.md) | NFR | NFR bounded booking work | 2 | Current selected document |
| [US-0003](user-stories/US-0003.md) | BUG | BUG bounded booking work | 2 | Current selected document |
| [US-0004](user-stories/US-0004.md) | TCH | TCH bounded booking work | 2 | Current selected document |
| [US-0005](user-stories/US-0005.md) | SPK | SPK bounded booking work | 2 | Current selected document |

Acceptance criteria and DoD remain in each linked story. A selected story change requires plan reconciliation before preparation.

## Scope

**Included:** Calendar and persistence

**Excluded:** Notifications

## Technical approach

Persist a booking through a small service boundary.

## Implementation tasks

| Task | Story | Action | Completion evidence | Status |
| --- | --- | --- | --- | --- |
| TASK-01 | [US-0001](user-stories/US-0001.md) | Implement booking persistence | Stored record | planned |

## Verification plan

| Story / criterion or DoD | Check | Method | Required evidence |
| --- | --- | --- | --- |
| US-0001 / DOD-01 | Persistence | Read after write | Test transcript |

## Authorization and agreements

No entries recorded.

Planning alone does not authorize implementation. Reuse existing permission only when it covers the selected scope.

## Plan changes

| Date | Change | Reason or source | Baseline impact |
| --- | --- | --- | --- |
| 2026-09-22T13:05:04+00:00 | Not recorded | Test actual requested scope | Not recorded |

## Delivery increments

| Increment | Selected stories | Objective | Authorization | Development status |
| --- | --- | --- | --- | --- |
| INC-0001 | US-0001 | Persist booking | DEC-0001 | implemented |

### Baseline for INC-0001

| Story | Kind | Criterion ID | Agreed requirement |
| --- | --- | --- | --- |
| US-0001 | Acceptance | AC-01 | One booking persists |
| US-0001 | DoD | DOD-01 | Verify persistence |

## Additional context

| Context | Detail |
| --- | --- |
| Item ids | US-0001<br>US-0002<br>US-0003<br>US-0004<br>US-0005 |
| Authorization note | Planning does not authorize execution. See sourced authorization references on each prepared delivery. |
| Increments / 1 / Scope | One calendar |
| Increments / 1 / Technical plan |  |
| Increments / 1 / Criteria | US-0001/AC-01: One booking persists |
| Increments / 1 / Required checks | US-0001/DOD-01: Verify persistence |
| Increments / 1 / States / Verification | passed |
| Increments / 1 / States / Acceptance | pending |
| Increments / 1 / Delivery revision | 1 |
| Increments / 1 / Suspended | false |
| Increments / 1 / Created at | 2026-09-22T13:05:05+00:00 |
| Increments / 1 / Iteration id | ITER-001 |
| Increments / 1 / Story baseline / Us-0001 / Criteria / 1 / Condition | A free slot is selected |
| Increments / 1 / Story baseline / Us-0001 / Dod / 1 / Evidence | Synthetic test transcript |
| Increments / 1 / Accepted parts | US-0001/AC-01: One booking persists |
