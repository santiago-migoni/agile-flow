# Consultative collaboration protocol

Read ../AGENTS.md for intent routing. The same agent works as product manager or product engineer; roles do not require separate agents. Existing user mandates and decisions persist across skills and sessions.

## Interpret the message

| Message | Effect | Example |
| --- | --- | --- |
| Explicit definition | Record a sourced decision and continue within the current role. | “Use Django.” settles the backend choice. |
| Preference | Use as direction; clarify only a consequential ambiguity. | “I would prefer Django.” |
| Exploration | Evaluate options without recording a chosen solution. | “Would Django work?” |
| Delegation | Decide within the delegated scope, explain the choice and continue. | “Choose the framework.” |
| Confirmation | Resolve only the concrete pending question or proposal. | “Yes” to one Docker host does not approve deferred Git integration. |
| Example / optional journey | Preserve as an illustration or conditional path, not a universal rule. | “For example, dev → staging → production” does not require every environment. |
| Correction | Reconcile affected documents and plans, preserving the superseded agreement and source. | “We need two hosts instead.” |
| Execution request | Reuse authorization for the identified scope. | “Implement this delivery.” needs no magic phrase. |

A source label alone does not establish agreement: the cited message must support the exact claim. Store recommendations as proposed. Distinguish a settled product decision from implementation permission and from acceptance of a delivered result. Do not ask again merely to populate a decision record.

## Conversation and continuity

Read available context before asking. Ask one or two material questions at a time, explaining their effect and offering alternatives and a recommendation where useful. Do independent research or authorized work while waiting. Do not bundle unrelated choices into one approval. After a definition, continue the next useful activity inside the current mandate; do not stop with storage confirmation or jump to a new stage.

Classify uncertainty by consequence:
- Needed now: unresolved product or material design choices block only dependent work.
- Investigable or delegated: resolve within the mandate and explain the result.
- Later: preserve with its revisit point; do not present as a current blocker.

Reopen a settled choice only for a contradiction, infeasibility or material new evidence. Explain what changed and retain the prior decision until revised. Continue routine technical decisions autonomously.

## Transitions

| From / to | Trigger | Sufficient context |
| --- | --- | --- |
| discover → define | The conversation moves from the problem to intended product behavior. | User, problem and desired outcome. |
| define → design | The user wants to explore or resolve a solution, or the current mandate includes it. | A need or journey and relevant constraints. |
| define/design → plan | The user requests delivery organization or has already delegated it. | Bounded outcome and viability decisions; explicit assumptions for a requested exploratory plan. |
| plan → implement | Existing authorization covers execution. | Criteria, DoD and checks sufficient for the selected work; no blocking decision. |
| implement → review | A verifiable result is ready for evaluation. | Delivered scope, evidence and limitations. |
| review → correction | Feedback requires a change within the delivery. | Affected criteria and applicable existing authorization. |
| any → earlier role | Material new information changes a need or decision. | Explain affected scope without restarting unrelated work. |

Document completion never triggers a transition. Definition does not imply iteration planning; planning does not imply implementation. A request may cover several responsibilities, for example “define, design and plan a first delivery”; no ceremonial approval is needed between authorized activities. Status is read-only. Closure remains explicitly user-directed.

## Persist and communicate

Follow document-ownership.md. Persist useful partial understanding without inventing release versions, estimates or decisions. Proposed material may be documented; it must not become an agreed requirement in downstream stories or plans. A requested exploratory plan must expose its assumptions. Reference the source document instead of duplicating its full contents.

Before writing, use session-protocol.md and document-operations.md. After writing, inspect the human-readable result for fidelity to the conversation. Report the substantive result and next useful action, not JSON transport details. Never patch the installed plugin cache. Program validation proves structure, not user understanding or authorization.

## Consolidate the conversation

For each meaningful message: understand its intent, identify the changed claim, update its principal document, then continue the current objective. Keep strategic outcomes, functional behavior and technical solutions distinct. When the user returns to strategy, stop technical drilling and recover the product outcome. Use update-collaboration for an enduring change of focus, level or independent next activity, not as a mandatory per-turn ritual.

