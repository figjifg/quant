# F009 RS Plus Liquidity Confirmation Metrics Summary

## Metadata

- panels: research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv
- combined_variant: F009
- zscore: final stock score is cross-sectionally z-scored within sector on each signal date
- missing_flow_policy: F006 requires both RS and foreign flow; F007/F008 confirmation missing flow inputs receive no bonus/penalty
- timing: signal quarter-end T uses stock/sector features through T; execution is T+1 or later
- macro_gate: D013 10 variables, 5 blocks, 60-month z-score, threshold -0.2

## IC Diagnostics

| carrier | rank_ic_pooled | rank_ic_mean | rank_ic_t_stat | rank_ic_n_quarters | spread | spread_t_stat | positive_spread_ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F009-A D013 direct | 0.0952696871778649 | 0.1070298714470574 | 3.565950908053253 | 22.0 | 0.1633588694509919 | 2.728715498753294 | 0.7272727272727273 |
| F009-B E014 | 0.0902850795018071 | 0.0808545531422325 | 2.4193163566517786 | 22.0 | 0.0973257521060144 | 2.1762561870395216 | 0.8181818181818182 |

## Carrier Comparison

| variant | cumulative_net_total_return | sharpe | max_drawdown | trade_count | baseline_variant | f002_variant | baseline_cumulative_net_total_return | baseline_sharpe | baseline_max_drawdown | cumulative_uplift_vs_f001 | sharpe_uplift_vs_f001 | mdd_uplift_vs_f001 | f002_cumulative_net_total_return | f002_sharpe | f002_max_drawdown | cumulative_diff_vs_f002 | sharpe_diff_vs_f002 | mdd_diff_vs_f002 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F009-A D013 direct | 0.1803902742753707 | 0.04205586372690154 | -0.7424014873130613 | 110 | F001-A D013 direct | F002-A D013 direct | 2.545770290335013 | 0.5333654677635088 | -0.3392346174957135 | -2.3653800160596425 | -0.4913096040366073 | -0.40316686981734784 | -0.8529580972033175 | -0.4072782866963429 | -0.9069895495190158 | 1.0333483714786882 | 0.4493341504232444 | 0.16458806220595446 |
| F009-B E014 | -0.3104962442593764 | -0.10314692348286694 | -0.7087357590268362 | 109 | F001-B E014 neutral | F002-B E014 | 3.621084739339225 | 0.6311872415922518 | -0.3564186937144888 | -3.9315809835986015 | -0.7343341650751187 | -0.35231706531234736 | -0.5751596013669438 | -0.2248055930760276 | -0.7864378005494476 | 0.2646633571075674 | 0.12165866959316066 | 0.0777020415226114 |

## Verdict

- Codex reports metrics only; F011 promotion decision is summarized in batch_summary.csv.
