# E005 Relative Strength Only Metrics Summary

## Metadata

- panels: research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv
- sector_aggregate_csv: data/processed/sector_aggregate_daily.csv
- kospi_baseline_csv: research_input_data/inputs/macro_features/krx_market_breadth_kospi_2010_2026.csv
- score: z-score across sectors of average(sector_rel_ret_20d, sector_rel_ret_60d)
- timing: signal quarter-end T uses sector and KOSPI data through T; execution is T+1 or later
- thin_sector_policy: n_stocks <= 2 excluded from score and Top-K selection
- macro_gate: D013 10 variables, 5 blocks, 60-month z-score, threshold -0.2

## Diagnostic Verdict

- verdict: PASS
- rank_ic_mean: 0.155464480874317
- rank_ic_std: 0.36561113374852755
- rank_ic_t_stat: 3.321059725163582
- top_bottom_spread_mean: 0.07488020339527693
- top_bottom_spread_std: 0.18998328341627285
- top_bottom_spread_t_stat: 3.0783397032798763
- positive_spread_ratio: 0.6721311475409836

## Subperiod Diagnostics

| period | n_quarters | rank_ic_mean | rank_ic_std | rank_ic_t_stat | spread_mean | spread_std | spread_t_stat | positive_spread_ratio |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2010_2017 | 28 | 0.19404761904761905 | 0.3397119343035194 | 3.0225711296059194 | 0.08969294868755659 | 0.18305464346609115 | 2.5927256702156267 | 0.75 |
| 2018_2026 | 33 | 0.12272727272727273 | 0.38839925315262325 | 1.815179871995113 | 0.062311813450312385 | 0.1976043472295013 | 1.811468831548407 | 0.6060606060606061 |
| spike_years_2020_2025_2026 | 9 | 0.22330447330447326 | 0.4882940822253589 | 1.371946628679885 | 0.17983187075064422 | 0.2918907294418357 | 1.8482793656502083 | 0.7777777777777778 |
| excluding_spike_years | 52 | 0.14372294372294372 | 0.3448287977625048 | 3.0055520096706134 | 0.05671549173761722 | 0.16376249372361462 | 2.4974047344229646 | 0.6538461538461539 |
| year_2020 | 4 | 0.42310606060606065 | 0.2802808481531422 | 3.01915784395572 | 0.37351870043375807 | 0.2654584436711189 | 2.814140663738064 | 1.0 |
| year_2025 | 4 | -0.09188311688311693 | 0.5482391158937844 | -0.3351935833083399 | -0.03926840278298353 | 0.1981459613933643 | -0.3963583462095089 | 0.5 |
| year_2026 | 1 | 0.6848484848484848 | nan | nan | 0.2814856461526997 | nan | nan | 1.0 |

## Comparison With E003/E004

| variant | verdict | rank_ic_mean | spread_t_stat | cumulative_net_total_return | sharpe | max_drawdown | trade_count |
| --- | --- | --- | --- | --- | --- | --- | --- |
| E003_A_d013_replication | BASELINE | <NA> | <NA> | 2.5457702903350135 | 0.5333654677635088 | -0.3392346174957135 | 110 |
| E004_flow_top3 | FAIL | 0.0039244908097367 | -0.7685649834695819 | <NA> | <NA> | <NA> | <NA> |
| E005_rs_top3 | PASS | 0.155464480874317 | 3.0783397032798763 | 1.763273164997528 | 0.3732257697380196 | -0.45803378557762275 | 110 |

## Portfolio Metrics

| variant | cumulative_net_total_return | sharpe | max_drawdown | trade_count |
| --- | --- | --- | --- | --- |
| E005_rs_top3 | 1.763273164997528 | 0.3732257697380196 | -0.45803378557762275 | 110 |

