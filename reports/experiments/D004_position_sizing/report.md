# D004 Metrics Summary

## Metadata

| key | value |
| --- | --- |
| panels_used | ["research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv"] |
| period_start | 2010-01-04 |
| period_end | 2026-05-04 |
| excluded_years | [2016] |
| macro_gate | D001 factor composite preserved; exposure = clip(composite, 0, 1.0) / 1.0 |
| sizing | per-stock target weight is 0.20 * exposure_scalar for five top-market-cap stocks; cash return is 0 |
| z_score_warmup | rows with fewer than 60 monthly observations have NaN composite and exposure 0 |
| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |
| selection | top 5 by signal-date market cap, D001 carrier unchanged |
| baselines | V2 cap-weighted KOSPI proxy buy-and-hold; V3 cash |
| d001_reference | D001 quarterly cumulative net +129.07%; cost-0 +139.71%; 60-month z-score window |
| c014_v11_reference | C014 v11 quarterly cumulative net +111.36%; cost-0 +148.39% |
| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |
| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |
| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |
| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |

## Variant Metrics

| variant | cumulative_net_total_return | max_drawdown | positive_years | annualized_return | annualized_volatility | sharpe | trade_count | cost_paid_total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| factor_macro_sized_mcap | 0.2114258147646717 | -0.12098009674398247 | 4 | 0.01288578618599856 | 0.03954119092042951 | 0.32588260206753 | 70 | 0.013141937827126124 |
| kospi_buy_and_hold | 20.095177626449328 | -0.34485340853513224 | 14 | 0.2257327915799301 | 0.18914309081113953 | 1.1934498406041465 | 0 | 0.0 |
| cash | 0.0 | 0.0 | 0 | 0.0 | 0.0 | nan | 0 | 0.0 |

## D004 Diagnostics

| metric | value |
| --- | ---: |
| d001_cumulative_net_total_return | 1.2906841868750734 |
| d001_cost_0_cumulative_net_total_return | 1.397144393892741 |
| d004_minus_d001_cumulative_net_pp | -1.0792583721104017 |
| d004_minus_d001_cost_0_cumulative_net_pp | -1.1702870073734968 |
| c014_v11_cumulative_net_total_return | 1.1136051550981834 |
| c014_v11_cost_0_cumulative_net_total_return | 1.483915813335873 |
| d004_minus_c014_v11_cumulative_net_pp | -0.9021793403335117 |
| d004_minus_c014_v11_cost_0_cumulative_net_pp | -1.2570584268166287 |
| subperiod_2010_2017_net_total_return | 0.0 |
| subperiod_2010_2017_cost_0_total_return | 0.0 |
| subperiod_2018_2026_net_total_return | 0.2114258147646717 |
| subperiod_2018_2026_cost_0_total_return | 0.22685738651924425 |
| composite_mean | -0.22008966303812005 |
| composite_std | 0.5317946006029692 |
| composite_positive_share | 0.4375 |
| exposure_scalar_mean | 0.11659024259493606 |
| exposure_scalar_std | 0.16363144619834197 |
| exposure_scalar_zero_share | 0.5625 |
| exposure_scalar_one_share | 0.0 |
| exposure_scalar_partial_share | 0.4375 |
| on_quarters_mean_exposure | 0.2664919830741395 |
| partial_exposure_quarter_count | 14 |
| partial_exposure_quarter_avg_return | 0.01453498120512622 |
| full_exposure_quarter_cumulative_gain | nan |
| partial_exposure_quarter_cumulative_gain | 0.20790839873614853 |
| d001_quarter_overlap_jaccard | 1.0 |

## Quarterly Year Breakdown

