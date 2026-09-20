# agile-flow Functional Specification

**Date:** September 20, 2026.  
**Version:** Earlier draft copy, translated into English.  
**Status:** Superseded draft. Use `docs/functional-specification.md` as the approved source.  
**Provenance:** Translated reference copy retained from the former root-level draft. Approval belongs to the document in `docs/`; this copy is not an independent source of requirements.  
**Basis:** Product vision and conversation agreements. Approval of this specification does not mean it has been implemented.

## 1. Purpose and Scope

agile-flow is a Codex plugin for software development between a person and an agent. It turns needs into verifiable increments, preserves context across sessions, and adapts work based on user review.

The first version covers the complete cycle in new projects and existing repositories: understand, prioritize, prepare, develop, verify, review, and adapt. It supports status queries, blockers and changes, resumption, and increment or project closure.

This specification defines behavior and observable outcomes. It does not prescribe a mandatory document chain, architecture, commands, languages, or storage formats. Technical planning is visible and proportional to the work.

## 2. Participants and Autonomy

The user directs the product: needs, priorities, constraints, and functional acceptance. The agent clarifies needs, investigates, proposes options, organizes technical work, implements, verifies, and maintains records.

| Situation | Expected behavior |
| --- | --- |
| Technical decision within authorized outcome and scope | The agent decides and advances, recording reasons when relevant to continuity |
| Missing technical detail that can be investigated | The agent investigates rather than returning the investigation as a question |
| An alternative changes expected behavior, scope, external cost, or a material product commitment | Present context, consequences, and a recommendation; wait before dependent work |
| Applicable authorization already exists | Reuse it without requesting it again |
| The request is limited to analysis or documentation | Complete that work without inferring authorization to implement |
| The user accepts a result | Record the specific delivery and scope covered |

Autonomy operates within actual environment permissions. The plugin does not bypass access restrictions or interpret functional acceptance as automatic permission to publish, deploy, or perform other external actions.

Questions explain what decision is missing and why it affects the result. Independent authorized work may continue while awaiting a response. Silence is not a decision.

## 3. Shared Concepts

| Concept | Functional meaning |
| --- | --- |
| Project | Product context linked to an identified work location |
| Vision | Problem, users, expected value, and success criteria |
| Backlog item | Pending need, fix, technical improvement, or investigation with stable identity |
| Increment | Bounded work aimed at a verifiable outcome |
| Technical task | Work needed to produce an increment; it does not replace the objective |
| Acceptance criterion | Observable condition for evaluating a particular need |
| Readiness | Sufficient information and authorization to proceed without independently resolving an outstanding product decision |
| Definition of done | Quality conditions applicable in addition to item-specific criteria |
| Evidence | A check result identified with its scope and the work state evaluated |
| Blocker | Impediment preventing an identified part of the work |
| Decision | Choice with author, reason, scope, and date or temporal reference |

A product increment targets a usable outcome. A bounded investigation has a question, work limit, and learning result. It is explicitly an investigation, not delivered functionality.

## 4. Functional Capabilities

### F01. Start a New Project

Collect or reuse the problem, users, expected outcome, constraints, and success criteria. Separate supplied facts, assumptions, and open questions. Propose an initial backlog and a valuable first increment or an investigation needed to define it.

Do not require full product detail before proceeding. Reuse sufficient input without repeating a questionnaire. Do not invent interviews, researched users, or market validation.

**Acceptance:** Given an initial idea, the user can identify the understood problem, assumptions, proposed first result, and missing decisions. Repeating initialization for an existing managed project retrieves its records without duplication.

### F02. Adopt an Existing Repository

Confirm the relevant project location and inspect instructions, documentation, code, and tests pertinent to the change. Distinguish observed behavior, documented behavior, and unverified information.

Reuse existing records with provenance. Do not automatically migrate, replace, or reorganize user documentation. Broaden inspection when concrete dependencies or risks require it, explaining why.

**Acceptance:** For a localized fix, identify affected areas, relevant dependencies, constraints, and the next step. Report disagreements between documentation and code without treating either as sufficient proof of functional acceptance.

### F03. Maintain and Prioritize the Backlog

Every item retains identity, need or purpose, type, state, and provenance. Refine near-term items with criteria, dependencies, and uncertainties; distant items can remain general.

Propose priorities using value, risk, dependencies, and effort as distinct factors. User-decided priorities prevail; explain dependencies that prevent following them. The agent may sequence technical tasks within an authorized increment.

Compare new requests with existing items. Update the same work while preserving the reason for the change; disclose ambiguous matches.

**Acceptance:** Adding an already recorded need does not silently create a duplicate. A priority change identifies the affected item, user decision, and effect on current work.

### F04. Prepare the Next Increment

Before implementation, make the objective, included and excluded scope, criteria, dependencies, relevant uncertainties, and verification approach explicit. Reuse project quality conditions and propose missing ones without imposing unrelated requirements.

