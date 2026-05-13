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
| total_return | -0.334107 |
| annualized_return | -0.0798085 |
| annualized_volatility | 0.288496 |
| sharpe | -0.276636 |
| max_drawdown | -0.690719 |
| hit_rate | 0.455738 |
| average_trade_return | -0.00345641 |
| median_trade_return | -0.00997868 |
| profit_factor | 0.930373 |
| average_holding_period | 20 |
| trade_count | 305 |
| turnover | 61.0451 |
| cost_paid_total | 0.160793 |
| return_before_cost | -0.173314 |
| return_after_cost | -0.334107 |
| exposure_ratio | 0.984411 |
| max_consecutive_losses | 11 |

## OOS Metrics

| metric | value |
| --- | ---: |
| total_return | 0.49543 |
| annualized_return | 0.132847 |
| annualized_volatility | 0.30061 |
| sharpe | 0.441923 |
| max_drawdown | -0.468831 |
| hit_rate | 0.478049 |
| average_trade_return | 0.0132854 |
| median_trade_return | -0.00636877 |
| profit_factor | 1.30991 |
| average_holding_period | 19.6049 |
| trade_count | 205 |
| turnover | 41.0694 |
| cost_paid_total | 0.0805232 |
| return_before_cost | 0.622297 |
| return_after_cost | 0.49543 |
| exposure_ratio | 0.997328 |
| max_consecutive_losses | 9 |

## IS Baseline Comparison

| run | total_return | annualized_return | sharpe | max_drawdown | hit_rate | trade_count |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| headline | -0.334107 | -0.0798085 | -0.276636 | -0.690719 | 0.455738 | 305 |
| B0_cash | 0 | 0 | nan | 0 | 0 | 0 |
| B1_buy_and_hold | 0 | 0 | nan | 0 | 0 | 0 |
| B2_universe_5d_rebalance | nan | nan | nan | -0.331101 | 0.444225 | 3039 |
| B3_price_momentum | -0.999314 | -0.774631 | -1.15348 | -0.999593 | 0.350371 | 1213 |

## OOS Baseline Comparison

| run | total_return | annualized_return | sharpe | max_drawdown | hit_rate | trade_count |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| headline | 0.49543 | 0.132847 | 0.441923 | -0.468831 | 0.478049 | 205 |
| B0_cash | 0 | 0 | nan | 0 | 0 | 0 |
| B1_buy_and_hold | 0 | 0 | nan | 0 | 0 | 0 |
| B2_universe_5d_rebalance | nan | nan | nan | 0 | 0 | 0 |
| B3_price_momentum | -0.982867 | -0.7165 | -1.03473 | -0.993023 | 0.376847 | 812 |

## Cost Sensitivity

| multiplier | is_total_return | oos_total_return | full_total_return | cost_paid_total |
| --- | --- | --- | --- | --- |
| 0 | -0.187279 | 0.715893 | 0.329271 | 0 |
| 1 | -0.334107 | 0.49543 | -0.0508428 | 0.241316 |
| 2 | -0.454768 | 0.302598 | -0.323069 | 0.414475 |
| 3 | -0.553862 | 0.13402 | -0.517799 | 0.538645 |

## Diagnostic Keys

- bottom_quintile
- cap_only
- cost_0_cap_only
- cost_0_headline
- diagnostic_estimate_included
- middle_quintile
- top_decile
