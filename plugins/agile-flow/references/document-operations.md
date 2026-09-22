# Release and story document operations

Version 0.5.0 uses schema 4. Plugin 0.4.0 uses schema 3. The published 0.3.0 release used schema 2; schema numbers and plugin versions are different. Always select the actual product root. Do not initialize a temporary directory as the product or modify installed plugin code.

## CLI and concurrency

Run `python3 <plugin>/scripts/agile_flow.py --root <product> inspect`. For mutations pass `--request <file.json> mutate` or JSON on stdin. Include operation, unique operation_id, purpose, and the latest expected_revision/expected_fingerprint. Initialize needs project.name and project.purpose but no previous revision. `validate` and `inspect` are read-only. `render` refreshes the two indexes; `render --force` first preserves manually edited indexes. `recover` completes a pending transaction only when affected bytes agree with its journal.

## Authored layout

```text
.agile-flow/
  constitution.md
  roadmap.md
  summary.md                         # generated
  backlog/
    product-backlog.md                # generated
    BL-0001.md
  release/
    v0.1.0/
      release-0.1.0.md
      ITER-001/
        sprint-planning.md
        verification.md
        review.md
        retrospective.md
        user-stories/
          US-0001.md
        evidence/                    # only actual supporting artifacts
  .internal/                         # metadata, journals and preserved backups
```

BL records are product needs. Each US record is concrete iteration work with type US, NFR, BUG, TCH or SPK. US identity is unique across the product, regardless of type/release/iteration. Each story has one BL parent, one iteration and its own acceptance criteria and Definition of Done. There is no parent DoD file. A BL may produce several stories across releases. A release may contain several iterations. Do not silently move a baselined story; create linked follow-up scope and preserve its original identity.

Roadmap versions describe strategic evolution and may identify an intended MVP milestone. The release owns the detailed MVP hypothesis, early users, usable scope, feedback and learning decision. Release plans and delivered outcomes are separate fields. A plan is not authorization; a release description is not proof that it was published.

## Product and planning mutations

| Operation | Payload |
| --- | --- |
| initialize | project with name, purpose and known context; preserve original source quotations. No global quality_policy. |
| update-project | project with changed purpose/vision/mission, users, stakeholders, objectives, boundaries, agreements, sourced facts, assumptions, proposals, questions, references or next_step. |
| update-backlog | item with purpose; optional existing BL id, value, users, outcome, scope, exclusions, success_indicators, dependencies (BL IDs), assumptions, open_questions, priority, order, provenance, references, target_release. |
| reorder-backlog | item_ids containing every BL exactly once. |
| retire-backlog / complete-backlog | item_id (BL), reason; records the actual decision without deleting its history. |
| update-roadmap | document with direction, versions (rows with version such as v0.1.0, stage, intended outcome, capabilities, dependencies, status), milestones, assumptions, uncertainties, adaptation_criteria, release_references and changes as useful. No detailed mvp. |
| update-release | release with version id, objective, optional users, value, item_ids (BL), scope, exclusions, mvp, dependencies, risks, open_questions, exit_conditions, delivered_outcome, learning, upgrade_notes and publication. New status defaults to draft. Published status requires delivered_outcome and publication references; publishing is never performed by this operation. |
| plan-iteration | iteration with release_id, goal and scope; optional existing id, item_ids, exclusions, technical_plan, tasks, verification_plan, dependencies, risks, open_decisions, timeframe. A draft may begin without stories; update-story selects its new story in that draft. |
| update-story | story with purpose, parent_id (BL), iteration_id and type for new work; existing US id for refinement. Include criteria, dod, scope, exclusions, value, priority/order, estimate/basis, dependencies (US), open_questions and provenance as useful. |

Story-specific fields follow the approved type: US uses story; NFR quality_attribute/applicability/verification_method; BUG reproduction/observed/expected/impact; TCH approach/components; SPK question/work_limit/findings/recommendation. Do not force technical or defect records into a fictional user-story sentence.

Criteria accept text or rows `{id: AC-01, condition: ..., result: ...}`. DoD accepts text or rows `{id: DOD-01, requirement: ..., evidence: ...}`. Text is normalized to numbered rows; keep existing IDs when refining or reordering structured conditions. Drafts may have unresolved criteria/DoD, but execution preparation requires both. No arbitrary point estimate is required.

## Delivery operations

Record sourced authorization with record-decision: decision.kind=authorization, author=user, reason, source, actual quote where available, and scope covering US IDs, increment IDs or the project. BL scope does not automatically authorize its future stories.

Prepare with iteration_id and increment containing selected US item_ids, objective, scope and authorization decision ID; optional required_checks, technical_plan and exclusions. Criteria and mandatory checks are taken from the selected stories and preserved as delivery baselines. Check identifiers include the story and condition ID. Newly selected stories receive a planning baseline. After refining a selected story, update plan-iteration to review and refresh the draft baseline before preparation. Preparing does not execute software changes.

Use start, mark-implemented, record-evidence, record-review, prepare-correction, mark-delivery-change, rebind-authorization and resume for actual work under the preserved lifecycle engine. Read the relevant domain payload in scripts/legacy_records.py when needed. Evidence carries increment_id, check, result, scope, paths and actual procedure/environment/limitations. Review carries increment_id, a real user_quote or message_reference, decision and scoped parts; never infer acceptance from tests.

record-blocker uses blocker with increment_id, condition, resolution_requirement; resolve-blocker needs blocker_id and resolution. record-improvement needs iteration_id and improvement with observation, adjustment, target_cycle; follow-up-improvement needs improvement_id, state and effect_evidence. pause/close/reopen accepts target=iteration plus iteration_id, or the existing project/increment targets. Closure does not establish completion.

## Markdown contract and templates

The current writer emits clean Markdown with no af markers. Templates in templates/markdown/ drive section order; templates/documents.json supplies field grouping. Portable document schemas store keys and types, not functional content. Read [clean Markdown and Git](clean-markdown-and-git.md) for editing, concurrency, migration and versioning contracts.

Use operations to add new structured fields or complex records. Existing text and homogeneous table rows can be edited manually. Preserve structured headings; ambiguous or duplicate headings require reconciliation. Additional Notes sections remain authored context and do not grant authorization. Root DoD and old iteration layouts remain historical.

## Report context

Use `update-report` with `iteration_id`, `document` and `fields` to maintain readable context without changing evidence or acceptance. Supported fields: verification — `scope`, `conclusion`; review — `presented_result`, `resulting_work`, `unresolved_feedback`; retrospective — `retain`, `follow_up`. Use the existing record-evidence, record-review and improvement operations for sourced events. Narrative context never grants authorization or acceptance.
