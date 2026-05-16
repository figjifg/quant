# C012 Metrics Summary

## Metadata

| key | value |
| --- | --- |
| panels_used | ["research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv"] |
| period_start | 2010-01-04 |
| period_end | 2026-05-04 |
| excluded_years | [2016] |
| macro_gate | USDKRW yoy <= 0, VIX 60d avg <= VIX 240d avg, DXY yoy <= 0, US 2-10y curve spread > 0, Brent yoy <= 0, KR10y yoy change <= 0, KR3m yoy change <= 0; ON when score >= 2 |
| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |
| selection | top 5 by signal-date market cap, equal weight when macro gate ON |
| baselines | V2 cap-weighted KOSPI proxy buy-and-hold; V3 cash |
| c011_v8_reference | C011 v8 quarterly cumulative net +55.00%; cost-0 +83.35%; yearly columns read from C011 output files |
| kr_rates_timing | IRLTLT01KRM156N and IR3TIB01KRM156N are monthly; each KRX signal date uses the latest FRED observation at or before the aligned lookup date, so quarter-end signals and the 12-month change base use no future monthly value |
| kr3m_formula | KR3m yoy is a percentage-point rate change, KR3M(T) - KR3M(T-12 months), not a return ratio |
| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |
| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |
| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |
| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |

## Variant Metrics

| variant | cumulative_net_total_return | max_drawdown | positive_years | annualized_return | annualized_volatility | sharpe | trade_count | cost_paid_total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| macro_gate_mcap | 0.5500320799221281 | -0.6747844542564327 | 7 | 0.029689267819052123 | 0.23643207927826884 | 0.12557207934592213 | 255 | 0.12058472944581584 |
| kospi_buy_and_hold | 20.095177626449328 | -0.34485340853513224 | 14 | 0.2257327915799301 | 0.18914309081113953 | 1.1934498406041465 | 0 | 0.0 |
| cash | 0.0 | 0.0 | 0 | 0.0 | 0.0 | nan | 0 | 0.0 |

## C011 V8 Reference

| metric | value |
| --- | ---: |
| c011_v8_cumulative_net_total_return | 0.5500320799221281 |
| c011_v8_cost_0_cumulative_net_total_return | 0.8334534338807984 |
| v9_minus_v8_cumulative_net_pp | 0.0 |
| v9_minus_v8_cost_0_cumulative_net_pp | 0.0 |
| regime_on_share | 0.8688524590163934 |
| kr3m_favorable_quarters | 35 |
| kr3m_total_quarters | 57 |
| kr3m_yoy_change_kr10y_yoy_change_correlation | 0.5114241961814303 |
| kr3m_yoy_change_us3m_yoy_change_correlation | 0.8107427549826876 |

## Quarterly Year Breakdown

| year | macro_gate_mcap_net_total_return | kospi_buy_and_hold_net_total_return | cash_net_total_return | c011_v8_macro_gate_mcap_net_total_return | v9_minus_v8_macro_gate_mcap_return |
| --- | --- | --- | --- | --- | --- |
| 2010.0 | 0.0 | 0.3293489579737485 | 0.0 | 0.0 | 0.0 |
| 2011.0 | -0.14885508113656898 | 0.004079681302652238 | 0.0 | -0.1488550811365689 | -8.326672684688674e-17 |
| 2012.0 | 0.02624455292442307 | 0.18731018909741426 | 0.0 | 0.026244552924423 | 6.938893903907228e-17 |
| 2013.0 | -0.028193098885755274 | 0.06125736750042954 | 0.0 | -0.0281930988857552 | -7.28583859910259e-17 |
| 2014.0 | -0.0783678455575052 | 0.05769800682302639 | 0.0 | -0.0783678455575052 | 0.0 |
| 2015.0 | -0.15879485716997876 | 0.16501292442133764 | 0.0 | -0.1587948571699787 | -5.551115123125783e-17 |
| 2017.0 | 0.0940147223548613 | 0.31675953872996554 | 0.0 | 0.0940147223548613 | 0.0 |
| 2018.0 | -0.4425899844893092 | -0.08401784948302582 | 0.0 | -0.4425899844893092 | 0.0 |
| 2019.0 | 0.11725673833786421 | 0.17019485930094325 | 0.0 | 0.1172567383378642 | 1.3877787807814457e-17 |
| 2020.0 | 0.46309904044504924 | 0.5251287429311848 | 0.0 | 0.4630990404450492 | 5.551115123125783e-17 |
| 2021.0 | -0.12419945981131264 | 0.13170240063376726 | 0.0 | -0.1241994598113126 | -4.163336342344337e-17 |
| 2022.0 | -0.09716827644733195 | -0.18442405395793493 | 0.0 | -0.0971682764473319 | -4.163336342344337e-17 |
| 2023.0 | -0.017729397197116303 | 0.3279894204214897 | 0.0 | -0.0177293971971163 | -3.469446951953614e-18 |
| 2024.0 | 0.014081826253520058 | 0.034981455283805474 | 0.0 | 0.01408182625352 | 5.724587470723463e-17 |
| 2025.0 | 0.7666554035490463 | 1.047004780803555 | 0.0 | 0.7666554035490463 | 0.0 |
| 2026.0 | 0.5621484118981515 | 0.7344109727369705 | 0.0 | 0.5621484118981515 | 0.0 |

## Subperiod Breakdown

| period | start | end | v1_net_total_return | v1_cost_0_total_return | v1_annualized_return | v1_cost_0_annualized_return | v1_max_drawdown | v1_cost_0_max_drawdown | v1_trade_count | v1_cost_0_trade_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2010-2017 | 2010-01-04 | 2017-12-31 | -0.21476707289130448 | -0.15844891619035273 | -0.03460513558149558 | -0.02481532410329257 | -0.44473873358615357 | -0.4127558511328513 | 105 | 105 |
| 2018-2026 | 2018-01-01 | 2026-05-04 | 0.9731854305082974 | 1.176349718711517 | 0.0873585360015714 | 0.10056937092935647 | -0.5757035067116882 | -0.5643704392116577 | 150 | 150 |

## Verdict Summary

| hypothesis | description | value | threshold | passes |
| --- | --- | --- | --- | --- |
| H1 | V1 cumulative net total return > 0 | 0.5500320799221281 | 0.0 | True |
| H2 | V1 cumulative net >= V2 cumulative net - 30pp | -19.5451455465272 | -0.3 | False |
| H3 | V1 positive in at least 2 of 2010, 2025, 2026 | 2.0 | 2.0 | True |
| H4 | V1 max drawdown improves on V2 by at least 5pp | -0.3299310457213005 | -0.05 | True |
| H5 | V1 positive in >= 8 of 16 years | 7.0 | 8.0 | False |
| H6 | V1 net / V1 cost-0 >= 0.7 | 0.6599433844324342 | 0.7 | False |
| H7 | V1 v9 cumulative net improves on C011 v8 by >= 5pp | 0.0 | 0.05 | False |
| H8 | C012 V1 subperiod cumulative net improves pre-2018 and remains >= 0 in 2018-2026 | -0.21476707289130448 | -0.21476707289130448 | False |
| H9 | KR3m yoy change correlations with KR10y and US 3m changes are descriptive redundancy checks | 0.8107427549826876 | 0.7 | <NA> |
