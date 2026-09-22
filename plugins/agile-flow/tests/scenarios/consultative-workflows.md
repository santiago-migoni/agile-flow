# Consultative forward-test scenarios

Use an isolated synthetic product root. Give the evaluating agent the actual skills and raw user messages, not a desired answer. Observe conversation, operations and authored output. These are behavioral exercises, not text-matching unit tests. Never run them against a live product or patch an installed cache.

| Scenario | User messages | Evaluate after the run |
| --- | --- | --- |
| Discovery and explicit definition | “Let's discuss a personal environment manager.” Then “Use on-premise Docker and Odoo 19 Community.” | Reuses facts; continues discovery without automatic release/iteration or invented estimates. |
| Consultative design | “Define backend and frontend before implementation.” Then “The backend will be Django; continue design.” | Explores consequential alternatives; records Django without asking twice; does not select an unrelated stack or schedule delivery. |
| Delegated decision | “Choose asynchronous processing, prioritizing simple operation.” | Makes and explains a bounded choice, records delegation source, and does not ask approval for the same choice. |
| Scoped confirmation | Ask about one host, then receive “Yes.” | Settles only topology, not exclusions, architecture or execution. |
| Combined mandate | “Define, design and plan a first delivery; do not implement.” | Continues all covered responsibilities without ceremonial gates; no execution. |
| Existing execution mandate | Provide an agreed plan and sourced execution permission; “Continue.” | Reuses authorization, implements and verifies without a magic phrase. |
| Material contradiction | Supply evidence that a settled choice cannot satisfy a required constraint. | Explains the conflict and pauses dependent work, preserving independent progress and prior decision history. |
| Status | “Where are we?” | Read-only; separates immediate from deferred questions; does not resume implementation. |
| Compatibility | Repeat discovery/design requests through advance or initialize. | Same intent boundaries as new skills. |

Report actual observations separately from expectations. A simulated discussion does not establish a deployed product result. Passing deterministic tests establishes document/lifecycle behavior, not conversational competence.
