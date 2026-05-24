# KR-EXECUTABLE-STATUS-PRE2018-EXTENSION-A0 — Final Close Note

Date: 2026-05-24  
Verdict source: Referee final close verdict, 2026-05-24.  
Initial pass commit accepted: `0d80010` on origin/main.

## Verdict

**CLOSED AS PRE2018-STATUS-SOURCE-ACQUIRED / RECONCILED / EXECUTION STILL CLOSED.**

- Decision: option **A** (close as pre-2018 source acquired).
- No additional pre-2018 source attempt required now.
- No execution simulation opened.
- No strategy testing reopened.
- No performance diagnostics reopened.
- No production / paper / P08 / live readiness / shadow-track work touched.

## Accepted deliverables (12)

1. `pre2018_referee_lock.md`
2. `source_feasibility_report.md`
3. `acquisition_attempt_log.csv`
4. `pre2018_status_source_report.md`
5. `pre2018_status_coverage_table.csv` (7,150 rows)
6. `pre2018_taxonomy_mapping.md`
7. `pre2018_panel_reconciliation_summary.md`
8. `pre2018_panel_reconciliation_ledger.csv` (7,150 rows)
9. `pre2018_gap_closure_assessment.md`
10. `pre2018_defect_ledger.csv` (5 entries)
11. `pre2018_gate_status.md`
12. `pre2018_final_summary.md`

## Accepted acquisition

- Source: OPENDART `list.json` pblntfty=I (거래소공시) with `OPENDART_API_KEY`.
- Date range: **2010-01-01 → 2017-12-31** (full 8-year target window).
- Method: 3-month chunks + 100-per-page pagination + 0.2s inter-chunk pause.
- API calls: ~3,000 (well below 20,000/day OPENDART limit).
- Runtime: ~25 min.
- Raw rows: **300,829**.
- Filtered status events: **7,150** (~2.4% retention).
- Storage: `data/acquired/round5_dart_pre2018/` (gitignored, reproducible via build
  script).

## Accepted filtered status-event distribution

| category | count |
|---|---:|
| suspension_related | 3,211 |
| resumption_related | 2,058 |
| delisting | 1,683 |
| managed | 178 |
| short_term_overheated | 10 |
| investment_alert | 8 |
| liquidation | 2 |
| **total** | **7,150** |

## Accepted reconciliation (2010-2017 panel + lifecycle + W001 terminal)

| class | count |
|---|---:|
| event_ticker_in_lifecycle_not_in_panel_without_terminal | 3,690 |
| event_ticker_in_lifecycle_not_in_panel_with_terminal | 2,314 |
| event_ticker_in_panel_and_lifecycle_with_terminal | 527 |
| event_ticker_in_panel_and_lifecycle_without_terminal | 472 |
| event_not_in_lifecycle_with_terminal | 27 |
| event_not_in_lifecycle_without_terminal | 113 |
| event_ticker_missing | 7 |

## Accepted gap closure

- `pre_2018_status_coverage_gap` (from `KR-EXECUTABLE-STATUS-COVERAGE-A0`):
  - prior status: **open**
  - **new status: CLOSED**
- Evidence: full 2010-2017 OPENDART pblntfty=I corpus acquired and filtered.

## Accepted defects (5)

1. `events_missing_stock_code` (low; 7 events, corp-only disclosures)
2. `report_nm_other_requires_manual_review` (medium)
3. `effective_date_unknown` (high; rcept_dt = filing date; S2 PARTIAL)
4. `intraday_halt_still_missing_pre2018` (high)
5. `pre2018_other_pool_requires_manual_review` (medium; 293,679 'other' rows preserved
   in raw for sample audit)

## Accepted gate state

**PRE2018_STATUS_RECONCILED_BUT_EXECUTION_STILL_CLOSED**

## Accepted limitations

- `rcept_dt` = filing date, NOT necessarily effective status date.
- Exact effective date requires DART body parsing; S2 remains PARTIAL.
- Intraday halt source still missing.
- Official limit-lock source still missing.
- "other" pool (293,679) requires sample audit before claiming complete taxonomy
  coverage.
- 7 events missing `stock_code` excluded from per-ticker reconciliation.
- Panel absence MUST NOT be interpreted as non-tradable.
- Panel disappearance MUST NOT be used as status proof.
- Unknown status MUST NOT be treated as executable.
- `rcept_dt` MUST NOT be treated as effective status date without audit.

## New hard prohibition (Referee 2026-05-24)

- No `rcept_dt` treated as effective status date without a separate effective-date
  linkage audit.

## Possible future phases (none active)

| Phase id | Purpose | Status |
|---|---|---|
| `KR-EXECUTABLE-EFFECTIVE-DATE-LINKAGE-A0` | Link rcept_dt → actual effective status date | NOT approved (**Referee-recommended next** for practical backtest-readiness) |
| `KR-INTRADAY-HALT-SOURCE-BACKLOG` | Intraday halt / VI / circuit-breaker source | NOT approved |
| `KR-EXECUTABLE-STATUS-LIMIT-LOCK-OFFICIAL-SOURCE-A0` | Direct KRX/KOSCOM official limit-lock acquisition | NOT approved |
| `KR-LIMIT-LOCK-CORPORATE-ACTION-ADJUSTMENT-A0` | CA effects on prev-close limit | NOT approved |
| `KR-LISTED-UNIVERSE-DAILY-LIFECYCLE-REFINEMENT-A0` | Monthly → daily lifecycle | NOT approved |
| `KR-OPS-NAV-UPDATE-QUARANTINE-PATCH-PHASE` | 4 remaining ops blockers | NOT approved |

Referee-recommended next candidate (if user chooses to continue):
**`KR-EXECUTABLE-EFFECTIVE-DATE-LINKAGE-A0`** — execution simulation cannot safely use
`rcept_dt` as the effective trading-status date without a linkage audit. Must NOT
auto-start.

Strategy testing + backtesting remain **premature**.

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
- No survivorship-safe claim unless explicitly supported.
- No unknown status treated as executable.
- No panel absence treated as non-tradable.
- No OHLCV signature treated as suspension proof.
- No rule-derived limit candidate treated as official lock evidence.
- No `rcept_dt` treated as effective status date without audit.
- No production / paper / P08 / live readiness / shadow connection.
- No card may be described as strategy-ready.

## End condition

`KR-EXECUTABLE-STATUS-PRE2018-EXTENSION-A0` is **closed as PRE2018-STATUS-SOURCE-
ACQUIRED / RECONCILED / EXECUTION STILL CLOSED**. No active work remains. Await
explicit user / Referee decision for any future effective-date linkage, intraday halt
source, official limit-lock source, lifecycle refinement, ops patch, parser, or
strategy phase.