| year | factor_macro_sized_mcap_net_total_return | kospi_buy_and_hold_net_total_return | cash_net_total_return | d001_factor_macro_gate_mcap_net_total_return | d004_minus_d001_factor_macro_return |
| --- | --- | --- | --- | --- | --- |
| 2010.0 | 0.0 | 0.3293489579737485 | 0.0 | 0.0 | 0.0 |
| 2011.0 | 0.0 | 0.004079681302652238 | 0.0 | 0.0 | 0.0 |
| 2012.0 | 0.0 | 0.18731018909741426 | 0.0 | 0.0 | 0.0 |
| 2013.0 | 0.0 | 0.06125736750042954 | 0.0 | 0.0 | 0.0 |
| 2014.0 | 0.0 | 0.05769800682302639 | 0.0 | 0.0 | 0.0 |
| 2015.0 | 0.0 | 0.16501292442133764 | 0.0 | 0.0 | 0.0 |
| 2017.0 | 0.0 | 0.31675953872996554 | 0.0 | 0.0 | 0.0 |
| 2018.0 | 0.0 | -0.08401784948302582 | 0.0 | 0.0 | 0.0 |
| 2019.0 | 0.0015282697029812553 | 0.17019485930094325 | 0.0 | 0.0277493483052602 | -0.026221078602278944 |
| 2020.0 | 0.03268340639327172 | 0.5251287429311848 | 0.0 | 0.2461360848272729 | -0.21345267843400118 |
| 2021.0 | -0.014285602972360922 | 0.13170240063376726 | 0.0 | -0.035316520549102 | 0.021030917576741075 |
| 2022.0 | 0.0 | -0.18442405395793493 | 0.0 | 0.0 | 0.0 |
| 2023.0 | -0.016636226642853802 | 0.3279894204214897 | 0.0 | -0.0177293971971159 | 0.001093170554262099 |
| 2024.0 | 0.001669704488448609 | 0.034981455283805474 | 0.0 | 0.0422472179791628 | -0.040577513490714194 |
| 2025.0 | 0.19934431718687828 | 1.047004780803555 | 0.0 | 0.7666554035490463 | -0.567311086362168 |
| 2026.0 | 0.0 | 0.7344109727369705 | 0.0 | 0.0 | 0.0 |

## Subperiod Breakdown

| period | start | end | v1_net_total_return | v1_cost_0_total_return | v1_annualized_return | v1_cost_0_annualized_return | v1_max_drawdown | v1_cost_0_max_drawdown | v1_trade_count | v1_cost_0_trade_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2010-2017 | 2010-01-04 | 2017-12-31 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0 |
| 2018-2026 | 2018-01-01 | 2026-05-04 | 0.2114258147646717 | 0.22685738651924425 | 0.023916283494396895 | 0.025514634795112734 | -0.12098009674398247 | -0.11819214341389628 | 70 | 70 |

## Exposure Distribution

