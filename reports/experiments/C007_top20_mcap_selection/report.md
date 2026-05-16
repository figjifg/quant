# C007 Metrics Summary

## Metadata

| key | value |
| --- | --- |
| panels_used | ["research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv"] |
| period_start | 2010-01-04 |
| period_end | 2026-05-04 |
| excluded_years | [2016] |
| macro_gate | USDKRW yoy <= 0, VIX 60d avg <= VIX 240d avg, DXY yoy <= 0, US 2-10y curve spread > 0; ON when score >= 2 |
| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |
| selection | top 20 by signal-date market cap, equal weight when macro gate ON |
| baselines | V2 cap-weighted KOSPI proxy buy-and-hold; V3 cash |
| c005_n5_reference | C005 v4 N=5 quarterly cumulative net -8.48%; cost-0 +3.67%; yearly columns read from C005 output files |
| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |
| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |
| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |
| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |

## Variant Metrics

| variant | cumulative_net_total_return | max_drawdown | positive_years | annualized_return | annualized_volatility | sharpe | trade_count | cost_paid_total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| macro_gate_mcap | -0.19246936387400493 | -0.6591896777611987 | 6 | -0.014169154441090015 | 0.16910430635477564 | -0.08378943591988465 | 760 | 0.0806575339497054 |
| kospi_buy_and_hold | 20.095177626449328 | -0.34485340853513224 | 14 | 0.2257327915799301 | 0.18914309081113953 | 1.1934498406041465 | 0 | 0.0 |
| cash | 0.0 | 0.0 | 0 | 0.0 | 0.0 | nan | 0 | 0.0 |

## C005 N5 Reference

| metric | value |
| --- | ---: |
| c005_n5_cumulative_net_total_return | -0.08478285179122336 |
| c005_n5_cost_0_cumulative_net_total_return | 0.03671567736697412 |
| n20_minus_n5_cumulative_net_pp | -0.10768651208278157 |
| n20_minus_n5_cost_0_cumulative_net_pp | -0.1213499343898955 |
| c005_n5_trade_count_reference | 190 |
| regime_on_share | 0.639344262295082 |

## Quarterly Year Breakdown

| year | macro_gate_mcap_net_total_return | kospi_buy_and_hold_net_total_return | cash_net_total_return | c005_n5_macro_gate_mcap_net_total_return | n20_minus_n5_macro_gate_mcap_return |
| --- | --- | --- | --- | --- | --- |
| 2010.0 | 0.0 | 0.3293489579737485 | 0.0 | 0.0 | 0.0 |
| 2011.0 | -0.22614733546813492 | 0.004079681302652238 | 0.0 | -0.1488550811365689 | -0.07729225433156603 |
| 2012.0 | -0.06899247080919468 | 0.18731018909741426 | 0.0 | -0.046826673821664 | -0.022165796987530684 |
| 2013.0 | 0.08503064912825442 | 0.06125736750042954 | 0.0 | -0.0281930988857549 | 0.11322374801400932 |
| 2014.0 | -0.09311390744953385 | 0.05769800682302639 | 0.0 | -0.0783678455575049 | -0.014746061892028955 |
| 2015.0 | -0.022777519523102474 | 0.16501292442133764 | 0.0 | -0.026594350089605 | 0.0038168305665025257 |
| 2017.0 | 0.08311522216028155 | 0.31675953872996554 | 0.0 | 0.0940147223548608 | -0.010899500194579248 |
| 2018.0 | -0.26705095501512255 | -0.08401784948302582 | 0.0 | -0.4425899844893091 | 0.17553902947418654 |
| 2019.0 | 0.0324763861645847 | 0.17019485930094325 | 0.0 | 0.0277493483052602 | 0.004727037859324504 |
| 2020.0 | -0.017430997122411918 | 0.5251287429311848 | 0.0 | 0.1219931437777739 | -0.13942414090018582 |
| 2021.0 | -0.11940830814914793 | 0.13170240063376726 | 0.0 | -0.1241994598113126 | 0.004791151662164664 |
| 2022.0 | -0.10632798461509108 | -0.18442405395793493 | 0.0 | -0.0971682764473317 | -0.009159708167759378 |
| 2023.0 | 0.03414331505102197 | 0.3279894204214897 | 0.0 | -0.0560070633060246 | 0.09015037835704656 |
| 2024.0 | -0.06978222390844191 | 0.034981455283805474 | 0.0 | 0.0103944363767178 | -0.08017666028515971 |
| 2025.0 | 0.3251997046211774 | 1.047004780803555 | 0.0 | 0.567009224531813 | -0.2418095199106356 |
| 2026.0 | 0.41743185908331437 | 0.7344109727369705 | 0.0 | 0.5621484118981519 | -0.14471655281483753 |

## Verdict Summary

| hypothesis | description | value | threshold | passes |
| --- | --- | --- | --- | --- |
| H1 | V1 cumulative net total return > 0 | -0.19246936387400493 | 0.0 | False |
| H2 | V1 cumulative net >= V2 cumulative net - 30pp | -20.28764699032333 | -0.3 | False |
| H3 | V1 positive in at least 2 of 2010, 2025, 2026 | 2.0 | 2.0 | True |
| H4 | V1 max drawdown improves on V2 by at least 5pp | -0.3143362692260665 | -0.05 | True |
| H5 | V1 positive in >= 8 of 16 years | 6.0 | 8.0 | False |
| H6 | V1 net / V1 cost-0 >= 0.7 | 2.274130720163098 | 0.7 | True |
| H7 | V1 N=20 cumulative net improves on C005 N=5 by >= 5pp | -0.10768651208278157 | 0.05 | False |
| H8 | V1 N=20 2018 net total return, descriptive concentration check | -0.26705095501512255 | nan | <NA> |
