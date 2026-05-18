# E014 RS+Breadth Top4 Registration Metrics Summary

## Metadata

- panels: research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv
- carrier: RS + Breadth score, Flow excluded, Top 4 sectors, holdings 2/1/1/1
- macro_gate: D013 10 variables, 5 blocks, 60-month z-score, threshold -0.2
- timing: signal quarter-end T uses stock, sector, and KOSPI data through T; execution is T+1 or later

## Champion Summary

| variant | cumulative_net_total_return | sharpe | max_drawdown | trade_count | e012_rs_breadth_exact_reproduction | e011_exact_match | d013_exact_match |
| --- | --- | --- | --- | --- | --- | --- | --- |
| E014_rs_breadth_top4 | 4.979884423916734 | 0.6995072799136423 | -0.3551638436079382 | 110 | False | False | False |

## D013/E011 Comparison

| variant | cumulative_net_total_return | sharpe | max_drawdown | trade_count | cumulative_diff_vs_e014 | sharpe_diff_vs_e014 | mdd_diff_vs_e014 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| E014_rs_breadth_top4 | 4.979884423916734 | 0.6995072799136423 | -0.3551638436079382 | 110 | 0.0 | 0.0 | 0.0 |
| D013 | 2.5457702903350135 | 0.5333654677635088 | -0.3392346174957135 | 110 | -2.4341141335817205 | -0.16614181215013346 | 0.015929226112224693 |
| E011 | 2.9652796624027413 | 0.5660027769289406 | -0.41474162966818906 | 110 | -2.0146047615139926 | -0.13350450298470162 | -0.05957778606025088 |

