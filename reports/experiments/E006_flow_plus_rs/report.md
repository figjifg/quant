# E006 Flow Plus RS Metrics Summary

## Metadata

- panels: research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv, research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv
- sector_aggregate_csv: data/processed/sector_aggregate_daily.csv
- sector_mapping_csv: data/processed/stock_sector_mapping_20260518.csv
- kospi_baseline_csv: research_input_data/inputs/macro_features/krx_market_breadth_kospi_2010_2026.csv
- score: average(Flow Score, RS Score), where each component is already cross-sectional z-scored
- timing: signal quarter-end T uses sector and KOSPI data through T; execution is T+1 or later
- thin_sector_policy: n_stocks <= 2 excluded from component scores and Top-K selection
- macro_gate: D013 10 variables, 5 blocks, 60-month z-score, threshold -0.2

## Diagnostic Verdict

- verdict: PASS
- rank_ic_mean: 0.07060535093321978
- rank_ic_std: 0.34359745970148364
- rank_ic_t_stat: 1.6049170436898728
- top_bottom_spread_mean: 0.049581267719072494
- top_bottom_spread_std: 0.1719939064825156
- top_bottom_spread_t_stat: 2.251487207038308
- positive_spread_ratio: 0.6229508196721312

## Subperiod Diagnostics

| period | n_quarters | rank_ic_mean | rank_ic_std | rank_ic_t_stat | spread_mean | spread_std | spread_t_stat | positive_spread_ratio |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2010_2017 | 28 | 0.12316017316017316 | 0.321860741356662 | 2.0247961167055553 | 0.05981460633543355 | 0.1581416881897431 | 2.001427643075457 | 0.6071428571428571 |
| 2018_2026 | 33 | 0.0260133805588351 | 0.35984158219523493 | 0.41528133951841406 | 0.04089843495367522 | 0.18492031137715245 | 1.2705127954147284 | 0.6363636363636364 |
| spike_years_2020_2025_2026 | 9 | 0.017724867724867723 | 0.36385059984178175 | 0.14614405802196237 | 0.10092116417307688 | 0.29584135886279994 | 1.0233981268982777 | 0.6666666666666666 |
| excluding_spike_years | 52 | 0.07975774225774225 | 0.3428522757214448 | 1.6775191514795225 | 0.04069551640972557 | 0.1432746949207452 | 2.0482300964300464 | 0.6153846153846154 |
| year_2020 | 4 | 0.22007575757575762 | 0.4175763714792221 | 1.0540623110266583 | 0.322115339268477 | 0.29313999668416696 | 2.197689451538942 | 1.0 |
| year_2025 | 4 | -0.15443722943722946 | 0.28229033602164005 | -1.0941729824246655 | -0.05836071097285431 | 0.16719575592424696 | -0.6981123492069544 | 0.5 |
| year_2026 | 1 | -0.10303030303030303 | nan | nan | -0.1467280356247988 | nan | nan | 0.0 |

## Comparison With E003/E004/E005

| variant | verdict | rank_ic_mean | spread_t_stat | cumulative_net_total_return | sharpe | max_drawdown | trade_count |
| --- | --- | --- | --- | --- | --- | --- | --- |
| E003_A_d013_replication | BASELINE | <NA> | <NA> | 2.5457702903350135 | 0.5333654677635088 | -0.3392346174957135 | 110 |
| E004_flow_top3 | FAIL | 0.0039244908097367 | -0.7685649834695819 | <NA> | <NA> | <NA> | <NA> |
| E005_rs_top3 | PASS | 0.155464480874317 | 3.0783397032798763 | 1.763273164997528 | 0.3732257697380196 | -0.45803378557762275 | 110 |
| E006_flow_plus_rs_top3 | PASS | 0.07060535093321978 | 2.251487207038308 | 1.6042647247607862 | 0.35325542427251233 | -0.44655883164336885 | 110 |

## Portfolio Metrics

| variant | cumulative_net_total_return | sharpe | max_drawdown | trade_count |
| --- | --- | --- | --- | --- |
| E006_flow_plus_rs_top3 | 1.6042647247607862 | 0.35325542427251233 | -0.44655883164336885 | 110 |

