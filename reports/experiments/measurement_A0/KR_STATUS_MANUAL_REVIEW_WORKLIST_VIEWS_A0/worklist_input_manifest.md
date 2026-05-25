# Worklist Input Manifest

Date: 2026-05-26
Phase: KR-STATUS-MANUAL-REVIEW-WORKLIST-VIEWS-A0

## Input artifacts (read-only)

- `reports/experiments/measurement_A0/KR_STATUS_RESIDUAL_MANUAL_REVIEW_PACKET_CONSOLIDATION_A0/manual_review_packet.csv`
- `reports/experiments/measurement_A0/KR_STATUS_RESIDUAL_MANUAL_REVIEW_PACKET_CONSOLIDATION_A0/manual_review_bucket_counts.csv`
- `reports/experiments/measurement_A0/KR_STATUS_RESIDUAL_MANUAL_REVIEW_PACKET_CONSOLIDATION_A0/prior_audit_sentinel_check.csv`
- `reports/experiments/measurement_A0/KR_STATUS_RESIDUAL_MANUAL_REVIEW_PACKET_CONSOLIDATION_A0/packet_build_defect_ledger.csv`

## No new data. No network. No parser invocation. No edits to closed artifacts.

## Determinism
- Worklist rows sorted by (review_bucket, rcept_no); worklist_id = WL-{i:05d}
  in that order. Re-running on the same packet yields identical IDs.

## New code
- `src/audit/measurement_a0/p_manual_review_worklist_views.py` (this phase).