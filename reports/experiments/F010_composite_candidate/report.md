# F010 Composite Candidate Metrics Summary

## Metadata

- panels: research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv
- combined_variant: F010
- zscore: final stock score is cross-sectionally z-scored within sector on each signal date
- missing_flow_policy: F006 requires both RS and foreign flow; F007/F008 confirmation missing flow inputs receive no bonus/penalty
- timing: signal quarter-end T uses stock/sector features through T; execution is T+1 or later
- macro_gate: D013 10 variables, 5 blocks, 60-month z-score, threshold -0.2

## IC Diagnostics

| carrier | rank_ic_pooled | rank_ic_mean | rank_ic_t_stat | rank_ic_n_quarters | spread | spread_t_stat | positive_spread_ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F010-A D013 direct | 0.082789975087767 | 0.1099477779961756 | 3.688131924347972 | 22.0 | 0.166228811476639 | 2.6489756399680435 | 0.6363636363636364 |
| F010-B E014 | 0.0794279190907025 | 0.0950884775620914 | 2.645494451390072 | 22.0 | 0.112321423711726 | 3.087968165998465 | 0.8181818181818182 |

## Carrier Comparison

| variant | cumulative_net_total_return | sharpe | max_drawdown | trade_count | baseline_variant | f002_variant | baseline_cumulative_net_total_return | baseline_sharpe | baseline_max_drawdown | cumulative_uplift_vs_f001 | sharpe_uplift_vs_f001 | mdd_uplift_vs_f001 | f002_cumulative_net_total_return | f002_sharpe | f002_max_drawdown | cumulative_diff_vs_f002 | sharpe_diff_vs_f002 | mdd_diff_vs_f002 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F010-A D013 direct | 0.34554280768351364 | 0.07657759416388611 | -0.7246351249505394 | 110 | F001-A D013 direct | F002-A D013 direct | 2.545770290335013 | 0.5333654677635088 | -0.3392346174957135 | -2.200227482651499 | -0.4567878735996227 | -0.3854005074548259 | -0.8529580972033175 | -0.4072782866963429 | -0.9069895495190158 | 1.1985009048868311 | 0.483855880860229 | 0.1823544245684764 |
| F010-B E014 | -0.2507740911059727 | -0.07884012859966505 | -0.6933400663054508 | 109 | F001-B E014 neutral | F002-B E014 | 3.621084739339225 | 0.6311872415922518 | -0.3564186937144888 | -3.871858830445198 | -0.7100273701919169 | -0.33692137259096194 | -0.5751596013669438 | -0.2248055930760276 | -0.7864378005494476 | 0.32438551026097107 | 0.14596546447636255 | 0.09309773424399681 |

## Verdict

- Codex reports metrics only; F011 promotion decision is summarized in batch_summary.csv.
