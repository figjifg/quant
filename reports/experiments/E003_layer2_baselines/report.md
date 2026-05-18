# E003 Layer 2 Baselines Metrics Summary

## Metadata

- panels: research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv
- sector_mapping_csv: data/processed/stock_sector_mapping_20260518.csv
- macro_gate: D013 10 variables, 5 blocks, 60-month z-score, threshold -0.2
- execution: signal quarter-end T executes on next KRX trading day
- cost_policy: commission 1.5 bps per leg, tax 20 bps sell leg, slippage 5 bps per leg

## Comparison Summary

| variant | cumulative_net_total_return | sharpe | max_drawdown | trade_count | positive_years | avg_quarterly_holdings | vs_A_cumulative_net_total_return_pp | vs_A_sharpe_pp | vs_A_max_drawdown_pp |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A_d013_replication | 2.5457702903350135 | 0.5333654677635088 | -0.3392346174957135 | 110 | 7 | 5.0 | 0.0 | 0.0 | 0.0 |
| B_count_matched | 1.5137604617737588 | 0.4015270500365329 | -0.3631773425015766 | 110 | 4 | 5.0 | -1.0320098285612547 | -0.1318384177269759 | -0.02394272500586314 |
| C_pure_basket | 1.1574917843876347 | 0.38578548068843027 | -0.41196277920465385 | 2052 | 5 | 93.4090909090909 | -1.3882785059473788 | -0.14757998707507852 | -0.07272816170894036 |

## Average Overlap

| metric | mean |
| --- | --- |
| A_d013_replication_vs_B_count_matched_ticker_overlap_pct | 0.7636363636363637 |
| A_d013_replication_vs_B_count_matched_sector_overlap_pct | 1.0 |
| A_d013_replication_vs_C_pure_basket_ticker_overlap_pct | 0.990909090909091 |
| A_d013_replication_vs_C_pure_basket_sector_overlap_pct | 0.9886363636363636 |
| B_count_matched_vs_C_pure_basket_ticker_overlap_pct | 0.9818181818181819 |
| B_count_matched_vs_C_pure_basket_sector_overlap_pct | 0.9818181818181819 |

