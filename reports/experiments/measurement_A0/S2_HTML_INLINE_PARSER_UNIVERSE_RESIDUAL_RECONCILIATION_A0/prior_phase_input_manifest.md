# Prior-Phase Input Manifest

Date: 2026-05-26
Phase: S2-HTML-INLINE-PARSER-UNIVERSE-RESIDUAL-RECONCILIATION-A0

Inputs used (existing local artifacts only — no new downloads):

- `reports/experiments/measurement_A0/S2_HTML_INLINE_PARSER_FULL_UNIVERSE_VALIDATION_A0/pass2_full_universe_parser_outputs.csv` — 12,187-row in-scope universe (authoritative row set).
- `reports/experiments/measurement_A0/S2_HTML_INLINE_PARSER_BODY_COVERAGE_EXPANSION_A0/post_acquisition_parser_outputs.csv` — expansion-phase re-parse (cross-check).
- `reports/experiments/measurement_A0/S2_HTML_INLINE_PARSER_BODY_COVERAGE_COMPLETION_A0/completion_parser_outputs.csv` — completion-phase re-parse (cross-check).
- `reports/experiments/measurement_A0/S2_HTML_INLINE_PARSER_BODY_COVERAGE_EXPANSION_A0/body_coverage_defect_ledger.csv` — expansion defect ledger (cross-check).
- `reports/experiments/measurement_A0/S2_HTML_INLINE_PARSER_BODY_COVERAGE_COMPLETION_A0/body_completion_defect_ledger.csv` — completion defect ledger (cross-check).
- `data/acquired/round5_manual_audit_samples/` — cached document.xml ZIPs (read-only body source).

Method: per in-scope rcept_no, classify the CURRENT cached body format
(html_inline / structured_xml / attachment_only / other / zip_unparseable)
or `unavailable` if no cached body. html_inline rows are re-parsed with
`krx_status_html_inline-1.1.0` to record current parse_status. No parser change.
