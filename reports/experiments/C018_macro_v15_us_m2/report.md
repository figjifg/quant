# C018 Metrics Summary

## Metadata

| key | value |
| --- | --- |
| panels_used | ["research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv"] |
| period_start | 2010-01-04 |
| period_end | 2026-05-04 |
| excluded_years | [2016] |
| macro_gate | USDKRW yoy <= 0, VIX 60d avg <= VIX 240d avg, DXY yoy <= 0, US 2-10y curve spread > 0, Brent yoy <= 0, KR10y yoy change <= 0, US CPI yoy decel <= 0, US PPI yoy decel <= 0, US M2 yoy >= 5%; ON when score >= 2 |
| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |
| selection | top 5 by signal-date market cap, equal weight when macro gate ON |
| baselines | V2 cap-weighted KOSPI proxy buy-and-hold; V3 cash |
| c014_v11_reference | C014 v11 quarterly cumulative net +111.36%; cost-0 +148.39%; yearly columns read from C014 output files |
| us_m2_timing | M2SL is monthly; each observation is treated as available 14 days after month-end, so quarter-end signals use only M2 releases available by the signal date |
| us_m2_formula | US M2 yoy is M2SL(T) / M2SL(T-12 months) - 1; favorable when yoy >= 0.05 |
| us_m2_sign | growth at or above 5% is favorable as an expansionary monetary stance |
| us_cpi_timing | CPIAUCSL is monthly; each observation is treated as available 14 days after month-end, so quarter-end signals use only CPI releases available by the signal date |
| us_ppi_timing | PPIACO is monthly; each observation is treated as available 14 days after month-end, so quarter-end signals use only PPI releases available by the signal date |
| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |
| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |
| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |
| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |

## Variant Metrics

| variant | cumulative_net_total_return | max_drawdown | positive_years | annualized_return | annualized_volatility | sharpe | trade_count | cost_paid_total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| macro_gate_mcap | 0.6902497584375944 | -0.6476661807998405 | 8 | 0.035659166971250045 | 0.2289003192224961 | 0.15578469742800383 | 255 | 0.13361333342616058 |
| kospi_buy_and_hold | 20.095177626449328 | -0.34485340853513224 | 14 | 0.2257327915799301 | 0.18914309081113953 | 1.1934498406041465 | 0 | 0.0 |
| cash | 0.0 | 0.0 | 0 | 0.0 | 0.0 | nan | 0 | 0.0 |

## C014 V11 Reference

| metric | value |
| --- | ---: |
| c014_v11_cumulative_net_total_return | 1.1136051550981834 |
| c014_v11_cost_0_cumulative_net_total_return | 1.483915813335873 |
| v15_minus_v11_cumulative_net_pp | -0.42335539666058897 |
| v15_minus_v11_cost_0_cumulative_net_pp | -0.48436905977134725 |
| regime_on_share | 0.8688524590163934 |
| us_m2_favorable_quarters | 32 |
| us_m2_total_quarters_with_data | 54 |
| us_m2_missing_quarters | 0 |
| us_m2_yoy_us_cpi_decel_correlation | 0.3737345014013765 |
| us_m2_yoy_curve_spread_correlation | 0.4164868729838499 |
| us_m2_yoy_usdkrw_yoy_correlation | -0.2798337619527256 |

## Quarterly Year Breakdown

| year | macro_gate_mcap_net_total_return | kospi_buy_and_hold_net_total_return | cash_net_total_return | c014_v11_macro_gate_mcap_net_total_return | v15_minus_v11_macro_gate_mcap_return |
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
| 2022.0 | -0.27800559202657427 | -0.18442405395793493 | 0.0 | -0.0971682764473317 | -0.18083731557924257 |
| 2023.0 | 0.14010321024790162 | 0.3279894204214897 | 0.0 | 0.1401032102479011 | 5.273559366969494e-16 |
| 2024.0 | 0.01408182625352028 | 0.034981455283805474 | 0.0 | 0.0140818262535202 | 7.979727989493313e-17 |
| 2025.0 | 0.7666554035490458 | 1.047004780803555 | 0.0 | 0.766655403549046 | -2.220446049250313e-16 |
| 2026.0 | 0.5621484118981523 | 0.7344109727369705 | 0.0 | 0.5621484118981521 | 2.220446049250313e-16 |

## Subperiod Breakdown

| period | start | end | v1_net_total_return | v1_cost_0_total_return | v1_annualized_return | v1_cost_0_annualized_return | v1_max_drawdown | v1_cost_0_max_drawdown | v1_trade_count | v1_cost_0_trade_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2010-2017 | 2010-01-04 | 2017-12-31 | -0.08160168142041113 | -0.025347528304094702 | -0.012323019581256145 | -0.0037328573071873095 | -0.3984379737991739 | -0.3720679820268781 | 90 | 90 |
| 2018-2026 | 2018-01-01 | 2026-05-04 | 0.8396936896514229 | 1.0493732250383871 | 0.07801275058601576 | 0.09244667634951886 | -0.5757035067116882 | -0.5643704392116582 | 165 | 165 |

## Verdict Summary

| hypothesis | description | value | threshold | passes |
| --- | --- | --- | --- | --- |
| H1 | V1 cumulative net total return > 0 | 0.6902497584375944 | 0.0 | True |
| H2 | V1 cumulative net >= V2 cumulative net - 30pp | -19.404927868011733 | -0.3 | False |
| H3 | V1 positive in at least 2 of 2010, 2025, 2026 | 2.0 | 2.0 | True |
| H4 | V1 max drawdown improves on V2 by at least 5pp | -0.30281277226470826 | -0.05 | True |
| H5 | V1 positive in >= 8 of 16 years | 8.0 | 8.0 | True |
| H6 | V1 net / V1 cost-0 >= 0.7 | 0.6905627535441096 | 0.7 | False |
| H7 | V1 v15 cumulative net improves on C014 v11 by >= 5pp | -0.42335539666058897 | 0.05 | False |
| H8 | C018 V1 subperiod cumulative net is >= 0 in both 2010-2017 and 2018-2026 | -0.08160168142041113 | 0.0 | False |
| H9 | US M2 yoy correlations with US CPI decel, curve, and USDKRW are descriptive checks | 0.4164868729838499 | 0.7 | <NA> |
