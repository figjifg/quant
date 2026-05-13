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
| total_return | -0.307262 |
| annualized_return | -0.0723393 |
| annualized_volatility | 0.244953 |
| sharpe | -0.29532 |
| max_drawdown | -0.550334 |
| hit_rate | 0.3675 |
| average_trade_return | -0.00210606 |
| median_trade_return | -0.0377818 |
| profit_factor | 0.949331 |
| average_holding_period | 14.6275 |
| trade_count | 400 |
| turnover | 79.3682 |
| cost_paid_total | 0.249117 |
| return_before_cost | -0.0581443 |
| return_after_cost | -0.307262 |
| exposure_ratio | 0.962452 |
| max_consecutive_losses | 20 |

## OOS Metrics

| metric | value |
| --- | ---: |
| total_return | 0.580792 |
| annualized_return | 0.152508 |
| annualized_volatility | 0.283145 |
| sharpe | 0.538621 |
| max_drawdown | -0.281816 |
| hit_rate | 0.419847 |
| average_trade_return | 0.0110066 |
| median_trade_return | -0.0249346 |
| profit_factor | 1.28855 |
| average_holding_period | 14.9275 |
| trade_count | 262 |
| turnover | 52.1703 |
| cost_paid_total | 0.13101 |
| return_before_cost | 0.773448 |
| return_after_cost | 0.580792 |
| exposure_ratio | 0.981841 |
| max_consecutive_losses | 8 |

## IS Baseline Comparison

| run | total_return | annualized_return | sharpe | max_drawdown | hit_rate | trade_count |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| headline | -0.307262 | -0.0723393 | -0.29532 | -0.550334 | 0.3675 | 400 |
| B0_cash | 0 | 0 | nan | 0 | 0 | 0 |
| B1_buy_and_hold | 0 | 0 | nan | 0 | 0 | 0 |
| B2_universe_5d_rebalance | nan | nan | nan | -0.331101 | 0.444225 | 3039 |
| B3_price_momentum | -0.999314 | -0.774631 | -1.15348 | -0.999593 | 0.350371 | 1213 |

## OOS Baseline Comparison

| run | total_return | annualized_return | sharpe | max_drawdown | hit_rate | trade_count |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| headline | 0.580792 | 0.152508 | 0.538621 | -0.281816 | 0.419847 | 262 |
| B0_cash | 0 | 0 | nan | 0 | 0 | 0 |
| B1_buy_and_hold | 0 | 0 | nan | 0 | 0 | 0 |
| B2_universe_5d_rebalance | nan | nan | nan | 0 | 0 | 0 |
| B3_price_momentum | -0.982867 | -0.7165 | -1.03473 | -0.993023 | 0.376847 | 812 |

## Cost Sensitivity

| multiplier | is_total_return | oos_total_return | full_total_return | cost_paid_total |
| --- | --- | --- | --- | --- |
| 0 | -0.0997659 | 0.881477 | 0.664825 | 0 |
| 1 | -0.307262 | 0.580792 | 0.0749718 | 0.380128 |
| 2 | -0.467601 | 0.327031 | -0.307359 | 0.62155 |
| 3 | -0.591349 | 0.113045 | -0.55466 | 0.773504 |

## Diagnostic Keys

- E001_replay
- cap_only
- cost_0_E001_replay
- cost_0_headline
- diagnostic_estimate_included
- stop_only
