# D003 Metrics Summary

## Metadata

| key | value |
| --- | --- |
| panels_used | ["research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv"] |
| period_start | 2010-01-04 |
| period_end | 2026-05-04 |
| excluded_years | [2016] |
| macro_gate | Thirteen raw variables transformed to 60-month rolling z-scores, sign-adjusted, averaged by five equal-weight factor blocks; ON when composite >= 0 |
| z_score_warmup | rows with fewer than 60 monthly observations have NaN composite and regime OFF |
| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |
| selection | top 5 by signal-date market cap, equal weight when factor macro gate ON |
| baselines | V2 cap-weighted KOSPI proxy buy-and-hold; V3 cash |
| d001_reference | D001 quarterly cumulative net +129.07%; cost-0 +139.71%; 60-month z-score window |
| c014_v11_reference | C014 v11 quarterly cumulative net +111.36%; cost-0 +148.39%; yearly columns read from C014 output files |
| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |
| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |
| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |
| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |

## Variant Metrics

| variant | cumulative_net_total_return | max_drawdown | positive_years | annualized_return | annualized_volatility | sharpe | trade_count | cost_paid_total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| factor_macro_gate_mcap | 0.16783785084513703 | -0.3392346174957134 | 4 | 0.010411125890650519 | 0.1136594572146083 | 0.09159929270991107 | 65 | 0.045832212979018475 |
| kospi_buy_and_hold | 20.095177626449328 | -0.34485340853513224 | 14 | 0.2257327915799301 | 0.18914309081113953 | 1.1934498406041465 | 0 | 0.0 |
| cash | 0.0 | 0.0 | 0 | 0.0 | 0.0 | nan | 0 | 0.0 |

## D003 Diagnostics

| metric | value |
| --- | ---: |
| d001_cumulative_net_total_return | 1.2906841868750734 |
| d001_cost_0_cumulative_net_total_return | 1.397144393892741 |
| d003_minus_d001_cumulative_net_pp | -1.1228463360299363 |
| d003_minus_d001_cost_0_cumulative_net_pp | -1.1788234067366306 |
| c014_v11_cumulative_net_total_return | 1.1136051550981834 |
| c014_v11_cost_0_cumulative_net_total_return | 1.483915813335873 |
| d003_minus_c014_v11_cumulative_net_pp | -0.9457673042530463 |
| d003_minus_c014_v11_cost_0_cumulative_net_pp | -1.2655948261797625 |
| subperiod_2010_2017_net_total_return | 0.0 |
| subperiod_2010_2017_cost_0_total_return | 0.0 |
| subperiod_2010_2017_trade_count | 0 |
| trade_count_2010_2014 | 0 |
| subperiod_2018_2026_net_total_return | 0.16783785084513703 |
| subperiod_2018_2026_cost_0_total_return | 0.21832098715611048 |
| regime_on_share | 0.21311475409836064 |
| composite_mean | -0.18327713224473358 |
| composite_std | 0.4190781070262904 |
| composite_positive_share | 0.43333333333333335 |
| global_risk_avg_score | 0.07657849286227444 |
| usd_fx_avg_score | 0.013005942736187052 |
| rates_avg_score | -0.6962741150925663 |
| inflation_avg_score | -0.015072102117271858 |
| commodity_avg_score | -0.29462387961229103 |
| usd_fx_within_block_avg_std | 0.4325059540017414 |
| rates_within_block_avg_std | 0.8899994188583054 |
| inflation_within_block_avg_std | 0.46387586431105104 |
| d001_trade_overlap_jaccard | 0.6875 |

## Quarterly Year Breakdown

