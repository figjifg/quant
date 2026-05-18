# P001 PIT Sector Validation Report

## Stage 3 Mapping Summary

- KRX PIT industries mapped: 41
- Custom groups: 01-12 plus 99 기타.
- Ambiguous buckets are recorded in manual_review_log.md.

## Stage 4 PIT Aggregate Summary

- stock_daily_rows: 402198
- mapped_row_ratio: 0.97821471
- sector_daily_rows: 50808
- quarter_count: 66
- quarters_ge_8_non_thin_groups: 64

## Stage 5 E014 PIT Result

- PIT cumulative_net_total_return: 1.46868241
- PIT Sharpe: 0.34582383
- PIT max_drawdown: -0.47384031
- Snapshot cumulative / Sharpe / MDD: 3.62108474 / 0.63118724 / -0.35641869
- D013 cumulative / Sharpe / MDD: 2.54577029 / 0.53336547 / -0.33923462

## Pass Criteria

| criterion | actual | threshold | passed |
| --- | ---: | ---: | --- |
| 1 cumulative >= 80% of E014 snapshot | 1.46868241 | 2.89686779 | False |
| 2 Sharpe >= 0.55 | 0.34582383 | 0.55000000 | False |
| 3 cumulative >= D013 + 50pp | 1.46868241 | 3.04577029 | False |
| 4 Top4 sector frequency Jaccard >= 0.70 | 0.60686963 | 0.70000000 | False |
| 5 Sector contribution top4 Jaccard >= 0.70 | 1.00000000 | 0.70000000 | True |

## Snapshot vs PIT Difference

- Cumulative return diff (PIT - snapshot): -2.15240233
- Sharpe diff (PIT - snapshot): -0.28536341
- MDD diff (PIT - snapshot): -0.11742161
- Trade-set Jaccard: 0.49659864
- Top4 sector frequency Jaccard: 0.60686963
- Sector contribution top4 Jaccard: 1.00000000

## Verdict

- FAIL
- Reason: PIT retained only 40.56% of snapshot cumulative return and Sharpe fell below 0.40; 4 of 5 registered pass criteria failed.
