# E001 Metrics Summary

## Metadata

| key | value |
| --- | --- |
| panels_used | ["research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv","research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv"] |
| is_start | 2018-01-02 |
| is_end | 2022-12-30 |
| oos_start | 2023-01-02 |
| oos_end | 2026-05-04 |
| estimate_row_policy | headline excludes rows where 거래대금추정여부 is True; 수급금액추정여부 is universally True in the Kiwoom panel and is not used as a filter; diagnostic_estimate_included reincludes the 거래대금추정여부 rows |
| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback; E003 price_gate_on uses kospi_proxy_5d_return from dynamic-Top100 traded-value-weighted returns, not an official KOSPI close |
| calendar_source | derived from panel non-null KRX종가 rows |
| krx_close_derivation_summary | {"from_종가_fallback":969208,"native":172543} |
| n_tickers | 833 |
| n_trading_days | 2046 |

## IS Metrics

| metric | value |
| --- | ---: |
| total_return | -0.546734 |
| annualized_return | -0.149433 |
| annualized_volatility | 0.385431 |
| sharpe | -0.387704 |
| max_drawdown | -0.722836 |
| hit_rate | 0.416393 |
| average_trade_return | -0.0050058 |
| median_trade_return | -0.0234893 |
| profit_factor | 0.9338 |
| average_holding_period | 20 |
| trade_count | 305 |
| turnover | 61.2779 |
| cost_paid_total | 0.167603 |
| return_before_cost | -0.379131 |
| return_after_cost | -0.546734 |
| exposure_ratio | 0.984415 |
| max_consecutive_losses | 9 |

## OOS Metrics

| metric | value |
| --- | ---: |
| total_return | 0.143022 |
| annualized_return | 0.0423049 |
| annualized_volatility | 0.419589 |
| sharpe | 0.100825 |
| max_drawdown | -0.655895 |
| hit_rate | 0.439024 |
| average_trade_return | 0.00915099 |
| median_trade_return | -0.0250371 |
| profit_factor | 1.14735 |
| average_holding_period | 19.6098 |
| trade_count | 205 |
| turnover | 40.8499 |
| cost_paid_total | 0.0572039 |
| return_before_cost | 0.274242 |
| return_after_cost | 0.143022 |
| exposure_ratio | 0.999417 |
| max_consecutive_losses | 6 |

## IS Baseline Comparison

| run | total_return | annualized_return | sharpe | max_drawdown | hit_rate | trade_count |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| headline | -0.546734 | -0.149433 | -0.387704 | -0.722836 | 0.416393 | 305 |
| B0_cash | 0 | 0 | nan | 0 | 0 | 0 |
| B1_buy_and_hold | 0 | 0 | nan | 0 | 0 | 0 |
| B2_universe_5d_rebalance | nan | nan | nan | -0.331101 | 0.444225 | 3039 |
| B3_price_momentum | -0.999314 | -0.774631 | -1.15348 | -0.999593 | 0.350371 | 1213 |

## OOS Baseline Comparison

| run | total_return | annualized_return | sharpe | max_drawdown | hit_rate | trade_count |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| headline | 0.143022 | 0.0423049 | 0.100825 | -0.655895 | 0.439024 | 205 |
| B0_cash | 0 | 0 | nan | 0 | 0 | 0 |
| B1_buy_and_hold | 0 | 0 | nan | 0 | 0 | 0 |
| B2_universe_5d_rebalance | nan | nan | nan | 0 | 0 | 0 |
| B3_price_momentum | -0.982867 | -0.7165 | -1.03473 | -0.993023 | 0.376847 | 812 |

## Cost Sensitivity

| multiplier | is_total_return | oos_total_return | full_total_return | cost_paid_total |
| --- | --- | --- | --- | --- |
| 0 | -0.44654 | 0.312351 | -0.301412 | 0 |
| 1 | -0.546734 | 0.143022 | -0.501713 | 0.224807 |
| 2 | -0.629036 | -0.00491707 | -0.644983 | 0.393346 |
| 3 | -0.696597 | -0.13411 | -0.747345 | 0.52007 |

## Diagnostic Keys

- A002_replay
- cost_0_A002_replay
- cost_0_headline
- diagnostic_estimate_included
