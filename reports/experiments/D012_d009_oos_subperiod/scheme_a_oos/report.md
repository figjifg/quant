# D012 Subperiod Metrics Summary

## Metadata

| key | value |
| --- | --- |
| subperiod | scheme_a_oos |
| trading_start | 2021-01-01 |
| trading_end | 2026-05-04 |
| macro_gate | frozen D009 factor aggregation; only trading window is restricted |
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
| factor_macro_gate_mcap | 0.7484247679033653 | -0.33368186647060516 | 3 | 0.11374114145695469 | 0.2089219769451755 | 0.544419228269136 | 50 | 0.03456665422438476 |
| kospi_buy_and_hold | 3.6387279185024477 | -0.26909466778914926 | 5 | 0.34427155986356395 | 0.2234044330250718 | 1.5410238516839445 | 0 | 0.0 |
| cash | 0.0 | 0.0 | 0 | 0.0 | 0.0 | nan | 0 | 0.0 |

## D009 Diagnostics

| metric | value |
| --- | ---: |
| cost_0_cumulative_net_total_return | 0.8054510652908617 |
| d001_cumulative_net_total_return | 1.2906841868750734 |
| d001_cost_0_cumulative_net_total_return | 1.397144393892741 |
| d009_minus_d001_cumulative_net_pp | -0.542259418971708 |
| d009_minus_d001_cost_0_cumulative_net_pp | -0.5916933286018793 |
| regime_on_share | 0.26229508196721313 |
| composite_mean | -0.033479997767023525 |
| composite_std | 0.41738983159305604 |
| composite_positive_share | 0.42105263157894735 |
| global_risk_avg_score | 0.23811249262650716 |
| usd_fx_avg_score | 0.055982348313387324 |
| us_rates_avg_score | -0.5002514470306956 |
| inflation_avg_score | -0.09127345214730313 |
| growth_avg_score | 0.13003006940298645 |
| return_2025_contribution_share | 0.5003034070706502 |
| d001_trade_quarter_overlap_jaccard | 0.2 |
| d009_on_d001_off_quarter_count | 10 |
| d009_off_d001_on_quarter_count | 8 |
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
| kr_cli_value_z_mean | 0.05082155929730396 |
| kr_cli_value_z_std | 1.224207628490567 |
| kr_cli_value_z_positive_share | 0.4473684210526316 |
| kr_exports_yoy_z_mean | 0.20923857950866892 |
| kr_exports_yoy_z_std | 1.2657037838380627 |
| kr_exports_yoy_z_positive_share | 0.5263157894736842 |

## Quarterly Year Breakdown

| year | factor_macro_gate_mcap_net_total_return | kospi_buy_and_hold_net_total_return | cash_net_total_return | d001_factor_macro_gate_mcap_net_total_return | d009_minus_d001_factor_macro_gate_mcap_return |
| --- | --- | --- | --- | --- | --- |
| 2021.0 | -0.12419945981131286 | 0.13170240063376726 | 0.0 | -0.035316520549102 | -0.08888293926221086 |
| 2022.0 | -0.09716827644733173 | -0.18442405395793326 | 0.0 | 0.0 | -0.09716827644733173 |
| 2023.0 | 0.0 | 0.32798942042148993 | 0.0 | -0.0177293971971159 | 0.0177293971971159 |
| 2024.0 | 0.010394436376717442 | 0.03498145528380325 | 0.0 | 0.0422472179791628 | -0.03185278160244536 |
| 2025.0 | 0.37443946131811434 | 1.0470047808035554 | 0.0 | 0.7666554035490463 | -0.3922159422309319 |
| 2026.0 | 0.5621484118981519 | 0.7344109727369705 | 0.0 | 0.0 | 0.5621484118981519 |

## Subperiod Breakdown

| period | start | end | v1_net_total_return | v1_cost_0_total_return | v1_annualized_return | v1_cost_0_annualized_return | v1_max_drawdown | v1_cost_0_max_drawdown | v1_trade_count | v1_cost_0_trade_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2010-2017 | 2010-01-04 | 2017-12-31 | nan | nan | nan | nan | nan | nan | 0 | 0 |
| 2018-2026 | 2018-01-01 | 2026-05-04 | 0.7484247679033653 | 0.8054510652908617 | 0.11374114145695469 | 0.12065457608202879 | -0.33368186647060516 | -0.3249118089570775 | 50 | 50 |

## Verdict Summary

| hypothesis | description | value | threshold | verdict | passes |
| --- | --- | --- | --- | --- | --- |
| scheme_a_oos_sharpe_band | D012 pre-registered OOS Sharpe band applied to this isolated D009 trading window | 0.544419228269136 | 0.3 | STRONG | True |
