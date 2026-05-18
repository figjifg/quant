# F005 Stock Liquidity Only Metrics Summary

## Metadata

- panels: research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv
- stock_liquidity: mean of 20d average traded value / 120d average traded value and 20d average turnover / 120d average turnover
- turnover: traded_value / market_cap
- zscore: within-sector cross-sectional z-score
- missing_liquidity_policy: traded_value missingness is 0% per F000; no imputation is applied; invalid denominator rows are excluded from diagnostics and portfolio candidates
- timing: signal quarter-end T uses stock liquidity, turnover, and market cap through T; execution is T+1 or later
- macro_gate: D013 10 variables, 5 blocks, 60-month z-score, threshold -0.2

## IC Diagnostics

| carrier | rank_ic_pooled | rank_ic_mean | rank_ic_t_stat | rank_ic_n_quarters | spread | spread_t_stat | positive_spread_ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F005-A D013 direct | 0.0376047814812541 | 0.0513815931872606 | 1.6092602131827731 | 22.0 | 0.0661837057859745 | 1.7263644308703627 | 0.7272727272727273 |
| F005-B E014 | -0.073590397880475 | -0.0286385189726212 | -0.6363451943960491 | 22.0 | -0.0595089818501158 | -1.2653402490434378 | 0.4090909090909091 |

## Carrier Comparison

| variant | cumulative_net_total_return | sharpe | max_drawdown | trade_count | baseline_variant | f002_variant | f003_variant | f004_variant | baseline_cumulative_net_total_return | baseline_sharpe | baseline_max_drawdown | cumulative_uplift_vs_f001 | sharpe_uplift_vs_f001 | mdd_uplift_vs_f001 | f002_cumulative_net_total_return | f002_sharpe | f002_max_drawdown | cumulative_diff_vs_f002 | sharpe_diff_vs_f002 | mdd_diff_vs_f002 | f003_cumulative_net_total_return | f003_sharpe | f003_max_drawdown | cumulative_diff_vs_f003 | sharpe_diff_vs_f003 | mdd_diff_vs_f003 | f004_cumulative_net_total_return | f004_sharpe | f004_max_drawdown | cumulative_diff_vs_f004 | sharpe_diff_vs_f004 | mdd_diff_vs_f004 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F005-A D013 direct | -0.17821914137044448 | -0.05425876213245047 | -0.7089212886389102 | 110 | F001-A D013 direct | F002-A D013 direct | F003-A D013 direct | F004-A D013 direct | 2.545770290335013 | 0.5333654677635088 | -0.3392346174957135 | -2.7239894317054576 | -0.5876242298959593 | -0.36968667114319675 | -0.8529580972033175 | -0.4072782866963429 | -0.9069895495190158 | 0.674738955832873 | 0.35301952456389246 | 0.19806826088010554 | 0.9140249795158836 | 0.240954750282348 | -0.4941753798241437 | -1.092244120886328 | -0.2952135124147985 | -0.21474590881476652 | -0.4790341678187421 | -0.2514739653017774 | -0.6403300661046598 | 0.3008150264482976 | 0.19721520316932695 | -0.06859122253425043 |
| F005-B E014 | 0.1027292455664206 | 0.030917462307062767 | -0.5638192243108182 | 108 | F001-B E014 neutral | F002-B E014 | F003-B E014 | F004-B E014 | 3.621084739339225 | 0.6311872415922518 | -0.3564186937144888 | -3.5183554937728045 | -0.6002697792851891 | -0.2074005305963294 | -0.5751596013669438 | -0.2248055930760276 | -0.7864378005494476 | 0.6778888469333644 | 0.25572305538309037 | 0.22261857623862935 | 3.0661868050450805 | 0.4657026471017708 | -0.4395937873103107 | -2.96345755947866 | -0.434785184794708 | -0.12422543700050753 | 0.6767651920475724 | 0.1653981765472665 | -0.5722545087785456 | -0.5740359464811517 | -0.13448071424020372 | 0.008435284467727344 |

## Verdict

- liquidity 단독 약함
