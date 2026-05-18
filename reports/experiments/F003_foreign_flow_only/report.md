# F003 Stock Foreign Flow Only Metrics Summary

## Metadata

- panels: research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv
- stock_foreign_flow: mean of 20d foreign net buy / 20d traded value and 60d foreign net buy / market cap
- zscore: within-sector cross-sectional z-score
- missing_flow_policy: stock-level foreign flow input NaNs are not imputed; affected stocks are excluded from diagnostics and portfolio candidates
- timing: signal quarter-end T uses stock flow, traded value, and market cap through T; execution is T+1 or later
- macro_gate: D013 10 variables, 5 blocks, 60-month z-score, threshold -0.2

## IC Diagnostics

| carrier | rank_ic_pooled | rank_ic_mean | rank_ic_t_stat | rank_ic_n_quarters | spread | spread_t_stat | positive_spread_ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F003-A D013 direct | -0.0143917045093361 | -0.0125667991506595 | -0.4924005666505902 | 22.0 | -0.0602995162632051 | -1.2140387785842166 | 0.3181818181818182 |
| F003-B E014 | -0.0348537487885203 | -0.0491274375154195 | -1.460612597325319 | 22.0 | 0.0347259697276444 | 0.6796433945314226 | 0.5454545454545454 |

## Carrier Comparison

| variant | cumulative_net_total_return | sharpe | max_drawdown | trade_count | baseline_variant | f002_variant | baseline_cumulative_net_total_return | baseline_sharpe | baseline_max_drawdown | cumulative_uplift_vs_f001 | sharpe_uplift_vs_f001 | mdd_uplift_vs_f001 | f002_cumulative_net_total_return | f002_sharpe | f002_max_drawdown | cumulative_diff_vs_f002 | sharpe_diff_vs_f002 | mdd_diff_vs_f002 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F003-A D013 direct | 0.9140249795158837 | 0.24095475028234803 | -0.4941753798241437 | 110 | F001-A D013 direct | F002-A D013 direct | 2.545770290335013 | 0.5333654677635088 | -0.3392346174957135 | -1.6317453108191293 | -0.29241071748116076 | -0.15494076232843024 | -0.8529580972033175 | -0.4072782866963429 | -0.9069895495190158 | 1.7669830767192012 | 0.648233036978691 | 0.41281416969487206 |
| F003-B E014 | 3.0661868050450805 | 0.4657026471017708 | -0.43959378731031074 | 109 | F001-B E014 neutral | F002-B E014 | 3.621084739339225 | 0.6311872415922518 | -0.3564186937144888 | -0.5548979342941447 | -0.16548459449048103 | -0.08317509359582193 | -0.5751596013669438 | -0.2248055930760276 | -0.7864378005494476 | 3.6413464064120245 | 0.6905082401777984 | 0.34684401323913683 |

## Verdict

- stock-level Flow 단독 약함
