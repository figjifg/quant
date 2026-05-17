# D015 Subperiod Metrics Summary

## Metadata

| key | value |
| --- | --- |
| subperiod | scheme_b_oos |
| trading_start | 2020-01-01 |
| trading_end | 2026-05-04 |
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
| factor_macro_gate_mcap | 2.321141335837856 | -0.3392346174957136 | 5 | 0.21472710689140206 | 0.24467313417616035 | 0.877608028418855 | 85 | 0.08517350691181312 |
| kospi_buy_and_hold | 6.2615186982553865 | -0.34485340853513247 | 6 | 0.3789111485704517 | 0.2339131885287381 | 1.6198793704353247 | 0 | 0.0 |
| cash | 0.0 | 0.0 | 0 | 0.0 | 0.0 | nan | 0 | 0.0 |

## D009 Diagnostics

| metric | value |
| --- | ---: |
| cost_0_cumulative_net_total_return | 2.5089586701558484 |
| d001_cumulative_net_total_return | 1.2906841868750734 |
| d001_cost_0_cumulative_net_total_return | 1.397144393892741 |
| d009_minus_d001_cumulative_net_pp | 1.0304571489627827 |
| d009_minus_d001_cost_0_cumulative_net_pp | 1.1118142762631074 |
| regime_on_share | 0.3770491803278688 |
| composite_mean | -0.03428530665464613 |
| composite_std | 0.40416182915908916 |
| composite_positive_share | 0.39473684210526316 |
| global_risk_avg_score | 0.23811249262650716 |
| usd_fx_avg_score | 0.055982348313387324 |
| us_rates_avg_score | -0.5002514470306956 |
| inflation_avg_score | -0.09127345214730313 |
| growth_avg_score | 0.12600352496487346 |
| return_2025_contribution_share | 0.24428035284940589 |
| d001_trade_quarter_overlap_jaccard | 0.34782608695652173 |
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
| 2020.0 | 0.4630990404450488 | 0.5251287429311826 | 0.0 | 0.2461360848272729 | 0.2169629556177759 |
| 2021.0 | -0.12419945981131242 | 0.13170240063376615 | 0.0 | -0.035316520549102 | -0.08888293926221041 |
| 2022.0 | -0.09716827644733184 | -0.1844240539579347 | 0.0 | 0.0 | -0.09716827644733184 |
| 2023.0 | 0.08224211251730695 | 0.3279894204214897 | 0.0 | -0.0177293971971159 | 0.09997150971442285 |
| 2024.0 | 0.04224721797916264 | 0.034981455283805696 | 0.0 | 0.0422472179791628 | -1.5959455978986625e-16 |
| 2025.0 | 0.5670092245318128 | 1.0470047808035559 | 0.0 | 0.7666554035490463 | -0.19964617901723347 |
| 2026.0 | 0.5621484118981517 | 0.7344109727369723 | 0.0 | 0.0 | 0.5621484118981517 |

## Subperiod Breakdown

| period | start | end | v1_net_total_return | v1_cost_0_total_return | v1_annualized_return | v1_cost_0_annualized_return | v1_max_drawdown | v1_cost_0_max_drawdown | v1_trade_count | v1_cost_0_trade_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2010-2017 | 2010-01-04 | 2017-12-31 | nan | nan | nan | nan | nan | nan | 0 | 0 |
| 2018-2026 | 2018-01-01 | 2026-05-04 | 2.321141335837856 | 2.5089586701558484 | 0.21472710689140206 | 0.22560473658113578 | -0.3392346174957136 | -0.3393494236202602 | 85 | 85 |

## Verdict Summary

| hypothesis | description | value | threshold | verdict | passes |
| --- | --- | --- | --- | --- | --- |
| scheme_b_oos_sharpe_band | D015 pre-registered OOS Sharpe band applied to this isolated D013 trading window | 0.877608028418855 | 0.3 | STRONG | True |
