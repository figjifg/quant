# C004 Metrics Summary

## Metadata

| key | value |
| --- | --- |
| panels_used | ["research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv"] |
| period_start | 2010-01-04 |
| period_end | 2026-05-04 |
| excluded_years | [2016] |
| macro_gate | USDKRW yoy <= 0, VIX 60d avg <= VIX 240d avg, DXY yoy <= 0; ON when score >= 2 |
| rebalance | signal on last available KRX trading day of Mar/Jun/Sep/Dec; execution at next KRX open |
| selection | top 5 by signal-date market cap, equal weight when macro gate ON |
| baselines | V2 cap-weighted KOSPI proxy buy-and-hold; V3 cash |
| c003_monthly_reference | C003 monthly cumulative net -54.17%; monthly columns read from C003 output files |
| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |
| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |
| open_price_policy | 시가 treated as KRX 09:00 open per AGENTS.md Kiwoom panel verification |
| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |

## Variant Metrics

| variant | cumulative_net_total_return | max_drawdown | positive_years | annualized_return | annualized_volatility | sharpe | trade_count | cost_paid_total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| macro_gate_mcap | -0.22013309027255956 | -0.7472593949754252 | 4 | -0.016460442770705352 | 0.19039235271884525 | -0.08645537772734335 | 125 | 0.04710251574424255 |
| kospi_buy_and_hold | 20.095177626449328 | -0.34485340853513224 | 14 | 0.2257327915799301 | 0.18914309081113953 | 1.1934498406041465 | 0 | 0.0 |
| cash | 0.0 | 0.0 | 0 | 0.0 | 0.0 | nan | 0 | 0.0 |

## C003 Monthly Reference

| metric | value |
| --- | ---: |
| c003_monthly_cumulative_net_total_return | -0.5417073809779971 |
| quarterly_minus_monthly_cumulative_net_pp | 0.3215742907054375 |
| c003_monthly_trade_count_reference | 370 |

## Quarterly Year Breakdown

| year | macro_gate_mcap_net_total_return | kospi_buy_and_hold_net_total_return | cash_net_total_return | c003_monthly_macro_gate_mcap_net_total_return | quarterly_minus_monthly_macro_gate_mcap_return |
| --- | --- | --- | --- | --- | --- |
| 2010.0 | 0.0 | 0.3293489579737485 | 0.0 | 0.0 | 0.0 |
| 2011.0 | -0.198001292652205 | 0.004079681302652238 | 0.0 | -0.1320839987819283 | -0.0659172938702767 |
| 2012.0 | -0.060477772867464696 | 0.18731018909741426 | 0.0 | -0.0615247731583582 | 0.001047000290893503 |
| 2013.0 | -0.028193098885755274 | 0.06125736750042954 | 0.0 | -0.0486191567017684 | 0.020426057816013123 |
| 2014.0 | -0.10156544500691278 | 0.05769800682302639 | 0.0 | -0.1252101052934492 | 0.023644660286536417 |
| 2015.0 | 0.0 | 0.16501292442133764 | 0.0 | 0.0 | 0.0 |
| 2017.0 | 0.0 | 0.31675953872996554 | 0.0 | -0.0155511542886437 | 0.0155511542886437 |
| 2018.0 | -0.41757656791630815 | -0.08401784948302582 | 0.0 | -0.4446780927249639 | 0.02710152480865574 |
| 2019.0 | 0.0 | 0.17019485930094325 | 0.0 | 0.0 | 0.0 |
| 2020.0 | 0.1219931437777737 | 0.5251287429311848 | 0.0 | 0.2295218797648426 | -0.10752873598706889 |
| 2021.0 | -0.12419945981131253 | 0.13170240063376726 | 0.0 | -0.1732887207530479 | 0.04908926094173538 |
| 2022.0 | 0.0 | -0.18442405395793493 | 0.0 | 0.0 | 0.0 |
| 2023.0 | -0.056007063306024896 | 0.3279894204214897 | 0.0 | -0.0738748326853482 | 0.0178677693793233 |
| 2024.0 | 0.0979754142311724 | 0.034981455283805474 | 0.0 | -0.0521865608453848 | 0.1501619750765572 |
| 2025.0 | 0.5670092245318126 | 1.047004780803555 | 0.0 | 0.1268401227916236 | 0.440169101740189 |
| 2026.0 | 0.26864408497789793 | 0.7344109727369705 | 0.0 | 0.2418885178645053 | 0.026755567113392636 |

## Verdict Summary

| hypothesis | description | value | threshold | passes |
| --- | --- | --- | --- | --- |
| H1 | V1 cumulative net total return > 0 | -0.22013309027255956 | 0.0 | False |
| H2 | V1 cumulative net >= V2 cumulative net - 30pp | -20.315310716721886 | -0.3 | False |
| H3 | V1 positive in at least 2 of 2010, 2025, 2026 | 2.0 | 2.0 | True |
| H4 | V1 max drawdown improves on V2 by at least 5pp | -0.4024059864402929 | -0.05 | True |
| H5 | V1 positive in >= 8 of 16 years | 4.0 | 8.0 | False |
| H6 | V1 net / V1 cost-0 >= 0.7 | 1.4336340978346231 | 0.7 | True |
| H7 | V1 quarterly cumulative net improves on C003 monthly by >= 10pp | 0.3215742907054375 | 0.1 | True |
