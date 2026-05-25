# S2-HTML-INLINE-PARSER-FULL-UNIVERSE-VALIDATION-A0 — Final Summary

Date: 2026-05-25
Predecessors: S2-HTML-INLINE-PARSER-REOPEN-PHASE CLOSED (`03a2dc9`);
KR-STATUS-CORRECTION-LINKAGE-A0 CLOSED (`a5b982e`).
Parser version: `krx_status_html_inline-1.0.0`.

## Scope respected

- Measurement-layer full-universe parser validation only.
- suspension_related + resumption_related only.
- HTML-inline body only.
- No parser feature expansion (defects logged only).
- No delisting / liquidation / managed / alert parser.
- No DART body alpha. No overhang. No all-event event log.
- No C2/C3 wiring. No strategy testing. No execution simulation.
- No performance diagnostics. No production / paper / P08 / live / shadow.

## What was delivered

Code:
- `src/audit/measurement_a0/p_full_universe_parser_validation.py`

Reports (this dir, 12 outputs):
1. `full_universe_referee_lock.md`
2. `status_event_universe_inventory.md`
3. `document_availability_audit.csv`
4. `full_universe_parser_outputs.csv`
5. `full_universe_parse_coverage_summary.md`
6. `negative_control_full_universe_check.md`
7. `correction_policy_application_summary.md`
8. `holdout_validation_sample.csv`
9. `holdout_validation_summary.md`
10. `full_universe_parser_defect_ledger.csv`
11. `full_universe_gate_status.md`
12. `full_universe_final_summary.md` (this file)

Additional bodies fetched for holdout: **5** (OPENDART document.xml).

## Headline results

- Total universe: **17924** events.
- In-scope (suspension+resumption) parsed: **12187**.
- In-scope with cached body: **1402** (11.5% body coverage).
- In-scope extracted: **1327** (10.9% overall, 94.7% given body).
- Out-of-scope rows checked as negative controls: **5737**.
- Negative-control false positives: **0**.
- Negative-control safe rows (no in-scope field extracted): **5737**.
- Correction in-scope rows: **166**.
- Correction high_validated (authoritative-use allowed): **35**.
- Correction blocked to manual review: **131**.
- Holdout sample: **184** rows.
- Holdout success rate: **89.1%**.
- Holdout false positives: **0**.
- Holdout wrong+missed: **20**.
- Holdout correction_not_forced_manual_review: **0**.
- Holdout body_unavailable in sample: **0**.
- Defect ledger rows: **10846**.
- Gate state: **FULL_UNIVERSE_VALIDATION_REQUIRES_MORE_WORK**.

## Identified defect class (holdout sample)

All `wrong_date` rows in the holdout sample share a single failure pattern:

- `report_nm` = `주권매매거래정지기간변경` / `매매거래정지기간변경` (SUSPENSION-PERIOD-CHANGE disclosures).
- The body contains BOTH the original `정지기간` (before-change) AND the
  changed `정지기간` (after-change).
- Parser picks the FIRST `정지기간` label-with-date occurrence, which is
  the ORIGINAL period — typically back-dated several weeks/months from
  `rcept_dt`.
- True effective date for this disclosure form would be the AFTER-CHANGE
  period, not the before-change one.

Per Referee scope: 'No new parser feature expansion unless limited to
defect logging.' This defect is **logged but NOT fixed** in this phase.
Resolution would require disambiguating multi-period disclosures, which
is a parser feature change requiring a fresh Referee verdict.

Recommended future work (if Referee approves):
- Detect `기간변경` in `report_nm`; in such cases, choose the LAST
  `정지기간` label match within body (heuristic for after-change period).
- Or treat 기간변경 disclosures as their own sub-category and apply
  CORRECTION-LINKAGE Pass-3 supersession rules to source events.

## Pass-criteria evaluation

| criterion | status |
|---|---|
| Full universe inventoried | YES |
| In-scope population identified | YES |
| Parser applied to full in-scope population | YES |
| Coverage metrics reported | YES |
| Negative controls show no material FP | YES |
| Correction policy applied (Pass-3 rule) | YES |
| Holdout validation completed | YES |
| Defect ledger produced | YES |
| Gate status explicitly stated | YES |
| No strategy / execution / performance produced | YES |

## Hard locks (preserved)

- No return / NAV / Sharpe / CAGR / MDD / alpha / strategy / execution sim /
  production / paper / P08 / live / shadow.
- No rcept_dt defaulted to effective date.
- No effective_date inferred from rcept_dt fallback.
- No panel / OHLCV used as effective-date proof.
- No card is strategy-ready.
- No C2/C3 wiring.
- No correction row treated as authoritative unless high_validated AND validated.
- No parser feature expansion.
- No credential committed.

## Awaiting Referee

Referee will decide whether to:
- A. close as full-universe parser validated for suspension / resumption,
- B. require another validation pass,
- C. open correction-linkage full-universe validation,
- D. open delisting / liquidation manual expansion,
- E. keep all strategy research closed.
