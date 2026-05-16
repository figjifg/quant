# C008 Metrics Summary

## Metadata

| key | value |
| --- | --- |
| panels_used | ["research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv"] |
| period_start | 2010-01-04 |
| period_end | 2026-05-04 |
| excluded_years | [2016] |
| macro_gate | USDKRW yoy <= 0, VIX 60d avg <= VIX 240d avg, DXY yoy <= 0, US 2-10y curve spread > 0, Brent yoy <= 0; ON when score >= 2 |
| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |
| selection | top 5 by signal-date market cap, equal weight when macro gate ON |
| baselines | V2 cap-weighted KOSPI proxy buy-and-hold; V3 cash |
| c005_v4_reference | C005 v4 quarterly cumulative net -8.48%; cost-0 +3.67%; yearly columns read from C005 output files |
| brent_timing | DCOILBRENTEU uses the aligned FRED observation available to the Korean signal date under src.data.macro_factors timing rules |
| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |
| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |
| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |
| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |

## Variant Metrics

| variant | cumulative_net_total_return | max_drawdown | positive_years | annualized_return | annualized_volatility | sharpe | trade_count | cost_paid_total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| macro_gate_mcap | 0.3697554631843185 | -0.7115598548289718 | 6 | 0.0212253850010915 | 0.23024431640947735 | 0.09218635809165111 | 235 | 0.10290997462967821 |
| kospi_buy_and_hold | 20.095177626449328 | -0.34485340853513224 | 14 | 0.2257327915799301 | 0.18914309081113953 | 1.1934498406041465 | 0 | 0.0 |
| cash | 0.0 | 0.0 | 0 | 0.0 | 0.0 | nan | 0 | 0.0 |

## C005 V4 Reference

| metric | value |
| --- | ---: |
| c005_v4_cumulative_net_total_return | -0.08478285179122336 |
| c005_v4_cost_0_cumulative_net_total_return | 0.03671567736697412 |
| v6_minus_v4_cumulative_net_pp | 0.45453831497554187 |
| v6_minus_v4_cost_0_cumulative_net_pp | 0.5615096726396218 |
| regime_on_share | 0.8032786885245902 |
| brent_favorable_quarters | 26 |
| brent_total_quarters | 57 |
| brent_yoy_usdkrw_yoy_correlation | -0.2836381123200502 |
| brent_yoy_vix_60d_avg_correlation | -0.00834886993292077 |

## Quarterly Year Breakdown

| year | macro_gate_mcap_net_total_return | kospi_buy_and_hold_net_total_return | cash_net_total_return | c005_v4_macro_gate_mcap_net_total_return | v6_minus_v4_macro_gate_mcap_return |
| --- | --- | --- | --- | --- | --- |
| 2010.0 | 0.0 | 0.3293489579737485 | 0.0 | 0.0 | 0.0 |
| 2011.0 | -0.14885508113656898 | 0.004079681302652238 | 0.0 | -0.1488550811365689 | -8.326672684688674e-17 |
| 2012.0 | -0.046826673821664055 | 0.18731018909741426 | 0.0 | -0.046826673821664 | -5.551115123125783e-17 |
| 2013.0 | -0.02819309888575494 | 0.06125736750042954 | 0.0 | -0.0281930988857549 | -4.163336342344337e-17 |
| 2014.0 | -0.07836784555750498 | 0.05769800682302639 | 0.0 | -0.0783678455575049 | -8.326672684688674e-17 |
| 2015.0 | -0.158794857169979 | 0.16501292442133764 | 0.0 | -0.026594350089605 | -0.13220050708037398 |
| 2017.0 | 0.09401472235486108 | 0.31675953872996554 | 0.0 | 0.0940147223548608 | 2.7755575615628914e-16 |
| 2018.0 | -0.4425899844893092 | -0.08401784948302582 | 0.0 | -0.4425899844893091 | -1.1102230246251565e-16 |
| 2019.0 | 0.059940094807804156 | 0.17019485930094325 | 0.0 | 0.0277493483052602 | 0.03219074650254396 |
| 2020.0 | 0.4630990404450499 | 0.5251287429311848 | 0.0 | 0.1219931437777739 | 0.341105896667276 |
| 2021.0 | -0.12419945981131264 | 0.13170240063376726 | 0.0 | -0.1241994598113126 | -4.163336342344337e-17 |
| 2022.0 | -0.09716827644733195 | -0.18442405395793493 | 0.0 | -0.0971682764473317 | -2.498001805406602e-16 |
| 2023.0 | -0.01772939719711597 | 0.3279894204214897 | 0.0 | -0.0560070633060246 | 0.03827766610890863 |
| 2024.0 | 0.01039443637671722 | 0.034981455283805474 | 0.0 | 0.0103944363767178 | -5.793976409762536e-16 |
| 2025.0 | 0.766655403549046 | 1.047004780803555 | 0.0 | 0.567009224531813 | 0.19964617901723303 |
| 2026.0 | 0.5621484118981519 | 0.7344109727369705 | 0.0 | 0.5621484118981519 | 0.0 |

## Verdict Summary

| hypothesis | description | value | threshold | passes |
| --- | --- | --- | --- | --- |
| H1 | V1 cumulative net total return > 0 | 0.3697554631843185 | 0.0 | True |
| H2 | V1 cumulative net >= V2 cumulative net - 30pp | -19.72542216326501 | -0.3 | False |
| H3 | V1 positive in at least 2 of 2010, 2025, 2026 | 2.0 | 2.0 | True |
| H4 | V1 max drawdown improves on V2 by at least 5pp | -0.3667064462938395 | -0.05 | True |
| H5 | V1 positive in >= 8 of 16 years | 6.0 | 8.0 | False |
| H6 | V1 net / V1 cost-0 >= 0.7 | 0.6180872528725866 | 0.7 | False |
| H7 | V1 v6 cumulative net improves on C005 v4 by >= 5pp | 0.45453831497554187 | 0.05 | True |
| H8 | Brent yoy and USDKRW yoy correlation, descriptive only | -0.2836381123200502 | nan | <NA> |
