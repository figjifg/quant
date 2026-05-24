# Survivorship Safety Assessment

Date: 2026-05-24  
Phase: KR-LISTED-UNIVERSE-COVERAGE-A0

## Headline verdict

**NOT SURVIVORSHIP-SAFE — partial lifecycle coverage.**

- Official ever-listed universe: **3653**
- Repo panel union: **925** (~25.3% of official)
- Tickers in official but NOT in any panel: **2728** (~74.7% of official)
- Tickers in coverage table with terminal status: **1723**
- Tickers in coverage table that disappeared without a terminal event: **519**

## Required checks (Referee-listed)

| check | status | evidence |
|---|---|---|
| delisted tickers represented? | PARTIAL | 1723 have terminal status; 519 disappeared without one |
| merged tickers represented? | NOT CERTIFIED | merger/split linkage not in scope; W001 v2 listing_status_events 47% disappearance unresolved |
| renamed tickers mapped? | PARTIAL | permanent_id_master maps via DART corp_code but rename HISTORY is not preserved |
| relisted / code-reused tickers separated? | NOT CERTIFIED | monthly snapshots cannot distinguish same-ticker-code reuse if relisting occurs in different month |
| panel disappearance explained? | PARTIAL | S3 covers 53.1% of 258 disappeared tickers per ACQUISITION_SUMMARY |
| dynamic_top100 historical members retained? | YES | all 4 panel files preserved in repo |
| current-only survivor universe avoided? | NO | panel selection is dynamic_top100 by liquidity — biased toward currently-liquid names |
| terminal event dates available and plausible? | PARTIAL | from W001 v2 listing_status_terminal — covers DART-flagged events only |

## Why NOT survivorship-safe

1. The repo panel covers ~25.3% of the official
   ever-listed universe. Roughly {0:.1f}% of historic listings are absent —
   primarily delisted small caps and tickers that never entered dynamic_top100.

2. Vendor dynamic_top100 selection is liquidity-biased. A backtest run only on
   panel data would systematically exclude failures (delisted small caps),
   producing survivorship-biased results.

3. The W001 v2 terminal-status coverage is partial (47% of historic
   disappearances unresolved). 519 tickers in the
   coverage table disappeared without a terminal event — they may be
   delisted, merged, or renamed; the audit cannot distinguish.

4. Code reuse: monthly snapshots cannot detect ticker code reuse if
   delisting + relisting occur in different months. Need daily-resolution
   universe to disambiguate, which is a future-phase option.

## What this means for future strategy work

- No survivorship-safe claim is supported by this phase.
- Any future strategy reopen requires:
  - acquisition of a complete (daily-resolution) listed-universe with
    explicit corporate-action linkage,
  - resolution of the 47%-unresolved disappearance subset,
  - explicit handling of code reuse,
  - Round of dependent A0 audits (sector aggregator, universe builder, panel
    loader) re-run with the corrected universe.

## Hard locks (preserved)

- No survivorship-safe claim made.
- No strategy testing.
- No execution simulation.
- No production / paper / P08 / live readiness.
