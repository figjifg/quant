# R002 — Buyback Cancellation and Retirement

Status: GENERATED

## Hypothesis

자사주 소각 공시는 단순 자사주 취득 공시보다 강한 주주환원 신호일 수 있다.

## Pre-Registered Design

- Event filter: OPENDART disclosure titles containing `자기주식소각`, `자사주소각`, `자사주 소각`, or `소각결정`.
- Exclusions: title-level correction/cancellation rows are excluded.
- Signal date: OPENDART `rcept_dt` disclosure date.
- Execution: next KRX trading-day open because the R000 parquet has date-only timestamps.
- Holding periods: 21 / 63 / 126 KRX trading days.
- Benchmark: KOSPI `cap_weighted_return`.
- Universe: dynamic_top100 Korean large-cap price panel, price-matched events only.
- Cost: gross only; R005 handles cost.
- Factor grid: none.

## Outputs

- `src/audit/r002_buyback_cancellation_retirement.py`
- `reports/experiments/R002_buyback_cancellation_retirement/`

## Limitation

Cancellation / retirement size and size-to-market-cap ratios are not available in the R000 title-level parquet and are not used in this run.
