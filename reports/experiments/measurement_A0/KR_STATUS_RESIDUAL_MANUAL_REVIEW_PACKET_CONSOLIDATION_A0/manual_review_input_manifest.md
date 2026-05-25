# Manual-Review Input Manifest

Date: 2026-05-26
Phase: KR-STATUS-RESIDUAL-MANUAL-REVIEW-PACKET-CONSOLIDATION-A0

## Input ledgers (read-only)

- `reports/experiments/measurement_A0/KR_STATUS_RESIDUAL_BLOCKER_REGISTER_A0/residual_blocker_register.csv`
- `reports/experiments/measurement_A0/KR_STATUS_PARSER_NONEXTRACTED_LOCAL_TAXONOMY_A0/parser_nonextracted_taxonomy_ledger.csv`
- `reports/experiments/measurement_A0/KR_STATUS_SOURCE_RECOVERY_CANDIDATE_MANIFEST_A0/source_recovery_candidate_manifest.csv`
- `reports/experiments/measurement_A0/KR_STATUS_CORRECTION_LINKAGE_FULL_UNIVERSE_VALIDATION_A0/correction_full_universe_links.csv`
- `reports/experiments/measurement_A0/KR_STATUS_CORRECTION_RESIDUAL_LOCAL_ADJUDICATION_A0/correction_residual_action_ledger.csv`
- `reports/experiments/measurement_A0/KR_STATUS_RESIDUAL_ROWKEY_INTEGRITY_AUDIT_A0/rowkey_mismatch_ledger.csv`
- `reports/experiments/measurement_A0/KR_STATUS_FAIL_CLOSED_INVARIANT_AUDIT_A0/fail_closed_violation_ledger.csv`

## No new data. No network. No parser invocation. No edits to closed artifacts.

## New code
- `src/audit/measurement_a0/p_residual_manual_review_packet_consolidation.py` (this phase).