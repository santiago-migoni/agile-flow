# Bookly — Project constitution

**Status:** Draft example · **Revision:** 1 · **Source:** [Fictional brief S1](README.md#example-brief)

Bookly helps an independent professional and their customers arrange appointments without coordinating every booking through messages.

## Purpose

**Problem.** Booking through messages requires both parties to exchange availability and confirm the same time. The product should make that coordination easier; the size of the problem has not been measured in this fictional scenario.

**Vision.** Customers can confidently arrange an appointment themselves, while the professional retains a reliable schedule.

**Mission.** Offer a clear path from available time to recorded booking, with enough information for both parties to understand the result.

## People and value

| Person | Need | Expected value |
| --- | --- | --- |
| Customer | Find a suitable time and know whether the booking succeeded. | Less coordination and a clear confirmation. |
| Independent professional | Control availability and see recorded bookings. | A dependable schedule with fewer manual exchanges. |

No additional team members or external stakeholder agreements are defined in this example.

## Objectives and success factors

| Objective | Proposed evidence | Current knowledge |
| --- | --- | --- |
| Make booking understandable. | Observe customers completing the booking journey and explaining its confirmation. | Not tested. |
| Preserve a reliable schedule. | Verify competing booking requests cannot allocate the same slot twice. | Not implemented or verified. |
| Make the product useful in daily work. | Ask the professional whether pilot bookings reduced coordination and remained manageable. | Pilot not started. |

Clear availability, trustworthy confirmation and professional visibility are essential success factors. The [roadmap](roadmap.md) defines the proposed learning sequence.

## Product boundaries

**Initial direction:** one professional, one calendar and fixed 30-minute appointments. Customers select an available slot and receive an on-screen result. The intended MVP also gives the professional a practical way to maintain availability and inspect bookings.

**Outside the initial proposal:** payments, multiple professionals, recurring appointments, automatic reminders and third-party calendar synchronization.

These exclusions limit the current proposal; they do not prohibit later refinement.

## Decisions and collaboration agreements

| ID | Proposal | Basis / source | Status | Supersedes |
| --- | --- | --- | --- | --- |
| D-01 | Start with one professional and fixed appointment duration. | S1: fictional operating boundary. | Scenario constraint; no real approval. | — |
| D-02 | Use prepared availability for the first development slice; add administration before a pilot. | S1 and S2: isolate the first customer journey. | Proposed. | — |
| A-01 | Present observed checks and user acceptance separately. | S2: collaboration proposal. | Proposed; no execution authorization. | — |

## Assumptions and open decisions

| Item | Why it matters | When to resolve |
| --- | --- | --- |
| Hypothesis: customers prefer self-service booking for this use case. | The product may not reduce coordination if customers still need assistance. | Test during the MVP pilot. |
| Open decision: customer contact information and its permitted use. | Changes form design, storage and operational handling. | Before implementing storage of real customer data. |
| Open decision: who administers availability and accesses bookings. | The professional needs a usable, appropriately restricted workflow. | Before planning pilot readiness. |

## Changes

| Revision | Change | Source |
| --- | --- | --- |
| 1 | Initial illustrative product definition; no prior decision or approval implied. | S1 and S2 in the example brief. |
