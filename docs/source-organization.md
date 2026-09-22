# Source organization

Files describe maintained responsibilities rather than audit rounds. This organization change preserves lifecycle behavior, migration compatibility and historical approval/evidence records.

## Current structure

- Behavioral test modules cover authorization, corrections, scoped review, evidence validity, review compatibility, record history, transitions and recovery. Shared delivered-record setup lives in `tests/record_scenarios.py`.
- The historical JSON-to-Markdown procedure is named `references/migration-json-to-authored-markdown.md`. Its historical version guard remains intact. `references/migration.md` is the current compatibility entry point.
- `templates/legacy/documents.json` and `templates/legacy/clean-markdown-v1/` hold historical field grouping and layouts. Current presentation remains in `templates/markdown/`.
- Historical specifications, implementation reports and example collections have explicit scope notices and links to the [documentation map](README.md).

The shared lifecycle engine and reused storage layers remain in place. Separating legacy writers from shared behavior is a different refactor. Persisted schema/codec identifiers, operation names, actual product release directories and historical package-exclusion names remain unchanged. In particular, packaging still rejects old audit-document paths even though those documents are absent from the current tree.

## Preservation evidence

- All 128 directly declared test-method bodies match the pre-change AST exactly; the moved delivered-record helper also matches. The discovered suite contains 134 runnable tests because existing workflow classes also reuse test methods.
- All 27 tests formerly grouped by audit stage have one behavioral destination; no assertion or scenario was removed.
- All 12 relocated compatibility assets are byte-identical to the historical inputs.
- Full suite: 134 tests passed. Plugin package validation and Git whitespace checks passed. Maintained local documentation links resolve; template links use product-relative destinations and are exercised by workflow tests.

The table below is historical traceability for locating an old finding or test name. It is not an additional test registry or an instruction to retain audit-based module names.

| Previous test location | Current behavioral location |
| --- | --- |
| `test_audit_regressions.py:test_a01_stale_review_cannot_accept_current_delivery_and_partial_parts_accumulate` | `test_review_acceptance.py:test_stale_review_cannot_accept_current_delivery_and_partial_parts_accumulate` |
| `test_audit_regressions.py:test_partial_acceptance_identifies_parts_without_accepting_whole` | `test_review_acceptance.py:test_partial_acceptance_identifies_parts_without_accepting_whole` |
| `test_audit_regressions.py:test_a02_correction_cycle_and_a05_lifecycle` | `test_correction_workflow.py:test_correction_cycle_and_lifecycle` |
| `test_audit_regressions.py:test_a03_technical_and_superseded_decisions_do_not_authorize` | `test_authorization.py:test_technical_and_superseded_decisions_do_not_authorize` |
| `test_audit_regressions.py:test_a04_history_keeps_multiple_prior_values_and_provenance` | `test_record_history.py:test_history_keeps_multiple_prior_values_and_provenance` |
| `test_audit_regressions.py:test_a06_replay_metadata_matches_committed_state` | `test_record_history.py:test_replay_metadata_matches_committed_state` |
| `test_audit_regressions.py:test_a07_invalid_backup_is_rejected_and_snapshots_are_unique` | `test_recovery.py:test_invalid_backup_is_rejected_and_snapshots_are_unique` |
| `test_audit_regressions.py:test_changed_file_marks_current_evidence_stale_without_writing_state` | `test_evidence_acceptance_validity.py:test_changed_file_marks_current_evidence_stale_without_writing_state` |
| `test_audit_regressions.py:test_manual_reconciliation_preserves_original_snapshot` | `test_recovery.py:test_manual_reconciliation_preserves_original_snapshot` |
| `test_reaudit_regressions.py:test_r01_view_matches_effective_state_after_external_edit` | `test_evidence_acceptance_validity.py:test_view_matches_effective_state_after_external_edit` |
| `test_reaudit_regressions.py:test_r02_failed_check_reopens_same_increment_without_user_review` | `test_correction_workflow.py:test_failed_check_reopens_same_increment_without_user_review` |
| `test_reaudit_regressions.py:test_r03_explicit_review_supersession_is_scoped` | `test_review_acceptance.py:test_explicit_review_supersession_is_scoped` |
| `test_reaudit_regressions.py:test_r04_replacement_authorization_resumes_and_corrects_same_increment` | `test_authorization.py:test_replacement_authorization_resumes_and_corrects_same_increment` |
| `test_reaudit_regressions.py:test_full_replacement_technical_correction_and_review_cycle` | `test_correction_workflow.py:test_full_replacement_technical_correction_and_review_cycle` |
| `test_reaudit_regressions.py:test_documented_defect_reopens_accepted_delivery` | `test_correction_workflow.py:test_documented_defect_reopens_accepted_delivery` |
| `test_reaudit_regressions.py:test_withdrawal_restores_prior_acceptance_without_erasing_reviews` | `test_review_acceptance.py:test_withdrawal_restores_prior_acceptance_without_erasing_reviews` |
| `test_reaudit_regressions.py:test_invalid_replacement_authorization_does_not_rebind` | `test_authorization.py:test_invalid_replacement_authorization_does_not_rebind` |
| `test_reaudit_regressions.py:test_superseded_grant_can_be_replaced_before_resume` | `test_authorization.py:test_superseded_grant_can_be_replaced_before_resume` |
| `test_round3_regressions.py:test_t01_project_reopen_rechecks_authorization_of_reactivated_work` | `test_authorization.py:test_project_reopen_rechecks_authorization_of_reactivated_work` |
| `test_round3_regressions.py:test_t01_reopen_requires_current_authorization` | `test_authorization.py:test_reopen_requires_current_authorization` |
| `test_round3_regressions.py:test_t01_closed_unfinished_work_frees_slot_but_cannot_reopen_into_conflict` | `test_transitions.py:test_closed_unfinished_work_frees_slot_but_cannot_reopen_into_conflict` |
| `test_round3_regressions.py:test_t02_nonbehavioral_change_needs_current_checks_and_new_acceptance` | `test_evidence_acceptance_validity.py:test_nonbehavioral_change_needs_current_checks_and_new_acceptance` |
| `test_round3_regressions.py:test_t02_behavior_change_requires_new_revision_and_review` | `test_evidence_acceptance_validity.py:test_behavior_change_requires_new_revision_and_review` |
| `test_round3_regressions.py:test_q01_new_check_preserves_unchanged_delivery_acceptance` | `test_evidence_acceptance_validity.py:test_new_check_preserves_unchanged_delivery_acceptance` |
| `test_round3_regressions.py:test_t02_legacy_review_without_binding_remains_readable_and_conservative` | `test_review_compatibility.py:test_legacy_review_without_binding_remains_readable_and_conservative` |
| `test_round3_regressions.py:test_t02_legacy_review_without_reconstructible_history_is_pending` | `test_review_compatibility.py:test_legacy_review_without_reconstructible_history_is_pending` |
| `test_round4_regressions.py:test_repeated_checks_preserve_acceptance_but_changed_files_do_not` | `test_evidence_acceptance_validity.py:test_repeated_checks_preserve_acceptance_but_changed_files_do_not` |
