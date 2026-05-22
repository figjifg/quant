# S001-G Corrected Smoke Test

Verdict: S-family permanently CLOSED

## Corrected Metrics

| signal | trade_count | gross_mean | net_mean | sharpe | hit_rate | placebo_trade_count | placebo_gross_mean | placebo_net_mean | placebo_sharpe | placebo_hit_rate | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| r1d_lt_m3_hold1 | 957 | 0.004071 | -0.000729 | -0.146535 | 0.453501 | 1135 | 0.001239 | -0.003561 | -1.587144 | 0.407930 | NULL_WEAK_CLOSE_S_FAMILY |
| r1d_lt_m3_hold3 | 677 | 0.012319 | 0.007519 | 0.465896 | 0.443131 | 1021 | 0.005268 | 0.000468 | 0.069014 | 0.453477 | NULL_WEAK_CLOSE_S_FAMILY |
| r1d_lt_m3_hold5 | 598 | 0.030571 | 0.025771 | 0.896401 | 0.491639 | 998 | 0.007523 | 0.002723 | 0.241763 | 0.471944 | NULL_WEAK_CLOSE_S_FAMILY |

## Placebo

| signal | trade_count | gross_mean | net_mean | sharpe | hit_rate |
| --- | --- | --- | --- | --- | --- |
| r1d_lt_m3_hold1 | 1135 | 0.001239 | -0.003561 | -1.587144 | 0.407930 |
| r1d_lt_m3_hold3 | 1021 | 0.005268 | 0.000468 | 0.069014 | 0.453477 |
| r1d_lt_m3_hold5 | 998 | 0.007523 | 0.002723 | 0.241763 | 0.471944 |

## Sanity Checks

| signal | impossible_return_fail_count | duplicate_signal_fail_count | max_exposure_ratio | exposure_fail_count | entry_exit_lineage_bad_count |
| --- | --- | --- | --- | --- | --- |
| r1d_lt_m3_hold1 | 0 | 0 | 0.400000 | 0 | 0 |
| r1d_lt_m3_hold3 | 1 | 0 | 0.260008 | 0 | 0 |
| r1d_lt_m3_hold5 | 4 | 0 | 0.260008 | 0 | 0 |

## 판정 기준

Null/weak는 gross < 1%, Sharpe < 1.5, 또는 placebo edge 없음 중 하나라도 해당할 때 적용했다. Strong가 나오더라도 S000 재활용 없이 S2-family를 새로 사전 등록해야 한다.
