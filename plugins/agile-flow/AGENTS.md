# Agile Flow macro workflow

Agile Flow helps a user and an agent turn a need into a useful, verified delivery while preserving shared understanding across sessions. This file is the workflow map. Skills contain the stage-specific actions; shared references define record, evidence, and authorization contracts.

Read this map when applying an Agile Flow skill. It does not authorize work, replace the user's request, or override applicable product-repository instructions. Installing the plugin does not install this file into the product repository. Resolve the actual product root before reading or changing its records.

## Route by intent

Use the earliest stage that needs attention, reusing context and decisions already available. Do not restart discovery or require every stage on every request.

| User intent | Skill | Required outcome |
| --- | --- | --- |
| Start a product or adopt a repository | [initialize](skills/initialize/SKILL.md) | Shared product understanding, labeled assumptions, and a proposed first useful outcome. |
| Capture or prioritize needs | [backlog](skills/backlog/SKILL.md) | Coherent needs, priority rationale, and a bounded next outcome. |
| Define the next delivery or advance authorized work | [advance](skills/advance/SKILL.md) | A reviewable preparation proposal, or implementation with scoped verification evidence. |
| Evaluate a delivered result | [review](skills/review/SKILL.md) | Actual user feedback and explicit follow-up for the reviewed scope. |
| Ask where work stands | [status](skills/status/SKILL.md) | A read-only account of facts, uncertainty, current validity, and next action. |
| Explicitly pause, cancel, close, or reopen | [close](skills/close/SKILL.md) | The requested administrative transition with unfinished work preserved. |

## Normal development cycle

**Constitution → version roadmap → concrete release and MVP definition → product BL needs → iteration US work → development and verification → review → learning.**

1. **Understand the product.** Reuse the user's statements and relevant repository evidence. Distinguish confirmed facts, assumptions, and proposals. Resolve ambiguities that would change the product; investigate technical uncertainty within the requested scope. Produce a readable synthesis rather than ending with storage confirmation.
2. **Choose the next useful outcome.** Maintain a coherent backlog, explain priority, and make near-term scope concrete. Correct related records when the user clarifies intent. Keep optional future expansion out of current blockers.
3. **Prepare a reviewable proposal.** State objective, included and excluded scope, observable criteria, checks, technical approach, and remaining product decisions. Preparation may proceed under a definition or planning request without implementation permission. A proposal is not an executable increment or delivery acceptance.
4. **Develop under existing authorization.** When scope is ready and execution is covered, use the normal authorized preparation/start flow. Keep at most one active development increment. Reuse valid permission; do not require ceremonial reapproval. Verify against the actual delivery and record limits or blockers honestly.
5. **Review the result.** Present what changed, the evidence, and what the user is evaluating. Keep implementation, verification, and user acceptance separate. Record only decisions the user actually made.
6. **Adapt or close.** Correct existing criteria within the same increment when appropriate. Record new needs separately, apply useful learning, and preserve history. Administrative closure requires the user's instruction and never manufactures completion.

## When to continue or stop

Continue useful work within the current request when remaining questions can be investigated or deferred without changing the agreed outcome. Ask a focused question when a material product decision is necessary, explaining its concrete impact. Do not turn every technical choice into a user question.

Stop dependent execution at missing authorization, a necessary unresolved product decision, a real blocker, or a delivery ready for user review. Continue independent authorized work where possible. A narrow explanation or status request does not start a development cycle or mutate records.

## Make progress reviewable

The user should be able to identify the understood product, agreed scope, current result, unresolved decisions, and next action without reading internal JSON requests.

- Present context through constitution.md, strategic version stages through roadmap.md and concrete delivery/MVP scope through release/<version>/release-<version>.md. BL documents own product needs; US documents inside an iteration own concrete typed work, criteria and DoD. Iteration planning is sprint-planning.md. Verification, review and retrospective appear when meaningful records exist.
- Keep existing authored product documents in place and reference them. Do not create a competing editable copy.
- Authored Markdown is the functional authority. Only `backlog/product-backlog.md` and `summary.md` are generated. Technical metadata lives in `.internal/state.json`; preserve manual authored edits.
- Temporary request files are transport only. They are not product documentation or a deliverable.
- After a write, check view generation and compare the readable result with the user's intent. Report rendering failures and preserve manual edits.
- Conclude with the substantive result and next useful action. A successful mutation is not proof of semantic correctness, completed functionality, or approval.

## Detailed contracts

- [Collaboration outcomes](references/collaboration-flow.md): synthesis, corrections, planning proposals, and communication.
- [Session protocol](references/session-protocol.md): root resolution, record operations, and resumption.
- [Authorization](references/authorization.md): scope, permission reuse, and boundaries.
- [Readiness and quality](references/readiness-and-quality.md): preparation and evidence.
- [Record contracts](references/record-contracts.md): document authority, evidence, and recovery.
- [Review and learning](references/review-and-learning.md): acceptance, corrections, and adaptation.

Keep this map and the detailed contracts consistent. When they conflict, follow higher-priority instructions and surface the discrepancy rather than inventing authorization.

## Source and product boundaries

The product checkout, plugin source repository, and installed plugin cache are separate. A product-format request does not authorize patching installed scripts or tests. Route renderer improvements to the actual source repository. Never patch the cache. Migration of a live schema-1 project is explicit, previewed and backed up. No installation, release or live migration follows automatically from source development.

Do not turn a release into only a changelog: preserve planned scope separately from delivered outcome. The roadmap may identify the MVP milestone; detailed MVP scope and learning belong in the release. No parent Definition of Done document is created.
