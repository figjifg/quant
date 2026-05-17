# D015 Subperiod Metrics Summary

## Metadata

| key | value |
| --- | --- |
| subperiod | scheme_c_is |
| trading_start | 2015-01-01 |
| trading_end | 2021-12-31 |
| macro_gate | frozen D013 factor aggregation; only trading window is restricted |
| z_score_warmup | 60-month rolling z-score is computed on full historical monthly regime before each trade quarter |
| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |
| selection | top 5 by signal-date market cap, equal weight when factor macro gate ON |
| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |
| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |
| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |
| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |

## Variant Metrics

| variant | cumulative_net_total_return | max_drawdown | positive_years | annualized_return | annualized_volatility | sharpe | trade_count | cost_paid_total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| factor_macro_gate_mcap | 0.4043431750564124 | -0.3392346174957135 | 3 | 0.05964724284808809 | 0.17530812592403677 | 0.3402423163997201 | 65 | 0.053697015645024854 |
| kospi_buy_and_hold | 1.857472708992793 | -0.34485340853513236 | 5 | 0.19618373364893626 | 0.16753243253189778 | 1.1710194299935526 | 0 | 0.0 |
| cash | 0.0 | 0.0 | 0 | 0.0 | 0.0 | nan | 0 | 0.0 |

## D009 Diagnostics

| metric | value |
| --- | ---: |
| cost_0_cumulative_net_total_return | 0.46520062175207944 |
| d001_cumulative_net_total_return | 1.2906841868750734 |
| d001_cost_0_cumulative_net_total_return | 1.397144393892741 |
| d009_minus_d001_cumulative_net_pp | -0.886341011818661 |
| d009_minus_d001_cost_0_cumulative_net_pp | -0.9319437721406616 |
| regime_on_share | 0.3770491803278688 |
| composite_mean | -0.03428530665464613 |
| composite_std | 0.40416182915908916 |
| composite_positive_share | 0.39473684210526316 |
| global_risk_avg_score | 0.23811249262650716 |
| usd_fx_avg_score | 0.055982348313387324 |
| us_rates_avg_score | -0.5002514470306956 |
| inflation_avg_score | -0.09127345214730313 |
| growth_avg_score | 0.12600352496487346 |
| return_2025_contribution_share | nan |
| d001_trade_quarter_overlap_jaccard | 0.17391304347826086 |
| d009_on_d001_off_quarter_count | 13 |
| d009_off_d001_on_quarter_count | 4 |
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
| 2015.0 | 0.0 | 0.1650129244213383 | 0.0 | 0.0 | 0.0 |
| 2017.0 | 0.09401472235486108 | 0.316759538729966 | 0.0 | 0.0 | 0.09401472235486108 |
| 2018.0 | -0.03586254487531926 | -0.08401784948302471 | 0.0 | 0.0 | -0.03586254487531926 |
| 2019.0 | 0.02774934830525999 | 0.1701948593009439 | 0.0 | 0.0277493483052602 | -2.0816681711721685e-16 |
| 2020.0 | 0.46309904044504946 | 0.525128742931184 | 0.0 | 0.2461360848272729 | 0.21696295561777657 |
| 2021.0 | -0.12652033124281192 | 0.13170240063376548 | 0.0 | -0.035316520549102 | -0.09120381069370992 |

## Subperiod Breakdown

| period | start | end | v1_net_total_return | v1_cost_0_total_return | v1_annualized_return | v1_cost_0_annualized_return | v1_max_drawdown | v1_cost_0_max_drawdown | v1_trade_count | v1_cost_0_trade_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2010-2017 | 2010-01-04 | 2017-12-31 | 0.09401472235486108 | 0.10111100738801637 | 0.047196502772218984 | 0.050677239382894035 | -0.11120123654025105 | -0.10825712142713284 | 10 | 10 |
| 2018-2026 | 2018-01-01 | 2026-05-04 | 0.2831451821648361 | 0.3292457279399186 | 0.06579314329902952 | 0.07545142672505678 | -0.3392346174957135 | -0.3393494236202602 | 55 | 55 |

## Verdict Summary

| hypothesis | description | value | threshold | verdict | passes |
| --- | --- | --- | --- | --- | --- |
| scheme_c_is_sharpe_band | D015 pre-registered OOS Sharpe band applied to this isolated D013 trading window | 0.3402423163997201 | 0.3 | ACCEPTABLE | True |
