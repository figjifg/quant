# P005 D013 Production Constraints

## Metadata

| key | value |
| --- | --- |
| carrier | D013 unchanged: 10 variables, 5 blocks, 60-month z-score, threshold -0.2, market-cap top 5 |
| implementation_scope | strategy layer only; src/backtest/engine.py unchanged |
| constraints | {"max_single_weight": 0.25, "max_top2_weight": 0.5, "min_avg_traded_value_20d": 5000000000, "max_quarterly_turnover": 1.0, "aum_cap_krw": 10000000000} |

## Variant Metrics

| variant | cumulative_net_total_return | max_drawdown | positive_years | annualized_return | annualized_volatility | sharpe | trade_count | cost_paid_total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| factor_macro_gate_mcap | 2.5457702903350135 | -0.3392346174957135 | 7 | 0.08816790559736765 | 0.16530486303710384 | 0.5333654677635088 | 110 | 0.1099665202744996 |
| d013_baseline | 2.5457702903350135 | -0.3392346174957135 | 7 | 0.08816790559736765 | 0.16530486303710384 | 0.5333654677635088 | 110 | 0.1099665202744996 |
| kospi_buy_and_hold | 20.095177626449328 | -0.34485340853513224 | 14 | 0.2257327915799301 | 0.18914309081113953 | 1.1934498406041465 | 0 | 0.0 |
| cash | 0.0 | 0.0 | 0 | 0.0 | 0.0 | nan | 0 | 0.0 |

## D013 Comparison

| metric | p005_constrained | d013_baseline | difference |
| --- | --- | --- | --- |
| cumulative_net_total_return | 2.5457702903350135 | 2.5457702903350135 | 0.0 |
| sharpe | 0.5333654677635088 | 0.5333654677635088 | 0.0 |
| max_drawdown | -0.3392346174957135 | -0.3392346174957135 | 0.0 |
| trade_count | 110.0 | 110.0 | 0.0 |

## Constraint Binding Frequency

| constraint | binding_quarters | total_quarters | binding_frequency |
| --- | --- | --- | --- |
| single_weight_bound | 0 | 22 | 0.0 |
| top2_weight_bound | 0 | 22 | 0.0 |
| liquidity_bound | 0 | 22 | 0.0 |
| status_bound | 0 | 22 | 0.0 |
| turnover_bound | 0 | 22 | 0.0 |

## Constraint Binding Log

| signal_date | candidate_count_before | candidate_count_after | liquidity_removed_count | status_removed_count | single_weight_bound | top2_weight_bound | liquidity_bound | status_bound | quarterly_turnover | turnover_bound |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2017-03-31 | 5 | 5 | 0 | 0 | False | False | False | False | 1.0 | False |
| 2017-06-30 | 5 | 5 | 0 | 0 | False | False | False | False | 0.2 | False |
| 2017-12-28 | 5 | 5 | 0 | 0 | False | False | False | False | 0.2 | False |
| 2019-06-28 | 5 | 5 | 0 | 0 | False | False | False | False | 0.4 | False |
| 2019-09-30 | 5 | 5 | 0 | 0 | False | False | False | False | 0.4 | False |
| 2019-12-30 | 5 | 5 | 0 | 0 | False | False | False | False | 0.2 | False |
| 2020-03-31 | 5 | 5 | 0 | 0 | False | False | False | False | 0.2 | False |
| 2020-06-30 | 5 | 5 | 0 | 0 | False | False | False | False | 0.0 | False |
| 2020-09-29 | 5 | 5 | 0 | 0 | False | False | False | False | 0.2 | False |
| 2020-12-30 | 5 | 5 | 0 | 0 | False | False | False | False | 0.2 | False |
| 2021-03-31 | 5 | 5 | 0 | 0 | False | False | False | False | 0.2 | False |
| 2021-06-30 | 5 | 5 | 0 | 0 | False | False | False | False | 0.2 | False |
| 2021-09-30 | 5 | 5 | 0 | 0 | False | False | False | False | 0.2 | False |
| 2021-12-30 | 5 | 5 | 0 | 0 | False | False | False | False | 0.2 | False |
| 2023-09-27 | 5 | 5 | 0 | 0 | False | False | False | False | 0.4 | False |
| 2023-12-28 | 5 | 5 | 0 | 0 | False | False | False | False | 0.2 | False |
| 2024-03-29 | 5 | 5 | 0 | 0 | False | False | False | False | 0.0 | False |
| 2024-09-30 | 5 | 5 | 0 | 0 | False | False | False | False | 0.0 | False |
| 2025-06-30 | 5 | 5 | 0 | 0 | False | False | False | False | 0.2 | False |
| 2025-09-30 | 5 | 5 | 0 | 0 | False | False | False | False | 0.2 | False |
| 2025-12-30 | 5 | 5 | 0 | 0 | False | False | False | False | 0.2 | False |
| 2026-03-31 | 5 | 5 | 0 | 0 | False | False | False | False | 0.0 | False |
