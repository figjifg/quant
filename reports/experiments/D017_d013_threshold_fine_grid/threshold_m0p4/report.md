# D011 Threshold -0.4 Metrics Summary

## Metadata

| key | value |
| --- | --- |
| panels_used | ["research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv"] |
| period_start | 2010-01-04 |
| period_end | 2026-05-04 |
| excluded_years | [2016] |
| macro_gate | D009 ten variables transformed to 60-month rolling z-scores, sign-adjusted, averaged by five equal-weight factor blocks; ON when composite >= -0.4 |
| z_score_warmup | rows with fewer than 60 monthly observations have NaN composite and regime OFF |
| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |
| selection | top 5 by signal-date market cap, equal weight when factor macro gate ON |
| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |
| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |
| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |
| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |

## Variant Metrics

| variant | cumulative_net_total_return | max_drawdown | positive_years | annualized_return | annualized_volatility | sharpe | trade_count | cost_paid_total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| factor_macro_gate_mcap | 0.6156561801244 | -0.5974704381808513 | 6 | 0.03254342845671032 | 0.20107408174685862 | 0.16184795262514606 | 155 | 0.0805981440228218 |
| kospi_buy_and_hold | 20.095177626449328 | -0.34485340853513224 | 14 | 0.2257327915799301 | 0.18914309081113953 | 1.1934498406041465 | 0 | 0.0 |
| cash | 0.0 | 0.0 | 0 | 0.0 | 0.0 | nan | 0 | 0.0 |

## D009 Diagnostics

| metric | value |
| --- | ---: |
| cost_0_cumulative_net_total_return | 0.7890975571356187 |
| d001_cumulative_net_total_return | 1.2906841868750734 |
| d001_cost_0_cumulative_net_total_return | 1.397144393892741 |
| d009_minus_d001_cumulative_net_pp | -0.6750280067506733 |
| d009_minus_d001_cost_0_cumulative_net_pp | -0.6080468367571223 |
| regime_on_share | 0.5409836065573771 |
| composite_mean | -0.03428530665464613 |
| composite_std | 0.40416182915908916 |
| composite_positive_share | 0.39473684210526316 |
| global_risk_avg_score | 0.23811249262650716 |
| usd_fx_avg_score | 0.055982348313387324 |
| us_rates_avg_score | -0.5002514470306956 |
| inflation_avg_score | -0.09127345214730313 |
| growth_avg_score | 0.12600352496487346 |
| return_2025_contribution_share | 1.2452655041879628 |
| d001_trade_quarter_overlap_jaccard | 0.40625 |
| d009_on_d001_off_quarter_count | 20 |
| d009_off_d001_on_quarter_count | 1 |
| vix_60d_vs_240d_z_mean | 0.06400131015837443 |
| vix_60d_vs_240d_z_std | 1.0884279098463474 |
| vix_60d_vs_240d_z_positive_share | 0.3684210526315789 |
| baa10y_spread_level_z_mean | -0.540226295411389 |
| baa10y_spread_level_z_std | 1.0246035410314371 |
| baa10y_spread_level_z_positive_share | 0.15789473684210525 |
| usdkrw_yoy_z_mean | 0.12524164955985112 |
| usdkrw_yoy_z_std | 1.0356332093588883 |
| usdkrw_yoy_z_positive_share | 0.5789473684210527 |
| dxy_yoy_z_mean | -0.23720634618662575 |
| dxy_yoy_z_std | 0.9453198884194114 |
| dxy_yoy_z_positive_share | 0.42105263157894735 |
| us_10y_real_level_z_mean | 0.2377902328857666 |
| us_10y_real_level_z_std | 1.4703813094534441 |
| us_10y_real_level_z_positive_share | 0.6842105263157895 |
| us_2_10_curve_z_mean | -0.7627126611756244 |
| us_2_10_curve_z_std | 1.1063571852001688 |
| us_2_10_curve_z_positive_share | 0.3157894736842105 |
| brent_yoy_z_mean | 0.2059977097289487 |
| brent_yoy_z_std | 1.180640927920303 |
| brent_yoy_z_positive_share | 0.39473684210526316 |
| us_breakeven_level_z_mean | -0.023450805434342498 |
| us_breakeven_level_z_std | 1.1858892037420037 |
| us_breakeven_level_z_positive_share | 0.5526315789473685 |
| kr_cli_value_z_mean | 0.04276847042107795 |
| kr_cli_value_z_std | 1.2150334479576115 |
| kr_cli_value_z_positive_share | 0.4473684210526316 |
| kr_exports_yoy_z_mean | 0.20923857950866892 |
| kr_exports_yoy_z_std | 1.2657037838380627 |
| kr_exports_yoy_z_positive_share | 0.5263157894736842 |

