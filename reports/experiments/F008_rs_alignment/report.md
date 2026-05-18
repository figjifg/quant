# F008 RS Plus Foreign/Institution Alignment Metrics Summary

## Metadata

- panels: research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv
- combined_variant: F008
- zscore: final stock score is cross-sectionally z-scored within sector on each signal date
- missing_flow_policy: F006 requires both RS and foreign flow; F007/F008 confirmation missing flow inputs receive no bonus/penalty
- timing: signal quarter-end T uses stock/sector features through T; execution is T+1 or later
- macro_gate: D013 10 variables, 5 blocks, 60-month z-score, threshold -0.2

## IC Diagnostics

| carrier | rank_ic_pooled | rank_ic_mean | rank_ic_t_stat | rank_ic_n_quarters | spread | spread_t_stat | positive_spread_ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F008-A D013 direct | 0.0910520617730208 | 0.1170005019109652 | 3.6583834367955816 | 22.0 | 0.1720260956782584 | 2.517892409618447 | 0.8636363636363636 |
| F008-B E014 | 0.0868525749883895 | 0.1122357732840071 | 2.5560188492040794 | 22.0 | 0.1393908170208156 | 3.752561673133073 | 0.9090909090909092 |

## Carrier Comparison

| variant | cumulative_net_total_return | sharpe | max_drawdown | trade_count | baseline_variant | f002_variant | baseline_cumulative_net_total_return | baseline_sharpe | baseline_max_drawdown | cumulative_uplift_vs_f001 | sharpe_uplift_vs_f001 | mdd_uplift_vs_f001 | f002_cumulative_net_total_return | f002_sharpe | f002_max_drawdown | cumulative_diff_vs_f002 | sharpe_diff_vs_f002 | mdd_diff_vs_f002 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F008-A D013 direct | -0.16657873691898106 | -0.04644015542424904 | -0.7648773467856584 | 110 | F001-A D013 direct | F002-A D013 direct | 2.545770290335013 | 0.5333654677635088 | -0.3392346174957135 | -2.7123490272539943 | -0.5798056231877579 | -0.42564272928994495 | -0.8529580972033175 | -0.4072782866963429 | -0.9069895495190158 | 0.6863793602843364 | 0.36083813127209385 | 0.14211220273335734 |
| F008-B E014 | -0.5593816206824578 | -0.2200361772062653 | -0.7645807953935938 | 108 | F001-B E014 neutral | F002-B E014 | 3.621084739339225 | 0.6311872415922518 | -0.3564186937144888 | -4.180466360021683 | -0.8512234187985172 | -0.408162101679105 | -0.5751596013669438 | -0.2248055930760276 | -0.7864378005494476 | 0.015777980684485993 | 0.004769415869762289 | 0.02185700515585376 |

## Verdict

- Codex reports metrics only; F011 promotion decision is summarized in batch_summary.csv.