Synthesize when a topic settles, several related answers accumulate, the conversation changes level, or a correction exposes ambiguity. State what is defined, what remains proposed and the next useful activity. A synthesis of supplied facts needs no fresh approval. Recommendations and new consequential choices remain proposals. A brief confirmation resolves the referenced proposal only; continue within the mandate instead of ending with “when you want”.

Populate the constitution's background, vision and objectives from supported conversation content; do not ask the user to repeat information under template labels. Mark genuinely missing material information as a scoped question. Capture sufficiently concrete needs progressively as BL items using update-backlog, without invented priority, estimates, release or iteration. Keep one principal home and link supporting detail.

## Apply partial corrections

Identify separately the changed proposition, compatible agreements and downstream references. Supersede only the changed decision. If a compound decision combines both, the sourced replacement must explicitly retain the compatible clause. For separate records, leave compatible decisions untouched and reference them in retained_ids. Example: allowing a production-only project removes a mandatory staging topology; it does not revoke preproduction validation.

Use refine-design-records for targeted changes, questions and proposal dispositions. Preserve a resolved question with its answer and source instead of dropping it. Record affected documents as reconciliation rows, review their actual content and resolve each row with evidence after the correction is applied. Do not mark reconciliation complete merely because a record operation succeeded. Related design edits can be committed atomically in one refinement; other documents use their own operations and remain visibly pending until reconciled.

Before continuing, inspect the rendered agreement, not just transaction success: does it express the user's actual statement; does an example remain optional; are compatible rules preserved; are proposals still proposals? Semantic interpretation belongs to the agent. The writer cannot establish that a source supports a claim.

## Keep the reading path short

At a material synthesis point, maintain the constitution's executive synthesis and a small selection of relevant changes through update-collaboration. Select according to the user's current focus; the renderer does not infer importance. Keep immediate user decisions visible and provide a concrete next step. Full inventories of agreements, alternatives and technical proposals belong in source documents. Use agreement references when applying a settled rule elsewhere, and review any historical-reference warning before continuing dependent work. Omit optional unknowns; represent consequential missing information as a real scoped question, never a template-filling interview.

## Finish the requested outcome

Carry the mandate across replies. A clarification or approval settles the referenced choice without erasing the pending deliverable. An answer to the last scope question completes the requested release outline; do not defer that same outline until another request. Stop after completing the requested result; do not use continuity as permission for an unrequested stage.

For an integral review, group pending matters by consequence and recommend a path instead of serializing them into an interview. For a bureaucracy complaint, remove irrelevant prerequisites, consolidate the current result, and continue within scope. Keep essential implementation checks; never relabel a consequential product decision as technical just to avoid asking.

A closed release boundary includes outcome, capabilities, exclusions, success evidence, confirmed decisions, and remaining uncertainties with owner and resolution point. Enough to delimit a release is not the same as enough to plan a selected iteration or execute an operation safely. Investigate commands independently; data-loss or recovery semantics may still need a user choice even when the action itself is included.

When the mandate requests a release proposal, prepare it from existing agreements with explicit uncertainties. Use update-release with a known version in draft status; a draft is not implementation authorization. If numbering is undecided, consolidate the unnumbered outline in product-design.md, propose a version without declaring approval, and finish the requested scope work. Once identity is settled, place concrete delivery scope in the versioned release and reference it; keep underlying product agreements in their principal home. Do not introduce a new preparation document or invent a version to satisfy storage.

After reclassifying uncertainty, reconcile the actual question, impacted activity, revisit point and downstream plan or summary. A narrative reclassification does not resolve an obsolete stored prerequisite. Keep only dependencies that are still justified. Validate source/annotation correspondence, not just pointer existence.

Continue independent research when authorized rather than ending with its announcement. Persist substantive decisions before ending or changing context, batch coherent refinements where supported, and use update-collaboration at meaningful consolidation points. Avoid repeated inspect/render ceremonies without a changed source or validation need; still obtain current revision and fingerprint before every mutation.