## Quarterly Year Breakdown

| year | factor_macro_gate_mcap_net_total_return | kospi_buy_and_hold_net_total_return | cash_net_total_return | d001_factor_macro_gate_mcap_net_total_return | d009_minus_d001_factor_macro_gate_mcap_return |
| --- | --- | --- | --- | --- | --- |
| 2010.0 | 0.0 | 0.3293489579737485 | 0.0 | 0.0 | 0.0 |
| 2011.0 | 0.0 | 0.004079681302652238 | 0.0 | 0.0 | 0.0 |
| 2012.0 | 0.0 | 0.18731018909741426 | 0.0 | 0.0 | 0.0 |
| 2013.0 | 0.0 | 0.06125736750042954 | 0.0 | 0.0 | 0.0 |
| 2014.0 | 0.0 | 0.05769800682302639 | 0.0 | 0.0 | 0.0 |
| 2015.0 | 0.0 | 0.16501292442133764 | 0.0 | 0.0 | 0.0 |
| 2017.0 | 0.09401472235486108 | 0.31675953872996554 | 0.0 | 0.0 | 0.09401472235486108 |
| 2018.0 | -0.44258998448930964 | -0.08401784948302582 | 0.0 | 0.0 | -0.44258998448930964 |
| 2019.0 | 0.05994009480780371 | 0.17019485930094325 | 0.0 | 0.0277493483052602 | 0.03219074650254351 |
| 2020.0 | 0.4630990404450499 | 0.5251287429311848 | 0.0 | 0.2461360848272729 | 0.216962955617777 |
| 2021.0 | -0.12419945981131253 | 0.13170240063376726 | 0.0 | -0.035316520549102 | -0.08888293926221053 |
| 2022.0 | -0.2591599190160777 | -0.18442405395793493 | 0.0 | 0.0 | -0.2591599190160777 |
| 2023.0 | -0.056007063306024896 | 0.3279894204214897 | 0.0 | -0.0177293971971159 | -0.038277666108908995 |
| 2024.0 | 0.014081826253519614 | 0.034981455283805474 | 0.0 | 0.0422472179791628 | -0.02816539172564319 |
| 2025.0 | 0.7666554035490463 | 1.047004780803555 | 0.0 | 0.7666554035490463 | 0.0 |
| 2026.0 | 0.5621484118981521 | 0.7344109727369705 | 0.0 | 0.0 | 0.5621484118981521 |

## Subperiod Breakdown

| period | start | end | v1_net_total_return | v1_cost_0_total_return | v1_annualized_return | v1_cost_0_annualized_return | v1_max_drawdown | v1_cost_0_max_drawdown | v1_trade_count | v1_cost_0_trade_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2010-2017 | 2010-01-04 | 2017-12-31 | 0.09401472235486108 | 0.10111100738801637 | 0.013174613461145235 | 0.014129268394949213 | -0.11120123654025105 | -0.10825712142713284 | 10 | 10 |
| 2018-2026 | 2018-01-01 | 2026-05-04 | 0.4762213968663245 | 0.6230885036388296 | 0.049165729942708625 | 0.06149980623130191 | -0.5974704381808513 | -0.5881028917067271 | 145 | 145 |

## Verdict Summary

| threshold | hypothesis | description | value | threshold_value | passes |
| --- | --- | --- | --- | --- | --- |
| -0.4 | H1 | Threshold 0.0 reproduces D009 Sharpe 0.4144 | 0.16184795262514606 | 0.4144 | <NA> |
| -0.4 | H7 | Threshold Sharpe is at least 0.40 for plateau count | 0.16184795262514606 | 0.4 | False |
| -0.4 | H8 | ON share, trade count, max DD, and subperiod returns are descriptive checks | 0.5409836065573771 |  | <NA> |
