# {{ITER_id}} — Verification

**Release:** {{version}} · **Planning:** [Sprint planning](sprint-planning.md) · **Overall result:** {{observed_verification_status}}

## Verified scope and baselines

| Delivery | Revision | Stories | Tested artifact | Environment |
| --- | --- | --- | --- | --- |
| {{INC_id}} | {{revision}} | {{US_ids}} | {{commit_or_artifact_reference}} | {{environment}} |

## Check results and execution details

| Evidence | Story / requirement | Check | Result | Evidence reference |
| --- | --- | --- | --- | --- |
| {{EVD_id}} | {{US_id}} / {{AC_or_DOD_id}} | {{check}} | {{passed_failed_blocked_or_not_run}} | {{artifact_link_or_execution_reference}} |

### {{EVD_id}} — {{check_name}}

**Delivery / revision:** {{INC_id}} / {{revision}} · **Executed:** {{timestamp_or_not_run}}

**Method.** {{actual_procedure_or_command}}

**Expected.** {{expected_result}}

**Observed.** {{actual_result_or_not_observed}}

**Limits.** {{limitations_and_uncovered_behavior}}

**Artifacts.** {{supporting_paths_or_links}}

## Unavailable checks and blockers

| Check or blocker | Why unavailable | Impact on confidence | Resolution requirement |
| --- | --- | --- | --- |
| {{check_or_blocker_id}} | {{reason}} | {{unverified_scope}} | {{required_next_action}} |

## Verification conclusion

{{what_is_demonstrated_what_is_not_and_next_action}}

User acceptance is recorded separately in [review.md](review.md).