Preparation is sufficient when the outcome is testable and does not depend on an unresolved product decision. Investigable technical uncertainty need not stop all preparation. Detail near-term work without elaborating every future task.

Selection must be covered by a user request or authorization. Once covered, communicate the technical plan and execute without another ceremonial approval. Do not start a different increment merely because it is in the backlog.

**Acceptance:** Proceed to development for an authorized, prepared increment. If access to a new feature requires a product decision, ask before implementing that rule while continuing independent investigation.

### F05. Develop and Manage Blockers

Make the necessary changes, keep work connected to its objective, and verify proportionally to affected paths. Preserve unrelated changes and distinguish preexisting work from the agent's contribution.

Keep one active development increment per project; organize its internal tasks by dependency. An explicit priority change may suspend it with a resumption point. A delivery awaiting review does not prevent working on another already-authorized increment.

Each blocker records what it prevents, affected work, relevant attempts, and its resolution condition. Elapsed time or opening another task does not resolve it.

**Acceptance:** If a credential is missing, record the affected check as not run, identify the blocker, and complete available independent checks. If a prior change prevents a test, distinguish the observed failure from an unconfirmed cause.

### F06. Verify and Present the Delivery

Map criteria and quality conditions to checks. Each check reports result, scope, reference to evaluated work, and limitations; distinguish passed, failed, and not run.

Explain what changed, how it addresses the objective, evidence, and what the user should review. Do not declare technical verification complete when a required check failed or could not run. Partial progress can be presented with explicit limitations.

**Acceptance:** Passing unit tests with a required functional check outstanding means partial verification. A later behavior-affecting change requires renewed verification; previous evidence remains historical.

### F07. Capture User Review

The user may accept, request changes, or defer review. Record the decision against the specific delivery. Clear acceptance in ordinary language is sufficient; no special phrase or command is required.

Ask when an ambiguous response does not identify what is accepted. Acceptance of a proposal or plan is not acceptance of a future delivery.

Changes needed to meet existing criteria stay linked to the increment. New needs are recorded with their impact and require the corresponding scope decision. Partial acceptance applies only to identified parts.

**Acceptance:** Distinguish a requested label correction from an added feature. If the user accepts a delivery with verification outstanding, record acceptance without marking the unperformed check as passed.

### F08. Adapt Work and Improve the Process

After review, update the backlog and propose the next step. When relevant learning exists, briefly reflect on observed facts: what helped, what hindered, and what adjustment to try.

Technical improvements within agreed autonomy may be applied directly. Changes to collaboration, scope, or user commitments are proposed for decision. Improvement actions specify what changes and how to observe their effect. Retrieve them in the next cycle and evaluate them, or explicitly note insufficient evidence.

**Acceptance:** If ambiguity caused rework, the next increment incorporates the agreed improvement in acceptance examples. If no improvement is identifiable, say so without fabricating actions or requiring a meeting.

### F09. Inspect Status and Resume

Expose the current objective, active increment, development state, verification, acceptance, blockers, pending decisions, and next step.

On resumption, read persistent context and compare relevant records with the repository. Report external changes and outdated references. Do not overwrite user decisions to match code or assume external changes were accepted.

**Acceptance:** A session without previous conversation history can recover those facts without asking the user to reconstruct the project. Missing or incomplete records lead to an explicit account of known, unknown, and evidence-reconstructible information, never invented prior decisions.

### F10. Change Direction, Pause, and Close

An explicit pause stops new development actions and preserves a resumption point. A status question neither pauses work nor cancels the current objective.

Explain a new priority's impact and apply an unambiguous instruction. If unclear whether it replaces or supplements current work, ask before dependent changes.

Closing an increment reports results, evidence, acceptance, and outstanding work. Closing or canceling a project preserves work and decisions; it does not delete files or mark unfinished work complete. The user may close with unfinished work explicitly identified.

**Acceptance:** Interrupting an increment for an authorized urgent need preserves completed work and the reason. On resumption, identify evidence that must be reassessed.

## 5. Work State

Three independent dimensions prevent a single label from hiding outstanding work. Labels and stored values use English.

| Dimension | Values |
| --- | --- |
| Development | `pending`, `preparing`, `ready`, `in_progress`, `implemented`, `canceled` |
| Verification | `not_run`, `partial`, `failed`, `passed` |
| Acceptance | `not_requested`, `pending`, `changes_requested`, `accepted` |

Blocked and suspended are additional conditions with reasons and scope; they do not erase achieved state. Partial acceptance is recorded against identified parts, never as full acceptance.

Transition rules:

- `ready` requires F04 information; `in_progress` requires applicable authorization.
- `implemented` describes completed changes, not test results.
- `passed` requires satisfactory evidence for all required checks of the current delivery.
- `accepted` requires a real user decision covering the identified scope and result.
- Changes reopen affected work only. Previous evidence and acceptance remain historical and must be reassessed if their basis changes.
- Report a delivery as completed and accepted only when implemented, technically passed, and accepted for its current state. Otherwise name the outstanding dimensions.
- Cancellation and administrative closure are not completion.

