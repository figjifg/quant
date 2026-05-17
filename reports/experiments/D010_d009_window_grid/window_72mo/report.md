# D010 72mo Metrics Summary

## Metadata

| key | value |
| --- | --- |
| panels_used | ["research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv"] |
| period_start | 2010-01-04 |
| period_end | 2026-05-04 |
| excluded_years | [2016] |
| macro_gate | D009 ten variables transformed to 72-month rolling z-scores, sign-adjusted, averaged by five equal-weight factor blocks; ON when composite >= 0 |
| z_score_warmup | rows with fewer than 72 monthly observations have NaN composite and regime OFF |
| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |
| selection | top 5 by signal-date market cap, equal weight when factor macro gate ON |
| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |
| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |
| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |
| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |

## Variant Metrics

| variant | cumulative_net_total_return | max_drawdown | positive_years | annualized_return | annualized_volatility | sharpe | trade_count | cost_paid_total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| factor_macro_gate_mcap | 1.2126283827568458 | -0.3423218420922356 | 3 | 0.05444602530833742 | 0.13039149918882045 | 0.417558089653482 | 60 | 0.048942417692015024 |
| kospi_buy_and_hold | 20.095177626449328 | -0.34485340853513224 | 14 | 0.2257327915799301 | 0.18914309081113953 | 1.1934498406041465 | 0 | 0.0 |
| cash | 0.0 | 0.0 | 0 | 0.0 | 0.0 | nan | 0 | 0.0 |

## D009 Diagnostics

| metric | value |
| --- | ---: |
| cost_0_cumulative_net_total_return | 1.3008358872632821 |
| d001_cumulative_net_total_return | 1.2906841868750734 |
| d001_cost_0_cumulative_net_total_return | 1.397144393892741 |
| d009_minus_d001_cumulative_net_pp | -0.07805580411822755 |
| d009_minus_d001_cost_0_cumulative_net_pp | -0.09630850662945889 |
| regime_on_share | 0.19672131147540983 |
| composite_mean | -0.07519914139633048 |
| composite_std | 0.42151326641190784 |
| composite_positive_share | 0.35294117647058826 |
| global_risk_avg_score | 0.2310026072639997 |
| usd_fx_avg_score | 0.07359950050725846 |
| us_rates_avg_score | -0.5365538260211328 |
| inflation_avg_score | -0.20039344212479493 |
| growth_avg_score | 0.056349453393017154 |
| return_2025_contribution_share | 0.467586964476906 |
| d001_trade_quarter_overlap_jaccard | 0.23809523809523808 |
| d009_on_d001_off_quarter_count | 7 |
| d009_off_d001_on_quarter_count | 9 |
| vix_60d_vs_240d_z_mean | 0.13099585005197947 |
| vix_60d_vs_240d_z_std | 1.0628607459714248 |
| vix_60d_vs_240d_z_positive_share | 0.38235294117647056 |
| baa10y_spread_level_z_mean | -0.5930010645799788 |
| baa10y_spread_level_z_std | 1.0151491482160864 |
| baa10y_spread_level_z_positive_share | 0.11764705882352941 |
| usdkrw_yoy_z_mean | 0.16557231956988006 |
| usdkrw_yoy_z_std | 1.0212529682288523 |
| usdkrw_yoy_z_positive_share | 0.5588235294117647 |
| dxy_yoy_z_mean | -0.312771320584397 |
| dxy_yoy_z_std | 0.859666751165742 |
| dxy_yoy_z_positive_share | 0.35294117647058826 |
| us_10y_real_level_z_mean | 0.24538992937639084 |
| us_10y_real_level_z_std | 1.565972831035822 |
| us_10y_real_level_z_positive_share | 0.6470588235294118 |
| us_2_10_curve_z_mean | -0.8277177226658745 |
| us_2_10_curve_z_std | 1.063571754691958 |
| us_2_10_curve_z_positive_share | 0.3235294117647059 |
| brent_yoy_z_mean | 0.22537475807959684 |
| brent_yoy_z_std | 1.1767017196939598 |
| brent_yoy_z_positive_share | 0.38235294117647056 |
| us_breakeven_level_z_mean | 0.17541212616999305 |
| us_breakeven_level_z_std | 1.2200015318665898 |
| us_breakeven_level_z_positive_share | 0.7058823529411765 |
| kr_cli_value_z_mean | -0.09289313477094596 |
| kr_cli_value_z_std | 1.1254293420851949 |
| kr_cli_value_z_positive_share | 0.4411764705882353 |
| kr_exports_yoy_z_mean | 0.20559204155698027 |
| kr_exports_yoy_z_std | 1.3721143695760458 |
| kr_exports_yoy_z_positive_share | 0.5294117647058824 |

