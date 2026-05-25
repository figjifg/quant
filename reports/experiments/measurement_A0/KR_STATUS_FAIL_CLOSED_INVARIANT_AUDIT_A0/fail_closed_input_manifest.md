# Fail-Closed Input Manifest

Date: 2026-05-26
Phase: KR-STATUS-FAIL-CLOSED-INVARIANT-AUDIT-A0

## Input ledgers (read-only)

- `reports/experiments/measurement_A0/S2_HTML_INLINE_PARSER_UNIVERSE_RESIDUAL_RECONCILIATION_A0/universe_body_status_reconciled.csv`
- `reports/experiments/measurement_A0/KR_STATUS_CORRECTION_LINKAGE_FULL_UNIVERSE_VALIDATION_A0/correction_full_universe_links.csv`
- `reports/experiments/measurement_A0/KR_STATUS_CORRECTION_LINKAGE_FULL_UNIVERSE_VALIDATION_A0/supersession_readiness_full_universe.csv`
- `reports/experiments/measurement_A0/KR_STATUS_CORRECTION_RESIDUAL_LOCAL_ADJUDICATION_A0/correction_residual_action_ledger.csv`
- `reports/experiments/measurement_A0/KR_STATUS_RESIDUAL_BLOCKER_REGISTER_A0/residual_blocker_register.csv`
- `reports/experiments/measurement_A0/KR_STATUS_PARSER_NONEXTRACTED_LOCAL_TAXONOMY_A0/parser_nonextracted_taxonomy_ledger.csv`
- `reports/experiments/measurement_A0/KR_STATUS_SOURCE_RECOVERY_CANDIDATE_MANIFEST_A0/source_recovery_candidate_manifest.csv`

## No new data. No network. No parser invocation. No edits to closed artifacts.

## Scoping note
- universe manual_review_required=True asserted on the 753 residual rows only (the 11,434 extracted rows are legitimately False / not residuals); executable_or_safe=False asserted universe-wide (holds for all 12,187).

## New code
- `src/audit/measurement_a0/p_fail_closed_invariant_audit.py` (this phase).