# C006 Metrics Summary

## Metadata

| key | value |
| --- | --- |
| panels_used | ["research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv"] |
| period_start | 2010-01-04 |
| period_end | 2026-05-04 |
| excluded_years | [2016] |
| macro_gate | USDKRW yoy <= 0, VIX 60d avg <= VIX 240d avg, DXY yoy <= 0, US 2-10y curve spread > 0, USDCNY yoy <= 0; ON when score >= 2 |
| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |
| selection | top 5 by signal-date market cap, equal weight when macro gate ON |
| baselines | V2 cap-weighted KOSPI proxy buy-and-hold; V3 cash |
| c005_v4_reference | C005 v4 quarterly cumulative net -8.48%; cost-0 +3.67%; yearly columns read from C005 output files |
| usdcny_timing | DEXCHUS uses the aligned FRED observation available to the Korean signal date under src.data.macro_factors timing rules |
| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |
| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |
| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |
| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |

## Variant Metrics

| variant | cumulative_net_total_return | max_drawdown | positive_years | annualized_return | annualized_volatility | sharpe | trade_count | cost_paid_total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| macro_gate_mcap | -0.19668525538708892 | -0.7409909683881025 | 7 | -0.014513565169724019 | 0.2160264195470589 | -0.06718421385752035 | 200 | 0.08536152602069665 |
| kospi_buy_and_hold | 20.095177626449328 | -0.34485340853513224 | 14 | 0.2257327915799301 | 0.18914309081113953 | 1.1934498406041465 | 0 | 0.0 |
| cash | 0.0 | 0.0 | 0 | 0.0 | 0.0 | nan | 0 | 0.0 |

## C005 V4 Reference

| metric | value |
| --- | ---: |
| c005_v4_cumulative_net_total_return | -0.08478285179122336 |
| c005_v4_cost_0_cumulative_net_total_return | 0.03671567736697412 |
| v5_minus_v4_cumulative_net_pp | -0.11190240359586556 |
| v5_minus_v4_cost_0_cumulative_net_pp | -0.12059703574653968 |
| regime_on_share | 0.6721311475409836 |
| usdcny_favorable_quarters | 27 |
| usdcny_total_quarters | 57 |
| usdcny_yoy_usdkrw_yoy_correlation | 0.4952931252904423 |

## Quarterly Year Breakdown

| year | macro_gate_mcap_net_total_return | kospi_buy_and_hold_net_total_return | cash_net_total_return | c005_v4_macro_gate_mcap_net_total_return | v5_minus_v4_macro_gate_mcap_return |
| --- | --- | --- | --- | --- | --- |
| 2010.0 | 0.0 | 0.3293489579737485 | 0.0 | 0.0 | 0.0 |
| 2011.0 | -0.14885508113656898 | 0.004079681302652238 | 0.0 | -0.1488550811365689 | -8.326672684688674e-17 |
| 2012.0 | 0.02624455292442307 | 0.18731018909741426 | 0.0 | -0.046826673821664 | 0.07307122674608707 |
| 2013.0 | -0.028193098885755274 | 0.06125736750042954 | 0.0 | -0.0281930988857549 | -3.7470027081099033e-16 |
| 2014.0 | -0.0783678455575052 | 0.05769800682302639 | 0.0 | -0.0783678455575049 | -3.0531133177191805e-16 |
| 2015.0 | -0.0265943500896052 | 0.16501292442133764 | 0.0 | -0.026594350089605 | -2.0122792321330962e-16 |
| 2017.0 | 0.0940147223548613 | 0.31675953872996554 | 0.0 | 0.0940147223548608 | 4.996003610813204e-16 |
| 2018.0 | -0.44258998448930953 | -0.08401784948302582 | 0.0 | -0.4425899844893091 | -4.440892098500626e-16 |
| 2019.0 | 0.027749348305260657 | 0.17019485930094325 | 0.0 | 0.0277493483052602 | 4.579669976578771e-16 |
| 2020.0 | 0.12199314377777437 | 0.5251287429311848 | 0.0 | 0.1219931437777739 | 4.718447854656915e-16 |
| 2021.0 | -0.12419945981131231 | 0.13170240063376726 | 0.0 | -0.1241994598113126 | 2.914335439641036e-16 |
| 2022.0 | -0.2591599190160774 | -0.18442405395793493 | 0.0 | -0.0971682764473317 | -0.16199164256874568 |
| 2023.0 | -0.056007063306024785 | 0.3279894204214897 | 0.0 | -0.0560070633060246 | -1.8735013540549517e-16 |
| 2024.0 | 0.01039443637671722 | 0.034981455283805474 | 0.0 | 0.0103944363767178 | -5.793976409762536e-16 |
| 2025.0 | 0.5670092245318135 | 1.047004780803555 | 0.0 | 0.567009224531813 | 4.440892098500626e-16 |
| 2026.0 | 0.5621484118981523 | 0.7344109727369705 | 0.0 | 0.5621484118981519 | 4.440892098500626e-16 |

## Verdict Summary

| hypothesis | description | value | threshold | passes |
| --- | --- | --- | --- | --- |
| H1 | V1 cumulative net total return > 0 | -0.19668525538708892 | 0.0 | False |
| H2 | V1 cumulative net >= V2 cumulative net - 30pp | -20.291862881836416 | -0.3 | False |
| H3 | V1 positive in at least 2 of 2010, 2025, 2026 | 2.0 | 2.0 | True |
| H4 | V1 max drawdown improves on V2 by at least 5pp | -0.3961375598529703 | -0.05 | True |
| H5 | V1 positive in >= 8 of 16 years | 7.0 | 8.0 | False |
| H6 | V1 net / V1 cost-0 >= 0.7 | 2.3448029357975164 | 0.7 | True |
| H7 | V1 v5 cumulative net improves on C005 v4 by >= 5pp | -0.11190240359586556 | 0.05 | False |
| H8 | USDCNY yoy and USDKRW yoy correlation, descriptive only | 0.4952931252904423 | nan | <NA> |
