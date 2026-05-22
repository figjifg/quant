# S001-E Tax Model

## Verdict

PASS

## Scenarios

| scenario | gain_tax | sell_tax | commission | slippage | count | mean | median | hit_rate | sharpe_like |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| conservative_s000_gain_tax_22pct | 0.220000 | 0.000000 | 0.002500 | 0.000500 | 1622 | 0.100165 | 0.049673 | 0.666461 | 1.667185 |
| ordinary_domestic_listed_small_shareholder | 0.000000 | 0.001800 | 0.000150 | 0.000500 | 1622 | 0.146033 | 0.068276 | 0.678792 | 1.920054 |
| large_shareholder_special_case | 0.220000 | 0.001800 | 0.000150 | 0.000500 | 1622 | 0.103065 | 0.052573 | 0.675092 | 1.715454 |

## Policy

This script tests tax arithmetic only. It does not decide legal treatment for a real account.
