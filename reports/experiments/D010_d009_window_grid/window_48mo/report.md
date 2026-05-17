# D010 48mo Metrics Summary

## Metadata

| key | value |
| --- | --- |
| panels_used | ["research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv"] |
| period_start | 2010-01-04 |
| period_end | 2026-05-04 |
| excluded_years | [2016] |
| macro_gate | D009 ten variables transformed to 48-month rolling z-scores, sign-adjusted, averaged by five equal-weight factor blocks; ON when composite >= 0 |
| z_score_warmup | rows with fewer than 48 monthly observations have NaN composite and regime OFF |
| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |
| selection | top 5 by signal-date market cap, equal weight when factor macro gate ON |
| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |
| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |
| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |
| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |

## Variant Metrics

| variant | cumulative_net_total_return | max_drawdown | positive_years | annualized_return | annualized_volatility | sharpe | trade_count | cost_paid_total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| factor_macro_gate_mcap | 1.3080507154536813 | -0.34232184209223526 | 4 | 0.05742221753640253 | 0.13592670398238718 | 0.4224498634487824 | 75 | 0.06164249558805014 |
| kospi_buy_and_hold | 20.095177626449328 | -0.34485340853513224 | 14 | 0.2257327915799301 | 0.18914309081113953 | 1.1934498406041465 | 0 | 0.0 |
| cash | 0.0 | 0.0 | 0 | 0.0 | 0.0 | nan | 0 | 0.0 |

## D009 Diagnostics

| metric | value |
| --- | ---: |
| cost_0_cumulative_net_total_return | 1.4234154559881729 |
| d001_cumulative_net_total_return | 1.2906841868750734 |
| d001_cost_0_cumulative_net_total_return | 1.397144393892741 |
| d009_minus_d001_cumulative_net_pp | 0.017366528578607987 |
| d009_minus_d001_cost_0_cumulative_net_pp | 0.02627106209543184 |
| regime_on_share | 0.26229508196721313 |
| composite_mean | -0.010760422246329863 |
| composite_std | 0.4203574761432307 |
| composite_positive_share | 0.38095238095238093 |
| global_risk_avg_score | 0.159635385571069 |
| usd_fx_avg_score | -0.07399709186055758 |
| us_rates_avg_score | -0.4458654124116166 |
| inflation_avg_score | 0.13753054026514658 |
| growth_avg_score | 0.1688944672043093 |
| return_2025_contribution_share | 0.43347648362024893 |
| d001_trade_quarter_overlap_jaccard | 0.2608695652173913 |
| d009_on_d001_off_quarter_count | 10 |
| d009_off_d001_on_quarter_count | 8 |
| vix_60d_vs_240d_z_mean | 0.12026780245147964 |
| vix_60d_vs_240d_z_std | 1.0783995145521104 |
| vix_60d_vs_240d_z_positive_share | 0.42857142857142855 |
| baa10y_spread_level_z_mean | -0.4395385735936176 |
| baa10y_spread_level_z_std | 0.9898534037677251 |
| baa10y_spread_level_z_positive_share | 0.23809523809523808 |
| usdkrw_yoy_z_mean | 0.20534005576358602 |
| usdkrw_yoy_z_std | 1.0497921376106345 |
| usdkrw_yoy_z_positive_share | 0.5714285714285714 |
| dxy_yoy_z_mean | -0.05734587204247084 |
| dxy_yoy_z_std | 1.1588095101752431 |
| dxy_yoy_z_positive_share | 0.4523809523809524 |
| us_10y_real_level_z_mean | 0.34967726833194257 |
| us_10y_real_level_z_std | 1.3964927611843205 |
| us_10y_real_level_z_positive_share | 0.7142857142857143 |
| us_2_10_curve_z_mean | -0.5420535564912906 |
| us_2_10_curve_z_std | 1.2526073370886623 |
| us_2_10_curve_z_positive_share | 0.30952380952380953 |
| brent_yoy_z_mean | -0.012898515273296255 |
| brent_yoy_z_std | 1.3171596398844656 |
| brent_yoy_z_positive_share | 0.35714285714285715 |
| us_breakeven_level_z_mean | -0.2621625652569969 |
| us_breakeven_level_z_std | 1.242951258933112 |
| us_breakeven_level_z_positive_share | 0.38095238095238093 |
| kr_cli_value_z_mean | 0.19543945923500766 |
| kr_cli_value_z_std | 1.2932603586953348 |
| kr_cli_value_z_positive_share | 0.5 |
| kr_exports_yoy_z_mean | 0.1423494751736109 |
| kr_exports_yoy_z_std | 1.2298637885120265 |
| kr_exports_yoy_z_positive_share | 0.4523809523809524 |

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
| 2018.0 | -0.03586254487531926 | -0.08401784948302582 | 0.0 | 0.0 | -0.03586254487531926 |
| 2019.0 | -0.04651535835890075 | 0.17019485930094325 | 0.0 | 0.0277493483052602 | -0.07426470666416095 |
| 2020.0 | 0.24613608482727312 | 0.5251287429311848 | 0.0 | 0.2461360848272729 | 2.220446049250313e-16 |
| 2021.0 | -0.12419945981131231 | 0.13170240063376726 | 0.0 | -0.035316520549102 | -0.0888829392622103 |
| 2022.0 | -0.09716827644733184 | -0.18442405395793493 | 0.0 | 0.0 | -0.09716827644733184 |
| 2023.0 | 0.0 | 0.3279894204214897 | 0.0 | -0.0177293971971159 | 0.0177293971971159 |
| 2024.0 | -0.07976588247723293 | 0.034981455283805474 | 0.0 | 0.0422472179791628 | -0.12201310045639574 |
| 2025.0 | 0.5670092245318126 | 1.047004780803555 | 0.0 | 0.7666554035490463 | -0.1996461790172337 |
| 2026.0 | 0.5621484118981521 | 0.7344109727369705 | 0.0 | 0.0 | 0.5621484118981521 |

## Subperiod Breakdown

| period | start | end | v1_net_total_return | v1_cost_0_total_return | v1_annualized_return | v1_cost_0_annualized_return | v1_max_drawdown | v1_cost_0_max_drawdown | v1_trade_count | v1_cost_0_trade_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2010-2017 | 2010-01-04 | 2017-12-31 | 0.09401472235486108 | 0.10111100738801637 | 0.013174613461145235 | 0.014129268394949213 | -0.11120123654025105 | -0.10825712142713284 | 10 | 10 |
| 2018-2026 | 2018-01-01 | 2026-05-04 | 1.1088607174720866 | 1.1985485086976122 | 0.09630545381733846 | 0.10194655282241438 | -0.34232184209223526 | -0.32923159475979114 | 65 | 65 |

## 2010-2014 Warmup Diagnosis

| period | start | end | trade_count | net_total_return | cost_0_total_return |
| --- | --- | --- | --- | --- | --- |
| 2010-2014 | 2010-01-04 | 2014-12-31 | 0 | 0.0 | 0.0 |

## Verdict Summary

| window | hypothesis | description | value | threshold | passes |
| --- | --- | --- | --- | --- | --- |
| 48 | H1 | 60-month D010 reproduces D009 Sharpe 0.4144 | 0.4224498634487824 | 0.4144 | <NA> |
| 48 | H7 | Window Sharpe is at least 0.40 for plateau count | 0.4224498634487824 | 0.4 | True |
| 48 | H8 | 2010-2014 warmup-artifact trade count and return diagnostic | 0.0 | >0 for 36mo/48mo | False |
| 48 | H9 | ON share, max DD, and composite distribution are descriptive checks | 0.26229508196721313 |  | <NA> |
