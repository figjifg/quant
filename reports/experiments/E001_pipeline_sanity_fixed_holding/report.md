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
| integrated_column_policy | KRX종가 preferred; 종가 only as pre-NXT fallback |
| calendar_source | derived from panel non-null KRX종가 rows |
| krx_close_derivation_summary | {"from_종가_fallback":969208,"native":172543} |
| n_tickers | 833 |
| n_trading_days | 2046 |

## IS Metrics

| metric | value |
| --- | ---: |
| total_return | -0.430824 |
| annualized_return | -0.108879 |
| annualized_volatility | 0.295134 |
| sharpe | -0.368913 |
| max_drawdown | -0.542476 |
| hit_rate | 0.460082 |
| average_trade_return | -0.00160813 |
| median_trade_return | -0.0048831 |
| profit_factor | 0.930817 |
| average_holding_period | 5 |
| trade_count | 1215 |
| turnover | 241.949 |
| cost_paid_total | 0.634994 |
| return_before_cost | 0.20417 |
| return_after_cost | -0.430824 |
| exposure_ratio | 0.984529 |
| max_consecutive_losses | 13 |

## OOS Metrics

| metric | value |
| --- | ---: |
| total_return | 0.164948 |
| annualized_return | 0.0484618 |
| annualized_volatility | 0.308448 |
| sharpe | 0.157115 |
| max_drawdown | -0.417525 |
| hit_rate | 0.466667 |
| average_trade_return | 0.00183579 |
| median_trade_return | -0.00462888 |
| profit_factor | 1.07604 |
| average_holding_period | 4.99259 |
| trade_count | 810 |
| turnover | 161.89 |
| cost_paid_total | 0.263075 |
| return_before_cost | 0.633512 |
| return_after_cost | 0.164948 |
| exposure_ratio | 0.999225 |
| max_consecutive_losses | 14 |

## IS Baseline Comparison

| run | total_return | annualized_return | sharpe | max_drawdown | hit_rate | trade_count |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| headline | -0.430824 | -0.108879 | -0.368913 | -0.542476 | 0.460082 | 1215 |
| B0_cash | 0 | 0 | nan | 0 | 0 | 0 |
| B1_buy_and_hold | 0 | 0 | nan | 0 | 0 | 0 |
| B2_universe_5d_rebalance | nan | nan | nan | -0.331101 | 0.444225 | 3039 |
| B3_price_momentum | -0.999314 | -0.774631 | -1.15348 | -0.999593 | 0.350371 | 1213 |

## OOS Baseline Comparison

| run | total_return | annualized_return | sharpe | max_drawdown | hit_rate | trade_count |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| headline | 0.164948 | 0.0484618 | 0.157115 | -0.417525 | 0.466667 | 810 |
| B0_cash | 0 | 0 | nan | 0 | 0 | 0 |
| B1_buy_and_hold | 0 | 0 | nan | 0 | 0 | 0 |
| B2_universe_5d_rebalance | nan | nan | nan | 0 | 0 | 0 |
| B3_price_momentum | -0.982867 | -0.7165 | -1.03473 | -0.993023 | 0.376847 | 812 |

## Cost Sensitivity

| multiplier | is_total_return | oos_total_return | full_total_return | cost_paid_total |
| --- | --- | --- | --- | --- |
| 0 | 0.267787 | 0.994171 | 1.4939 | 0 |
| 1 | -0.430824 | 0.164948 | -0.345939 | 0.898069 |
| 2 | -0.745191 | -0.320912 | -0.829313 | 1.06559 |
| 3 | -0.886252 | -0.604987 | -0.955679 | 1.06502 |

## Diagnostic Keys

- diagnostic_estimate_included
