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
