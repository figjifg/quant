# KR-EXECUTABLE-STATUS-PRE2018-EXTENSION-A0 — Final Summary

Date: 2026-05-24  
Predecessor: KR-EXECUTABLE-STATUS-LIMIT-LOCK-SOURCE-A0 CLOSED.

## Scope respected

- Measurement-layer executable-status source extension only.
- No strategy testing.
- No performance diagnostics.
- No execution simulation.
- No production / paper / P08 / live / shadow.

## What was delivered

Code artifacts:
- `src/audit/measurement_a0/p_pre2018_executable_status_extension.py`

Data artifacts (gitignored, reproducible via build script):
- `data/acquired/round5_dart_pre2018/dart_pblntfty_I_all_2010_2017.csv` (raw)
- `data/acquired/round5_dart_pre2018/krx_status_events_2010_2017.csv` (filtered)
- `data/acquired/round5_dart_pre2018/acquisition_attempt_log.csv`

Reports (this dir, 12 outputs):
1. `pre2018_referee_lock.md`
2. `source_feasibility_report.md`
3. `acquisition_attempt_log.csv` (mirror of attempt log)
4. `pre2018_status_source_report.md`
5. `pre2018_status_coverage_table.csv`
6. `pre2018_taxonomy_mapping.md`
7. `pre2018_panel_reconciliation_summary.md`
8. `pre2018_panel_reconciliation_ledger.csv`
9. `pre2018_gap_closure_assessment.md`
10. `pre2018_defect_ledger.csv`
11. `pre2018_gate_status.md`
12. `pre2018_final_summary.md` (this file)

## Acquisition headline

- Source: OPENDART `list.json` pblntfty=I (거래소공시) with OPENDART_API_KEY.
- Date range acquired: **20100104 → 20171228**.
- Raw rows: **300829**.
- Filtered status events: **7150**.

## Category breakdown (filtered)

| category | count |
|---|---:|
| `suspension_related` | 3211 |
| `resumption_related` | 2058 |
| `delisting` | 1683 |
| `managed` | 178 |
| `short_term_overheated` | 10 |
| `investment_alert` | 8 |
| `liquidation` | 2 |

## Reconciliation against 2010-2017 repo panels + lifecycle

| class | count |
|---|---:|
| `event_ticker_in_lifecycle_not_in_panel_without_terminal` | 3690 |
| `event_ticker_in_lifecycle_not_in_panel_with_terminal` | 2314 |
| `event_ticker_in_panel_and_lifecycle_with_terminal` | 527 |
| `event_ticker_in_panel_and_lifecycle_without_terminal` | 472 |
| `event_not_in_lifecycle_without_terminal` | 113 |
| `event_not_in_lifecycle_with_terminal` | 27 |
| `event_ticker_missing` | 7 |

## Gap closure: **closed**

## Pre-2018 gate state: **PRE2018_STATUS_RECONCILED_BUT_EXECUTION_STILL_CLOSED**

## Defect ledger

- Total defects: **5** (see `pre2018_defect_ledger.csv`).
- Classes: acquisition failure (if 0 events) / events missing stock_code /
  `other` requires manual review / effective_date unknown / intraday halt still
  missing.

## Pass criteria evaluation

| criterion | status |
|---|---|
| Pre-2018 source feasibility documented | YES |
| Acquisition attempt logged | YES |
| Acquired or unavailable source status explicitly stated | YES |
| Acquired events mapped into taxonomy | YES |
| 2010-2017 panel linkage assessed | YES |
| `pre_2018_status_coverage_gap` updated with evidence | YES |
| Defect ledger produced | YES |
| Gate status explicitly stated | YES |
| No strategy test / execution sim / performance metric produced | YES |

## Hard locks (preserved)

- No return / NAV / Sharpe / CAGR / MDD / alpha / strategy / execution sim
  / production / paper / P08 / live / shadow.
- No survivorship-safe claim.
- No executable claim from panel presence.
- No credential committed.
- No card is strategy-ready.

## Awaiting Referee

Per Referee-defined exit conditions, Referee will decide whether to:
- A. close as pre-2018 source acquired or source-unavailable documented,
- B. require another pre-2018 source attempt,
- C. open official limit-lock source acquisition,
- D. open lifecycle daily refinement,
- E. keep all strategy research closed.
