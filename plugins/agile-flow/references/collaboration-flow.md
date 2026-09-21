# Collaboration outcomes

Read [the macro workflow](../AGENTS.md) for stage ordering, intent routing, and transition boundaries. This reference supplies the collaboration details used within that map.

Persistence supports the collaboration; a successful write establishes storage integrity, not agreement or product understanding. Follow the user's current intent rather than requiring a fixed ceremony or an AGENTS.md file. Existing repository instructions still apply.

| Stage | Reviewable outcome | Transition |
| --- | --- | --- |
| Understand | Product purpose, users, confirmed facts, assumptions, constraints, and success criteria | Propose a first useful outcome once material ambiguities are bounded. |
| Prioritize | Needs with value, priority rationale, and dependencies | Select a bounded outcome within the user's request. |
| Prepare | Objective, scope, exclusions, criteria, checks, technical approach, and unresolved product decisions | Execute only under applicable implementation authorization; continue permitted investigation meanwhile. |
| Develop | A usable result with scoped verification evidence and limitations | Present the result or explain a concrete blocker. |
| Review | Actual user feedback, criterion-level acceptance, and follow-up | Close or correct within existing scope; capture genuinely new needs separately. |

## Understand before recording conclusions

Distinguish user statements, observed facts, agent hypotheses, and proposals. Use `project.confirmed_facts` for sourced statements (include their source), `assumptions` for interpretations, and `proposals` for recommendations. Store `users` explicitly. A benchmark does not establish a requirement. Do not expand ambiguous "environment CRUD" into business-record CRUD or "my servers" into SSH/multi-server management. Ask the material product question with concrete alternatives while doing independent work.

A correction must reconcile affected project questions, backlog uncertainties, iteration plans, and recorded decisions. Retain history and source quotations, but remove resolved questions from current lists. Decisions superseded by actual later decisions retain their references; do not invent approvals to clean up records.

## Synthesize and prepare

During product definition, consolidate known context in authored `constitution.md`. Reference existing authored vision documents without copying their full content. Develop `roadmap.md` with version stages, then a release document with concrete scope and any MVP learning hypothesis when enough information exists. An MVP is a usable minimum for early users that tests whether the product is useful; it is not just the first technical task.

Use `plan-iteration` with a goal, selected item IDs, scope, exclusions, criteria references, checks, approach and open decisions. It produces `release/<version>/ITER-*/sprint-planning.md`, without an increment or authorization. Once scope is ready and execution authorized, use `prepare` with that iteration, the selected stories’ own DoD baselines and the actual permission reference.

Success criteria describe the product outcome for its user, not merely completion of this planning exercise. Keep candidate technical designs in proposals rather than confirmed facts.

Do not introduce a new blocking question for optional expansion beyond the requested first outcome. For example, proposing one development environment does not require resolving support for multiple environments now. State the bounded proposal and defer expansion unless the user requires it.

Distinguish product decisions requiring the user's choice from technical questions the agent can investigate. Propose a reasoned technical approach instead of returning each implementation detail to the user. Do not interpret agreement with an outline as permission to deploy or as acceptance of future work.

## Communicate the outcome

Prefer links to authored documents and generated indexes over state.json or temporary request files. After a write, inspect the documents and report any failure. Explain the understood result, remaining material uncertainty, and next useful action; do not end with storage confirmation alone. A question is optional, not a mandatory closing step. For a narrow factual or status request, answer within that scope without updating records or advancing work.

Authored documents and generated indexes have distinct ownership. Edit the relevant authored source; regenerate only the two indexes. Compare actual prose with user statements before reporting it as confirmed.

## Progressive refinement

Apply DEEP to the backlog: detail near work, estimate relatively when useful, allow sourced changes and preserve meaningful order. Apply INVEST to stories: independent meaning, negotiable scope, user value, estimability, iteration-sized scope and testable criteria. Explain deficiencies and refine or split; never fabricate six passing labels or story points. Use appropriate NFR, bug, technical-work and bounded-investigation formats. Keep distant work lightweight.
