# C013 Metrics Summary

## Metadata

| key | value |
| --- | --- |
| panels_used | ["research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv"] |
| period_start | 2010-01-04 |
| period_end | 2026-05-04 |
| excluded_years | [2016] |
| macro_gate | USDKRW yoy <= 0, VIX 60d avg <= VIX 240d avg, DXY yoy <= 0, US 2-10y curve spread > 0, Brent yoy <= 0, KR10y yoy change <= 0, US CPI yoy decel <= 0; ON when score >= 2 |
| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |
| selection | top 5 by signal-date market cap, equal weight when macro gate ON |
| baselines | V2 cap-weighted KOSPI proxy buy-and-hold; V3 cash |
| c011_v8_reference | C011 v8 quarterly cumulative net +55.00%; cost-0 +83.35%; yearly columns read from C011 output files |
| us_cpi_timing | CPIAUCSL is monthly; each observation is treated as available 14 days after month-end, so quarter-end signals use only CPI releases available by the signal date |
| us_cpi_formula | CPI yoy is CPI(T) / CPI(T-12 months) - 1; CPI decel is CPI yoy(T) - CPI yoy(T-12 months); favorable when decel <= 0 |
| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |
| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |
| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |
| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |

## Variant Metrics

| variant | cumulative_net_total_return | max_drawdown | positive_years | annualized_return | annualized_volatility | sharpe | trade_count | cost_paid_total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| macro_gate_mcap | 0.8128975579087656 | -0.6476661807998405 | 7 | 0.04051345064688339 | 0.22397532005935986 | 0.1808835484023247 | 240 | 0.1305654887246479 |
| kospi_buy_and_hold | 20.095177626449328 | -0.34485340853513224 | 14 | 0.2257327915799301 | 0.18914309081113953 | 1.1934498406041465 | 0 | 0.0 |
| cash | 0.0 | 0.0 | 0 | 0.0 | 0.0 | nan | 0 | 0.0 |

## C011 V8 Reference

| metric | value |
| --- | ---: |
| c011_v8_cumulative_net_total_return | 0.5500320799221281 |
| c011_v8_cost_0_cumulative_net_total_return | 0.8334534338807984 |
| v10_minus_v8_cumulative_net_pp | 0.2628654779866375 |
| v10_minus_v8_cost_0_cumulative_net_pp | 0.28998263013294867 |
| regime_on_share | 0.819672131147541 |
| us_cpi_favorable_quarters | 36 |
| us_cpi_total_quarters | 54 |
| us_cpi_yoy_brent_yoy_correlation | 0.44844688775351615 |
| us_cpi_yoy_curve_spread_correlation | -0.44781825104585843 |
| us_cpi_yoy_usdkrw_yoy_correlation | 0.33660400359412046 |
| us_cpi_decel_brent_yoy_correlation | 0.48869597598143544 |
| us_cpi_decel_curve_spread_correlation | 0.14930245471820902 |
| us_cpi_decel_usdkrw_yoy_correlation | 0.16220577939002376 |
| inflation_spike_2022_regime_on_quarters | 0 |
| inflation_spike_2022_total_quarters | 4 |
| inflation_spike_2022_cpi_favorable_quarters | 0 |

## Quarterly Year Breakdown

