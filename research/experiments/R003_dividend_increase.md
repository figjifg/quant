# R003 — Dividend Increase

Status: GENERATED

## Hypothesis

현금배당, 중간배당, 분기배당 공시 이후 1/3/6개월 수익률이 KOSPI 대비 양의 초과수익을 낼 수 있는지 검증한다.

## Pre-Registered Design

- Event filter: OPENDART disclosure titles containing `현금ㆍ현물배당`, `현금/현물배당`, `현금배당`, `중간배당`, or `분기배당`.
- Exclusions: title-level correction/cancellation rows are excluded.
- Signal date: OPENDART `rcept_dt` disclosure date.
- Execution: next KRX trading-day open because the R000 parquet has date-only timestamps.
- Holding periods: 21 / 63 / 126 KRX trading days.
- Benchmark: KOSPI `cap_weighted_return`.
- Universe: dynamic_top100 Korean large-cap price panel, price-matched events only.
- Cost: gross only; R005 handles cost.
- Factor grid: none.

## Outputs

- `src/audit/r003_dividend_increase.py`
- `reports/experiments/R003_dividend_increase/`

## Limitation

Dividend amount, dividend yield, prior-year increase, first-dividend, and quarterly-dividend-introduction flags are not available in the R000 title-level parquet and are not used in this run.
