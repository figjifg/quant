# D002 Metrics Summary

## Metadata

| key | value |
| --- | --- |
| panels_used | ["research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv"] |
| period_start | 2010-01-04 |
| period_end | 2026-05-04 |
| excluded_years | [2016] |
| macro_gate | C014 eight raw variables transformed to 24-month rolling z-scores, sign-adjusted, averaged by six equal-weight factor blocks; ON when composite >= 0 |
| z_score_warmup | rows with fewer than 24 monthly observations have NaN composite and regime OFF |
| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |
| selection | top 5 by signal-date market cap, equal weight when factor macro gate ON |
| baselines | V2 cap-weighted KOSPI proxy buy-and-hold; V3 cash |
| d001_reference | D001 quarterly cumulative net +129.07%; cost-0 +139.71%; 60-month z-score window |
| c014_v11_reference | C014 v11 quarterly cumulative net +111.36%; cost-0 +148.39%; yearly columns read from C014 output files |
| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |
| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |
| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |
| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |

## Variant Metrics

| variant | cumulative_net_total_return | max_drawdown | positive_years | annualized_return | annualized_volatility | sharpe | trade_count | cost_paid_total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| factor_macro_gate_mcap | 0.5345828561256147 | -0.3467179466668159 | 4 | 0.029000958087306516 | 0.13498073369502922 | 0.21485257409276107 | 95 | 0.05962952689071275 |
| kospi_buy_and_hold | 20.095177626449328 | -0.34485340853513224 | 14 | 0.2257327915799301 | 0.18914309081113953 | 1.1934498406041465 | 0 | 0.0 |
| cash | 0.0 | 0.0 | 0 | 0.0 | 0.0 | nan | 0 | 0.0 |

## D002 Diagnostics

| metric | value |
| --- | ---: |
| d001_cumulative_net_total_return | 1.2906841868750734 |
| d001_cost_0_cumulative_net_total_return | 1.397144393892741 |
| d002_minus_d001_cumulative_net_pp | -0.7561013307494586 |
| d002_minus_d001_cost_0_cumulative_net_pp | -0.7647785678647432 |
| c014_v11_cumulative_net_total_return | 1.1136051550981834 |
| c014_v11_cost_0_cumulative_net_total_return | 1.483915813335873 |
| d002_minus_c014_v11_cumulative_net_pp | -0.5790222989725686 |
| d002_minus_c014_v11_cost_0_cumulative_net_pp | -0.8515499873078751 |
| trade_count_2010_2014 | 5 |
| d001_trade_count_reference | 70 |
| d002_minus_d001_trade_count | 25 |
| regime_on_share | 0.3114754098360656 |
| composite_mean | -0.06823178233568707 |
| composite_std | 0.517366552037983 |
| composite_positive_share | 0.4318181818181818 |
| global_risk_avg_score | -0.18941267688669597 |
| usd_fx_avg_score | -0.06363226185357197 |
| us_rates_avg_score | -0.17484537864683294 |
| inflation_avg_score | -0.07487388044797988 |
| commodity_avg_score | 0.1573470015793716 |
| korea_avg_score | -0.06397349775841321 |
| c014_trade_overlap_jaccard | 0.3877551020408163 |

## Quarterly Year Breakdown

| year | factor_macro_gate_mcap_net_total_return | kospi_buy_and_hold_net_total_return | cash_net_total_return | d001_factor_macro_gate_mcap_net_total_return | d002_minus_d001_factor_macro_gate_mcap_return |
| --- | --- | --- | --- | --- | --- |
| 2010.0 | 0.0 | 0.3293489579737485 | 0.0 | 0.0 | 0.0 |
| 2011.0 | 0.0 | 0.004079681302652238 | 0.0 | 0.0 | 0.0 |
| 2012.0 | 0.0 | 0.18731018909741426 | 0.0 | 0.0 | 0.0 |
| 2013.0 | 0.0 | 0.06125736750042954 | 0.0 | 0.0 | 0.0 |
| 2014.0 | -0.04636892576731588 | 0.05769800682302639 | 0.0 | 0.0 | -0.04636892576731588 |
| 2015.0 | -0.13061155683433656 | 0.16501292442133764 | 0.0 | 0.0 | -0.13061155683433656 |
| 2017.0 | 0.0 | 0.31675953872996554 | 0.0 | 0.0 | 0.0 |
| 2018.0 | 0.0 | -0.08401784948302582 | 0.0 | 0.0 | 0.0 |
| 2019.0 | 0.11725673833786399 | 0.17019485930094325 | 0.0 | 0.0277493483052602 | 0.08950739003260379 |
| 2020.0 | 0.09045907919498974 | 0.5251287429311848 | 0.0 | 0.2461360848272729 | -0.15567700563228315 |
| 2021.0 | -0.03531652054910206 | 0.13170240063376726 | 0.0 | -0.035316520549102 | -6.245004513516506e-17 |
| 2022.0 | 0.0 | -0.18442405395793493 | 0.0 | 0.0 | 0.0 |
| 2023.0 | -0.017729397197115748 | 0.3279894204214897 | 0.0 | -0.0177293971971159 | 1.5265566588595902e-16 |
| 2024.0 | 0.04224721797916309 | 0.034981455283805474 | 0.0 | 0.0422472179791628 | 2.8449465006019636e-16 |
| 2025.0 | 0.567009224531813 | 1.047004780803555 | 0.0 | 0.7666554035490463 | -0.19964617901723325 |
| 2026.0 | 0.0 | 0.7344109727369705 | 0.0 | 0.0 | 0.0 |

## Subperiod Breakdown

| period | start | end | v1_net_total_return | v1_cost_0_total_return | v1_annualized_return | v1_cost_0_annualized_return | v1_max_drawdown | v1_cost_0_max_drawdown | v1_trade_count | v1_cost_0_trade_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2010-2017 | 2010-01-04 | 2017-12-31 | -0.17036748200004936 | -0.1622151006332977 | -0.026839402828928938 | -0.02545225769554227 | -0.24449845191773845 | -0.23958523545478305 | 15 | 15 |
| 2018-2026 | 2018-01-01 | 2026-05-04 | 0.8497139671250278 | 0.9484307096749232 | 0.07873457347771584 | 0.08566820820873966 | -0.3392346174957135 | -0.3393494236202601 | 80 | 80 |

## Verdict Summary

| hypothesis | description | value | threshold | passes |
| --- | --- | --- | --- | --- |
| H1 | V1 cumulative net total return > 0 | 0.5345828561256147 | 0.0 | True |
| H2 | V1 cumulative net >= V2 cumulative net - 30pp | -19.560594770323714 | -0.3 | False |
| H3 | V1 positive in at least 2 of 2010, 2025, 2026 | 1.0 | 2.0 | False |
| H4 | V1 max drawdown improves on V2 by at least 5pp | -0.0018645381316836351 | -0.05 | False |
| H5 | V1 positive in >= 8 of 16 years | 4.0 | 8.0 | False |
| H6 | V1 net / V1 cost-0 >= 0.7 | 0.8453696169564138 | 0.7 | True |
| H7 | D002 Sharpe >= 0.40 and 2010-2014 trade count > 0 | 0.21485257409276107 | 0.4 | False |
| H8 | D002 V1 subperiod cumulative net is >= 0 in both 2010-2017 and 2018-2026 | -0.17036748200004936 | 0.0 | False |
| H9 | Regime ON share and composite/block distributions are descriptive checks | 0.3114754098360656 |  | <NA> |
