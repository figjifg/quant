# X-KR001 결과 보고

## Verdict

CLOSE. 사전 등록 kill gate 기준에서 하나 이상 실패했으므로 X-KR001은 diagnostic 결과로만 보관한다.

## 실행 메타데이터

- Pair 후보 수: 50
- Variant 수: 6 pre-registered x 2 portfolio modes = 12 rows
- Random/placebo trials: 1000
- Execution: signal_date T close, execution_date T+1 or later
- Cost: turnover leg 15 bps, 22% diagnostic tax layer, domestic ordinary small-shareholder tax 0 alternative
- W001 modules: calendar, corporate action, tradability, sleeve NAV, random/placebo, sanity checks used

## Top Variants By After-Cost Sharpe

| variant | mode | after_cost_sharpe | after_cost_cagr | after_cost_mdd | random_percentile |
|---|---:|---:|---:|---:|---:|
| XKR001_V02 | long_only | 1.497033 | 1.757801 | -0.996989 | 100.000000 |
| XKR001_V01 | long_only | 1.118900 | 0.748520 | -0.963965 | 100.000000 |
| XKR001_V06 | long_short | 1.045038 | 0.610276 | -0.990246 | 100.000000 |
| XKR001_V05 | long_short | 1.032494 | 0.563543 | -0.951163 | 100.000000 |
| XKR001_V03 | long_short | 0.449125 | nan | -1.027943 | 100.000000 |

## Kill Gate Summary

| gate | failed_count |
|---|---:|
| 1_after_cost_sharpe_lt_1 | 8 |
| 2_no_random_difference | 6 |
| 3_top10_pair_dominance | 0 |
| 4_short_borrow_feasibility | 6 |
| 5_long_only_fallback_weak | 4 |
| 6_two_subperiod_fail | 11 |
| 7_turnover_tax_slippage_kills | 12 |

## A0 Sanity Summary

| status | count |
|---|---:|
| PASS | 140 |
| FAIL | 4 |

## Note

Long-short 결과는 borrow/short 현실성 미확정 때문에 production 후보가 아니다. Long-only fallback이 kill gate를 통과하지 못하면 retail 후보도 아니다. 결과와 무관하게 이 실험은 X-Lab 마지막 timeboxed experiment로 취급한다.
