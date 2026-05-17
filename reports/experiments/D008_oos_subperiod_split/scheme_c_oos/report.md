# D008 Subperiod Metrics Summary

## Metadata

| key | value |
| --- | --- |
| subperiod | scheme_c_oos |
| trading_start | 2022-01-01 |
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
| factor_macro_gate_mcap | 0.7990753959134018 | -0.22305633883403742 | 2 | 0.1499835642943197 | 0.19268119702472777 | 0.7784027015104724 | 50 | 0.03741024740505952 |
| kospi_buy_and_hold | 3.0828170337150835 | -0.23481956191334674 | 4 | 0.3976043051853482 | 0.23542841582243818 | 1.6888543542901135 | 0 | 0.0 |
| cash | 0.0 | 0.0 | 0 | 0.0 | 0.0 | nan | 0 | 0.0 |

## D001 Diagnostics

| metric | value |
| --- | ---: |
| c014_v11_cumulative_net_total_return | 1.1136051550981834 |
| c014_v11_cost_0_cumulative_net_total_return | 1.483915813335873 |
| d001_minus_c014_v11_cumulative_net_pp | -0.31452975918478154 |
| d001_minus_c014_v11_cost_0_cumulative_net_pp | -0.6255378951582644 |
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
| c014_trade_overlap_jaccard | 0.20408163265306123 |

## Quarterly Year Breakdown

| year | factor_macro_gate_mcap_net_total_return | kospi_buy_and_hold_net_total_return | cash_net_total_return |
| --- | --- | --- | --- |
| 2022.0 | 0.0 | -0.18442405395793393 | 0.0 |
| 2023.0 | -0.01772939719711608 | 0.32798942042148904 | 0.0 |
| 2024.0 | 0.04224721797916309 | 0.0349814552838037 | 0.0 |
| 2025.0 | 0.766655403549046 | 1.0470047808035599 | 0.0 |
| 2026.0 | 0.0 | 0.7344109727369708 | 0.0 |

## Subperiod Breakdown

| period | start | end | v1_net_total_return | v1_cost_0_total_return | v1_annualized_return | v1_cost_0_annualized_return | v1_max_drawdown | v1_cost_0_max_drawdown | v1_trade_count | v1_cost_0_trade_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2010-2017 | 2010-01-04 | 2017-12-31 | nan | nan | nan | nan | nan | nan | 0 | 0 |
| 2018-2026 | 2018-01-01 | 2026-05-04 | 0.7990753959134018 | 0.8583779181776086 | 0.1499835642943197 | 0.15889269890792135 | -0.22305633883403742 | -0.2180930837979156 | 50 | 50 |

## Verdict Summary

| hypothesis | description | value | threshold | verdict | passes |
| --- | --- | --- | --- | --- | --- |
| scheme_c_oos_sharpe_band | D008 pre-registered OOS Sharpe band applied to this isolated trading window | 0.7784027015104724 | 0.3 | STRONG | True |
