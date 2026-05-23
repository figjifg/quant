# KRX Calendar Source Check

Date: 2026-05-23  
Scope: measurement-layer A0 only.

## Question

What is the authoritative KRX trading-calendar source available in this repo?

## Candidate sources

| candidate | file/method | nature | comment |
|---|---|---|---|
| **panel dates (union)** | 4 equity panels' `날짜` column | derived | not a calendar source; *follows* whatever trading days the panel rows cover; cannot be used to verify completeness |
| **market_flow_2010_2017_krx_trading_days.csv** | file name claims `krx_trading_days` | semi-authoritative | 1 row per day; file name explicitly tagged with `krx_trading_days`; period 2010-01-04 to 2017-12-28 |
| **market_flow_2018_2026_integrated.csv** | 1 row per day | semi-authoritative | period 2018-01-02 onwards; not file-name-tagged as calendar |
| **market_flow_2025_2026_krx.csv** | 1 row per day, KRX-tagged | semi-authoritative | post-NXT, KRX-tagged |
| **pykrx `get_market_ohlcv_by_date`** | pykrx API | external authoritative | requires KRX_ID/KRX_PW; used for S1 acquisition. Source = KRX official, but not committed to repo as a calendar file |
| **KRX 공식 휴장일 리스트** | not in repo | authoritative | KRX 발표 휴장일 / 임시휴장 / 거래시간 변경 정보. Currently NOT acquired into repo. |

## Finding

Repo does **not** carry a standalone, named KRX trading-calendar file.
The market_flow files implicitly act as a per-day trading-day index but only one of three
(`kiwoom_market_flow_2010_2017_krx_trading_days.csv`) is explicitly tagged as a calendar.
All other inputs (equity panels, S1 adjusted OHLC) are *consumers* of the calendar.

## Per-Referee kill gate

Referee verdict: **If KRX calendar source is unclear, execution simulation remains closed.**

**Status: UNCLEAR.** Therefore execution simulation remains CLOSED (unchanged).

## Working calendar used for this audit

For the alignment check in this phase the executor uses the **union of dates that appear
in at least one of**:
- 4 equity panels (`날짜`)
- 3 market_flow files (`date`)
- S1 adjusted_ohlc_all_tickers_2018_2026.csv (`date`)

This **union** is treated as a working KRX-trading-day candidate, not an authoritative calendar.
It cannot validate KRX days the entire dataset universe missed.

## Required for closure

1. Acquisition of an authoritative KRX calendar (KRX `getJsonData.cmd` or pykrx `get_business_days`).
2. Side-by-side reconciliation of:
   - market_flow calendar
   - panel-derived union calendar
   - KRX official calendar
3. Anomaly ledger of mismatches (휴장 / 임시휴장 / 거래시간단축).

Until then, calendar source is **unclear** and execution-simulation gating remains closed.
