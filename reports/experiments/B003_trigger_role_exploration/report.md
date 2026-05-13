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
| signal_exit_policy | Signal-reversal exits at next trading-day open when fnv_5 <= 0 or inv_5 <= 0; NaN or missing signal components during hold are treated as <= 0 for conservative exit |
| calendar_source | derived from panel non-null KRX종가 rows |
| krx_close_derivation_summary | {"from_종가_fallback":969208,"native":172543} |
| n_tickers | 833 |
| n_trading_days | 2046 |

## IS Metrics

| metric | value |
| --- | ---: |
| total_return |  |
| annualized_return |  |
| annualized_volatility |  |
| sharpe |  |
| max_drawdown |  |
| hit_rate |  |
| average_trade_return |  |
| median_trade_return |  |
| profit_factor |  |
| average_holding_period |  |
| trade_count |  |
| turnover |  |
| cost_paid_total |  |
| return_before_cost |  |
| return_after_cost |  |
| exposure_ratio |  |
| max_consecutive_losses |  |

## OOS Metrics

| metric | value |
| --- | ---: |
| total_return |  |
| annualized_return |  |
| annualized_volatility |  |
| sharpe |  |
| max_drawdown |  |
| hit_rate |  |
| average_trade_return |  |
| median_trade_return |  |
| profit_factor |  |
| average_holding_period |  |
| trade_count |  |
| turnover |  |
| cost_paid_total |  |
| return_before_cost |  |
| return_after_cost |  |
| exposure_ratio |  |
| max_consecutive_losses |  |

## IS Baseline Comparison

| run | total_return | annualized_return | sharpe | max_drawdown | hit_rate | trade_count |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| headline |  |  |  |  |  |  |
| B0_cash | 0 | 0 | nan | 0 | 0 | 0 |
| B1_buy_and_hold | 0 | 0 | nan | 0 | 0 | 0 |
| B2_universe_5d_rebalance | nan | nan | nan | -0.331101 | 0.444225 | 3039 |
| B3_price_momentum | -0.999314 | -0.774631 | -1.15348 | -0.999593 | 0.350371 | 1213 |

## OOS Baseline Comparison

| run | total_return | annualized_return | sharpe | max_drawdown | hit_rate | trade_count |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| headline |  |  |  |  |  |  |
| B0_cash | 0 | 0 | nan | 0 | 0 | 0 |
| B1_buy_and_hold | 0 | 0 | nan | 0 | 0 | 0 |
| B2_universe_5d_rebalance | nan | nan | nan | 0 | 0 | 0 |
| B3_price_momentum | -0.982867 | -0.7165 | -1.03473 | -0.993023 | 0.376847 | 812 |

## Cost Sensitivity

| run | multiplier | is_total_return | oos_total_return | full_total_return | cost_paid_total |
| --- | --- | --- | --- | --- | --- |
| T3_acceleration | 0 | -0.544953 | 1.87452 | 0.289896 | 0 |
| T3_acceleration | 1 | -0.792557 | 0.780086 | -0.635864 | 0.540412 |
| T3_acceleration | 2 | -0.90578 | 0.0998862 | -0.89781 | 0.725219 |
| T3_acceleration | 3 | -0.957364 | -0.321932 | -0.971493 | 0.800894 |

## Diagnostic Keys

- T1_immediate
- T2_freshness
- T3_acceleration
- T4_persistence_3d
- cost_0_T1_immediate
- cost_0_T2_freshness
- cost_0_T3_acceleration
- cost_0_T4_persistence_3d
- diagnostic_estimate_included
