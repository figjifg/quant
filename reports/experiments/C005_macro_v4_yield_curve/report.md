# C005 Metrics Summary

## Metadata

| key | value |
| --- | --- |
| panels_used | ["research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv"] |
| period_start | 2010-01-04 |
| period_end | 2026-05-04 |
| excluded_years | [2016] |
| macro_gate | USDKRW yoy <= 0, VIX 60d avg <= VIX 240d avg, DXY yoy <= 0, US 2-10y curve spread > 0; ON when score >= 2 |
| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |
| selection | top 5 by signal-date market cap, equal weight when macro gate ON |
| baselines | V2 cap-weighted KOSPI proxy buy-and-hold; V3 cash |
| c004_v3_reference | C004 v3 quarterly cumulative net -22.01%; yearly columns read from C004 output files |
| yield_curve_timing | DGS2 and DGS10 use the aligned FRED observations available to the Korean signal date under src.data.macro_factors timing rules |
| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |
| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |
| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |
| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |

## Variant Metrics

| variant | cumulative_net_total_return | max_drawdown | positive_years | annualized_return | annualized_volatility | sharpe | trade_count | cost_paid_total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| macro_gate_mcap | -0.08478285179122336 | -0.705896777852288 | 6 | -0.005896630518691048 | 0.21285379820090727 | -0.027702726324504528 | 190 | 0.07888653611891933 |
| kospi_buy_and_hold | 20.095177626449328 | -0.34485340853513224 | 14 | 0.2257327915799301 | 0.18914309081113953 | 1.1934498406041465 | 0 | 0.0 |
| cash | 0.0 | 0.0 | 0 | 0.0 | 0.0 | nan | 0 | 0.0 |

## C004 V3 Reference

| metric | value |
| --- | ---: |
| c004_v3_cumulative_net_total_return | -0.22013309027255956 |
| v4_minus_v3_cumulative_net_pp | 0.1353502384813362 |
| regime_on_share | 0.639344262295082 |
| yield_curve_favorable_quarters | 53 |
| yield_curve_total_quarters | 61 |

## Quarterly Year Breakdown

| year | macro_gate_mcap_net_total_return | kospi_buy_and_hold_net_total_return | cash_net_total_return | c004_v3_macro_gate_mcap_net_total_return | v4_minus_v3_macro_gate_mcap_return |
| --- | --- | --- | --- | --- | --- |
| 2010.0 | 0.0 | 0.3293489579737485 | 0.0 | 0.0 | 0.0 |
| 2011.0 | -0.14885508113656898 | 0.004079681302652238 | 0.0 | -0.198001292652205 | 0.04914621151563603 |
| 2012.0 | -0.046826673821664055 | 0.18731018909741426 | 0.0 | -0.0604777728674646 | 0.013651099045800544 |
| 2013.0 | -0.02819309888575494 | 0.06125736750042954 | 0.0 | -0.0281930988857552 | 2.6020852139652106e-16 |
| 2014.0 | -0.07836784555750498 | 0.05769800682302639 | 0.0 | -0.1015654450069127 | 0.02319759944940772 |
| 2015.0 | -0.02659435008960509 | 0.16501292442133764 | 0.0 | 0.0 | -0.02659435008960509 |
| 2017.0 | 0.09401472235486086 | 0.31675953872996554 | 0.0 | 0.0 | 0.09401472235486086 |
| 2018.0 | -0.4425899844893091 | -0.08401784948302582 | 0.0 | -0.4175765679163081 | -0.02501341657300099 |
| 2019.0 | 0.027749348305260213 | 0.17019485930094325 | 0.0 | 0.0 | 0.027749348305260213 |
| 2020.0 | 0.12199314377777393 | 0.5251287429311848 | 0.0 | 0.1219931437777737 | 2.220446049250313e-16 |
| 2021.0 | -0.12419945981131264 | 0.13170240063376726 | 0.0 | -0.1241994598113125 | -1.3877787807814457e-16 |
| 2022.0 | -0.09716827644733173 | -0.18442405395793493 | 0.0 | 0.0 | -0.09716827644733173 |
| 2023.0 | -0.056007063306024674 | 0.3279894204214897 | 0.0 | -0.0560070633060248 | 1.249000902703301e-16 |
| 2024.0 | 0.010394436376717886 | 0.034981455283805474 | 0.0 | 0.0979754142311724 | -0.08758097785445451 |
| 2025.0 | 0.567009224531813 | 1.047004780803555 | 0.0 | 0.5670092245318126 | 4.440892098500626e-16 |
| 2026.0 | 0.5621484118981519 | 0.7344109727369705 | 0.0 | 0.2686440849778979 | 0.293504326920254 |

## Verdict Summary

| hypothesis | description | value | threshold | passes |
| --- | --- | --- | --- | --- |
| H1 | V1 cumulative net total return > 0 | -0.08478285179122336 | 0.0 | False |
| H2 | V1 cumulative net >= V2 cumulative net - 30pp | -20.179960478240552 | -0.3 | False |
| H3 | V1 positive in at least 2 of 2010, 2025, 2026 | 2.0 | 2.0 | True |
| H4 | V1 max drawdown improves on V2 by at least 5pp | -0.36104336931715575 | -0.05 | True |
| H5 | V1 positive in >= 8 of 16 years | 6.0 | 8.0 | False |
| H6 | V1 net / V1 cost-0 >= 0.7 | -2.3091730255666163 | 0.7 | False |
| H7 | V1 v4 cumulative net improves on C004 v3 by >= 5pp | 0.1353502384813362 | 0.05 | True |
