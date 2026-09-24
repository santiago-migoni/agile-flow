# Strategic and operational lifecycle implementation

The approved model connects strategic product definition with bounded operational delivery. Strategy and operations continuously inform each other through the backlog. A document becoming complete never authorizes a transition.

## Implemented responsibilities

| Responsibility | Skill | Principal records |
| --- | --- | --- |
| Context, objectives, costs and viability | discover | constitution.md |
| Needs and expected behavior | define / backlog | product-design.md and BL records |
| Technical and interface solution | design | architecture.md |
| Possible version outcomes | roadmap | roadmap.md |
| Bounded release and fulfillment | release | Versioned release document |
| Selected work and owner review access | sprint | sprint-planning.md and typed US records |
| Authorized execution and verification | implement | Code and verification.md |
| Actual user evaluation | review | review.md |
| Observed process learning | retrospective | retrospective.md |

initialize, plan and advance remain compatibility entrypoints. The package identity, marketplace path and document directory layout are preserved. The managed project instruction template is version 2; updating existing projects remains explicit.

## Runtime contract

The current schema remains 4 / editorial-v2. Explicit adoption records iterative-v1 in the constitution. Agreements, findings, progress and conclusions remain authored Markdown; commitment fingerprints and story definition digests live in portable technical baselines. Existing record transactions provide concurrency checks, idempotency, journaling and recovery.

Release commitments bind bounded BL contributions and exit conditions. Sprint commitments bind the selected definitions, tasks and owner access method. They do not create execution authorization. Drafts may coexist; only one committed, unconcluded sprint owns execution. A committed sprint cannot be silently extended or rebaselined. Source-defined release revisions retain previous scope without modifying active sprint commitments.

Findings distinguish necessary implementation details, current-scope defects, opportunities and material changes. Opportunities require a BL link but acquire no automatic target release or sprint. Material findings block only dependent execution until a sourced resolution or interruption. Task observations do not overwrite the agreed plan or imply user acceptance.

Sprint completion requires implemented, currently verified and accepted selected work. Interruption preserves outstanding story identities and history. Follow-up stories retain the BL parent and reference the original US in another iteration. Accepted and verified follow-up work can fulfill the release without rewriting the interrupted sprint. Explicit release assessment still requires evidence for each committed BL contribution and exit condition.

Release fulfillment is separate from publication. Later stale delivery evidence produces needs_reassessment in inspection and the generated summary; the historical assessment remains available. Publication references record external facts only and do not invoke Git or deployment.

## Adoption

Use the lifecycle CLI preview and apply procedure in [document operations](../plugins/agile-flow/references/document-operations.md). Adoption preserves current documents, authored notes, IDs, decisions, acceptance and delivery baselines. It reports missing commitments and existing interface content rather than inventing or moving them. Existing prepared sprints can supply missing review access when recording their sourced commitment; conflicting historical criteria or DoD must be reconciled first.

Old interface records remain readable in product-design.md. New interface solution design belongs in architecture.md. Content relocation requires a reviewed editorial reconciliation. Older plugin writers must not manage adopted projects. No live app-odoo migration, installation or publication is part of source implementation.

## Verification boundaries

The automated suite uses isolated temporary product checkouts. Lifecycle scenarios exercise scope protection, manual-edit rejection, independent execution permission, future opportunity capture, separate task observations, material-change blocking, interrupted carry-over, release completion without publication, stale evidence, active-project adoption and Markdown preservation. Existing tests cover evidence validity, recovery, Git, migrations, packaging and instruction preservation.

Skill and package validation plus relative-link checks validate structure and discoverability. They do not establish real conversational behavior. The following fresh-agent acceptance exercises remain operational validation after an authorized installation:

| User scenario | Expected behavior |
| --- | --- |
| Define a new product and discuss architecture | Consolidate strategy without automatically planning release or sprint. |
| Approve a release, then request sprint planning | Reuse the agreement, establish bounded selected work and review access, and distinguish execution permission. |
| Suggest a new capability during implementation | Capture an unassigned need; preserve current sprint commitment. |
| Report a defect in an agreed criterion | Correct and reverify under existing applicable permission. |
| Discover an infeasible architecture assumption | Explain impact, continue independent work and reconcile or interrupt only the dependent scope. |
| Close a sprint with unfinished work | Record actual review/learning, preserve outstanding work and propose future selection without scheduling it automatically. |
| Complete the next sprint and release | Verify contributions and actual acceptance; do not publish without publication authorization. |

No independent live Codex exercise is claimed by deterministic test success.

The deterministic regression checks and lifecycle fixtures are in [test_iterative_lifecycle.py](../plugins/agile-flow/tests/test_iterative_lifecycle.py). Package/skill validation and reference-link checks also passed during implementation. Live conversational evaluation remains pending an authorized installation.
