# R004 — Shareholder Return Composite

Status: GENERATED

## Hypothesis

자사주 취득, 자사주 소각, 배당 공시를 단순 union으로 결합하면 단일 이벤트보다 안정적인 주주환원 이벤트 신호가 될 수 있다.

## Pre-Registered Design

- Event filter: R001 + R002 + R003 title filters.
- Weighting: pre-registered simple union, any qualifying event receives score 1.
- Duplicate handling: same ticker events within 21 KRX trading days are collapsed to the earliest event.
- Exclusions: title-level correction/cancellation rows are excluded.
- Signal date: OPENDART `rcept_dt` disclosure date.
- Execution: next KRX trading-day open because the R000 parquet has date-only timestamps.
- Holding periods: 21 / 63 / 126 KRX trading days.
- Benchmark: KOSPI `cap_weighted_return`.
- Universe: dynamic_top100 Korean large-cap price panel, price-matched events only.
- Cost: gross only; R005 handles cost.
- Factor grid: none.

## Outputs

- `src/audit/r004_shareholder_return_composite.py`
- `reports/experiments/R004_shareholder_return_composite/`

## Limitation

Low-valuation filtering is not applied because the ticket marks it optional and no valuation source is present in the R000 event parquet.
