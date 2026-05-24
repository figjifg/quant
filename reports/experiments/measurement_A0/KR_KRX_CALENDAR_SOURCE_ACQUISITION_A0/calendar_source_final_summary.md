# KR-KRX-CALENDAR-SOURCE-ACQUISITION-A0 — Final Summary

Date: 2026-05-24  
Predecessor: KR-OHLCV-RESIDUAL-BLOCKER-PATCH-PHASE CLOSED.

## Scope respected

- Measurement-layer source acquisition + reconciliation only.
- No strategy testing.
- No performance diagnostics.
- No execution simulation.
- No production / paper / P08 / live readiness / shadow.

## What was delivered

Code artifacts:
- `src/audit/measurement_a0/p_krx_calendar_acquisition.py` (acquisition +
  reconciliation builder)

Data artifacts:
- `data/acquired/krx_calendar/krx_official_calendar_2010_2026.csv` (4034 dates, 2010-01-04 → 2026-05-22)

Reports (this dir, 11 outputs):

1. `calendar_source_referee_lock.md`
2. `official_krx_calendar_source_report.md`
3. `acquired_calendar_inventory.csv`
4. `calendar_reconciliation_summary.md`
5. `calendar_reconciliation_ledger.csv`
6. `t_plus_1_official_mapping_check.md`
7. `t_plus_1_mapping_delta.csv`
8. `calendar_anomaly_ledger.csv`
9. `calendar_usage_contract.md`
10. `execution_simulation_gate_status.md`
11. `calendar_source_final_summary.md` (this file)

## Acquisition

- Source method: `composite_pykrx_005930_plus_market_flow_secondary`
- Endpoint: `pykrx.stock.get_market_ohlcv` (anonymous via pykrx)
- Ticker used: **005930 (Samsung Electronics)**
- Date range: **2010-01-04 → 2026-05-22** (4034 dates)
- Limitations: see `official_krx_calendar_source_report.md`

## Reconciliation headline

- Official calendar dates: **4034**
- Repo union calendar dates: **4022**
- Matched: **4022**
- Official-only: **12**
- Repo-only: **0**

## T+1 mapping

- Common from-dates: **4021**
- Next-day matches: **4021**
- Next-day mismatches: **0**

## Anomaly rows: **12**

## Execution-simulation gate state: **CALENDAR_SOURCE_RECONCILED_BUT_EXECUTION_STILL_CLOSED**

## Pass criteria evaluation

| criterion | status |
|---|---|
| Official or best-available KRX calendar source identified + documented | YES |
| Date range coverage stated | YES |
| Calendar source limitations stated | YES |
| Repo union calendar reconciled against acquired source | YES |
| T+1 mapping rebuilt from acquired source | YES |
| Differences from prior union-calendar mapping recorded | YES |
| Calendar anomaly ledger produced | YES |
| Future calendar usage contract defined | YES |
| No strategy test or execution simulation run | YES |

## Hard locks (preserved)

- No return / NAV / Sharpe / CAGR / MDD / alpha / strategy / execution sim /
  production / paper / P08 / live / shadow.
- No card is strategy-ready.
- No survivorship-safe claim.
- Calendar acquired via anonymous pykrx — no credential committed.

## Awaiting Referee

Per Referee-defined exit conditions, Referee will decide whether to:
- A. close as calendar source acquired and reconciled,
- B. require another calendar reconciliation pass,
- C. open listed-universe source acquisition,
- D. open executable-status source acquisition,
- E. keep all strategy research closed.
