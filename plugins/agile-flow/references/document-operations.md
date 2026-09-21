# Document operations and metadata

## CLI

```sh
python3 <plugin>/scripts/agile_flow.py --root <product> inspect
python3 <plugin>/scripts/agile_flow.py --root <product> --request <request.json> mutate
python3 <plugin>/scripts/agile_flow.py --root <product> validate
python3 <plugin>/scripts/agile_flow.py --root <product> render
python3 <plugin>/scripts/agile_flow.py --root <product> recover
python3 <plugin>/scripts/agile_flow.py --root <product> migrate --dry-run
python3 <plugin>/scripts/agile_flow.py --root <product> --request <migration.json> migrate --apply
```

Migration request: `expected_source_fingerprint` from preview and optional `item_types` mapping legacy IDs to `story`, `nfr`, `bug`, `technical`, or `research`. Use the same mapping file for preview and apply. Unresolved legacy items retain their IDs until explicit classification. Preserve the returned backup and unresolved report. A pending interrupted migration is completed with `recover`, not by rerunning migration. Preview reports target conflicts rather than overwriting existing documents.

## Mutation payloads

Every mutation also carries the session protocol fields. Read `inspect` rather than guessing IDs.

| Operation | Payload and meaning |
| --- | --- |
| initialize | `project` with name, purpose and known context. Optional vision, mission, background, objectives, agreements, scope, exclusions, stakeholders, success_factors, users, confirmed_facts, assumptions, proposals, constraints, success_criteria, references, open_questions, next_step. |
| update-project | `project` with changed context fields; no global preparation. |
| update-roadmap | `document` containing horizons, MVP hypothesis, audience, minimum scope, exclusions, learning/validation method and milestones. Milestone `item_ids` must exist. Dates/budgets only when sourced. |
| update-dod | `document` with nonempty string-list `criteria` and applicable scope/rationale. Criteria become shared required checks when preparing a delivery. Optional `scoped_criteria` entries contain `criterion` and `types`; only rules matching selected work types apply, so investigations need not inherit deployment checks. |
| update-backlog | `item` with purpose, explicit type for new work, existing id for refinement. Optional order, priority/basis, criteria, dependencies, uncertainties, provenance, estimate/basis, story, value, scope, exclusions and type-specific fields. |
| reorder-backlog | `item_ids` containing every recorded item once, in order. |
| retire-backlog | `item_id`, `reason`; preserve identity and provenance. |
| classify-backlog | `item_id`, `type`, `reason`; resolve a migrated unknown type with an explicit identity mapping. |
| plan-iteration | `iteration` with goal, scope, item_ids; optional existing id, exclusions, technical_plan, tasks, timeframe, risks, open_decisions and verification approach. Creates a draft without permission. Once deliveries are baselined, use another iteration for new scope. |
| record-decision | `decision` with kind, author, reason, scope, source and actual quote where available. Authorization requires user author and structured scope (item_ids, increment_ids or project=true). |
| prepare | `iteration_id`, `increment` with item_ids, objective, scope, criteria, required_checks, authorization decision ID; optional exclusions and technical_plan. Requires applicable DoD and resolved material decisions. |
| start / mark-implemented | `increment_id`; completion may include `baseline`. These record actual work, never perform implementation. |
| record-evidence | `evidence` with increment_id, check, result (passed/failed/not_run), scope, paths; include command/procedure, environment, criterion links and limitations when relevant. |
| record-review | `review` with increment_id, decision, user_quote; scoped parts, accepted_parts, requested_changes and explicit supersession as relevant. |
| record-blocker / resolve-blocker | `blocker` with increment_id, condition and resolution_requirement for new blocker; resolving uses blocker_id and resolution. |
| record-improvement | `iteration_id`, `improvement` with observation, adjustment and target_cycle; include expected benefit when known. |
| follow-up-improvement | `improvement_id`, `state` (applied, insufficient_evidence or closed), `effect_evidence`. |
| pause / close / reopen | `target` project, iteration or increment; matching iteration_id/increment_id, reason; close action cancel for cancellation. Never imply completion. |

Correction/rebinding/resumption and delivery-change payloads follow the preserved domain engine in `scripts/legacy_records.py`; inspect the relevant operation before use rather than inventing fields. This module supplies validated domain transitions and the migration reader; `agile_flow.py` is the only current workflow entry point.

## Markdown contract

```markdown
<!-- af: {"key": "vision", "type": "text"} -->
## Vision

Customers book independently.
<!-- /af -->
```

Supported types: text, string-list, number, boolean, null, object, array. Text lists use Markdown bullets with two-space continuation lines. Object/array containers contain nested marked fields; arrays use numeric keys in sequence. Decision and agreement object lists use compact Markdown tables. Their hidden column/type metadata preserves optional fields and exact quotes; use record operations to add rows or columns. Functional values are visible in Markdown, not hidden JSON. Preserve these markers during manual editing. Use operation requests to add structured fields; free prose outside fields is preserved as notes and is not silently promoted to a decision. Titles are descriptive; IDs within marked fields own identity. Do not copy full authored documents into JSON metadata.