## 6. Minimum Persistent Information

Physical format is a design decision. Preserve:

| Logical record | Required information |
| --- | --- |
| Context | Project identity and location, vision, constraints, relevant references |
| Backlog | Item identities, purposes, priorities, provenance, relationships |
| Increment | Objective, scope, criteria, technical approach, applicable authorization, states |
| Decisions | Author, reason, scope, temporal reference, superseded decisions |
| Evidence | Check performed, evaluated state, result, limitation, inspectable reference |
| Blockers and pauses | Affected work, known cause, continuation condition |
| Review and learning | Feedback, acceptance, changes, improvements, follow-up |

Relevant changes retain provenance. Repeating an operation must not duplicate records or lose prior results. Failed persistence must be reported without claiming the update was saved.

Distinguish plugin-managed records from user documents. Detect incompatible or concurrent edits, preserve changes, and resolve discrepancies before overwriting affected content. Concurrent multi-agent execution is outside this version.

## 7. User Experience and Language

Users express intentions naturally: initialize, continue, inspect, reprioritize, review, pause, or close. Public command names are design decisions.

Responses present the outcome or current situation and next step. Detail scales with the decision; a small correction does not require restating the whole project. Ask only about outcome-relevant information that cannot be inferred or investigated, reusing valid answers and authorization.

All plugin-owned content uses English: skill names and instructions, document names and prose, references, templates, code identifiers, comments, diagnostics, tests, examples, structured values, generated views, and authored record summaries. Recognize user requests in their language; conversation may follow the user's preferred language.

Preserve existing product naming/content and original external sources. Verbatim evidence, user quotes, and command output retain original wording and may be accompanied by an English summary. Never translate evidence in place or imply a translated approval is a verbatim quote. This policy does not require translating the user's product.

Do not invent precise estimates, performance metrics, or consensus without data. Use increments without requiring periodic meetings or fixed-duration sprints.

## 8. First-Version Non-Goals

Exclude human-team management, simulated independent participants, multi-agent coordination, external boards, task-system synchronization, recurring automation, productivity charts, statistical estimation, and a dedicated deployment system.

The complete cycle does not require every technique in the book. Do not mandate full Scrum, compare productivity by points, or depend on spec-flow or its document structure.

Not every increment must be published or deployed; those actions depend on the need, agreed criteria, and actual authorization.

## 9. First-Version Validation

Future validation includes two complete journeys and exception cases. Writing this document does not execute them.

| Case | Observable outcome | Coverage |
| --- | --- | --- |
| New project | Need to implemented, verified, reviewed increment and updated next step | F01, F03-F08 |
| Existing repository | Proportional diagnosis, compatible change, evidence distinguished from prior work | F02, F04-F07 |
| Resume without prior conversation | Recover objective, states, decisions, next step and compare with repository | F09 |
| Priority change during work | Explicit continuation or suspension without lost work or reasons | F03, F10 |
| Required check unavailable | Partial verification and visible blocker, never fabricated success | F05-F06 |
| Acceptance and changes | Decision linked to delivery; correction distinguished from expansion | F07 |
| Applied learning | Retrieve action in next cycle with effect or explicit uncertainty | F08 |
| Repeated operation or failed write | No duplicates or false persistence confirmation | Section 6 |
| Existing authorization versus new scope | Autonomous progress in the former; reasoned consultation in the latter | Section 2, F04 |
| External change after verification | Affected evidence no longer establishes current validity until reassessed | F06, F09 |
| Language consistency | Plugin-owned artifacts and identifiers are English; original source evidence is preserved | Section 7 |

Coverage requires these journeys and F01-F10 scenarios to produce the specified outcomes without fabricated evidence, acceptance, or authorization.

## 10. Decisions and Authoritative Source

Vision, collaboration, and autonomy come from conversation agreements. Approved details include one active development increment per project, three independent state dimensions, delivery-specific acceptance, and minimum logical records. The user subsequently approved English throughout the plugin and its authored documents.

Architecture, skills, public names, record locations, and distribution are addressed in the plugin design rather than improvised in this specification.

## 11. Relationship to the Book

| Methodological basis | agile-flow application | Printed pages |
| --- | --- | --- |
| Shared vision and brief charter | Contextualize projects and guide increments | 389-391 |
| Backlog and progressive planning | Refine near-term work and adapt priorities | 393-394, 397 |
| Readiness and definition of done | Separate preparation from verification conditions | 395 |
| Stories and exploration | Observable outcomes and bounded investigations | 403-405 |
| Work in progress | Focus development and expose blockers | 420-421 |
| Product review | Capture acceptance and delivery feedback | 444-445 |
| Retrospective | Apply observable improvements in the next cycle | 448-451 |

State, autonomy, persistence, and repository-adoption rules are product adaptations for user-agent collaboration, not literal prescriptions from the book. This specification builds on the vision and source analysis from this conversation and does not claim conformity with an external edition of Scrum or another framework.
