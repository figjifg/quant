# D008 Subperiod Metrics Summary

## Metadata

| key | value |
| --- | --- |
| subperiod | scheme_b_oos |
| trading_start | 2020-01-01 |
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
| factor_macro_gate_mcap | 1.2259897517614262 | -0.2367345977471278 | 3 | 0.13846285651058654 | 0.17574643406771914 | 0.7878558517849279 | 60 | 0.05439774398210909 |
| kospi_buy_and_hold | 6.2615186982553865 | -0.34485340853513247 | 6 | 0.3789111485704517 | 0.2339131885287381 | 1.6198793704353247 | 0 | 0.0 |
| cash | 0.0 | 0.0 | 0 | 0.0 | 0.0 | nan | 0 | 0.0 |

## D001 Diagnostics

| metric | value |
| --- | ---: |
| c014_v11_cumulative_net_total_return | 1.1136051550981834 |
| c014_v11_cost_0_cumulative_net_total_return | 1.483915813335873 |
| d001_minus_c014_v11_cumulative_net_pp | 0.11238459666324285 |
| d001_minus_c014_v11_cost_0_cumulative_net_pp | -0.16951496813904887 |
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
| c014_trade_overlap_jaccard | 0.24489795918367346 |

## Quarterly Year Breakdown

| year | factor_macro_gate_mcap_net_total_return | kospi_buy_and_hold_net_total_return | cash_net_total_return |
| --- | --- | --- | --- |
| 2020.0 | 0.24613608482727267 | 0.5251287429311826 | 0.0 |
| 2021.0 | -0.03531652054910184 | 0.13170240063376615 | 0.0 |
| 2022.0 | 0.0 | -0.1844240539579347 | 0.0 |
| 2023.0 | -0.017729397197116303 | 0.3279894204214897 | 0.0 |
| 2024.0 | 0.04224721797916264 | 0.034981455283805696 | 0.0 |
| 2025.0 | 0.7666554035490463 | 1.0470047808035559 | 0.0 |
| 2026.0 | 0.0 | 0.7344109727369723 | 0.0 |

## Subperiod Breakdown

| period | start | end | v1_net_total_return | v1_cost_0_total_return | v1_annualized_return | v1_cost_0_annualized_return | v1_max_drawdown | v1_cost_0_max_drawdown | v1_trade_count | v1_cost_0_trade_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2010-2017 | 2010-01-04 | 2017-12-31 | nan | nan | nan | nan | nan | nan | 0 | 0 |
| 2018-2026 | 2018-01-01 | 2026-05-04 | 1.2259897517614262 | 1.314400845196824 | 0.13846285651058654 | 0.14567158740171737 | -0.2367345977471278 | -0.22938446576201033 | 60 | 60 |

## Verdict Summary

| hypothesis | description | value | threshold | verdict | passes |
| --- | --- | --- | --- | --- | --- |
| scheme_b_oos_sharpe_band | D008 pre-registered OOS Sharpe band applied to this isolated trading window | 0.7878558517849279 | 0.3 | STRONG | True |
