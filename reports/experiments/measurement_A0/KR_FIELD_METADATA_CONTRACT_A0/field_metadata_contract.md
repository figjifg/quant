# KR Field Metadata Contract — A0 Audit

Date: 2026-05-23
Scope: KR equity strategy-relevant datasets (raw + processed). Non-KR datasets (US prices, US fundamentals, macro, futures, global ETF) listed only as out-of-scope markers.

## Verdict

Measurement-layer A0 ONLY. No strategy testing. No return / NAV / Sharpe.

## Summary

- Datasets contracted: 27
- Columns evaluated: 372
- Columns flagged UNKNOWN (undocumented): 0
- Undocumented-field defects: 31
- Allowlist breakdown: ALLOW=196 / ALLOW_WITH_GUARD=176 / QUARANTINE=0

## Contract fields

- `source`
- `unit`
- `raw_or_adjusted`
- `timestamp_semantics`
- `pit_status`
- `identifier_key`
- `upstream_dependency`

## Dataset list

| dataset_id | role | scope | rowcount | n_cols |
|---|---|---|---:|---:|
| `equity_panel_kiwoom_2010_2016` | equity_panel | KR_in_scope | 1093386 | 25 |
| `equity_panel_dynamic_top100_2017_2024` | equity_panel | KR_in_scope | 1087741 | 20 |
| `equity_panel_dynamic_top100_2018_2024` | equity_panel | KR_in_scope | 969208 | 20 |
| `equity_panel_krx_2025_2026` | equity_panel | KR_in_scope | 172543 | 26 |
| `market_flow_kiwoom_2010_2017` | market_flow | KR_in_scope | 1976 | 12 |
| `market_flow_kiwoom_2018_2026_integrated` | market_flow | KR_in_scope | 2045 | 12 |
| `market_flow_kiwoom_2025_2026_krx` | market_flow | KR_in_scope | 325 | 12 |
| `opendart_kospi_disclosures_20180101_20260505` | event | KR_in_scope | 450190 | 26 |
| `w001_v2_panel_with_adjusted_ohlc_2018_2026` | derived_panel | KR_in_scope_processed | 1141751 | 33 |
| `w001_v2_panel_with_tradable_state` | derived_panel | KR_in_scope_processed | 1141751 | 34 |
| `w001_v2_permanent_id_master` | universe_lifecycle | KR_in_scope_processed | 833 | 9 |
| `w001_v2_listing_status_events` | universe_lifecycle | KR_in_scope_processed | 10769 | 5 |
| `w001_v2_listing_status_terminal` | universe_lifecycle | KR_in_scope_processed | 1854 | 3 |
| `s1_adjusted_ohlc_all_tickers_2018_2026` | derived_panel | KR_in_scope_processed | 1578220 | 8 |
| `s3_krx_status_events_2018_2026` | universe_lifecycle | KR_in_scope_processed | 10774 | 10 |
| `s3_dart_pblntfty_I_all_2018_2026` | event | KR_in_scope_processed | 425294 | 9 |
| `s4_krx_ever_listed_table` | universe_lifecycle | KR_in_scope_processed | 3154 | 6 |
| `s4_krx_listed_companies_master` | universe_lifecycle | KR_in_scope_processed | 22305 | 4 |
| `s6_reconciliation_sample_2024_01` | reconciliation_sample | KR_in_scope_processed | 440 | 8 |
| `krx_pit_sector_classifications` | sector | KR_in_scope_processed | 148600 | 5 |
| `sector_aggregate_daily` | sector | KR_in_scope_processed | 48071 | 13 |
| `sector_aggregate_daily_pit` | sector | KR_in_scope_processed | 50808 | 13 |
| `stock_sector_mapping_20260518` | sector | KR_in_scope_processed | 923 | 8 |
| `stock_sector_mapping_pit_daily` | sector | KR_in_scope_processed | 393436 | 6 |
| `sector_membership_kis_snapshot_20260518` | sector | KR_in_scope_processed | 923 | 21 |
| `stock_with_sector_daily` | derived_panel | KR_in_scope_processed | 402198 | 11 |
| `stock_with_sector_daily_pit` | derived_panel | KR_in_scope_processed | 402198 | 13 |

Non-KR markers in `dataset_inventory.csv` (US prices, fundamentals, macro, futures, global ETF) are NOT column-contracted in this phase.

## Decision policy applied

- `UNKNOWN` source → QUARANTINE + defect entry.
- `available_with_lookahead_risk` → ALLOW_WITH_GUARD.
- `uncertain` PIT status → QUARANTINE.
- Vendor regex-derived flags → ALLOW_WITH_GUARD (not authoritative for event truth).
- Vendor estimation columns → ALLOW_WITH_GUARD (reconciliation gap noted in FLOW_000007).
- RAW unadjusted price/volume columns → ALLOW_WITH_GUARD (corporate-action handling required).
- Else → ALLOW.

## Cross references

- `dataset_inventory.csv`
- `column_contract_table.csv`
- `field_allowlist_denylist.csv`
- `undocumented_field_defect_ledger.csv`
- `downstream_field_usage_audit.md`

## Hard locks

- No field with `QUARANTINE` decision may be used in any strategy code path.
- No `ALLOW_WITH_GUARD` field may be used as a strategy signal without the guard documented.
- No metadata change without re-running this script and re-committing all 6 artifacts.
