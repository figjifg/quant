# E014 RS+Breadth Top4 Registration Metrics Summary

## Metadata

- panels: research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv
- carrier: RS + Breadth score, Flow excluded, Top 4 sectors, holdings 2/1/1/1
- macro_gate: D013 10 variables, 5 blocks, 60-month z-score, threshold -0.2
- timing: signal quarter-end T uses stock, sector, and KOSPI data through T; execution is T+1 or later

## Champion Summary

| variant | cumulative_net_total_return | sharpe | max_drawdown | trade_count | e012_rs_breadth_exact_reproduction | e011_exact_match | d013_exact_match |
| --- | --- | --- | --- | --- | --- | --- | --- |
| E014_rs_breadth_top4 | 3.621084739339225 | 0.6311872415922518 | -0.35641869371448887 | 110 | True | False | False |

## D013/E011 Comparison

| variant | cumulative_net_total_return | sharpe | max_drawdown | trade_count | cumulative_diff_vs_e014 | sharpe_diff_vs_e014 | mdd_diff_vs_e014 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| E014_rs_breadth_top4 | 3.621084739339225 | 0.6311872415922518 | -0.35641869371448887 | 110 | 0.0 | 0.0 | 0.0 |
| D013 | 2.5457702903350135 | 0.5333654677635088 | -0.3392346174957135 | 110 | -1.0753144490042117 | -0.09782177382874302 | 0.01718407621877538 |
| E011 | 2.9652796624027413 | 0.5660027769289406 | -0.41474162966818906 | 110 | -0.6558050769364838 | -0.06518446466331118 | -0.058322935953700195 |

