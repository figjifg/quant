# D008 Subperiod Metrics Summary

## Metadata

| key | value |
| --- | --- |
| subperiod | scheme_a_oos |
| trading_start | 2021-01-01 |
| trading_end | 2026-05-04 |
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
| factor_macro_gate_mcap | 0.7355383127242421 | -0.2367345977471278 | 2 | 0.11215372298011306 | 0.18506169545463655 | 0.6060342347160915 | 55 | 0.03993165275567582 |
| kospi_buy_and_hold | 3.6387279185024477 | -0.26909466778914926 | 5 | 0.34427155986356395 | 0.2234044330250718 | 1.5410238516839445 | 0 | 0.0 |
| cash | 0.0 | 0.0 | 0 | 0.0 | 0.0 | nan | 0 | 0.0 |

## D001 Diagnostics

| metric | value |
| --- | ---: |
| c014_v11_cumulative_net_total_return | 1.1136051550981834 |
| c014_v11_cost_0_cumulative_net_total_return | 1.483915813335873 |
| d001_minus_c014_v11_cumulative_net_pp | -0.3780668423739413 |
| d001_minus_c014_v11_cost_0_cumulative_net_pp | -0.6864485491114152 |
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
| c014_trade_overlap_jaccard | 0.22448979591836735 |

## Quarterly Year Breakdown

| year | factor_macro_gate_mcap_net_total_return | kospi_buy_and_hold_net_total_return | cash_net_total_return |
| --- | --- | --- | --- |
| 2021.0 | -0.03531652054910228 | 0.13170240063376726 | 0.0 |
| 2022.0 | 0.0 | -0.18442405395793326 | 0.0 |
| 2023.0 | -0.017729397197116303 | 0.32798942042148993 | 0.0 |
| 2024.0 | 0.04224721797916309 | 0.03498145528380325 | 0.0 |
| 2025.0 | 0.766655403549046 | 1.0470047808035554 | 0.0 |
| 2026.0 | 0.0 | 0.7344109727369705 | 0.0 |

## Subperiod Breakdown

| period | start | end | v1_net_total_return | v1_cost_0_total_return | v1_annualized_return | v1_cost_0_annualized_return | v1_max_drawdown | v1_cost_0_max_drawdown | v1_trade_count | v1_cost_0_trade_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2010-2017 | 2010-01-04 | 2017-12-31 | nan | nan | nan | nan | nan | nan | 0 | 0 |
| 2018-2026 | 2018-01-01 | 2026-05-04 | 0.7355383127242421 | 0.7974672642244578 | 0.11215372298011306 | 0.11969738822764353 | -0.2367345977471278 | -0.22938446576200988 | 55 | 55 |

## Verdict Summary

| hypothesis | description | value | threshold | verdict | passes |
| --- | --- | --- | --- | --- | --- |
| scheme_a_oos_sharpe_band | D008 pre-registered OOS Sharpe band applied to this isolated trading window | 0.6060342347160915 | 0.3 | STRONG | True |
