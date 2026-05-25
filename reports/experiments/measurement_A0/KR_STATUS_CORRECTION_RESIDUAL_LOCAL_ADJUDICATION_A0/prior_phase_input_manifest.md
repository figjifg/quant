# Prior-Phase Input Manifest

Date: 2026-05-26
Phase: KR-STATUS-CORRECTION-RESIDUAL-LOCAL-ADJUDICATION-A0

## Inputs used (read-only)

- `reports/experiments/measurement_A0/KR_STATUS_CORRECTION_LINKAGE_FULL_UNIVERSE_VALIDATION_A0/correction_full_universe_links.csv` — 166-row accepted full-universe links
  (confidence_5tier, evidence_state, body_format_cache, blocked_overlay, body
  cross-check flags, candidate fields, supersession_ready).
- `reports/experiments/measurement_A0/KR_STATUS_CORRECTION_LINKAGE_FULL_UNIVERSE_VALIDATION_A0/no_link_medium_low_root_cause_ledger.csv` — accepted no_link / medium / low root causes.
- Reconciliation baseline: KR-STATUS-CORRECTION-LINKAGE-FULL-UNIVERSE-VALIDATION-A0
  accepted counts 17 / 52 / 7 / 73 / 17 (total 166), 39 zip_unparseable.

## No inputs from outside the local repo. No network. No parser invocation.

## New code

- `src/audit/measurement_a0/p_correction_residual_local_adjudication.py`
  (this phase; pure local transformation of accepted CSV/MD artifacts).
