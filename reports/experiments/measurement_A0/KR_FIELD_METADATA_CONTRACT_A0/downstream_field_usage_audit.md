# Downstream Field Usage Audit

Source-file count per keyword across `src/`, `scripts/`, `configs/`, `research/`.
Counts measure presence as substring, not authoritative call-graph reach.

## Usage counts

| keyword | files_referencing |
|---|---:|
| `종가` | 27 |
| `KRX종가` | 26 |
| `시가` | 24 |
| `거래대금추정` | 20 |
| `동적유니버스포함` | 13 |
| `final_sector_code` | 13 |
| `final_sector_name` | 13 |
| `시가총액추정` | 11 |
| `rcept_no` | 10 |
| `고가` | 9 |
| `report_nm` | 9 |
| `저가` | 8 |
| `외국인순매수금액추정` | 8 |
| `corp_code` | 8 |
| `stock_code` | 8 |
| `기관순매수금액추정` | 7 |
| `rcept_dt` | 7 |
| `rcept_date` | 7 |
| `외국인순매매량` | 4 |
| `거래량` | 3 |
| `Change` | 3 |
| `기관순매매량` | 3 |
| `kospi_foreign_net` | 3 |
| `kospi_institution_net` | 3 |
| `상장주식수` | 2 |
| `adj_open` | 2 |
| `adj_high` | 2 |
| `adj_low` | 2 |
| `adj_close` | 2 |
| `tradable_state` | 2 |
| `키움거래대금순위` | 1 |
| `adj_volume` | 1 |
| `adj_return_pct` | 1 |
| `adjusted_source` | 1 |
| `kospi_individual_net` | 1 |
| `program_total_net_mil` | 1 |
| `program_arb_net_mil` | 1 |
| `program_nonarb_net_mil` | 1 |
| `flag_treasury_stock` | 1 |
| `flag_cb_bw` | 1 |
| `flag_capital_reduction` | 1 |
| `flag_merger_split` | 1 |
| `permanent_id` | 1 |
| `terminal_status` | 1 |
| `terminal_date` | 1 |
| `krx_first_snapshot` | 1 |
| `krx_last_snapshot` | 1 |

## Quarantined columns referenced in code

No quarantined columns appear in this keyword scan.

## Notes

- This scan is presence-only; semantic correctness of usage requires per-callsite review.
- No strategy reopen is implied by these counts.
