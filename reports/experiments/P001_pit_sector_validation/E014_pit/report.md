# P001 E014 PIT Sector Validation Metrics Summary

## Metadata

- panels: research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv
- carrier: E014 frozen RS + Breadth Top 4, holdings 2/1/1/1
- sector_membership: point-in-time KRX industry classifications mapped to frozen 12 groups
- macro_gate: D013 10 variables, 5 blocks, 60-month z-score, threshold -0.2
- timing: signal quarter-end T uses stock, sector, and KOSPI data through T; execution is T+1 or later

## Champion Summary

| variant | cumulative_net_total_return | sharpe | max_drawdown | trade_count |
| --- | --- | --- | --- | --- |
| P001_E014_pit | 1.468682405568845 | 0.3458238305516483 | -0.47384030791424325 | 110 |

## Snapshot/D013 Comparison

| variant | cumulative_net_total_return | sharpe | max_drawdown | trade_count | cumulative_diff_vs_pit | sharpe_diff_vs_pit | mdd_diff_vs_pit |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P001_E014_pit | 1.468682405568845 | 0.3458238305516483 | -0.47384030791424325 | 110 | 0.0 | 0.0 | 0.0 |
| E014_snapshot | 3.621084739339225 | 0.6311872415922518 | -0.35641869371448887 | 110 | 2.15240233377038 | 0.28536341104060353 | 0.11742161419975439 |
| D013 | 2.5457702903350135 | 0.5333654677635088 | -0.3392346174957135 | 110 | 1.0770878847661685 | 0.1875416372118605 | 0.13460569041852977 |

