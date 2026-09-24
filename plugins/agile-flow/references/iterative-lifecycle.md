# Strategic and operational lifecycle

Strategy and delivery are concurrent, mutually informing responsibilities, not a one-way document pipeline. Strategy: constitution -> requirements/product-design and BL needs -> architecture including interface design -> roadmap. Operations: release -> sprint and typed US work -> implementation/verification -> user review -> retrospective -> next sprint or release assessment. Learning feeds strategy and the backlog in either direction.

## Boundaries and sources

The backlog bridges both levels. BL records are needs; iteration US records are selected work of type US/NFR/BUG/TCH/SPK. An explicit user definition settles that decision. Reuse authorization covering the activity; scope commitment never substitutes for execution authority. Do not demand another approval when the user's current instruction already covers it. Unknown future details do not block independent work.

Before execution, record the release and sprint commitments using their actual agreement sources. Capture the owner review/access method before sprint commitment. One committed, unclosed sprint owns execution at a time; multiple exploratory drafts are allowed. Implementation increments remain internal evidence units, with at most one active increment. Tasks have an immutable agreed plan and separate dated progress observations.

## Discoveries during a sprint

| Classification | Treatment |
| --- | --- |
| implementation-detail | Resolve within the existing mandate and selected criteria. |
| defect | Correct and reverify the current agreed criteria. |
| opportunity | Capture an unassigned BL need for future prioritization. |
| material-change | Record impact, stop only dependent work, and obtain or reuse the actual decision to interrupt/replan. |

Use record-finding with classification, origin, impact, source and disposition. Opportunities require a BL link. A discovery does not automatically enter this sprint or the next one. Strategy may evolve without changing a sprint commitment. Never silently refresh a committed baseline. If the goal becomes infeasible, conclude the sprint as interrupted with the sourced reason and outstanding work; plan a new sprint with links to the original work. Routine corrections use existing correction/evidence operations.

## Closure

Review records actual user evaluation, not test success. Retrospective records observed process learning, not product acceptance. conclude-sprint requires both records, a sourced conclusion and an explicit list of outstanding selected stories. Completed closure requires all selected work implemented, effectively verified and accepted. Interrupted closure preserves unfinished states and frees the execution slot. Follow-up stories keep the same parent BL and reference the original US through follows_up; never move or erase the old story.

assess-release records either incomplete or completed fulfillment, separate from publication. Completed fulfillment requires all release iterations closed, current verified/accepted coverage for every selected story, and satisfied exit conditions with actual evidence and acceptance source. Removing a contribution requires revise-release, preserving previous scope and rationale; closing a sprint never removes release scope. Published historical releases remain immutable. Publication is an external authorized action, not a side effect of any record operation.

## Adoption and compatibility

New initialization follows initialize then adopt-lifecycle under the same mandate, before any delivery planning. Existing projects require explicit adoption: lifecycle --dry-run reports the checkout fingerprint, active work, missing agreements and legacy interface content; lifecycle --apply requires that fingerprint and authorization_source. Adoption records the new contract only. It never invents commitments or moves authored content. Existing active work remains recorded but dependent new preparation/start requires reconciliation and commitments. Old evidence and review sources remain unchanged. Structural legacy migrations still use migrate first.

The transactional journal backs up changed bytes under .internal/local. Existing UI design content in product-design remains readable and referenceable; relocate it only through a separately reviewed, sourced reconciliation. New interface solution design belongs in architecture. Updating the plugin does not migrate a live project or reinstall project instructions.
