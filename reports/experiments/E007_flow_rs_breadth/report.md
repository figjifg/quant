# E007 Flow RS Breadth Metrics Summary

## Metadata

- panels: research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv
- sector_aggregate_csv: data/processed/sector_aggregate_daily.csv
- stock_sector_daily_csv: data/processed/stock_with_sector_daily.csv
- sector_mapping_csv: data/processed/stock_sector_mapping_20260518.csv
- kospi_baseline_csv: research_input_data/inputs/macro_features/krx_market_breadth_kospi_2010_2026.csv
- breadth_score: z-score across sectors of strict breadth, the share of stocks with positive 20-day foreign net buy and positive 20-day relative return versus KOSPI
- combined_score: average(Flow Score, RS Score, Breadth Score), requiring all three component scores to be valid
- timing: signal quarter-end T uses stock, sector, and KOSPI data through T; execution is T+1 or later
- thin_sector_policy: n_stocks <= 2 excluded from breadth, combined score, and Top-K selection
- macro_gate: D013 10 variables, 5 blocks, 60-month z-score, threshold -0.2

## Breadth Standalone Diagnostic

- rank_ic_mean: 0.06728178506628603
- rank_ic_std: 0.3479883755622414
- rank_ic_t_stat: 1.5100721084701654
- top_bottom_spread_mean: 0.03288255745369161
- top_bottom_spread_t_stat: 1.3799718930746223

## Combined Diagnostic Verdict

- verdict: PASS
- rank_ic_mean: 0.08828684976225963
- rank_ic_std: 0.3306030215841017
- rank_ic_t_stat: 2.0857109425029736
- top_bottom_spread_mean: 0.05846670096766326
- top_bottom_spread_std: 0.17954595587510824
- top_bottom_spread_t_stat: 2.543301685957553
- positive_spread_ratio: 0.6557377049180327

## Combined Subperiod Diagnostics

| period | n_quarters | rank_ic_mean | rank_ic_std | rank_ic_t_stat | spread_mean | spread_std | spread_t_stat | positive_spread_ratio |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2010_2017 | 28 | 0.17077922077922078 | 0.2704069071660851 | 3.34192163961027 | 0.06633459862754694 | 0.1670291692649424 | 2.101487447493547 | 0.75 |
| 2018_2026 | 33 | 0.0182933228387774 | 0.36363848996851506 | 0.2889879425849569 | 0.05179090901382257 | 0.19184425271076866 | 1.5508211330135644 | 0.5757575757575758 |
| spike_years_2020_2025_2026 | 9 | 0.0737854737854738 | 0.3590085801464393 | 0.6165769666734157 | 0.1525601046803437 | 0.2913098339246916 | 1.571111788005581 | 0.6666666666666666 |
| excluding_spike_years | 52 | 0.0907967032967033 | 0.3291279032554405 | 1.989330993460473 | 0.04218130417123781 | 0.15093437141509128 | 2.0152713212960642 | 0.6538461538461539 |
| year_2020 | 4 | 0.3030303030303031 | 0.39186712139776175 | 1.5465972340287997 | 0.39004284294313096 | 0.26074069214865714 | 2.991806455133242 | 1.0 |
| year_2025 | 4 | -0.13549783549783548 | 0.2440161093489192 | -1.1105646742698188 | -0.06060580025749086 | 0.13919085096021033 | -0.8708302282714815 | 0.25 |
| year_2026 | 1 | -0.006060606060606061 | nan | nan | 0.05529277138053296 | nan | nan | 1.0 |

## Breadth Subperiod Diagnostics

| period | n_quarters | rank_ic_mean | rank_ic_std | rank_ic_t_stat | spread_mean | spread_std | spread_t_stat | positive_spread_ratio |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2010_2017 | 28 | 0.14429746192015006 | 0.28403594554075406 | 2.6882174953715636 | 0.060055326753136455 | 0.186970913589216 | 1.6996382639774148 | 0.6785714285714286 |
| 2018_2026 | 33 | 0.0019351501599771728 | 0.38651065806473495 | 0.02876140953035528 | 0.009826874411738417 | 0.18507097749596732 | 0.30502403154553465 | 0.3939393939393939 |
| spike_years_2020_2025_2026 | 9 | 0.21062467502450272 | 0.3278528185613582 | 1.9273100284640436 | 0.10745394553292262 | 0.27741403280125826 | 1.1620242615113512 | 0.7777777777777778 |
| excluding_spike_years | 52 | 0.042472438727363906 | 0.3483553504331044 | 0.8791973795443127 | 0.01997597105536317 | 0.16590494470501987 | 0.8682608953621758 | 0.4807692307692308 |
| year_2020 | 4 | 0.35871039438807223 | 0.3730642724722535 | 1.923048765891948 | 0.23324962994063209 | 0.35415939494718884 | 1.3172014255073683 | 0.75 |
| year_2025 | 4 | 0.013253621332393013 | 0.23091510098259446 | 0.11479215760247764 | -0.030270646443592536 | 0.1806787964842728 | -0.33507691032497494 | 0.75 |
| year_2026 | 1 | 0.40776601233866383 | nan | nan | 0.15516957580814533 | nan | nan | 1.0 |

## Comparison With All E

| variant | verdict | rank_ic_mean | spread_t_stat | cumulative_net_total_return | sharpe | max_drawdown | trade_count |
| --- | --- | --- | --- | --- | --- | --- | --- |
| E003_A_d013_replication | BASELINE | <NA> | <NA> | 2.5457702903350135 | 0.5333654677635088 | -0.3392346174957135 | 110 |
| E004_flow_top3 | FAIL | 0.0039244908097367 | -0.7685649834695819 | <NA> | <NA> | <NA> | <NA> |
| E005_rs_top3 | PASS | 0.155464480874317 | 3.0783397032798763 | 1.763273164997528 | 0.3732257697380196 | -0.45803378557762275 | 110 |
| E006_flow_plus_rs_top3 | PASS | 0.0706053509332197 | 2.251487207038308 | 1.6042647247607862 | 0.35325542427251233 | -0.44655883164336885 | 110 |
| E007_flow_rs_breadth_top3 | PASS | 0.08828684976225963 | 2.543301685957553 | 2.3200922451001436 | 0.48218421304767917 | -0.3968185249283369 | 110 |

## Portfolio Metrics

| variant | cumulative_net_total_return | sharpe | max_drawdown | trade_count |
| --- | --- | --- | --- | --- |
| E007_flow_rs_breadth_top3 | 2.3200922451001436 | 0.48218421304767917 | -0.3968185249283369 | 110 |

