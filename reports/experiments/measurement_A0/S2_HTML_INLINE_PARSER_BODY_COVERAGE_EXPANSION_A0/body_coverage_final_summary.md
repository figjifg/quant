# S2-HTML-INLINE-PARSER-BODY-COVERAGE-EXPANSION-A0 — Final Summary

Date: 2026-05-25
Parser version: `krx_status_html_inline-1.1.0` (no feature change in this phase).

## Scope respected

- Measurement-layer body-coverage expansion A0 only.
- suspension_related + resumption_related only.
- HTML-inline body candidates only.
- body_unavailable rows from prior validation phase.
- Parser 1.1.0 used as-is (no feature expansion).
- No delisting / liquidation / managed / alert parser.
- No DART body alpha. No overhang. No all-event event log.
- No C2/C3 wiring. No strategy testing. No execution simulation.
- No performance diagnostics. No production / paper / P08 / live / shadow.

## What was delivered

Code:
- `src/audit/measurement_a0/p_body_coverage_expansion.py`

Reports (this dir, 12 outputs):
1. `body_coverage_referee_lock.md`
2. `body_unavailable_target_universe.csv`
3. `cache_inventory_summary.md`
4. `body_acquisition_plan.md`
5. `body_acquisition_attempt_log.csv`
6. `body_coverage_delta_summary.md`
7. `post_acquisition_parser_outputs.csv`
8. `new_body_validation_sample.csv`
9. `new_body_validation_summary.md`
10. `body_coverage_defect_ledger.csv`
11. `body_coverage_gate_status.md`
12. `body_coverage_final_summary.md` (this file)

## Headline results

- Target body_unavailable rows: **10744**.
- Already-cached at start: **0**.
- Download attempts: **5000**.
- Download successes: **4996**.
  - html_inline: 4996
  - structured_xml: 0
  - attachment_only: 0
  - other_format: 0
  - zip_unparseable: 4
- API no_document: 0
- Rate limited: 0
- Credential / API errors: 0
- Not attempted (budget exhausted): **5744**

- Body available on target rows (after): **5000**.
- Body unavailable on target rows (after): **5744**.
- Coverage shift on target rows: **46.5%**.

- New extractions: **4526**.
- Holdout sample: **84** (drawn from newly extracted).
- Holdout success rate: **100.0%**.
- Holdout FP: **0**.
- Holdout wrong+missed: **0**.
- Holdout correction_not_forced_manual_review: **0**.
- Defect ledger rows: **5748**.
- Gate state: **READY_FOR_NEXT_A0_REVIEW**.

## Pass-criteria evaluation

| criterion | status |
|---|---|
| target universe documented | YES |
| cache inventory produced | YES |
| acquisition attempt log produced | YES |
| coverage before vs after quantified | YES |
| newly acquired bodies parsed with existing parser only | YES |
| new body validation sample completed | YES |
| body_unavailable preserved and not silently dropped | YES |
| defect ledger produced | YES |
| gate status explicitly stated | YES |
| no strategy / execution / performance produced | YES |

## Hard locks (preserved)

- No return / NAV / Sharpe / CAGR / MDD / alpha / strategy / execution sim /
  production / paper / P08 / live / shadow.
- No `rcept_dt` defaulted to effective date.
- No `effective_date` inferred from `rcept_dt` fallback.
- No panel / OHLCV used as effective-date proof.
- No card is strategy-ready.
- No C2/C3 wiring.
- No correction row treated as authoritative unless high_validated AND validated.
- No parser feature expansion.
- No `body_unavailable` row treated as parsed or safe.
- No credential committed.

## Awaiting Referee

Referee will decide whether to:
- A. close as body coverage expanded,
- B. require another coverage pass,
- C. open correction-linkage full-universe validation,
- D. open delisting / liquidation manual expansion,
- E. keep all strategy research closed.
