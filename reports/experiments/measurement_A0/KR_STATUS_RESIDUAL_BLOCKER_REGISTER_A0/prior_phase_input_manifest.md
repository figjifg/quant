# Prior-Phase Input Manifest

Date: 2026-05-26
Phase: KR-STATUS-RESIDUAL-BLOCKER-REGISTER-A0

## Inputs used (read-only)

- `reports/experiments/measurement_A0/S2_HTML_INLINE_PARSER_UNIVERSE_RESIDUAL_RECONCILIATION_A0/universe_body_status_reconciled.csv`
  (12,187-row universe body status: body_format / parse_status / residual_class /
  manual_review_required / executable_or_safe).
- `reports/experiments/measurement_A0/KR_STATUS_CORRECTION_RESIDUAL_LOCAL_ADJUDICATION_A0/correction_residual_action_ledger.csv`
  (166-row correction residual action ledger: residual_action_class).
- Context only: `reports/experiments/measurement_A0/KR_STATUS_CORRECTION_LINKAGE_FULL_UNIVERSE_VALIDATION_A0/correction_full_universe_links.csv` (full-universe correction links) and
  KR_STATUS_CORRECTION_LINKAGE_A0 (Pass-3 origin).

## No network. No parser invocation. No downloads / API / acquisition / body repair.

## New code

- `src/audit/measurement_a0/p_residual_blocker_register.py` (this phase; pure local
  consolidation of accepted CSV artifacts).
