# Workshop — Product design

**Status:** draft · **Updated:** 2026-09-22T16:08:49+00:00 · [Constitution](constitution.md) · [Architecture](architecture.md)

## Design purpose

Explore how the owner finds and understands an environment

## Experience boundaries

**Included:** An overview of projects and environment state

**Excluded:** Not recorded

## User journeys

| ID | Actor | Trigger | Steps | Expected outcome | Knowledge |
| --- | --- | --- | --- | --- | --- |
| J-001 | Owner | Check an environment | Open a project<br>Select an environment<br>Read its current state | Understand whether the environment is usable | proposed |

## Screens and interactions

| ID | Journey | Screen or interaction | Information | Actions | Knowledge |
| --- | --- | --- | --- | --- | --- |
| SCREEN-001 | J-001 | Environment overview | Observed state<br>Last update<br>Failure details | Refresh state | proposed |

## States and recovery

| Context | State | Expected behavior | Recovery | Knowledge |
| --- | --- | --- | --- | --- |
| Environment overview | Unknown | Show that no recent observation is available | Refresh and retain the last known result | proposed |

## Accessibility

| Need | Expected behavior | Verification | Knowledge |
| --- | --- | --- | --- |
| Operate without a pointer | Keyboard navigation and visible focus | Exercise the journey using only the keyboard | proposed |

## Questions and revisit points

| Question | Impact | Timing | Revisit when |
| --- | --- | --- | --- |
| Which state information helps the owner decide what to do? | Defines overview content | now | Not recorded |

## Changes

| Date | Change | Reason or source |
| --- | --- | --- |
| 2026-09-22T16:08:49+00:00 | Synthetic consultative example | Synthetic discussion, not an actual product agreement |
