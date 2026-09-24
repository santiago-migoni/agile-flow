# Agile Flow macro workflow

Agile Flow helps a user and an agent turn a need into a useful, verified delivery while preserving shared understanding across sessions. This file is the workflow map. Skills contain the stage-specific actions; shared references define record, evidence, and authorization contracts.

Read this map when applying an Agile Flow skill. It does not authorize work, replace the user's request, or override applicable product-repository instructions. Installing the plugin does not install this file into the product repository. Project instruction setup uses the separate [managed project template workflow](references/project-instructions.md); it never copies this internal map wholesale. Resolve the actual product root before reading or changing its records.

## Route by intent and responsibility

The same collaborator first helps decide what to build, then designs and delivers it under the current mandate. Roles do not require separate agents. Read [the collaboration protocol](references/collaboration-protocol.md) for message semantics and transition rules.

| Intent | Skill | Role and outcome |
| --- | --- | --- |
| Explore a problem or adopt a product | [discover](skills/discover/SKILL.md) | Product manager: shared understanding |
| Define behavior, journeys, scope or priorities | [define](skills/define/SKILL.md) | Product manager: agreed needs and experience |
| Discuss interface or technical solution | [design](skills/design/SKILL.md) | Product engineer, consultative: alternatives and sourced choices |
| Project possible versions | [roadmap](skills/roadmap/SKILL.md) | Product manager: strategic direction |
| Delimit or assess a release | [release](skills/release/SKILL.md) | Product manager with engineering input: bounded outcome |
| Organize an iteration | [sprint](skills/sprint/SKILL.md) | Product engineer: committed sprint and review access |
| Learn from the process | [retrospective](skills/retrospective/SKILL.md) | Both: observed adjustments |
| Capture and prioritize discoveries | [backlog](skills/backlog/SKILL.md) | Both: needs without automatic scheduling |
| Execute authorized work | [implement](skills/implement/SKILL.md) | Product engineer: usable result and evidence |
| Evaluate delivery | [review](skills/review/SKILL.md) | Both: actual acceptance, corrections and learning |
| Ask where work stands | [status](skills/status/SKILL.md) | Read-only situation and next action |
| Pause, cancel, close or reopen | [close](skills/close/SKILL.md) | Requested administrative change |

initialize routes to discover; plan routes to roadmap/release/sprint; advance routes by current intent and mandate. Read [the iterative lifecycle contract](references/iterative-lifecycle.md) for commitments, findings, closure and adoption. Strategy and operations continuously inform each other through the backlog. Existing record operation names remain compatible.

## Continue within the mandate

Treat explicit user definitions as settled within their stated scope. Record them and continue the current responsibility without redundant confirmation. A confirmation of one host does not approve a stack, exclusions or implementation. Distinguish definitions, preferences, exploration, delegation and execution requests. Resolve delegated and routine technical choices autonomously.

Discovery does not automatically create a release. Definition does not imply planning. Planning does not imply execution. Document completion never triggers a transition. Existing authorization may cover several activities; reuse it without ceremonial approval or special phrases. During focused exploration, ask one or two material questions at a time, with context, alternatives and a recommendation where useful. When the user requests an integral review, present grouped pending matters and complete the requested synthesis; apply the completed-outcome contract in the collaboration protocol. Continue independent authorized work while a necessary decision is pending. Defer future uncertainty rather than presenting it as a current blocker.

Reopen a settled decision only for contradiction, infeasibility or material new evidence, preserving its source and history. Return to the relevant role without restarting unrelated work. Keep at most one active implementation increment; development, verification and user acceptance remain separate.

## Make progress reviewable

The user should be able to identify the understood product, agreed scope, current result, unresolved decisions, and next action without reading internal JSON requests.

- Follow [document ownership](references/document-ownership.md). product-design.md owns needs, journeys and expected behavior; architecture.md owns the solution, including interface design, technical alternatives and decisions. Create them only with useful content, independently of releases or iterations. Present context through constitution.md, strategic version stages through roadmap.md and concrete delivery/MVP scope through release/<version>/release-<version>.md. BL documents own product needs; US documents inside an iteration own concrete typed work, criteria and DoD. Iteration planning is sprint-planning.md. Verification, review and retrospective appear when meaningful records exist.
- Keep existing authored product documents in place and reference them. Do not create a competing editable copy.
- Authored Markdown is the functional authority. Only `backlog/product-backlog.md` and `summary.md` are generated. Portable technical metadata lives in `.internal/registry.json`; local control lives in `.internal/local/`; preserve manual authored edits.
- Temporary request files are transport only. They are not product documentation or a deliverable.
- After a write, check view generation and compare the readable result with the user's intent. Report rendering failures and preserve manual edits.
- Maintain a concise agent-authored executive synthesis in the constitution when consolidating meaningful progress. Summary projects that selection and groups proposal inventories; it does not decide relevance. Reference principal agreements by document and ID, and reconcile historical-reference warnings before dependent work.
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

The product checkout, plugin source repository, and installed plugin cache are separate. A product-format request does not authorize patching installed scripts or tests. Route renderer improvements to the actual source repository. Never patch the cache. Migration of a live legacy project is explicit, previewed and backed up. No installation, release or live migration follows automatically from source development.

Do not turn a release into only a changelog: preserve planned scope separately from delivered outcome. The roadmap may identify the MVP milestone; detailed MVP scope and learning belong in the release. No parent Definition of Done document is created.

## Clean documents and Git

The current source implements schema 4. Read [clean Markdown and Git](references/clean-markdown-and-git.md). Documents contain no private field markers. Executable Markdown templates and portable structural schemas coordinate partial updates. Preserve user notes and reject ambiguous headings. Reconstruct from the current checkout, never from stale local caches. At a coherent outcome, follow the user-sourced Git policy; preview explicit paths before committing. Initialization, publishing and destructive Git operations require their own authorization.
