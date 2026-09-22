# Workshop — Architecture

**Status:** draft · **Updated:** 2026-09-22T16:08:49+00:00 · [Constitution](constitution.md) · [Product design](product-design.md)

## Architecture purpose

Compare proportionate solutions for the proposed environment overview

## Constraints and boundaries

**Constraints:** Keep operation simple

**Included:** Not recorded

**Excluded:** Not recorded

## Alternatives and recommendations

| Topic | Alternative | Benefits | Costs | Recommendation | Status |
| --- | --- | --- | --- | --- | --- |
| Frontend | Server-rendered pages with partial updates | One application to operate | Investigate live-update requirements | Initial candidate | proposed |
| Frontend | Separate frontend application | Independent interface development | Additional build and deployment | Consider if interaction requirements justify it | proposed |

## Components and responsibilities

| Component | Responsibility | Interfaces | Boundary | Knowledge |
| --- | --- | --- | --- | --- |
| Application | Project and environment information | Owner interface | Observation before lifecycle operations are defined | proposed |

## Architecture decisions

| ID | Decision | Scope | Basis | Source | Rationale | Status | Replaces |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ARCH-001 | Use Django for the backend | Backend framework only | user-definition | Synthetic user: The backend will be Django. | Explicit choice; no reconfirmation needed | decided | Not recorded |

## Questions and revisit points

| Question | Impact | Timing | Revisit when |
| --- | --- | --- | --- |
| Which update mechanism meets the agreed interaction needs? | Interface complexity | investigate | Not recorded |
| What production recovery guarantee is needed? | Operational design | later | Before defining a production delivery |

## Changes

| Date | Change | Reason or source |
| --- | --- | --- |
| 2026-09-22T16:08:49+00:00 | Synthetic consultative example | Synthetic example: user explicitly chose Django |
