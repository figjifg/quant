# Prior-Phase Input Manifest

Date: 2026-05-26
Phase: KR-STATUS-PARSER-NONEXTRACTED-LOCAL-TAXONOMY-A0

## Inputs used (read-only)

- `reports/experiments/measurement_A0/S2_HTML_INLINE_PARSER_UNIVERSE_RESIDUAL_RECONCILIATION_A0/universe_body_status_reconciled.csv`
  (12,187-row universe body status → the 711 no_label_match + label_no_value rows).
- `reports/experiments/measurement_A0/KR_STATUS_CORRECTION_RESIDUAL_LOCAL_ADJUDICATION_A0/correction_residual_action_ledger.csv`
  (166 correction ids → correction overlap of 11 no_label + 7 label_no_value).
- `reports/experiments/measurement_A0/KR_STATUS_RESIDUAL_BLOCKER_REGISTER_A0/residual_blocker_register.csv` (blocker register; context).
- Cached bodies: `data/acquired/round5_manual_audit_samples/` (read-only; for body inspection).

## Parser helpers CALLED read-only (NOT modified)

- `src/parsers/krx_status_html_inline.py`: `extract_body_from_zip`,
  `find_label_hits`, `_normalize_for_scan`. No parser code changed.

## No network. No downloads / API / acquisition / body repair.

## New code

- `src/audit/measurement_a0/p_parser_nonextracted_local_taxonomy.py` (this phase).
