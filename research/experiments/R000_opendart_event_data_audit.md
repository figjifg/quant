# R000 — OPENDART Event Data Audit

Status: READY

## Purpose

Validate OPENDART event-date and timestamp accuracy before starting Korean
shareholder-return event sleeve research.

## Event Types

- 자기주식취득결정
- 자기주식처분결정
- 자기주식소각결정
- 현금/현물배당결정
- 중간배당
- 분기배당
- 주주환원정책 공시
- 기업가치 제고 계획

## Audit Items

- 공시일 / 공시 시간
- 장중/장후 여부 and whether next-trading-day application is possible
- 정정공시 처리
- 취소공시 처리

## Data

`research_input_data/inputs/events/opendart_kospi_disclosures_20180101_20260505.parquet`

## Required Outputs

Write outputs under `reports/experiments/R000_opendart_event_data_audit/`:

- `config.yaml`
- `event_type_distribution.csv`
- `ticker_distribution.csv`
- `time_distribution.csv`
- `sample_buyback_events.csv`
- `sample_dividend_events.csv`
- `report.md`

## Verdict

`PASS`, `NEEDS DATA`, or `FAIL`.

