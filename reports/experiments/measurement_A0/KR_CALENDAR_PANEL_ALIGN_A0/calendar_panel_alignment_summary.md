# Calendar / Panel Alignment Summary — A0 Audit

Date: 2026-05-23  
Scope: KR equity panel × KRX trading calendar.
Output rule: measurement-layer only. No return / NAV / Sharpe.

## Headline numbers

- Union working-calendar trading days (all sources): 4022 (2010-01-04 → 2026-05-06)
- Off-calendar panel rows (date not in matching flow calendar): 0 distinct (panel, date) pairs
- Missing calendar-panel days (flow-calendar days with zero panel rows): 0
- Duplicate (ticker, date) rows across all panels + W001 v2 tradable: 0

## Per-panel coverage

| panel | row_count | first_date | last_date | n_distinct_dates | n_distinct_tickers |
|---|---:|---|---|---:|---:|
| `kiwoom_2010_2016` | 1093386 | 2010-01-04 | 2016-12-29 | 1733 | 713 |
| `dynamic_top100_2017_2024` | 1087741 | 2017-01-02 | 2024-12-30 | 1964 | 840 |
| `dynamic_top100_2018_2024` | 969208 | 2018-01-02 | 2024-12-30 | 1721 | 815 |
| `krx_2025_2026` | 172543 | 2025-01-02 | 2026-05-06 | 325 | 538 |

## Per-period off-calendar dates (top 10 by row count)

| panel | calendar_ref | off_date | row_count |
|---|---|---|---:|
| (none) | | | |

## Missing-day counts per panel

| panel | calendar_ref | missing_day_count |
|---|---|---:|
| (none) | | 0 |

## Duplicate (ticker, date) summary per panel

| panel | duplicate_pairs |
|---|---:|
| (none) | 0 |

## Kill gates (Referee)

- **Calendar source clear?** UNCLEAR → execution simulation remains CLOSED (see `krx_calendar_source_check.md`).
- **T+1 mapping reproducible?** YES relative to union working calendar, PENDING against official KRX (see `t_plus_1_mapping_reproducibility.md`).
- **Listed-universe certified survivorship-safe?** NO. Panel-only union cannot certify survivorship — that is the explicit purpose of `KR-LISTED-UNIVERSE-COVERAGE-BACKLOG-001` (P2 backlog).
- **Executable status certified?** NO. Tradability flag / panel presence ≠ executable — `KR-EXECUTABLE-STATUS-BACKLOG-001` (P2 backlog) tracks the gap.

## Cross references

- `krx_calendar_source_check.md` (P0-2 artifact 2)
- `off_calendar_rows.csv` (P0-2 artifact 3)
- `missing_calendar_panel_days.csv` (P0-2 artifact 4)
- `duplicate_stock_date_rows.csv` (P0-2 artifact 5)
- `t_plus_1_mapping_reproducibility.md` (P0-2 artifact 6)
- `../KR_FIELD_METADATA_CONTRACT_A0/` (P0-1 artifacts)
- `../KR_LISTED_UNIVERSE_COVERAGE_BACKLOG/source_requirement_register.md`
- `../KR_EXECUTABLE_STATUS_BACKLOG/source_requirement_register.md`

## Hard locks

- No return / NAV / CAGR / Sharpe / alpha / MDD anywhere.
- No use of off-calendar rows as evidence of anything until the matching trading-day is verified.
- No use of missing days as evidence of a halt or suspension (the missing day might be a vendor gap rather than a true non-trading day).
- No executable assumption from panel presence.
