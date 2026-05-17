# D010 36mo Metrics Summary

## Metadata

| key | value |
| --- | --- |
| panels_used | ["research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv"] |
| period_start | 2010-01-04 |
| period_end | 2026-05-04 |
| excluded_years | [2016] |
| macro_gate | D009 ten variables transformed to 36-month rolling z-scores, sign-adjusted, averaged by five equal-weight factor blocks; ON when composite >= 0 |
| z_score_warmup | rows with fewer than 36 monthly observations have NaN composite and regime OFF |
| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |
| selection | top 5 by signal-date market cap, equal weight when factor macro gate ON |
| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |
| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |
| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |
| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |

## Variant Metrics

| variant | cumulative_net_total_return | max_drawdown | positive_years | annualized_return | annualized_volatility | sharpe | trade_count | cost_paid_total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| factor_macro_gate_mcap | 1.0718741666171416 | -0.3336818664706048 | 5 | 0.04982963163975973 | 0.15651888224250662 | 0.31836179076818916 | 120 | 0.08326651517003898 |
| kospi_buy_and_hold | 20.095177626449328 | -0.34485340853513224 | 14 | 0.2257327915799301 | 0.18914309081113953 | 1.1934498406041465 | 0 | 0.0 |
| cash | 0.0 | 0.0 | 0 | 0.0 | 0.0 | nan | 0 | 0.0 |

## D009 Diagnostics

| metric | value |
| --- | ---: |
| cost_0_cumulative_net_total_return | 1.2422867576364762 |
| d001_cumulative_net_total_return | 1.2906841868750734 |
| d001_cost_0_cumulative_net_total_return | 1.397144393892741 |
| d009_minus_d001_cumulative_net_pp | -0.21881002025793173 |
| d009_minus_d001_cost_0_cumulative_net_pp | -0.1548576362562648 |
| regime_on_share | 0.4098360655737705 |
| composite_mean | 0.037691919136321916 |
| composite_std | 0.45777655053852717 |
| composite_positive_share | 0.5434782608695652 |
| global_risk_avg_score | 0.15513743288606482 |
| usd_fx_avg_score | -0.05400299398224213 |
| us_rates_avg_score | -0.31435363576099307 |
| inflation_avg_score | 0.2105127848775798 |
| growth_avg_score | 0.1911660076612003 |
| return_2025_contribution_share | 0.7152475798242504 |
| d001_trade_quarter_overlap_jaccard | 0.35714285714285715 |
| d009_on_d001_off_quarter_count | 15 |
| d009_off_d001_on_quarter_count | 4 |
| vix_60d_vs_240d_z_mean | 0.11492278116058911 |
| vix_60d_vs_240d_z_std | 1.0999169140859095 |
| vix_60d_vs_240d_z_positive_share | 0.45652173913043476 |
| baa10y_spread_level_z_mean | -0.4251976469327189 |
| baa10y_spread_level_z_std | 1.2724902775211036 |
| baa10y_spread_level_z_positive_share | 0.2826086956521739 |
| usdkrw_yoy_z_mean | 0.10096338656128281 |
| usdkrw_yoy_z_std | 1.0712510560101849 |
| usdkrw_yoy_z_positive_share | 0.5869565217391305 |
| dxy_yoy_z_mean | 0.007042601403201454 |
| dxy_yoy_z_std | 1.1865618806867646 |
| dxy_yoy_z_positive_share | 0.45652173913043476 |
| us_10y_real_level_z_mean | 0.3971096511874745 |
| us_10y_real_level_z_std | 1.3259569666489859 |
| us_10y_real_level_z_positive_share | 0.6739130434782609 |
| us_2_10_curve_z_mean | -0.23159762033451198 |
| us_2_10_curve_z_std | 1.401933003220326 |
| us_2_10_curve_z_positive_share | 0.41304347826086957 |
| brent_yoy_z_mean | -0.11492682821971531 |
| brent_yoy_z_std | 1.4545002378690506 |
| brent_yoy_z_positive_share | 0.3695652173913043 |
| us_breakeven_level_z_mean | -0.3060987415354442 |
| us_breakeven_level_z_std | 1.2212516523751513 |
| us_breakeven_level_z_positive_share | 0.391304347826087 |
| kr_cli_value_z_mean | 0.334051043339913 |
| kr_cli_value_z_std | 1.3823694382881955 |
| kr_cli_value_z_positive_share | 0.5869565217391305 |
| kr_exports_yoy_z_mean | 0.04828097198248762 |
| kr_exports_yoy_z_std | 1.1863460940743267 |
| kr_exports_yoy_z_positive_share | 0.5 |

