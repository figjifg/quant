# Prior-Phase Input Manifest

Date: 2026-05-26
Phase: KR-STATUS-SOURCE-RECOVERY-CANDIDATE-MANIFEST-A0

## Inputs used (read-only)

- `reports/experiments/measurement_A0/KR_STATUS_RESIDUAL_BLOCKER_REGISTER_A0/residual_blocker_register.csv` (862-row blocker register → the 42 zip_unparseable
  rows; is_correction, correction_action_class, blocker_tags, stock_code,
  parse_status, body_format, residual_class).
- `reports/experiments/measurement_A0/S2_HTML_INLINE_PARSER_UNIVERSE_RESIDUAL_RECONCILIATION_A0/universe_residual_ledger.csv` (42-row universe residual ledger → rcept_dt,
  event_category, source_period, reason).
- `reports/experiments/measurement_A0/KR_STATUS_CORRECTION_RESIDUAL_LOCAL_ADJUDICATION_A0/correction_residual_action_ledger.csv` (correction action classes; context).
- `reports/experiments/measurement_A0/KR_STATUS_CORRECTION_LINKAGE_FULL_UNIVERSE_VALIDATION_A0/correction_full_universe_links.csv` (correction corp_name + underlying confidence_5tier).
- `reports/experiments/measurement_A0/KR_STATUS_RESIDUAL_BLOCKER_REGISTER_A0/source_recovery_candidate_subset.csv` (prior source-recovery subset; cross-check).

## No network. No parser invocation. No downloads / API / credentials / body repair.

## New code

- `src/audit/measurement_a0/p_source_recovery_candidate_manifest.py` (this phase;
  pure local consolidation of accepted CSV artifacts).
