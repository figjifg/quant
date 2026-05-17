# D001 Metrics Summary

## Metadata

| key | value |
| --- | --- |
| panels_used | ["research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv"] |
| period_start | 2010-01-04 |
| period_end | 2026-05-04 |
| excluded_years | [2016] |
| macro_gate | C014 eight raw variables transformed to 60-month rolling z-scores, sign-adjusted, averaged by six equal-weight factor blocks; ON when composite >= 0 |
| z_score_warmup | rows with fewer than 60 monthly observations have NaN composite and regime OFF |
| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |
| selection | top 5 by signal-date market cap, equal weight when factor macro gate ON |
| baselines | V2 cap-weighted KOSPI proxy buy-and-hold; V3 cash |
| c014_v11_reference | C014 v11 quarterly cumulative net +111.36%; cost-0 +148.39%; yearly columns read from C014 output files |
| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |
| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |
| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |
| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |

## Variant Metrics

| variant | cumulative_net_total_return | max_drawdown | positive_years | annualized_return | annualized_volatility | sharpe | trade_count | cost_paid_total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| factor_macro_gate_mcap | 1.2906841868750734 | -0.23673459774712757 | 4 | 0.05688921504561084 | 0.11748600765260132 | 0.48422119520674023 | 70 | 0.06251536919142661 |
| kospi_buy_and_hold | 20.095177626449328 | -0.34485340853513224 | 14 | 0.2257327915799301 | 0.18914309081113953 | 1.1934498406041465 | 0 | 0.0 |
| cash | 0.0 | 0.0 | 0 | 0.0 | 0.0 | nan | 0 | 0.0 |

## D001 Diagnostics

| metric | value |
| --- | ---: |
| c014_v11_cumulative_net_total_return | 1.1136051550981834 |
| c014_v11_cost_0_cumulative_net_total_return | 1.483915813335873 |
| d001_minus_c014_v11_cumulative_net_pp | 0.17707903177689 |
| d001_minus_c014_v11_cost_0_cumulative_net_pp | -0.08677141944313194 |
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
| c014_trade_overlap_jaccard | 0.2857142857142857 |

## Quarterly Year Breakdown

| year | factor_macro_gate_mcap_net_total_return | kospi_buy_and_hold_net_total_return | cash_net_total_return | c014_v11_macro_gate_mcap_net_total_return | d001_minus_c014_v11_macro_gate_mcap_return |
| --- | --- | --- | --- | --- | --- |
| 2010.0 | 0.0 | 0.3293489579737485 | 0.0 | 0.0 | 0.0 |
| 2011.0 | 0.0 | 0.004079681302652238 | 0.0 | 0.0 | 0.0 |
| 2012.0 | 0.0 | 0.18731018909741426 | 0.0 | 0.0262445529244228 | -0.0262445529244228 |
| 2013.0 | 0.0 | 0.06125736750042954 | 0.0 | -0.0281930988857549 | 0.0281930988857549 |
| 2014.0 | 0.0 | 0.05769800682302639 | 0.0 | -0.0783678455575046 | 0.0783678455575046 |
| 2015.0 | 0.0 | 0.16501292442133764 | 0.0 | -0.1587948571699793 | 0.1587948571699793 |
| 2017.0 | 0.0 | 0.31675953872996554 | 0.0 | 0.0940147223548615 | -0.0940147223548615 |
| 2018.0 | 0.0 | -0.08401784948302582 | 0.0 | -0.4425899844893092 | 0.4425899844893092 |
| 2019.0 | 0.027749348305260213 | 0.17019485930094325 | 0.0 | 0.1172567383378644 | -0.08950739003260419 |
| 2020.0 | 0.2461360848272729 | 0.5251287429311848 | 0.0 | 0.4630990404450497 | -0.2169629556177768 |
| 2021.0 | -0.03531652054910206 | 0.13170240063376726 | 0.0 | -0.1241994598113124 | 0.08888293926221034 |
| 2022.0 | 0.0 | -0.18442405395793493 | 0.0 | -0.0971682764473317 | 0.0971682764473317 |
| 2023.0 | -0.01772939719711597 | 0.3279894204214897 | 0.0 | 0.1401032102479011 | -0.15783260744501706 |
| 2024.0 | 0.042247217979162865 | 0.034981455283805474 | 0.0 | 0.0140818262535202 | 0.028165391725642665 |
| 2025.0 | 0.7666554035490463 | 1.047004780803555 | 0.0 | 0.766655403549046 | 2.220446049250313e-16 |
| 2026.0 | 0.0 | 0.7344109727369705 | 0.0 | 0.5621484118981521 | -0.5621484118981521 |

## Subperiod Breakdown

| period | start | end | v1_net_total_return | v1_cost_0_total_return | v1_annualized_return | v1_cost_0_annualized_return | v1_max_drawdown | v1_cost_0_max_drawdown | v1_trade_count | v1_cost_0_trade_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2010-2017 | 2010-01-04 | 2017-12-31 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0 |
| 2018-2026 | 2018-01-01 | 2026-05-04 | 1.2906841868750734 | 1.397144393892741 | 0.10753528692482495 | 0.11375257799603444 | -0.23673459774712757 | -0.22938446576201021 | 70 | 70 |

## Verdict Summary

| hypothesis | description | value | threshold | passes |
| --- | --- | --- | --- | --- |
| H1 | V1 cumulative net total return > 0 | 1.2906841868750734 | 0.0 | True |
| H2 | V1 cumulative net >= V2 cumulative net - 30pp | -18.804493439574255 | -0.3 | False |
| H3 | V1 positive in at least 2 of 2010, 2025, 2026 | 1.0 | 2.0 | False |
| H4 | V1 max drawdown improves on V2 by at least 5pp | 0.10811881078800467 | -0.05 | False |
| H5 | V1 positive in >= 8 of 16 years | 4.0 | 8.0 | False |
| H6 | V1 net / V1 cost-0 >= 0.7 | 0.9238015716320866 | 0.7 | True |
| H7 | D001 cumulative net improves on C014 v11 by >= 5pp | 0.17707903177689 | 0.05 | True |
| H8 | D001 V1 subperiod cumulative net is >= 0 in both 2010-2017 and 2018-2026 | 0.0 | 0.0 | True |
| H9 | Regime ON share and composite/block distributions are descriptive checks | 0.22950819672131148 |  | <NA> |