| signal_date | quarter | composite | exposure_scalar | is_zero | is_partial | is_full |
| --- | --- | --- | --- | --- | --- | --- |
| 2017-12-28 00:00:00 | 2017Q4 | -0.9687090264120095 | 0.0 | True | False | False |
| 2018-03-30 00:00:00 | 2018Q1 | -1.1360078297017127 | 0.0 | True | False | False |
| 2018-06-29 00:00:00 | 2018Q2 | -1.1141840741469748 | 0.0 | True | False | False |
| 2018-09-28 00:00:00 | 2018Q3 | -0.576079536888737 | 0.0 | True | False | False |
| 2018-12-28 00:00:00 | 2018Q4 | -0.4073895350378036 | 0.0 | True | False | False |
| 2019-03-29 00:00:00 | 2019Q1 | -0.14134607961397616 | 0.0 | True | False | False |
| 2019-06-28 00:00:00 | 2019Q2 | 0.3421985262665735 | 0.3421985262665735 | False | True | False |
| 2019-09-30 00:00:00 | 2019Q3 | 0.22808480070388715 | 0.22808480070388715 | False | True | False |
| 2019-12-30 00:00:00 | 2019Q4 | -0.05810945016956437 | 0.0 | True | False | False |
| 2020-03-31 00:00:00 | 2020Q1 | -0.5028209425422792 | 0.0 | True | False | False |
| 2020-06-30 00:00:00 | 2020Q2 | -0.12736266221788034 | 0.0 | True | False | False |
| 2020-09-29 00:00:00 | 2020Q3 | 0.13272132072704226 | 0.13272132072704226 | False | True | False |
| 2020-12-30 00:00:00 | 2020Q4 | 0.40009800065978657 | 0.40009800065978657 | False | True | False |
| 2021-03-31 00:00:00 | 2021Q1 | -0.23113777380474423 | 0.0 | True | False | False |
| 2021-06-30 00:00:00 | 2021Q2 | -0.4437125413354644 | 0.0 | True | False | False |
| 2021-09-30 00:00:00 | 2021Q3 | -0.41859862800447606 | 0.0 | True | False | False |
| 2021-12-30 00:00:00 | 2021Q4 | -0.7178047450573325 | 0.0 | True | False | False |
| 2022-03-31 00:00:00 | 2022Q1 | -1.1472766472941949 | 0.0 | True | False | False |
| 2022-06-30 00:00:00 | 2022Q2 | -1.1791740118216183 | 0.0 | True | False | False |
| 2022-09-30 00:00:00 | 2022Q3 | -1.1188100949187751 | 0.0 | True | False | False |
| 2022-12-29 00:00:00 | 2022Q4 | -0.3662253374640972 | 0.0 | True | False | False |
| 2023-03-31 00:00:00 | 2023Q1 | 0.11110100363047261 | 0.11110100363047261 | False | True | False |
| 2023-06-30 00:00:00 | 2023Q2 | 0.4488542163174268 | 0.4488542163174268 | False | True | False |
| 2023-09-27 00:00:00 | 2023Q3 | 0.46946949564920654 | 0.46946949564920654 | False | True | False |
| 2023-12-28 00:00:00 | 2023Q4 | 0.3246494443899061 | 0.3246494443899061 | False | True | False |
| 2024-03-29 00:00:00 | 2024Q1 | 0.09390143901567 | 0.09390143901567 | False | True | False |
| 2024-06-28 00:00:00 | 2024Q2 | -0.1190080638261554 | 0.0 | True | False | False |
| 2024-09-30 00:00:00 | 2024Q3 | 0.406119394065737 | 0.406119394065737 | False | True | False |
| 2024-12-30 00:00:00 | 2024Q4 | 0.02045978126894817 | 0.02045978126894817 | False | True | False |
| 2025-03-31 00:00:00 | 2025Q1 | 0.10464141011208321 | 0.10464141011208321 | False | True | False |
| 2025-06-30 00:00:00 | 2025Q2 | 0.25389500186775044 | 0.25389500186775044 | False | True | False |
| 2025-09-30 00:00:00 | 2025Q3 | 0.3946939283634632 | 0.3946939283634632 | False | True | False |

## Magnitude Return Scatter

