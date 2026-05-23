# Trading Value Unit Plausibility

Date: 2026-05-23  
Scope: measurement-layer A0 only. No turnover / liquidity / alpha derivation.

## Method

When `거래대금추정여부 == True`, the vendor estimation rule is `거래대금추정 = 종가 × 거래량`.
For each panel we compare `거래대금추정` to `close × volume` on the estimated subset and
count mismatches above relative tolerance `1e-6`.

## Panel-level results

| panel | rows_total | rows_estimated | mismatch_count | mismatch_pct_of_estimated |
|---|---:|---:|---:|---:|
| `kiwoom_2010_2016` | 1093386 | 0 | 0 | 0.0% |
| `dynamic_top100_2017_2024` | 1087741 | 0 | 0 | 0.0% |
| `dynamic_top100_2018_2024` | 969208 | 0 | 0 | 0.0% |
| `krx_2025_2026` | 172543 | 98 | 98 | 100.0% |

## Aggregate flow unit plausibility (market_flow files)

`kospi_foreign_net`, `kospi_institution_net`, `kospi_individual_net` carry the column
unit `KRW_mil_or_count` per `KR_FIELD_METADATA_CONTRACT_A0/column_contract_table.csv`.

Plausibility heuristic — KOSPI total daily trading is on the order of ~10^13 KRW
(~10 trillion KRW = 10 million 백만원). Observed magnitudes of `kospi_foreign_net`
in panel files range in the low thousands per day. This is consistent with **count**
(unit = number of net contracts / shares) or **억원** (10^8 KRW), but **not** with **백만원**
as the column name pattern `_mil` might suggest.

Conclusion: unit string `KRW_mil_or_count` is ambiguous; this defect is recorded in
`KR_FIELD_METADATA_CONTRACT_A0/undocumented_field_defect_ledger.csv` as `unit_ambiguous`.
Until resolved, downstream usage of those columns is **ALLOW_WITH_GUARD**: any code that
treats them as KRW must annotate the conversion factor at the call site.

## Hard locks

- These checks must NOT be converted into liquidity / turnover / alpha signals.
- These checks must NOT be used to grade a stock as tradable.
- No phase-allowed output here recommends strategy reopen.
