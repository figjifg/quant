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
| signal_exit_policy | B002 exits at next trading-day open when fnv_5 <= 0 or inv_5 <= 0; NaN or missing signal components during hold are treated as <= 0 for conservative exit |
| calendar_source | derived from panel non-null KRX종가 rows |
| krx_close_derivation_summary | {"from_종가_fallback":969208,"native":172543} |
| n_tickers | 833 |
| n_trading_days | 2046 |

## IS Metrics

| metric | value |
| --- | ---: |
| total_return | -0.840174 |
| annualized_return | -0.312758 |
| annualized_volatility | 0.263015 |
| sharpe | -1.18912 |
| max_drawdown | -0.841277 |
| hit_rate | 0.391269 |
| average_trade_return | -0.00694816 |
| median_trade_return | -0.0110677 |
| profit_factor | 0.708215 |
| average_holding_period | 5.00329 |
| trade_count | 1214 |
| turnover | 241.565 |
| cost_paid_total | 0.369465 |
| return_before_cost | -0.470709 |
| return_after_cost | -0.840174 |
| exposure_ratio | 0.994905 |
| max_consecutive_losses | 16 |

## OOS Metrics

| metric | value |
| --- | ---: |
| total_return | 0.64064 |
| annualized_return | 0.165859 |
| annualized_volatility | 0.282793 |
| sharpe | 0.586505 |
| max_drawdown | -0.477413 |
| hit_rate | 0.419178 |
| average_trade_return | 0.00444002 |
| median_trade_return | -0.00810129 |
| profit_factor | 1.19158 |
| average_holding_period | 5.54247 |
| trade_count | 730 |
| turnover | 144.393 |
| cost_paid_total | 0.0754027 |
| return_before_cost | 1.11907 |
| return_after_cost | 0.64064 |
| exposure_ratio | 1.0121 |
| max_consecutive_losses | 14 |

## IS Baseline Comparison

| run | total_return | annualized_return | sharpe | max_drawdown | hit_rate | trade_count |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| headline | -0.840174 | -0.312758 | -1.18912 | -0.841277 | 0.391269 | 1214 |
| B0_cash | 0 | 0 | nan | 0 | 0 | 0 |
| B1_buy_and_hold | 0 | 0 | nan | 0 | 0 | 0 |
| B2_universe_5d_rebalance | nan | nan | nan | -0.331101 | 0.444225 | 3039 |
| B3_price_momentum | -0.999314 | -0.774631 | -1.15348 | -0.999593 | 0.350371 | 1213 |

## OOS Baseline Comparison

| run | total_return | annualized_return | sharpe | max_drawdown | hit_rate | trade_count |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| headline | 0.64064 | 0.165859 | 0.586505 | -0.477413 | 0.419178 | 730 |
| B0_cash | 0 | 0 | nan | 0 | 0 | 0 |
| B1_buy_and_hold | 0 | 0 | nan | 0 | 0 | 0 |
| B2_universe_5d_rebalance | nan | nan | nan | 0 | 0 | 0 |
| B3_price_momentum | -0.982867 | -0.7165 | -1.03473 | -0.993023 | 0.376847 | 812 |

## Cost Sensitivity

| multiplier | is_total_return | oos_total_return | full_total_return | cost_paid_total |
| --- | --- | --- | --- | --- |
| 0 | -0.643491 | 1.65956 | -0.0649966 | 0 |
| 1 | -0.840174 | 0.64064 | -0.741426 | 0.444867 |
| 2 | -0.928617 | 0.00980937 | -0.92892 | 0.612552 |
| 3 | -0.96824 | -0.379881 | -0.980579 | 0.690266 |

## Diagnostic Keys

- A002_replay
- cost_0_A002_replay
- cost_0_headline
- diagnostic_estimate_included