| signal_date | quarter | composite | exposure_scalar | forward_quarter_return |
| --- | --- | --- | --- | --- |
| 2017-12-28 00:00:00 | 2017Q4 | -0.9687090264120095 | 0.0 | 0.0 |
| 2018-03-30 00:00:00 | 2018Q1 | -1.1360078297017127 | 0.0 | 0.0 |
| 2018-06-29 00:00:00 | 2018Q2 | -1.1141840741469748 | 0.0 | 0.0 |
| 2018-09-28 00:00:00 | 2018Q3 | -0.576079536888737 | 0.0 | 0.0 |
| 2018-12-28 00:00:00 | 2018Q4 | -0.4073895350378036 | 0.0 | 0.0 |
| 2019-03-29 00:00:00 | 2019Q1 | -0.14134607961397616 | 0.0 | 0.0 |
| 2019-06-28 00:00:00 | 2019Q2 | 0.3421985262665735 | 0.3421985262665735 | -0.013290920240398685 |
| 2019-09-30 00:00:00 | 2019Q3 | 0.22808480070388715 | 0.22808480070388715 | 0.018373933695620792 |
| 2019-12-30 00:00:00 | 2019Q4 | -0.05810945016956437 | 0.0 | 0.0 |
| 2020-03-31 00:00:00 | 2020Q1 | -0.5028209425422792 | 0.0 | 0.0 |
| 2020-06-30 00:00:00 | 2020Q2 | -0.12736266221788034 | 0.0 | 0.0 |
| 2020-09-29 00:00:00 | 2020Q3 | 0.13272132072704226 | 0.13272132072704226 | 0.03296428960057107 |
| 2020-12-30 00:00:00 | 2020Q4 | 0.40009800065978657 | 0.40009800065978657 | -0.018350477290941414 |
| 2021-03-31 00:00:00 | 2021Q1 | -0.23113777380474423 | 0.0 | 0.0 |
| 2021-06-30 00:00:00 | 2021Q2 | -0.4437125413354644 | 0.0 | 0.0 |
| 2021-09-30 00:00:00 | 2021Q3 | -0.41859862800447606 | 0.0 | 0.0 |
| 2021-12-30 00:00:00 | 2021Q4 | -0.7178047450573325 | 0.0 | 0.0 |
| 2022-03-31 00:00:00 | 2022Q1 | -1.1472766472941949 | 0.0 | 0.0 |
| 2022-06-30 00:00:00 | 2022Q2 | -1.1791740118216183 | 0.0 | 0.0 |
| 2022-09-30 00:00:00 | 2022Q3 | -1.1188100949187751 | 0.0 | 0.0 |
| 2022-12-29 00:00:00 | 2022Q4 | -0.3662253374640972 | 0.0 | 0.0 |
| 2023-03-31 00:00:00 | 2023Q1 | 0.11110100363047261 | 0.11110100363047261 | 0.005647966422058781 |
| 2023-06-30 00:00:00 | 2023Q2 | 0.4488542163174268 | 0.4488542163174268 | -0.056380252884967064 |
| 2023-09-27 00:00:00 | 2023Q3 | 0.46946949564920654 | 0.46946949564920654 | 0.03895168520012815 |
| 2023-12-28 00:00:00 | 2023Q4 | 0.3246494443899061 | 0.3246494443899061 | 0.029813286715079323 |
| 2024-03-29 00:00:00 | 2024Q1 | 0.09390143901567 | 0.09390143901567 | 0.005163688545446243 |
| 2024-06-28 00:00:00 | 2024Q2 | -0.1190080638261554 | 0.0 | 0.0 |
| 2024-09-30 00:00:00 | 2024Q3 | 0.406119394065737 | 0.406119394065737 | -0.03153340966878526 |
| 2024-12-30 00:00:00 | 2024Q4 | 0.02045978126894817 | 0.02045978126894817 | 0.0007432186890814485 |
| 2025-03-31 00:00:00 | 2025Q1 | 0.10464141011208321 | 0.10464141011208321 | 0.00786855744649273 |
| 2025-06-30 00:00:00 | 2025Q2 | 0.25389500186775044 | 0.25389500186775044 | 0.039332273777246796 |
| 2025-09-30 00:00:00 | 2025Q3 | 0.3946939283634632 | 0.3946939283634632 | 0.14418589686513417 |

## Verdict Summary

| hypothesis | description | value | threshold | passes |
| --- | --- | --- | --- | --- |
| H1 | V1 cumulative net total return > 0 | 0.2114258147646717 | 0.0 | True |
| H2 | V1 cumulative net >= V2 cumulative net - 30pp | -19.883751811684657 | -0.3 | False |
| H3 | V1 positive in at least 2 of 2010, 2025, 2026 | 1.0 | 2.0 | False |
| H4 | V1 max drawdown improves on V2 by at least 5pp | 0.22387331179114978 | -0.05 | False |
| H5 | V1 positive in >= 8 of 16 years | 4.0 | 8.0 | False |
| H6 | V1 net / V1 cost-0 >= 0.7 | 0.9319767718770599 | 0.7 | True |
| H7 | D004 sizing improves Sharpe versus D001 or cumulative net versus D001; strong if both pass | -1.0792583721104017 | 0.0 | False |
| H8 | Composite magnitude diagnostics: ON-quarter exposure and partial-vs-full quarter returns | 0.2664919830741395 |  | <NA> |
| H9 | Exposure scalar distribution and D001 quarter overlap are descriptive checks | 0.11659024259493606 |  | <NA> |
| H7_STRONG | Sharpe >= D001 0.48 and cumulative net >= D001 +129.07% | 0.32588260206753 | 0.48 | False |