| year | factor_macro_gate_mcap_net_total_return | kospi_buy_and_hold_net_total_return | cash_net_total_return | d001_factor_macro_gate_mcap_net_total_return | d003_minus_d001_factor_macro_gate_mcap_return |
| --- | --- | --- | --- | --- | --- |
| 2010.0 | 0.0 | 0.3293489579737485 | 0.0 | 0.0 | 0.0 |
| 2011.0 | 0.0 | 0.004079681302652238 | 0.0 | 0.0 | 0.0 |
| 2012.0 | 0.0 | 0.18731018909741426 | 0.0 | 0.0 | 0.0 |
| 2013.0 | 0.0 | 0.06125736750042954 | 0.0 | 0.0 | 0.0 |
| 2014.0 | 0.0 | 0.05769800682302639 | 0.0 | 0.0 | 0.0 |
| 2015.0 | 0.0 | 0.16501292442133764 | 0.0 | 0.0 | 0.0 |
| 2017.0 | 0.0 | 0.31675953872996554 | 0.0 | 0.0 | 0.0 |
| 2018.0 | 0.0 | -0.08401784948302582 | 0.0 | 0.0 | 0.0 |
| 2019.0 | 0.027749348305260213 | 0.17019485930094325 | 0.0 | 0.0277493483052602 | 1.3877787807814457e-17 |
| 2020.0 | 0.09045907919499019 | 0.5251287429311848 | 0.0 | 0.2461360848272729 | -0.1556770056322827 |
| 2021.0 | -0.03531652054910228 | 0.13170240063376726 | 0.0 | -0.035316520549102 | -2.8449465006019636e-16 |
| 2022.0 | 0.0 | -0.18442405395793493 | 0.0 | 0.0 | 0.0 |
| 2023.0 | -0.01772939719711608 | 0.3279894204214897 | 0.0 | -0.0177293971971159 | -1.8041124150158794e-16 |
| 2024.0 | 0.04224721797916331 | 0.034981455283805474 | 0.0 | 0.0422472179791628 | 5.065392549852277e-16 |
| 2025.0 | 0.046255164319910946 | 1.047004780803555 | 0.0 | 0.7666554035490463 | -0.7204002392291353 |
| 2026.0 | 0.0 | 0.7344109727369705 | 0.0 | 0.0 | 0.0 |

## Subperiod Breakdown

| period | start | end | v1_net_total_return | v1_cost_0_total_return | v1_annualized_return | v1_cost_0_annualized_return | v1_max_drawdown | v1_cost_0_max_drawdown | v1_trade_count | v1_cost_0_trade_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2010-2017 | 2010-01-04 | 2017-12-31 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0 |
| 2018-2026 | 2018-01-01 | 2026-05-04 | 0.16783785084513703 | 0.21832098715611048 | 0.01930317032607043 | 0.02463265586887564 | -0.3392346174957134 | -0.3393494236202603 | 65 | 65 |

## Verdict Summary

| hypothesis | description | value | threshold | passes |
| --- | --- | --- | --- | --- |
| H1 | V1 cumulative net total return > 0 | 0.16783785084513703 | 0.0 | True |
| H2 | V1 cumulative net >= V2 cumulative net - 30pp | -19.92733977560419 | -0.3 | False |
| H3 | V1 positive in at least 2 of 2010, 2025, 2026 | 1.0 | 2.0 | False |
| H4 | V1 max drawdown improves on V2 by at least 5pp | 0.005618791039418869 | -0.05 | False |
| H5 | V1 positive in >= 8 of 16 years | 4.0 | 8.0 | False |
| H6 | V1 net / V1 cost-0 >= 0.7 | 0.7687664526962061 | 0.7 | True |
| H7 | D003 block expansion improves D001 net, or improves/holds risk-adjusted profile with Sharpe >= 0.40 | -1.1228463360299363 | 0.0 | False |
| H8 | D003 V1 subperiod cumulative net is >= 0 in both 2010-2017 and 2018-2026 | 0.0 | 0.0 | True |
| H9 | Block scores, within-block dispersion, composite distribution, ON share, and D001 overlap are descriptive checks | 0.21311475409836064 |  | <NA> |
