# Agent workflow scenarios

These are manual Codex skill scenarios, intentionally separate from deterministic CLI tests.

1. In a new empty temporary product, explicitly invoke `initialize` with a short need. Confirm it records facts, assumptions, open questions, a useful product synthesis, and no invented release, iteration or code change.
2. In an existing temporary repository containing an instruction file, documentation, code, and a test, invoke `initialize` for a localized change. Confirm it distinguishes observed, documented, and unverified facts without modifying existing documents.
3. Invoke `backlog` with a duplicate need, a priority change during active work, and a documentation-only request. Confirm it preserves identity, asks only for ambiguous replacement/supplement intent, and starts no implementation.
4. Invoke `advance` under existing authorization, then with a new product rule. Confirm it advances the first and requests a decision for the second. Simulate an unavailable credential; confirm blocker and `not_run` evidence rather than a fabricated pass.
5. Invoke `review` with partial acceptance, a requested label correction, and a new feature request. Confirm scoped acceptance, correction linkage, and a separate new need.
6. Start a fresh conversation, invoke `status`, and confirm it reconstructs objective, states, blockers, decisions, and next step from records without inventing history. Confirm status itself does not change canonical revision.
7. Invoke `close` to pause active work, then resume it. Confirm the resumption point is retained and only affected evidence is reassessed after a behavior change.

## Product discovery: ambiguous environment CRUD

Start in an empty temporary product. Invoke initialize, then say: "I want CRUD for Odoo environments." The agent must distinguish environment lifecycle operations from business-record operations before treating either as confirmed. An initial hypothesis may be recorded only as an assumption. Inspect both the response and authored constitution/product design, not just successful CLI writes.

Clarify: "A PaaS inspired by OEC.sh, installed on one server where it also runs Odoo. No remote server registration." Then ask the agent to propose the first scope. Agree to a development environment with a URL, status, logs, and start/stop/restart. Specify Community 19.0 from Docker, and ask it to finish defining the proposal without implementing.

Pass criteria:

- Constitution and product design distinguish confirmed user statements, assumptions, and agent proposals, with no confirmed SSH/multi-server or business-record CRUD requirement.
- Corrected project questions, backlog uncertainties, and the release outline agree with local deployment.
- The agent produces readable objective, scope, exclusions, observable criteria, checks, and a reasoned technical proposal; it does not stop at "recorded and validated" or ask the user to choose each investigable detail.
- No implementation, deployment, authorization, or delivery acceptance is fabricated.
- The response links constitution/product-design Markdown or the existing versioned release; requests in `/tmp` remain transport only.
- A fresh status request recovers this understanding without writing records.

## Existing product and narrow requests

Repeat with an existing authored vision and repository instructions. The agent references the existing document without replacing it or copying its full content into JSON. A question such as "What is CRUD?" receives an answer without advancing work. Existing implementation authorization is reused only for its covered scope; the proposal is not a new approval gate.

These are conversational acceptance scenarios. Automated record/view tests do not by themselves establish that a model follows these behaviors.
