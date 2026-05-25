# Row-Key Input Manifest

Date: 2026-05-26
Phase: KR-STATUS-RESIDUAL-ROWKEY-INTEGRITY-AUDIT-A0

## Input ledgers (read-only; key column)

- `reports/experiments/measurement_A0/S2_HTML_INLINE_PARSER_UNIVERSE_RESIDUAL_RECONCILIATION_A0/universe_body_status_reconciled.csv` (rcept_no)
- `reports/experiments/measurement_A0/KR_STATUS_CORRECTION_LINKAGE_FULL_UNIVERSE_VALIDATION_A0/correction_full_universe_links.csv` (correction_rcept_no)
- `reports/experiments/measurement_A0/KR_STATUS_CORRECTION_RESIDUAL_LOCAL_ADJUDICATION_A0/correction_residual_action_ledger.csv` (correction_rcept_no)
- `reports/experiments/measurement_A0/KR_STATUS_RESIDUAL_BLOCKER_REGISTER_A0/residual_blocker_register.csv` (rcept_no)
- `reports/experiments/measurement_A0/KR_STATUS_PARSER_NONEXTRACTED_LOCAL_TAXONOMY_A0/parser_nonextracted_taxonomy_ledger.csv` (rcept_no)
- `reports/experiments/measurement_A0/KR_STATUS_SOURCE_RECOVERY_CANDIDATE_MANIFEST_A0/source_recovery_candidate_manifest.csv` (rcept_no)

## No new data. No network. No parser invocation. No edits to closed artifacts.

## New code
- `src/audit/measurement_a0/p_residual_rowkey_integrity_audit.py` (this phase).