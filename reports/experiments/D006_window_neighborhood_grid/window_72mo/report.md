# D006 72mo Metrics Summary

## Metadata

| key | value |
| --- | --- |
| panels_used | ["research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv"] |
| period_start | 2010-01-04 |
| period_end | 2026-05-04 |
| excluded_years | [2016] |
| macro_gate | D001 eight raw variables transformed to 72-month rolling z-scores, sign-adjusted, averaged by six equal-weight factor blocks; ON when composite >= 0 |
| z_score_warmup | rows with fewer than 72 monthly observations have NaN composite and regime OFF |
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
| factor_macro_gate_mcap | 1.1947792772228127 | -0.23673459774712757 | 4 | 0.05387604987188732 | 0.11326317729390425 | 0.4756713625654831 | 65 | 0.05733894259015339 |
| kospi_buy_and_hold | 20.095177626449328 | -0.34485340853513224 | 14 | 0.2257327915799301 | 0.18914309081113953 | 1.1934498406041465 | 0 | 0.0 |
| cash | 0.0 | 0.0 | 0 | 0.0 | 0.0 | nan | 0 | 0.0 |

## D006 Diagnostics

| metric | value |
| --- | ---: |
| cost_0_cumulative_net_total_return | 1.2893618637045297 |
| regime_on_share | 0.21311475409836064 |
| regime_on_share_complete_quarters | 0.4642857142857143 |
| composite_mean | -0.172155889429335 |
| composite_std | 0.4932325992929362 |
| composite_positive_share | 0.4642857142857143 |
| global_risk_avg_score | -0.06927715475368099 |
| usd_fx_avg_score | -0.052513252930337276 |
| us_rates_avg_score | -0.747566090599326 |
| inflation_avg_score | 0.006503334208626703 |
| commodity_avg_score | 0.014910807732148007 |
| korea_avg_score | -0.18499298023344066 |

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
| 2020.0 | 0.2461360848272729 | 0.5251287429311848 | 0.0 |
| 2021.0 | -0.03531652054910206 | 0.13170240063376726 | 0.0 |
| 2022.0 | 0.0 | -0.18442405395793493 | 0.0 |
| 2023.0 | -0.01772939719711597 | 0.3279894204214897 | 0.0 |
| 2024.0 | 0.042247217979162865 | 0.034981455283805474 | 0.0 |
| 2025.0 | 0.6885511907579549 | 1.047004780803555 | 0.0 |
| 2026.0 | 0.0 | 0.7344109727369705 | 0.0 |

## Subperiod Breakdown

| period | start | end | v1_net_total_return | v1_cost_0_total_return | v1_annualized_return | v1_cost_0_annualized_return | v1_max_drawdown | v1_cost_0_max_drawdown | v1_trade_count | v1_cost_0_trade_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2010-2017 | 2010-01-04 | 2017-12-31 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0 |
| 2018-2026 | 2018-01-01 | 2026-05-04 | 1.1947792772228127 | 1.2893618637045297 | 0.10171357684127114 | 0.1074564831320104 | -0.23673459774712757 | -0.22938446576201021 | 65 | 65 |

## 2010-2014 Warmup Diagnosis

| period | start | end | trade_count | net_total_return | cost_0_total_return |
| --- | --- | --- | --- | --- | --- |
| 2010-2014 | 2010-01-04 | 2014-12-31 | 0 | 0.0 | 0.0 |

## Verdict Summary

| window | hypothesis | description | value | threshold | passes |
| --- | --- | --- | --- | --- | --- |
| 72 | H1 | 60-month D006 reproduces D001 Sharpe 0.4842 | 0.4756713625654831 | 0.4842 | <NA> |
| 72 | H7 | Window Sharpe is at least 0.40 for plateau count | 0.4756713625654831 | 0.4 | True |
| 72 | H8 | 2010-2014 warmup-artifact trade count and return diagnostic | 0.0 | >0 for 36mo/48mo | True |
| 72 | H9 | ON share, max DD, and composite distribution are descriptive checks | 0.21311475409836064 |  | <NA> |
