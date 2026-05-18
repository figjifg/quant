# F002 Stock RS Only Metrics Summary

## Metadata

- panels: research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv
- stock_rs: stock 20d/60d cumulative return minus sector 20d/60d cumulative return
- timing: signal quarter-end T uses stock and sector returns through T; execution is T+1 or later
- macro_gate: D013 10 variables, 5 blocks, 60-month z-score, threshold -0.2

## IC Diagnostics

| carrier | rank_ic_pooled | rank_ic_mean | rank_ic_t_stat | rank_ic_n_quarters | spread | spread_t_stat | positive_spread_ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F002-A D013 direct | 0.1477536205450212 | 0.1609407673519818 | 5.266185871047337 | 22.0 | 0.1966572191935779 | 4.136562155646367 | 0.9090909090909092 |
| F002-B E014 | 0.0898173718444489 | 0.1164790984065188 | 2.335549649214219 | 22.0 | 0.0775197016703825 | 1.4743887265047504 | 0.6363636363636364 |

## Carrier Comparison

| variant | cumulative_net_total_return | sharpe | max_drawdown | trade_count | baseline_variant | baseline_cumulative_net_total_return | baseline_sharpe | baseline_max_drawdown | cumulative_uplift_vs_f001 | sharpe_uplift_vs_f001 | mdd_uplift_vs_f001 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F002-A D013 direct | -0.8529580972033175 | -0.4072782866963429 | -0.9069895495190158 | 109 | F001-A D013 direct | 2.545770290335013 | 0.5333654677635088 | -0.3392346174957135 | -3.3987283875383305 | -0.9406437544598517 | -0.5677549320233023 |
| F002-B E014 | -0.5751596013669438 | -0.22480559307602763 | -0.7864378005494476 | 109 | F001-B E014 neutral | 3.621084739339225 | 0.6311872415922518 | -0.3564186937144888 | -4.196244340706169 | -0.8559928346682795 | -0.43001910683495875 |

## Verdict

- RS 종목 단위 약함