| year | macro_gate_mcap_net_total_return | kospi_buy_and_hold_net_total_return | cash_net_total_return | c011_v8_macro_gate_mcap_net_total_return | v10_minus_v8_macro_gate_mcap_return |
| --- | --- | --- | --- | --- | --- |
| 2010.0 | 0.0 | 0.3293489579737485 | 0.0 | 0.0 | 0.0 |
| 2011.0 | 0.0 | 0.004079681302652238 | 0.0 | -0.1488550811365689 | 0.1488550811365689 |
| 2012.0 | 0.026244552924422848 | 0.18731018909741426 | 0.0 | 0.026244552924423 | -1.5265566588595902e-16 |
| 2013.0 | -0.02819309888575494 | 0.06125736750042954 | 0.0 | -0.0281930988857552 | 2.6020852139652106e-16 |
| 2014.0 | -0.07836784555750465 | 0.05769800682302639 | 0.0 | -0.0783678455575052 | 5.551115123125783e-16 |
| 2015.0 | -0.15879485716997932 | 0.16501292442133764 | 0.0 | -0.1587948571699787 | -6.106226635438361e-16 |
| 2017.0 | 0.09401472235486152 | 0.31675953872996554 | 0.0 | 0.0940147223548613 | 2.220446049250313e-16 |
| 2018.0 | -0.4425899844893092 | -0.08401784948302582 | 0.0 | -0.4425899844893092 | 0.0 |
| 2019.0 | 0.11725673833786443 | 0.17019485930094325 | 0.0 | 0.1172567383378642 | 2.3592239273284576e-16 |
| 2020.0 | 0.4630990404450497 | 0.5251287429311848 | 0.0 | 0.4630990404450492 | 4.996003610813204e-16 |
| 2021.0 | -0.12419945981131242 | 0.13170240063376726 | 0.0 | -0.1241994598113126 | 1.8041124150158794e-16 |
| 2022.0 | -0.09716827644733173 | -0.18442405395793493 | 0.0 | -0.0971682764473319 | 1.8041124150158794e-16 |
| 2023.0 | -0.017729397197116414 | 0.3279894204214897 | 0.0 | -0.0177293971971163 | -1.1449174941446927e-16 |
| 2024.0 | 0.014081826253520058 | 0.034981455283805474 | 0.0 | 0.01408182625352 | 5.724587470723463e-17 |
| 2025.0 | 0.7666554035490452 | 1.047004780803555 | 0.0 | 0.7666554035490463 | -1.1102230246251565e-15 |
| 2026.0 | 0.5621484118981521 | 0.7344109727369705 | 0.0 | 0.5621484118981515 | 6.661338147750939e-16 |

## Subperiod Breakdown

| period | start | end | v1_net_total_return | v1_cost_0_total_return | v1_annualized_return | v1_cost_0_annualized_return | v1_max_drawdown | v1_cost_0_max_drawdown | v1_trade_count | v1_cost_0_trade_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2010-2017 | 2010-01-04 | 2017-12-31 | -0.08160168142041113 | -0.025347528304094702 | -0.012323019581256145 | -0.0037328573071873095 | -0.3984379737991739 | -0.3720679820268781 | 90 | 90 |
| 2018-2026 | 2018-01-01 | 2026-05-04 | 0.9731854305082979 | 1.1763497187115117 | 0.0873585360015714 | 0.10056937092935603 | -0.5757035067116882 | -0.5643704392116582 | 150 | 150 |

## Verdict Summary

| hypothesis | description | value | threshold | passes |
| --- | --- | --- | --- | --- |
| H1 | V1 cumulative net total return > 0 | 0.8128975579087656 | 0.0 | True |
| H2 | V1 cumulative net >= V2 cumulative net - 30pp | -19.28228006854056 | -0.3 | False |
| H3 | V1 positive in at least 2 of 2010, 2025, 2026 | 2.0 | 2.0 | True |
| H4 | V1 max drawdown improves on V2 by at least 5pp | -0.30281277226470826 | -0.05 | True |
| H5 | V1 positive in >= 8 of 16 years | 7.0 | 8.0 | False |
| H6 | V1 net / V1 cost-0 >= 0.7 | 0.7235815049451879 | 0.7 | True |
| H7 | V1 v10 cumulative net improves on C011 v8 by >= 5pp | 0.2628654779866375 | 0.05 | True |
| H8 | C013 V1 subperiod cumulative net is >= 0 in both 2010-2017 and 2018-2026 | -0.08160168142041113 | 0.0 | False |
| H9 | US CPI yoy correlations with Brent, curve, and USDKRW are descriptive redundancy checks | 0.44844688775351615 | 0.7 | <NA> |
