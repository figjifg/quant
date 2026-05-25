# Prior-Phase Input Manifest

Date: 2026-05-26
Phase: KR-STATUS-CORRECTION-LINKAGE-FULL-UNIVERSE-VALIDATION-A0

## Inputs used (read-only)

- `data/acquired/round5_manual_audit_samples/` — cached document.xml ZIPs (read-only body
  source; populated by prior body-coverage-expansion/completion + residual
  reconciliation phases).
- Filtered status universe + raw pool via
  `src.audit.measurement_a0.p_status_correction_linkage_pass2.load_full_universe()`
  and `load_raw_pool()` (same loaders Pass 1/2/3 used).
- Pass-3 accepted artifacts (reference / reconciliation baseline) under
  `reports/experiments/measurement_A0/KR_STATUS_CORRECTION_LINKAGE_A0/`:
  - `pass3_candidate_links_recalibrated.csv`
  - `pass3_final_summary.md`, `CLOSE_NOTE.md`
  - prior accepted universe counts: 166 = 35 high_validated / 42 medium /
    18 low / 71 no_link / 0 rejected (score-only).

## Code reused (not modified)

- `src/audit/measurement_a0/p_status_correction_linkage.py` (Pass 1 helpers)
- `src/audit/measurement_a0/p_status_correction_linkage_pass2.py` (Pass 2 helpers)
- `src/audit/measurement_a0/p_status_correction_linkage_pass3.py`
  (candidate_search_pass3, assign_confidence_pass3, confirm_body — body gate)
- `src/audit/measurement_a0/p_universe_residual_reconciliation.py`
  (classify_cached_body — read-only body-format classifier)
- `src/parsers/krx_status_html_inline.py` (parser 1.1.0, used as-is)

## New code

- `src/audit/measurement_a0/p_correction_linkage_full_universe_validation.py`
  (this phase; audit-only orchestrator, cache-only).
