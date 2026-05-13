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
| total_return | -0.31403 |
| annualized_return | -0.0742006 |
| annualized_volatility | 0.205743 |
| sharpe | -0.360647 |
| max_drawdown | -0.451035 |
| hit_rate | 0.469388 |
| average_trade_return | -0.00519771 |
| median_trade_return | -0.0105359 |
| profit_factor | 0.881494 |
| average_holding_period | 20 |
| trade_count | 245 |
| turnover | 48.9658 |
| cost_paid_total | 0.126454 |
| return_before_cost | -0.187576 |
| return_after_cost | -0.31403 |
| exposure_ratio | 0.781355 |
| max_consecutive_losses | 11 |

## OOS Metrics

| metric | value |
| --- | ---: |
| total_return | 0.587581 |
| annualized_return | 0.15404 |
| annualized_volatility | 0.249436 |
| sharpe | 0.617553 |
| max_drawdown | -0.365426 |
| hit_rate | 0.46 |
| average_trade_return | 0.0189863 |
| median_trade_return | -0.0156652 |
| profit_factor | 1.48492 |
| average_holding_period | 20 |
| trade_count | 150 |
| turnover | 27.593 |
| cost_paid_total | 0.0643416 |
| return_before_cost | 0.682685 |
| return_after_cost | 0.587581 |
| exposure_ratio | 0.760637 |
| max_consecutive_losses | 10 |

## IS Baseline Comparison

| run | total_return | annualized_return | sharpe | max_drawdown | hit_rate | trade_count |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| headline | -0.31403 | -0.0742006 | -0.360647 | -0.451035 | 0.469388 | 245 |
| B0_cash | 0 | 0 | nan | 0 | 0 | 0 |
| B1_buy_and_hold | 0 | 0 | nan | 0 | 0 | 0 |
| B2_universe_5d_rebalance | nan | nan | nan | -0.331101 | 0.444225 | 3039 |
| B3_price_momentum | -0.999314 | -0.774631 | -1.15348 | -0.999593 | 0.350371 | 1213 |

## OOS Baseline Comparison

| run | total_return | annualized_return | sharpe | max_drawdown | hit_rate | trade_count |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| headline | 0.587581 | 0.15404 | 0.617553 | -0.365426 | 0.46 | 150 |
| B0_cash | 0 | 0 | nan | 0 | 0 | 0 |
| B1_buy_and_hold | 0 | 0 | nan | 0 | 0 | 0 |
| B2_universe_5d_rebalance | nan | nan | nan | 0 | 0 | 0 |
| B3_price_momentum | -0.982867 | -0.7165 | -1.03473 | -0.993023 | 0.376847 | 812 |

## Cost Sensitivity

| multiplier | is_total_return | oos_total_return | full_total_return | cost_paid_total |
| --- | --- | --- | --- | --- |
| 0 | -0.19538 | 0.757223 | 0.394476 | 0 |
| 1 | -0.31403 | 0.587581 | 0.0740649 | 0.190795 |
| 2 | -0.415493 | 0.433833 | -0.173441 | 0.338063 |
| 3 | -0.502213 | 0.294534 | -0.364466 | 0.451699 |

## Diagnostic Keys

- cap_only
- cost_0_cap_only
- cost_0_headline
- diagnostic_estimate_included
- double_gate
- inverted_gate
- price_gate
