# KR-KRX-CALENDAR-SOURCE-ACQUISITION-A0 — Final Close Note

Date: 2026-05-24  
Verdict source: Referee final close verdict, 2026-05-24.  
Initial pass commit accepted: `d27a851` on origin/main.

## Verdict

**CLOSED AS CALENDAR-SOURCE-RECONCILED / EXECUTION STILL CLOSED.**

- Decision: option **A** (close as calendar source acquired and reconciled).
- No additional reconciliation pass required now.
- No execution simulation opened.
- No strategy testing reopened.
- No performance diagnostics reopened.
- No production / paper / P08 / live readiness / shadow-track work touched.

## Accepted deliverables (11)

1. `calendar_source_referee_lock.md`
2. `official_krx_calendar_source_report.md`
3. `acquired_calendar_inventory.csv`
4. `calendar_reconciliation_summary.md`
5. `calendar_reconciliation_ledger.csv` (4,034 rows)
6. `t_plus_1_official_mapping_check.md`
7. `t_plus_1_mapping_delta.csv`
8. `calendar_anomaly_ledger.csv` (12 rows)
9. `calendar_usage_contract.md`
10. `execution_simulation_gate_status.md`
11. `calendar_source_final_summary.md`

## Composite source — accepted with L1/L2 provenance

| layer | source | coverage | role |
|---|---|---|---|
| L1 | pykrx `get_market_ohlcv("005930")` (Samsung Electronics, anonymous-accessible) | 2014-03-03 → 2026-05-22 (3,000 dates) | authoritative |
| L2 | `kiwoom_market_flow_2010_2017_krx_trading_days.csv` (file-name-tagged) | 2010-01-04 → 2014-03-02 (1,034 dates) | secondary reference per Referee-permitted |
| **total** | composite | **2010-01-04 → 2026-05-22 (4,034 dates)** | |

Storage: `data/acquired/krx_calendar/krx_official_calendar_2010_2026.csv` (gitignored;
reproducible via build script).

## Accepted reconciliation

- 4,034 official/composite dates.
- 4,022 matched dates.
- **0 repo-only dates**.
- 12 official-only vendor-cutoff dates (2026-05-07 → 2026-05-22; repo last fetched
  2026-05-06).
- 12-row anomaly ledger accepted as vendor-cutoff, not true KRX disagreement.

## Accepted t+1 mapping

- Common from-dates: 4,021.
- Next-day matches: **4,021 / 4,021** (100%).
- Next-day mismatches: **0**.
- Prior union-calendar t+1 mapping is **validated** against the acquired source over
  the overlap window.

## Execution-simulation gate (accepted)

`CALENDAR_SOURCE_RECONCILED_BUT_EXECUTION_STILL_CLOSED`

- Calendar source ambiguity materially reduced.
- Other blockers still preserved:
  - listed-universe / lifecycle source coverage,
  - executable-status / halt / limit-lock source coverage,
  - residual ops blockers (4 rows in `src/ops/nav_update.py`),
  - future Referee review.

## Accepted limitations

- Composite, not a single direct official KRX 휴장일 endpoint.
- Pre-2014 layer uses existing KRX-tagged market_flow source as secondary reference.
- pykrx 005930 calendar can theoretically undercount rare dates where Samsung is
  suspended while market is open; no material mismatch found in this audit.
- Date-level only; no intraday halt / shortened trading session / executable-status
  metadata.
- This phase does NOT certify execution readiness.
- This phase does NOT certify survivorship safety.
- This phase does NOT certify tradability / executable status.

## Continuing hard locks

- No return backtest.
- No NAV / CAGR / Sharpe / hit rate / alpha / excess return / MDD.
- No post-event drift / migration return / turnover return / resume return / reversal
  return / flow-return.
- No raw jump alpha.
- No price-only mean reversion.
- No generic value / quality / momentum / RS ranking.
- No DART body alpha test.
- No overhang filter alpha test.
- No flow strategy testing.
- No execution simulation.
- No executable assumption from panel presence.
- No survivorship-safe claim without official listed universe.
- No use of ALLOW_WITH_GUARD fields without documented guard.
- No use of invalid OHLCV rows without quarantine.
- No production / paper / P08 / live readiness / shadow connection.
- No card may be described as strategy-ready.

## Possible future phases (none active)

| Phase id | Purpose | Status |
|---|---|---|
| `KR-LISTED-UNIVERSE-COVERAGE-A0` | Acquire / validate official listed-universe / lifecycle source | NOT approved (**Referee-recommended next** for cleanest path toward safe future backtesting) |
| `KR-EXECUTABLE-STATUS-COVERAGE-A0` | Acquire / validate official executable-status / halt / limit-lock source | NOT approved |
| `KR-OPS-NAV-UPDATE-QUARANTINE-PATCH-PHASE` | Patch the 4 remaining ops blockers | NOT approved (touches ops/paper/live-related code) |
| `KR-CLOSED-STRATEGY-CODEPATH-QUARANTINE-A0` | Optional follow-up before any strategy reopen | NOT approved (lower priority) |

Referee-recommended next candidate (if user chooses to continue):
**`KR-LISTED-UNIVERSE-COVERAGE-A0`** — survivorship-safe universe remains a hard
blocker. Must NOT auto-start.

## End condition

`KR-KRX-CALENDAR-SOURCE-ACQUISITION-A0` is **closed as CALENDAR-SOURCE-RECONCILED /
EXECUTION STILL CLOSED**. No active work remains. Await explicit user / Referee
decision for any future listed-universe, executable-status, ops patch, parser, or
strategy phase.