## Quarterly Year Breakdown

| year | factor_macro_gate_mcap_net_total_return | kospi_buy_and_hold_net_total_return | cash_net_total_return | d001_factor_macro_gate_mcap_net_total_return | d009_minus_d001_factor_macro_gate_mcap_return |
| --- | --- | --- | --- | --- | --- |
| 2010.0 | 0.0 | 0.3293489579737485 | 0.0 | 0.0 | 0.0 |
| 2011.0 | 0.0 | 0.004079681302652238 | 0.0 | 0.0 | 0.0 |
| 2012.0 | 0.0 | 0.18731018909741426 | 0.0 | 0.0 | 0.0 |
| 2013.0 | 0.0 | 0.06125736750042954 | 0.0 | 0.0 | 0.0 |
| 2014.0 | 0.0 | 0.05769800682302639 | 0.0 | 0.0 | 0.0 |
| 2015.0 | 0.0 | 0.16501292442133764 | 0.0 | 0.0 | 0.0 |
| 2017.0 | 0.0 | 0.31675953872996554 | 0.0 | 0.0 | 0.0 |
| 2018.0 | -0.03586254487531937 | -0.08401784948302582 | 0.0 | 0.0 | -0.03586254487531937 |
| 2019.0 | 0.0 | 0.17019485930094325 | 0.0 | 0.0277493483052602 | -0.0277493483052602 |
| 2020.0 | 0.24613608482727267 | 0.5251287429311848 | 0.0 | 0.2461360848272729 | -2.220446049250313e-16 |
| 2021.0 | -0.12419945981131286 | 0.13170240063376726 | 0.0 | -0.035316520549102 | -0.08888293926221086 |
| 2022.0 | -0.09716827644733184 | -0.18442405395793493 | 0.0 | 0.0 | -0.09716827644733184 |
| 2023.0 | 0.0 | 0.3279894204214897 | 0.0 | -0.0177293971971159 | 0.0177293971971159 |
| 2024.0 | -0.07976588247723293 | 0.034981455283805474 | 0.0 | 0.0422472179791628 | -0.12201310045639574 |
| 2025.0 | 0.5670092245318132 | 1.047004780803555 | 0.0 | 0.7666554035490463 | -0.19964617901723303 |
| 2026.0 | 0.5621484118981519 | 0.7344109727369705 | 0.0 | 0.0 | 0.5621484118981519 |

## Subperiod Breakdown

| period | start | end | v1_net_total_return | v1_cost_0_total_return | v1_annualized_return | v1_cost_0_annualized_return | v1_max_drawdown | v1_cost_0_max_drawdown | v1_trade_count | v1_cost_0_trade_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2010-2017 | 2010-01-04 | 2017-12-31 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0 |
| 2018-2026 | 2018-01-01 | 2026-05-04 | 1.2117406252526504 | 1.2983963628323605 | 0.10275920847115105 | 0.10799410064362291 | -0.3423218420922356 | -0.32923159475979136 | 60 | 60 |

## 2010-2014 Warmup Diagnosis

| period | start | end | trade_count | net_total_return | cost_0_total_return |
| --- | --- | --- | --- | --- | --- |
| 2010-2014 | 2010-01-04 | 2014-12-31 | 0 | 0.0 | 0.0 |

## Verdict Summary

| window | hypothesis | description | value | threshold | passes |
| --- | --- | --- | --- | --- | --- |
| 72 | H1 | 60-month D010 reproduces D009 Sharpe 0.4144 | 0.417558089653482 | 0.4144 | <NA> |
| 72 | H7 | Window Sharpe is at least 0.40 for plateau count | 0.417558089653482 | 0.4 | True |
| 72 | H8 | 2010-2014 warmup-artifact trade count and return diagnostic | 0.0 | >0 for 36mo/48mo | True |
| 72 | H9 | ON share, max DD, and composite distribution are descriptive checks | 0.19672131147540983 |  | <NA> |
