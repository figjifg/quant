# D008 Subperiod Metrics Summary

## Metadata

| key | value |
| --- | --- |
| subperiod | scheme_c_is |
| trading_start | 2015-01-01 |
| trading_end | 2021-12-31 |
| macro_gate | frozen D001 factor aggregation; only trading window is restricted |
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
| factor_macro_gate_mcap | 0.27325635828179307 | -0.13801786499317925 | 2 | 0.04207825889450478 | 0.09311959997073886 | 0.4518732781039342 | 20 | 0.014882533818039608 |
| kospi_buy_and_hold | 1.857472708992793 | -0.34485340853513236 | 5 | 0.19618373364893626 | 0.16753243253189778 | 1.1710194299935526 | 0 | 0.0 |
| cash | 0.0 | 0.0 | 0 | 0.0 | 0.0 | nan | 0 | 0.0 |

## D001 Diagnostics

| metric | value |
| --- | ---: |
| c014_v11_cumulative_net_total_return | 1.1136051550981834 |
| c014_v11_cost_0_cumulative_net_total_return | 1.483915813335873 |
| d001_minus_c014_v11_cumulative_net_pp | -0.8403487968163903 |
| d001_minus_c014_v11_cost_0_cumulative_net_pp | -1.1940035891078398 |
| regime_on_share | 0.22950819672131148 |
| composite_mean | -0.22008966303812005 |
| composite_std | 0.5317946006029692 |
| composite_positive_share | 0.4375 |
| global_risk_avg_score | -0.16208804642358676 |
| usd_fx_avg_score | 0.04816539688195462 |
| us_rates_avg_score | -0.7420741808117228 |
| inflation_avg_score | -0.009818070624069405 |
| commodity_avg_score | -0.24558840573852606 |
| korea_avg_score | -0.2091346715127701 |
| c014_trade_overlap_jaccard | 0.08163265306122448 |

## Quarterly Year Breakdown

| year | factor_macro_gate_mcap_net_total_return | kospi_buy_and_hold_net_total_return | cash_net_total_return |
| --- | --- | --- | --- |
| 2015.0 | 0.0 | 0.1650129244213383 | 0.0 |
| 2017.0 | 0.0 | 0.316759538729966 | 0.0 |
| 2018.0 | 0.0 | -0.08401784948302471 | 0.0 |
| 2019.0 | 0.027749348305260213 | 0.1701948593009439 | 0.0 |
| 2020.0 | 0.2461360848272729 | 0.525128742931184 | 0.0 |
| 2021.0 | -0.03531652054910206 | 0.13170240063376548 | 0.0 |

## Subperiod Breakdown

| period | start | end | v1_net_total_return | v1_cost_0_total_return | v1_annualized_return | v1_cost_0_annualized_return | v1_max_drawdown | v1_cost_0_max_drawdown | v1_trade_count | v1_cost_0_trade_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2010-2017 | 2010-01-04 | 2017-12-31 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0 |
| 2018-2026 | 2018-01-01 | 2026-05-04 | 0.27325635828179307 | 0.2899122242280332 | 0.06368783846311854 | 0.06722687832144136 | -0.13801786499317925 | -0.1380683948764938 | 20 | 20 |

## Verdict Summary

| hypothesis | description | value | threshold | verdict | passes |
| --- | --- | --- | --- | --- | --- |
| scheme_c_is_sharpe_band | D008 pre-registered OOS Sharpe band applied to this isolated trading window | 0.4518732781039342 | 0.3 | STRONG | True |
