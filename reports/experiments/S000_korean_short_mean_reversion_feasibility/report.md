# S000 Korean Short-Horizon Mean Reversion Feasibility

Verdict: PASS

## Gate Results

| signal | trade_count | gross_mean | net_mean | gross_hit_rate | net_hit_rate | sharpe | random_trade_count | random_gross_mean | random_net_mean | random_gross_hit_rate | random_net_hit_rate | random_sharpe | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| r1d_lt_m3_hold1 | 606 | 0.051984 | 0.029961 | 0.689769 | 0.666667 | 5.117086 | 604 | 0.003454 | -0.006115 | 0.461921 | 0.365894 | -2.524994 | PASS_diagnostic_only |
| r1d_lt_m3_hold3 | 530 | 0.182369 | 0.124691 | 0.673585 | 0.656604 | 1.660757 | 522 | 0.005537 | -0.008639 | 0.473180 | 0.409962 | -0.684607 | PASS_diagnostic_only |
| r1d_lt_m3_hold5 | 486 | 0.234024 | 0.160958 | 0.687243 | 0.676955 | 1.572243 | 475 | 0.008123 | -0.008966 | 0.446316 | 0.410526 | -0.460922 | PASS_diagnostic_only |
| r3d_lt_m7_hold3 | 549 | 0.738155 | 0.558271 | 0.659381 | 0.652095 | 0.514425 | 541 | 0.005105 | -0.009027 | 0.471349 | 0.410351 | -0.711589 | PASS_diagnostic_only |
| volume_z_gt2_crash_hold1 | 672 | 0.003306 | -0.007044 | 0.480655 | 0.398810 | -2.453386 | 669 | 0.003356 | -0.006191 | 0.451420 | 0.358744 | -2.528148 | FAIL_net_negative |
| volume_z_gt2_crash_hold3 | 652 | 0.008174 | -0.007448 | 0.513804 | 0.466258 | -0.626079 | 643 | 0.006001 | -0.008319 | 0.475894 | 0.415241 | -0.661765 | FAIL_net_negative |

## Subperiod Breakdown

| signal | subperiod | trade_count | gross_mean | net_mean |
| --- | --- | --- | --- | --- |
| r1d_lt_m3_hold1 | 2018_2020 | 235 | 0.042028 | 0.022054 |
| r1d_lt_m3_hold1 | 2021_2023 | 224 | 0.064172 | 0.039964 |
| r1d_lt_m3_hold1 | 2024_2026 | 147 | 0.049330 | 0.027360 |
| r1d_lt_m3_hold3 | 2018_2020 | 232 | 0.222277 | 0.155905 |
| r1d_lt_m3_hold3 | 2021_2023 | 201 | 0.129698 | 0.082113 |
| r1d_lt_m3_hold3 | 2024_2026 | 97 | 0.196066 | 0.138264 |
| r1d_lt_m3_hold5 | 2018_2020 | 228 | 0.252785 | 0.176845 |
| r1d_lt_m3_hold5 | 2021_2023 | 182 | 0.187544 | 0.122104 |
| r1d_lt_m3_hold5 | 2024_2026 | 76 | 0.289046 | 0.206340 |
| r3d_lt_m7_hold3 | 2018_2020 | 235 | 1.479518 | 1.136050 |
| r3d_lt_m7_hold3 | 2021_2023 | 210 | 0.160156 | 0.107040 |
| r3d_lt_m7_hold3 | 2024_2026 | 104 | 0.230073 | 0.163850 |
| volume_z_gt2_crash_hold1 | 2018_2020 | 239 | 0.010408 | -0.001216 |
| volume_z_gt2_crash_hold1 | 2021_2023 | 240 | -0.001924 | -0.011425 |
| volume_z_gt2_crash_hold1 | 2024_2026 | 193 | 0.001016 | -0.008814 |
| volume_z_gt2_crash_hold3 | 2018_2020 | 239 | 0.016778 | -0.001917 |
| volume_z_gt2_crash_hold3 | 2021_2023 | 234 | -0.002349 | -0.016062 |
| volume_z_gt2_crash_hold3 | 2024_2026 | 179 | 0.010443 | -0.003571 |

## Timing Policy

- Signal date T uses KRX close data available after close.
- Execution date is T+1 open or later.
- Rows with `거래대금추정여부 == True` are excluded.
- Pre-NXT panels synthesize `KRX종가` from `종가`; NXT panel rows assert equality.
