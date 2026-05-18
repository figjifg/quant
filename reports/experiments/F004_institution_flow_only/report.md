# F004 Stock Institution Flow Only Metrics Summary

## Metadata

- panels: research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv
- stock_institution_flow: mean of 20d institution net buy / 20d traded value and 60d institution net buy / market cap
- zscore: within-sector cross-sectional z-score
- missing_flow_policy: stock-level institution flow input NaNs are not imputed; affected stocks are excluded from diagnostics and portfolio candidates
- missing_flow_rate_note: current stock-sector daily input has institution flow missingness comparable to foreign flow; exact source-panel rate is documented in the ticket
- timing: signal quarter-end T uses stock flow, traded value, and market cap through T; execution is T+1 or later
- macro_gate: D013 10 variables, 5 blocks, 60-month z-score, threshold -0.2

## IC Diagnostics

| carrier | rank_ic_pooled | rank_ic_mean | rank_ic_t_stat | rank_ic_n_quarters | spread | spread_t_stat | positive_spread_ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F004-A D013 direct | -0.0139215115590111 | -0.0053573210903397 | -0.2109663055451181 | 22.0 | -0.001409564774808 | -0.0394796674023229 | 0.3636363636363636 |
| F004-B E014 | -0.0199574288231164 | -0.0036012155863338 | -0.0959373965824256 | 22.0 | 0.0563732632473241 | 1.5120635752260267 | 0.5909090909090909 |

## Carrier Comparison

| variant | cumulative_net_total_return | sharpe | max_drawdown | trade_count | baseline_variant | f003_variant | baseline_cumulative_net_total_return | baseline_sharpe | baseline_max_drawdown | cumulative_uplift_vs_f001 | sharpe_uplift_vs_f001 | mdd_uplift_vs_f001 | f003_cumulative_net_total_return | f003_sharpe | f003_max_drawdown | cumulative_diff_vs_f003 | sharpe_diff_vs_f003 | mdd_diff_vs_f003 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F004-A D013 direct | -0.4790341678187421 | -0.2514739653017774 | -0.6403300661046598 | 109 | F001-A D013 direct | F003-A D013 direct | 2.545770290335013 | 0.5333654677635088 | -0.3392346174957135 | -3.024804458153755 | -0.7848394330652861 | -0.3010954486089463 | 0.9140249795158836 | 0.240954750282348 | -0.4941753798241437 | -1.3930591473346257 | -0.4924287155841254 | -0.1461546862805161 |
| F004-B E014 | 0.6767651920475724 | 0.16539817654726655 | -0.5722545087785456 | 109 | F001-B E014 neutral | F003-B E014 | 3.621084739339225 | 0.6311872415922518 | -0.3564186937144888 | -2.944319547291653 | -0.4657890650449853 | -0.21583581506405675 | 3.0661868050450805 | 0.4657026471017708 | -0.4395937873103107 | -2.3894216129975083 | -0.30030447055450427 | -0.13266072146823488 |

## Verdict

- stock-level institution Flow 단독 약함