## Quarterly Year Breakdown

| year | factor_macro_gate_mcap_net_total_return | kospi_buy_and_hold_net_total_return | cash_net_total_return | d001_factor_macro_gate_mcap_net_total_return | d009_minus_d001_factor_macro_gate_mcap_return |
| --- | --- | --- | --- | --- | --- |
| 2010.0 | 0.0 | 0.3293489579737485 | 0.0 | 0.0 | 0.0 |
| 2011.0 | 0.0 | 0.004079681302652238 | 0.0 | 0.0 | 0.0 |
| 2012.0 | 0.0 | 0.18731018909741426 | 0.0 | 0.0 | 0.0 |
| 2013.0 | 0.0 | 0.06125736750042954 | 0.0 | 0.0 | 0.0 |
| 2014.0 | -0.07836784555750509 | 0.05769800682302639 | 0.0 | 0.0 | -0.07836784555750509 |
| 2015.0 | -0.010098189080947173 | 0.16501292442133764 | 0.0 | 0.0 | -0.010098189080947173 |
| 2017.0 | 0.09401472235486152 | 0.31675953872996554 | 0.0 | 0.0 | 0.09401472235486152 |
| 2018.0 | -0.03586254487531937 | -0.08401784948302582 | 0.0 | 0.0 | -0.03586254487531937 |
| 2019.0 | -0.04651535835890053 | 0.17019485930094325 | 0.0 | 0.0277493483052602 | -0.07426470666416073 |
| 2020.0 | 0.2461360848272729 | 0.5251287429311848 | 0.0 | 0.2461360848272729 | 0.0 |
| 2021.0 | -0.12419945981131253 | 0.13170240063376726 | 0.0 | -0.035316520549102 | -0.08888293926221053 |
| 2022.0 | -0.09716827644733184 | -0.18442405395793493 | 0.0 | 0.0 | -0.09716827644733184 |
| 2023.0 | 0.0 | 0.3279894204214897 | 0.0 | -0.0177293971971159 | 0.0177293971971159 |
| 2024.0 | 0.014081826253520502 | 0.034981455283805474 | 0.0 | 0.0422472179791628 | -0.0281653917256423 |
| 2025.0 | 0.7666554035490458 | 1.047004780803555 | 0.0 | 0.7666554035490463 | -4.440892098500626e-16 |
| 2026.0 | 0.26864408497789793 | 0.7344109727369705 | 0.0 | 0.0 | 0.26864408497789793 |

## Subperiod Breakdown

| period | start | end | v1_net_total_return | v1_cost_0_total_return | v1_annualized_return | v1_cost_0_annualized_return | v1_max_drawdown | v1_cost_0_max_drawdown | v1_trade_count | v1_cost_0_trade_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2010-2017 | 2010-01-04 | 2017-12-31 | -0.038746384844015824 | -0.016311214112985306 | -0.0057396977620735035 | -0.0023926924908275193 | -0.20603497913434277 | -0.19818363962490138 | 35 | 35 |
| 2018-2026 | 2018-01-01 | 2026-05-04 | 1.154522854629282 | 1.2770507742529924 | 0.09920320147533279 | 0.10672088265008561 | -0.3336818664706048 | -0.3249118089570776 | 85 | 85 |

## 2010-2014 Warmup Diagnosis

| period | start | end | trade_count | net_total_return | cost_0_total_return |
| --- | --- | --- | --- | --- | --- |
| 2010-2014 | 2010-01-04 | 2014-12-31 | 20 | -0.11530293526238955 | -0.10576139208782243 |

## Verdict Summary

| window | hypothesis | description | value | threshold | passes |
| --- | --- | --- | --- | --- | --- |
| 36 | H1 | 60-month D010 reproduces D009 Sharpe 0.4144 | 0.31836179076818916 | 0.4144 | <NA> |
| 36 | H7 | Window Sharpe is at least 0.40 for plateau count | 0.31836179076818916 | 0.4 | False |
| 36 | H8 | 2010-2014 warmup-artifact trade count and return diagnostic | 20.0 | >0 for 36mo/48mo | True |
| 36 | H9 | ON share, max DD, and composite distribution are descriptive checks | 0.4098360655737705 |  | <NA> |
