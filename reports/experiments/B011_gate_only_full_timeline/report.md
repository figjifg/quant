# B011 Metrics Summary

## Metadata

| key | value |
| --- | --- |
| panels_used | ["research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv", "research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv"] |
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
| gate_only_mcap | -0.778333940950358 | -0.9166595878432839 | 4 | -0.16876176710035373 | 0.2513601296393719 | -0.6713943350621175 | 1785 | 0.4296918767507003 | 0.45372341504353275 |
| kospi_buy_and_hold | 9.054997364678258 | -0.21555700105536646 | 9 | 0.327332339669848 | 0.1915495651468043 | 1.7088649583671947 | 0 | 0.0 | 0.0 |
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
| 2018.0 | nan | nan | nan |
| 2019.0 | nan | nan | nan |
| 2020.0 | nan | nan | nan |
| 2021.0 | nan | nan | nan |
| 2022.0 | nan | nan | nan |
| 2023.0 | nan | nan | nan |
| 2024.0 | nan | nan | nan |
| 2025.0 | 0.29259062574694705 | 1.0470047808035559 | 0.0 |
| 2026.0 | 0.4624719465421576 | 0.7344109727369725 | 0.0 |

## Gate Only Summary

| h1_cumulative_survival_pass | h1_v1_cumulative_net_total_return | h2_vs_kospi_pass | h2_v1_minus_v2_cumulative_delta | h3_spike_capture_pass | h3_v1_2010_net | h3_v1_2025_net | h3_v1_2026_net | h4_drawdown_protection_pass | h4_v1_max_drawdown | h4_v2_max_drawdown | h5_positive_years_pass | h5_v1_positive_years | candidate_year_count | hypotheses_passed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| False | -0.778333940950358 | False | -9.833331305628615 | True | 0.11059905860255848 | 0.29259062574694705 | 0.4624719465421576 | True | -0.9166595878432839 | -0.21555700105536646 | False | 4 | 16 | 2 |
