# F006 RS Plus Foreign Flow Metrics Summary

## Metadata

- panels: research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv
- combined_variant: F006
- zscore: final stock score is cross-sectionally z-scored within sector on each signal date
- missing_flow_policy: F006 requires both RS and foreign flow; F007/F008 confirmation missing flow inputs receive no bonus/penalty
- timing: signal quarter-end T uses stock/sector features through T; execution is T+1 or later
- macro_gate: D013 10 variables, 5 blocks, 60-month z-score, threshold -0.2

## IC Diagnostics

| carrier | rank_ic_pooled | rank_ic_mean | rank_ic_t_stat | rank_ic_n_quarters | spread | spread_t_stat | positive_spread_ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F006-A D013 direct | 0.0636960497931207 | 0.0909407681848286 | 2.616870280718191 | 22.0 | 0.1081126741135054 | 3.009347858962799 | 0.8181818181818182 |
| F006-B E014 | 0.0765631324241297 | 0.0479778780886999 | 1.3394144338404237 | 22.0 | 0.1057198174490632 | 1.9458546092647344 | 0.6818181818181818 |

## Carrier Comparison

| variant | cumulative_net_total_return | sharpe | max_drawdown | trade_count | baseline_variant | f002_variant | baseline_cumulative_net_total_return | baseline_sharpe | baseline_max_drawdown | cumulative_uplift_vs_f001 | sharpe_uplift_vs_f001 | mdd_uplift_vs_f001 | f002_cumulative_net_total_return | f002_sharpe | f002_max_drawdown | cumulative_diff_vs_f002 | sharpe_diff_vs_f002 | mdd_diff_vs_f002 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F006-A D013 direct | -0.0650793161695471 | -0.019315476801235607 | -0.7166816287411188 | 110 | F001-A D013 direct | F002-A D013 direct | 2.545770290335013 | 0.5333654677635088 | -0.3392346174957135 | -2.6108496065045603 | -0.5526809445647444 | -0.37744701124540536 | -0.8529580972033175 | -0.4072782866963429 | -0.9069895495190158 | 0.7878787810337704 | 0.3879628098951073 | 0.19030792077789693 |
| F006-B E014 | 0.2333211655670544 | 0.05824950119472223 | -0.6485745390768336 | 109 | F001-B E014 neutral | F002-B E014 | 3.621084739339225 | 0.6311872415922518 | -0.3564186937144888 | -3.3877635737721707 | -0.5729377403975295 | -0.2921558453623448 | -0.5751596013669438 | -0.2248055930760276 | -0.7864378005494476 | 0.8084807669339982 | 0.2830550942707498 | 0.13786326147261396 |

## Verdict

- Codex reports metrics only; F011 promotion decision is summarized in batch_summary.csv.
