# D010 84mo Metrics Summary

## Metadata

| key | value |
| --- | --- |
| panels_used | ["research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv"] |
| period_start | 2010-01-04 |
| period_end | 2026-05-04 |
| excluded_years | [2016] |
| macro_gate | D009 ten variables transformed to 84-month rolling z-scores, sign-adjusted, averaged by five equal-weight factor blocks; ON when composite >= 0 |
| z_score_warmup | rows with fewer than 84 monthly observations have NaN composite and regime OFF |
| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |
| selection | top 5 by signal-date market cap, equal weight when factor macro gate ON |
| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |
| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |
| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |
| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |

## Variant Metrics

| variant | cumulative_net_total_return | max_drawdown | positive_years | annualized_return | annualized_volatility | sharpe | trade_count | cost_paid_total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| factor_macro_gate_mcap | 1.2940096492430464 | -0.34232184209223526 | 3 | 0.056991569288500576 | 0.12771997737456395 | 0.4462228263739947 | 55 | 0.04741202675291962 |
| kospi_buy_and_hold | 20.095177626449328 | -0.34485340853513224 | 14 | 0.2257327915799301 | 0.18914309081113953 | 1.1934498406041465 | 0 | 0.0 |
| cash | 0.0 | 0.0 | 0 | 0.0 | 0.0 | nan | 0 | 0.0 |

## D009 Diagnostics

| metric | value |
| --- | ---: |
| cost_0_cumulative_net_total_return | 1.3777042738173986 |
| d001_cumulative_net_total_return | 1.2906841868750734 |
| d001_cost_0_cumulative_net_total_return | 1.397144393892741 |
| d009_minus_d001_cumulative_net_pp | 0.003325462367973042 |
| d009_minus_d001_cost_0_cumulative_net_pp | -0.01944012007534246 |
| regime_on_share | 0.18032786885245902 |
| composite_mean | -0.06798745973362916 |
| composite_std | 0.43018260252097235 |
| composite_positive_share | 0.36666666666666664 |
| global_risk_avg_score | 0.25239844335209954 |
| usd_fx_avg_score | -0.00044962788033327353 |
| us_rates_avg_score | -0.5300900876946228 |
| inflation_avg_score | -0.11304191115640093 |
| growth_avg_score | 0.05124588471111173 |
| return_2025_contribution_share | 0.43818005906176555 |
| d001_trade_quarter_overlap_jaccard | 0.25 |
| d009_on_d001_off_quarter_count | 6 |
| d009_off_d001_on_quarter_count | 9 |
| vix_60d_vs_240d_z_mean | 0.061943013037210296 |
| vix_60d_vs_240d_z_std | 1.0406267208682118 |
| vix_60d_vs_240d_z_positive_share | 0.36666666666666664 |
| baa10y_spread_level_z_mean | -0.5667398997414093 |
| baa10y_spread_level_z_std | 0.8924854697107786 |
| baa10y_spread_level_z_positive_share | 0.1 |
| usdkrw_yoy_z_mean | 0.3147012386119118 |
| usdkrw_yoy_z_std | 1.0135806116930814 |
| usdkrw_yoy_z_positive_share | 0.6666666666666666 |
| dxy_yoy_z_mean | -0.3138019828512453 |
| dxy_yoy_z_std | 0.8614324101152447 |
| dxy_yoy_z_positive_share | 0.3333333333333333 |
| us_10y_real_level_z_mean | 0.28929049816504465 |
| us_10y_real_level_z_std | 1.5129953233074438 |
| us_10y_real_level_z_positive_share | 0.6333333333333333 |
| us_2_10_curve_z_mean | -0.7708896772242008 |
| us_2_10_curve_z_std | 0.9713732501960128 |
| us_2_10_curve_z_positive_share | 0.3 |
| brent_yoy_z_mean | 0.014955701232195254 |
| brent_yoy_z_std | 1.1307195893841884 |
| brent_yoy_z_positive_share | 0.36666666666666664 |
| us_breakeven_level_z_mean | 0.21112812108060655 |
| us_breakeven_level_z_std | 1.2852698182561386 |
| us_breakeven_level_z_positive_share | 0.7333333333333333 |
| kr_cli_value_z_mean | -0.14697231609688152 |
| kr_cli_value_z_std | 1.1905517320473011 |
| kr_cli_value_z_positive_share | 0.3 |
| kr_exports_yoy_z_mean | 0.24946408551910496 |
| kr_exports_yoy_z_std | 1.5227532059522226 |
| kr_exports_yoy_z_positive_share | 0.5333333333333333 |

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
| 2018.0 | 0.0 | -0.08401784948302582 | 0.0 | 0.0 | 0.0 |
| 2019.0 | 0.0 | 0.17019485930094325 | 0.0 | 0.0277493483052602 | -0.0277493483052602 |
| 2020.0 | 0.24613608482727267 | 0.5251287429311848 | 0.0 | 0.2461360848272729 | -2.220446049250313e-16 |
| 2021.0 | -0.12419945981131209 | 0.13170240063376726 | 0.0 | -0.035316520549102 | -0.08888293926221008 |
| 2022.0 | -0.09716827644733184 | -0.18442405395793493 | 0.0 | 0.0 | -0.09716827644733184 |
| 2023.0 | 0.0 | 0.3279894204214897 | 0.0 | -0.0177293971971159 | 0.0177293971971159 |
| 2024.0 | -0.07976588247723282 | 0.034981455283805474 | 0.0 | 0.0422472179791628 | -0.12201310045639563 |
| 2025.0 | 0.5670092245318126 | 1.047004780803555 | 0.0 | 0.7666554035490463 | -0.1996461790172337 |
| 2026.0 | 0.5621484118981521 | 0.7344109727369705 | 0.0 | 0.0 | 0.5621484118981521 |

## Subperiod Breakdown

| period | start | end | v1_net_total_return | v1_cost_0_total_return | v1_annualized_return | v1_cost_0_annualized_return | v1_max_drawdown | v1_cost_0_max_drawdown | v1_trade_count | v1_cost_0_trade_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2010-2017 | 2010-01-04 | 2017-12-31 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0 |
| 2018-2026 | 2018-01-01 | 2026-05-04 | 1.2940096492430464 | 1.3777042738173986 | 0.1077332915748479 | 0.11263558665204831 | -0.34232184209223526 | -0.3292315947597916 | 55 | 55 |

## 2010-2014 Warmup Diagnosis

| period | start | end | trade_count | net_total_return | cost_0_total_return |
| --- | --- | --- | --- | --- | --- |
| 2010-2014 | 2010-01-04 | 2014-12-31 | 0 | 0.0 | 0.0 |

## Verdict Summary

| window | hypothesis | description | value | threshold | passes |
| --- | --- | --- | --- | --- | --- |
| 84 | H1 | 60-month D010 reproduces D009 Sharpe 0.4144 | 0.4462228263739947 | 0.4144 | <NA> |
| 84 | H7 | Window Sharpe is at least 0.40 for plateau count | 0.4462228263739947 | 0.4 | True |
| 84 | H8 | 2010-2014 warmup-artifact trade count and return diagnostic | 0.0 | >0 for 36mo/48mo | True |
| 84 | H9 | ON share, max DD, and composite distribution are descriptive checks | 0.18032786885245902 |  | <NA> |
