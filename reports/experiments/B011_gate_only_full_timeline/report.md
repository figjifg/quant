# B011 Metrics Summary

## Metadata

| key | value |
| --- | --- |
| panels_used | ["research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv"] |
| period_start | 2010-01-04 |
| period_end | 2026-05-04 |
| excluded_years | [2016] |
| regime_gate | KOSPI proxy level > 200-day SMA; B004(c) frozen gate window |
| selection | top 5 by prior-day market cap, equal weight when gate ON |
| exit | exit_on_gate_off plus universe exit when name leaves eligibility |
| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is not used as a filter |
| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback where absent |
| calendar_source | derived from panel non-null KRX종가 rows after excluding configured years |

## Variant Metrics

| variant | cumulative_net_total_return | max_drawdown | positive_years | annualized_return | annualized_volatility | sharpe | trade_count | hit_rate | cost_paid_total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| gate_only_mcap | -0.9479231572258411 | -0.9804205228386049 | 5 | -0.1790255226382047 | 0.24405658161577945 | -0.7335410561475709 | 3040 | 0.42335526315789473 | 0.48023055988463986 |
| kospi_buy_and_hold | 20.095177626449328 | -0.34485340853513224 | 14 | 0.2257327915799301 | 0.18914309081113953 | 1.1934498406041465 | 0 | 0.0 | 0.0 |
| cash | 0.0 | 0.0 | 0 | 0.0 | 0.0 | nan | 0 | 0.0 | 0.0 |

## Gate Only Year Breakdown

| year | gate_only_mcap_net_total_return | kospi_buy_and_hold_net_total_return | cash_net_total_return |
| --- | --- | --- | --- |
| 2010.0 | 0.11059905860255848 | 0.3293489579737485 | 0.0 |
| 2011.0 | -0.3199388893865034 | 0.004079681302652238 | 0.0 |
| 2012.0 | -0.3286388908270661 | 0.18731018909741426 | 0.0 |
| 2013.0 | -0.32384177298656003 | 0.06125736750042954 | 0.0 |
| 2014.0 | -0.3123462365373184 | 0.05769800682302639 | 0.0 |
| 2015.0 | -0.4690686643223181 | 0.16501292442133764 | 0.0 |
| 2017.0 | 0.014508608954979074 | 0.31675953872996554 | 0.0 |
| 2018.0 | -0.409472472880848 | -0.08401784948302582 | 0.0 |
| 2019.0 | -0.08416529682416707 | 0.17019485930094325 | 0.0 |
| 2020.0 | 0.2187269658120592 | 0.5251287429311848 | 0.0 |
| 2021.0 | -0.3589646546557287 | 0.13170240063376726 | 0.0 |
| 2022.0 | -0.2062743388306688 | -0.18442405395793493 | 0.0 |
| 2023.0 | -0.2927515135696932 | 0.3279894204214897 | 0.0 |
| 2024.0 | -0.08876495506913429 | 0.034981455283805474 | 0.0 |
| 2025.0 | 0.279738447597665 | 1.047004780803555 | 0.0 |
| 2026.0 | 0.46247194654215784 | 0.7344109727369705 | 0.0 |

## Gate Only Summary

| h1_cumulative_survival_pass | h1_v1_cumulative_net_total_return | h2_vs_kospi_pass | h2_v1_minus_v2_cumulative_delta | h3_spike_capture_pass | h3_v1_2010_net | h3_v1_2025_net | h3_v1_2026_net | h4_drawdown_protection_pass | h4_v1_max_drawdown | h4_v2_max_drawdown | h5_positive_years_pass | h5_v1_positive_years | candidate_year_count | hypotheses_passed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| False | -0.9479231572258411 | False | -21.04310078367517 | True | 0.11059905860255848 | 0.279738447597665 | 0.46247194654215784 | True | -0.9804205228386049 | -0.34485340853513224 | False | 5 | 16 | 2 |
