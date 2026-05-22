# R001 — Buyback Announcement

Status: GENERATED

## Hypothesis

자사주 취득 공시 후 1/3/6개월 보유 수익률이 KOSPI 대비 양의 초과수익을 낼 수 있는지 검증한다.

## Pre-Registered Design

- Event filter: OPENDART disclosure titles containing `자기주식취득`, `자사주취득`, `자사주 취득`, or `자기주식취득신탁계약`.
- Exclusions: title-level correction/cancellation rows are excluded.
- Signal date: OPENDART `rcept_dt` disclosure date.
- Execution: next KRX trading-day open because the R000 parquet has date-only timestamps.
- Holding periods: 21 / 63 / 126 KRX trading days.
- Benchmark: KOSPI `cap_weighted_return`.
- Universe: dynamic_top100 Korean large-cap price panel, price-matched events only.
- Cost: gross only; R005 handles cost.
- Factor grid: none.

## Outputs

- `src/audit/r001_buyback_announcement.py`
- `reports/experiments/R001_buyback_announcement/`

## Required Comparisons

- KOSPI: implemented.
- Sector: current source files do not include sector classification; reported as `unknown`.
- Market-cap bucket: implemented from event-date available panel market cap.
