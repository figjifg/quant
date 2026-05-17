# D007 Threshold 0.2 Metrics Summary

## Metadata

| key | value |
| --- | --- |
| panels_used | ["research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv"] |
| period_start | 2010-01-04 |
| period_end | 2026-05-04 |
| excluded_years | [2016] |
| macro_gate | D001 eight raw variables transformed to 60-month rolling z-scores, sign-adjusted, averaged by six equal-weight factor blocks; ON when composite >= 0.2 |
| z_score_warmup | rows with fewer than 60 monthly observations have NaN composite and regime OFF |
| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |
| selection | top 5 by signal-date market cap, equal weight when factor macro gate ON |
| baselines | V2 cap-weighted KOSPI proxy buy-and-hold; V3 cash |
| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |
| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |
| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |
| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |

## Variant Metrics

| variant | cumulative_net_total_return | max_drawdown | positive_years | annualized_return | annualized_volatility | sharpe | trade_count | cost_paid_total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| factor_macro_gate_mcap | 0.503614974972816 | -0.266477947631111 | 3 | 0.027601550056027824 | 0.09757966775803155 | 0.28286169332397637 | 45 | 0.030839611707989552 |
| kospi_buy_and_hold | 20.095177626449328 | -0.34485340853513224 | 14 | 0.2257327915799301 | 0.18914309081113953 | 1.1934498406041465 | 0 | 0.0 |
| cash | 0.0 | 0.0 | 0 | 0.0 | 0.0 | nan | 0 | 0.0 |

## D007 Diagnostics

| metric | value |
| --- | ---: |
| cost_0_cumulative_net_total_return | 0.5478772935349889 |
| regime_on_share | 0.14754098360655737 |
| regime_on_share_complete_quarters | 0.28125 |
| composite_mean | -0.22008966303812005 |
| composite_std | 0.5317946006029692 |
| composite_positive_share | 0.4375 |
| global_risk_avg_score | -0.16208804642358676 |
| usd_fx_avg_score | 0.04816539688195462 |
| us_rates_avg_score | -0.7420741808117228 |
| inflation_avg_score | -0.009818070624069405 |
| commodity_avg_score | -0.24558840573852606 |
| korea_avg_score | -0.2091346715127701 |

## Quarterly Year Breakdown

| year | factor_macro_gate_mcap_net_total_return | kospi_buy_and_hold_net_total_return | cash_net_total_return |
| --- | --- | --- | --- |
| 2010.0 | 0.0 | 0.3293489579737485 | 0.0 |
| 2011.0 | 0.0 | 0.004079681302652238 | 0.0 |
| 2012.0 | 0.0 | 0.18731018909741426 | 0.0 |
| 2013.0 | 0.0 | 0.06125736750042954 | 0.0 |
| 2014.0 | 0.0 | 0.05769800682302639 | 0.0 |
| 2015.0 | 0.0 | 0.16501292442133764 | 0.0 |
| 2017.0 | 0.0 | 0.31675953872996554 | 0.0 |
| 2018.0 | 0.0 | -0.08401784948302582 | 0.0 |
| 2019.0 | 0.027749348305260213 | 0.17019485930094325 | 0.0 |
| 2020.0 | 0.0 | 0.5251287429311848 | 0.0 |
| 2021.0 | -0.03531652054910206 | 0.13170240063376726 | 0.0 |
| 2022.0 | 0.0 | -0.18442405395793493 | 0.0 |
| 2023.0 | -0.05600706330602501 | 0.3279894204214897 | 0.0 |
| 2024.0 | 0.010394436376717886 | 0.034981455283805474 | 0.0 |
| 2025.0 | 0.5670092245318132 | 1.047004780803555 | 0.0 |
| 2026.0 | 0.0 | 0.7344109727369705 | 0.0 |

## Subperiod Breakdown

| period | start | end | v1_net_total_return | v1_cost_0_total_return | v1_annualized_return | v1_cost_0_annualized_return | v1_max_drawdown | v1_cost_0_max_drawdown | v1_trade_count | v1_cost_0_trade_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2010-2017 | 2010-01-04 | 2017-12-31 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0 |
| 2018-2026 | 2018-01-01 | 2026-05-04 | 0.503614974972816 | 0.5478772935349889 | 0.051545538316305484 | 0.055311658827009946 | -0.266477947631111 | -0.26179350954595537 | 45 | 45 |

## Verdict Summary

| threshold | hypothesis | description | value | threshold_value | passes |
| --- | --- | --- | --- | --- | --- |
| 0.2 | H1 | Threshold 0.0 reproduces D001 Sharpe 0.4842 | 0.28286169332397637 | 0.4842 | <NA> |
| 0.2 | H7 | Threshold Sharpe is at least 0.40 for plateau count | 0.28286169332397637 | 0.4 | False |
| 0.2 | H8 | ON share, trade count, max DD, and subperiod returns are descriptive checks | 0.14754098360655737 |  | <NA> |
