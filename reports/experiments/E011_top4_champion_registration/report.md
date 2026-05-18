# E011 Top4 Champion Metrics Summary

## Metadata

- panels: research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv
- carrier: E007 Flow + RS + Breadth, Top 4 sectors, holdings 2/1/1/1
- macro_gate: D013 10 variables, 5 blocks, 60-month z-score, threshold -0.2
- timing: signal quarter-end T uses stock, sector, and KOSPI data through T; execution is T+1 or later

## Champion Summary

| variant | cumulative_net_total_return | sharpe | max_drawdown | trade_count | e008_top4_exact_reproduction | e007_exact_match | d013_exact_match |
| --- | --- | --- | --- | --- | --- | --- | --- |
| E011_top4_champion | 2.9652796624027413 | 0.5660027769289406 | -0.41474162966818906 | 110 | True | False | False |

