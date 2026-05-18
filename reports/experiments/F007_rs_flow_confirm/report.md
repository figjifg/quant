# F007 RS Plus Flow Confirmation Metrics Summary

## Metadata

- panels: research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv
- combined_variant: F007
- zscore: final stock score is cross-sectionally z-scored within sector on each signal date
- missing_flow_policy: F006 requires both RS and foreign flow; F007/F008 confirmation missing flow inputs receive no bonus/penalty
- timing: signal quarter-end T uses stock/sector features through T; execution is T+1 or later
- macro_gate: D013 10 variables, 5 blocks, 60-month z-score, threshold -0.2

## IC Diagnostics

| carrier | rank_ic_pooled | rank_ic_mean | rank_ic_t_stat | rank_ic_n_quarters | spread | spread_t_stat | positive_spread_ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F007-A D013 direct | 0.0815202972540208 | 0.1078204577310744 | 3.484461857478083 | 22.0 | 0.1231529275480759 | 2.7322366235088094 | 0.8636363636363636 |
| F007-B E014 | 0.067431176899356 | 0.0626711445276742 | 1.4141523336933082 | 22.0 | 0.1365430468235032 | 3.004854963280505 | 0.7727272727272727 |

## Carrier Comparison

| variant | cumulative_net_total_return | sharpe | max_drawdown | trade_count | baseline_variant | f002_variant | baseline_cumulative_net_total_return | baseline_sharpe | baseline_max_drawdown | cumulative_uplift_vs_f001 | sharpe_uplift_vs_f001 | mdd_uplift_vs_f001 | f002_cumulative_net_total_return | f002_sharpe | f002_max_drawdown | cumulative_diff_vs_f002 | sharpe_diff_vs_f002 | mdd_diff_vs_f002 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F007-A D013 direct | -0.5062702035430413 | -0.1777109799724661 | -0.7871676067715438 | 110 | F001-A D013 direct | F002-A D013 direct | 2.545770290335013 | 0.5333654677635088 | -0.3392346174957135 | -3.0520404938780543 | -0.7110764477359749 | -0.44793298927583036 | -0.8529580972033175 | -0.4072782866963429 | -0.9069895495190158 | 0.3466878936602762 | 0.22956730672387682 | 0.11982194274747193 |
| F007-B E014 | -0.503619405765684 | -0.19335270941395133 | -0.6923655104295494 | 108 | F001-B E014 neutral | F002-B E014 | 3.621084739339225 | 0.6311872415922518 | -0.3564186937144888 | -4.124704145104909 | -0.8245399510062031 | -0.3359468167150606 | -0.5751596013669438 | -0.2248055930760276 | -0.7864378005494476 | 0.07154019560125979 | 0.03145288366207627 | 0.09407229011989815 |

## Verdict

- Codex reports metrics only; F011 promotion decision is summarized in batch_summary.csv.
