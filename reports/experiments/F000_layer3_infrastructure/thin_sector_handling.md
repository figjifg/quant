# F000 Thin Sector Handling

## Summary

- E014 Top 4 selected sector-quarter rows: 244 total, 236 executable.
- Thin by Layer 3 allocation need: 2 total quarters / 8 rows; executable quarters: 0 / 0 rows.
- Thin by E014 carrier min_sector_stocks=3: 2 total quarters / 8 rows; executable quarters: 0 / 0 rows.

## Handling Plan

- For Layer 3, evaluate stock selection only on carrier-executable quarters (`execution_date - signal_date <= 10 calendar days`).
- Non-executable quarters, such as 2017-09-29 to 2017-10-10, remain cash exactly as the existing carrier does.
- If a future executable Layer 3 run encounters a thin selected sector, keep the carrier sector order frozen and leave the unfilled slot in cash unless the experiment ticket pre-registers a replacement rule.

## Selected Executable Sector Count Summary

| sector_code | sector_name | selected_executable_quarters | mean_eligible | min_eligible | max_eligible | thin_alloc_quarters | thin_min3_quarters |
| ----------- | ----------- | ---------------------------- | ------------- | ------------ | ------------ | ------------------- | ------------------ |
| 01          | 반도체/IT하드웨어  | 24                           | 11.62         | 6            | 18           | 0                   | 0                  |
| 02          | 자동차/운송장비    | 24                           | 8.5           | 6            | 11           | 0                   | 0                  |
| 03          | 2차전지/화학/소재  | 19                           | 16.79         | 10           | 29           | 0                   | 0                  |
| 04          | 철강금속        | 10                           | 4.2           | 3            | 7            | 0                   | 0                  |
| 05          | 조선/기계/산업재   | 37                           | 9.81          | 5            | 16           | 0                   | 0                  |
| 06          | 금융          | 14                           | 14.79         | 10           | 20           | 0                   | 0                  |
| 07          | 헬스케어        | 26                           | 6.46          | 3            | 15           | 0                   | 0                  |
| 08          | 인터넷/게임/SW   | 18                           | 13.22         | 9            | 16           | 0                   | 0                  |
| 09          | 소비재/유통      | 25                           | 7.84          | 3            | 15           | 0                   | 0                  |
| 10          | 음식료         | 19                           | 3.74          | 3            | 5            | 0                   | 0                  |
| 12          | 건설/부동산      | 20                           | 4.1           | 3            | 6            | 0                   | 0                  |

## Thin Rows Including Non-Executable Quarters

| signal_date | execution_date | calendar_gap_days | carrier_executable_quarter | regime_on | sector_code | sector_name | e014_top4_rank | eligible_sector_count | raw_dynamic_sector_count | layer3_required_holdings |
| ----------- | -------------- | ----------------- | -------------------------- | --------- | ----------- | ----------- | -------------- | --------------------- | ------------------------ | ------------------------ |
| 2015-12-30  | 2017-01-02     | 369               | False                      | False     | 01          | 반도체/IT하드웨어  | 2              | 0                     | 9                        | 1                        |
| 2015-12-30  | 2017-01-02     | 369               | False                      | False     | 03          | 2차전지/화학/소재  | 1              | 0                     | 18                       | 2                        |
| 2015-12-30  | 2017-01-02     | 369               | False                      | False     | 05          | 조선/기계/산업재   | 4              | 0                     | 8                        | 1                        |
| 2015-12-30  | 2017-01-02     | 369               | False                      | False     | 07          | 헬스케어        | 3              | 0                     | 6                        | 1                        |
| 2017-09-29  | 2017-10-10     | 11                | False                      | True      | 01          | 반도체/IT하드웨어  | 4              | 0                     | 10                       | 1                        |
| 2017-09-29  | 2017-10-10     | 11                | False                      | True      | 03          | 2차전지/화학/소재  | 2              | 0                     | 20                       | 1                        |
| 2017-09-29  | 2017-10-10     | 11                | False                      | True      | 07          | 헬스케어        | 1              | 0                     | 9                        | 2                        |
| 2017-09-29  | 2017-10-10     | 11                | False                      | True      | 10          | 음식료         | 3              | 0                     | 4                        | 1                        |
