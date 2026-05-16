# C014 Metrics Summary

## Metadata

| key | value |
| --- | --- |
| panels_used | ["research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv"] |
| period_start | 2010-01-04 |
| period_end | 2026-05-04 |
| excluded_years | [2016] |
| macro_gate | USDKRW yoy <= 0, VIX 60d avg <= VIX 240d avg, DXY yoy <= 0, US 2-10y curve spread > 0, Brent yoy <= 0, KR10y yoy change <= 0, US CPI yoy decel <= 0, US PPI yoy decel <= 0; ON when score >= 2 |
| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |
| selection | top 5 by signal-date market cap, equal weight when macro gate ON |
| baselines | V2 cap-weighted KOSPI proxy buy-and-hold; V3 cash |
| c013_v10_reference | C013 v10 quarterly cumulative net +81.29%; cost-0 +112.34%; yearly columns read from C013 output files |
| us_cpi_timing | CPIAUCSL is monthly; each observation is treated as available 14 days after month-end, so quarter-end signals use only CPI releases available by the signal date |
| us_ppi_timing | PPIACO is monthly; each observation is treated as available 14 days after month-end, so quarter-end signals use only PPI releases available by the signal date |
| us_ppi_formula | PPI yoy is PPI(T) / PPI(T-12 months) - 1; PPI decel is PPI yoy(T) - PPI yoy(T-12 months); favorable when decel <= 0 |
| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |
| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |
| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |
| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |

## Variant Metrics

| variant | cumulative_net_total_return | max_drawdown | positive_years | annualized_return | annualized_volatility | sharpe | trade_count | cost_paid_total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| macro_gate_mcap | 1.1136051550981834 | -0.6476661807998405 | 8 | 0.05122808944513246 | 0.2257602833912648 | 0.22691364785518603 | 245 | 0.13912817072045328 |
| kospi_buy_and_hold | 20.095177626449328 | -0.34485340853513224 | 14 | 0.2257327915799301 | 0.18914309081113953 | 1.1934498406041465 | 0 | 0.0 |
| cash | 0.0 | 0.0 | 0 | 0.0 | 0.0 | nan | 0 | 0.0 |

## C013 V10 Reference

| metric | value |
| --- | ---: |
| c013_v10_cumulative_net_total_return | 0.8128975579087656 |
| c013_v10_cost_0_cumulative_net_total_return | 1.123436064013747 |
| v11_minus_v10_cumulative_net_pp | 0.30070759718941775 |
| v11_minus_v10_cost_0_cumulative_net_pp | 0.3604797493221259 |
| regime_on_share | 0.8360655737704918 |
| us_ppi_favorable_quarters | 26 |
| us_ppi_total_quarters | 54 |
| us_ppi_decel_us_cpi_decel_correlation | 0.7848186679989109 |
| us_ppi_decel_brent_yoy_correlation | 0.5483735866684537 |
| us_ppi_decel_dxy_yoy_correlation | -0.2186347330024009 |
| us_ppi_yoy_us_cpi_yoy_correlation | 0.7672815031406546 |

## Quarterly Year Breakdown

| year | macro_gate_mcap_net_total_return | kospi_buy_and_hold_net_total_return | cash_net_total_return | c013_v10_macro_gate_mcap_net_total_return | v11_minus_v10_macro_gate_mcap_return |
| --- | --- | --- | --- | --- | --- |
| 2010.0 | 0.0 | 0.3293489579737485 | 0.0 | 0.0 | 0.0 |
| 2011.0 | 0.0 | 0.004079681302652238 | 0.0 | 0.0 | 0.0 |
| 2012.0 | 0.026244552924422848 | 0.18731018909741426 | 0.0 | 0.0262445529244228 | 4.85722573273506e-17 |
| 2013.0 | -0.02819309888575494 | 0.06125736750042954 | 0.0 | -0.0281930988857549 | -4.163336342344337e-17 |
| 2014.0 | -0.07836784555750465 | 0.05769800682302639 | 0.0 | -0.0783678455575046 | -4.163336342344337e-17 |
| 2015.0 | -0.15879485716997932 | 0.16501292442133764 | 0.0 | -0.1587948571699793 | -2.7755575615628914e-17 |
| 2017.0 | 0.09401472235486152 | 0.31675953872996554 | 0.0 | 0.0940147223548615 | 2.7755575615628914e-17 |
| 2018.0 | -0.4425899844893092 | -0.08401784948302582 | 0.0 | -0.4425899844893092 | 0.0 |
| 2019.0 | 0.11725673833786443 | 0.17019485930094325 | 0.0 | 0.1172567383378644 | 2.7755575615628914e-17 |
| 2020.0 | 0.4630990404450497 | 0.5251287429311848 | 0.0 | 0.4630990404450497 | 0.0 |
| 2021.0 | -0.12419945981131242 | 0.13170240063376726 | 0.0 | -0.1241994598113124 | -1.3877787807814457e-17 |
| 2022.0 | -0.09716827644733173 | -0.18442405395793493 | 0.0 | -0.0971682764473317 | -2.7755575615628914e-17 |
| 2023.0 | 0.14010321024790118 | 0.3279894204214897 | 0.0 | -0.0177293971971164 | 0.1578326074450176 |
| 2024.0 | 0.01408182625352028 | 0.034981455283805474 | 0.0 | 0.01408182625352 | 2.7929047963226594e-16 |
| 2025.0 | 0.766655403549046 | 1.047004780803555 | 0.0 | 0.7666554035490452 | 8.881784197001252e-16 |
| 2026.0 | 0.5621484118981521 | 0.7344109727369705 | 0.0 | 0.5621484118981521 | 0.0 |

## Subperiod Breakdown

| period | start | end | v1_net_total_return | v1_cost_0_total_return | v1_annualized_return | v1_cost_0_annualized_return | v1_max_drawdown | v1_cost_0_max_drawdown | v1_trade_count | v1_cost_0_trade_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2010-2017 | 2010-01-04 | 2017-12-31 | -0.08160168142041113 | -0.025347528304094702 | -0.012323019581256145 | -0.0037328573071873095 | -0.3984379737991739 | -0.3720679820268781 | 90 | 90 |
| 2018-2026 | 2018-01-01 | 2026-05-04 | 1.3004801786471654 | 1.5458122207072047 | 0.10811783962318078 | 0.12204150360843169 | -0.5757035067116882 | -0.5643704392116582 | 155 | 155 |

## Verdict Summary

| hypothesis | description | value | threshold | passes |
| --- | --- | --- | --- | --- |
| H1 | V1 cumulative net total return > 0 | 1.1136051550981834 | 0.0 | True |
| H2 | V1 cumulative net >= V2 cumulative net - 30pp | -18.981572471351143 | -0.3 | False |
| H3 | V1 positive in at least 2 of 2010, 2025, 2026 | 2.0 | 2.0 | True |
| H4 | V1 max drawdown improves on V2 by at least 5pp | -0.30281277226470826 | -0.05 | True |
| H5 | V1 positive in >= 8 of 16 years | 8.0 | 8.0 | True |
| H6 | V1 net / V1 cost-0 >= 0.7 | 0.750450359171506 | 0.7 | True |
| H7 | V1 v11 cumulative net improves on C013 v10 by >= 5pp | 0.30070759718941775 | 0.05 | True |
| H8 | C014 V1 subperiod cumulative net is >= 0 in both 2010-2017 and 2018-2026 | -0.08160168142041113 | 0.0 | False |
| H9 | US PPI decel vs US CPI decel correlation is a descriptive redundancy check | 0.7848186679989109 | 0.7 | <NA> |
