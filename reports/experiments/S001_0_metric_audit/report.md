# S001-0 Metric / Implementation Audit

## Verdict

FAIL. S000 recalculation is required before any S-family promotion because timing, filtered-row execution, overlap/leverage, and random-control checks failed.

## Audit Results

| item | status | check | evidence |
| --- | --- | --- | --- |
| return_unit | PASS | gross/net mean fields match decimal per-trade means; not cumulative or annualized. | max_reported_mean_diff=5.55e-17; max_abs_trade_return=297.750000 |
| entry_exit_alignment | FAIL | Signal must be T close, entry T+1 open, exit after holding horizon on KRX trading calendar. | bad_entry_rows=1533; bad_exit_rows=1353; S000 recalculation required if nonzero. |
| filtered_panel_row_jump | FAIL | S000 implementation built trades from the post-filtered panel; next row can skip KRX trading days. | rows_matching_filtered_ticker_next_row_not_raw_calendar=1533; S000 recalculation required if nonzero. |
| no_lookahead_dynamic_universe | WARN | Rows are dynamic-universe filtered, but S000 used same-day membership; PIT T-1 membership proof is not present. | missing_member_rows=0; non_member_rows=0; S000 recalculation required unless T-1 membership is reconstructed. |
| adjusted_price | FAIL | KRX close derivation is internally consistent, but split/right-adjustment treatment is not documented in S000 artifacts. | 종가_ne_KRX종가_rows=0; adjustment_columns_present=false; max_abs_trade_return=297.750000; S000 recalculation required if extreme returns are corporate-action artifacts. |
| duplicate_event | WARN | No identical signal/ticker/date duplicates are allowed; consecutive signal handling should be explicit. | duplicate_rows=0; consecutive_same_signal_ticker_rows=374. |
| overlap_leverage | FAIL | S000 reports per-trade means; applying each overlapping trade as 100% notional creates leverage unless sleeve NAV is simulated. | max_new_signals_same_day=18; max_active_positions=122; S000 recalculation required for portfolio-level claim. |
| tax_cost_application | PASS | S000 applies two-way commission/slippage and gain-only 22% tax in return space. | max_net_recompute_diff=4.44e-16; positive_tax_bad=0; negative_tax_bad=0. |
| random_control | FAIL | S000 random control samples arbitrary panel rows, not same signal dates/universe/counts; market rebound day effect is not controlled. | date_count_match_rate=0.109737; S000 recalculation required with date-matched controls. |

## Detail

| metric | value |
| --- | --- |
| trade_count | 3495 |
| signals | 6 |
| bad_entry_rows | 1533 |
| bad_exit_rows | 1353 |
| max_active_positions | 122 |

## Source

Read-only inputs: `/home/jin/code/quant/reports/experiments/S000_korean_short_mean_reversion_feasibility` and equity panels. No frozen strategy or engine files were modified.
