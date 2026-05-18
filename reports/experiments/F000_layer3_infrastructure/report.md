# F000 Layer 3 Infrastructure Report

## Verdict: PROCEED

- D013 reproduction: OK
- E014 reproduction: OK
- D013 direct top 5 feasible across carrier-executable quarters: True
- E014 2/1/1/1 thin executable quarters: 0
- Non-executable thin quarters retained as cash by carrier: 2

## Stock Data Quality
- foreign_net_buy_amount_missing_pct: 9.471348%
- institution_net_buy_amount_missing_pct: 9.471348%
- foreign_net_buy_shares_missing_pct: 9.471348%
- institution_net_buy_shares_missing_pct: 9.471348%
- traded_value_missing_pct_mean: 0.000000%
- market_cap_missing_pct_mean: 0.000000%
- daily_return_missing_pct_mean: 0.000000%
- krx_close_missing_pct_mean: 0.000000%
- open_missing_pct_mean: 0.000000%

## Universe Size Distribution
- Carrier-executable quarter-end eligible universe count: mean 96.27, min 91, max 100
- Regime-ON and executable quarter-end eligible universe count: mean 96.59, min 91, max 100
- Raw dynamic top100 count over executable quarters: mean 100.00, min 100, max 100

## E014 Top 4 Sector Counts On Executable Quarters

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

## Artifacts

- carrier_reproduction.md
- stock_data_quality.csv
- universe_size_by_quarter.csv
- thin_sector_handling.md
