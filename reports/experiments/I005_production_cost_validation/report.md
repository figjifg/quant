# I005 production cost validation

## 방법

- P08_IEF30만 재계산했다: SPY 29% / QQQ 21% / H001 20% / IEF 30%, quarterly rebalance.
- D013, H001 strategy, `engine.py`, 기존 I000-I004 산출물은 수정하지 않았다.
- 초기자본 가정: 100,000,000 KRW. 연 양도소득세 공제 2,500,000 KRW는 normalized NAV 0.025000로 적용했다.
- US ETF 가격은 기존 I003.5와 같은 KRW 환산 total-return proxy를 사용하고, 배당 원천징수 sensitivity는 별도 비용 차감으로 단순화했다.

## 분기 turnover 분석

- 평균 one-way turnover: 0.020278
- 최대 one-way turnover: 0.058914
- 관측 rebalance 수: 65

| date | quarter | one_way_turnover | buy_amount | sell_amount |
| --- | --- | --- | --- | --- |
| 2010-04-01 | 2010Q2 | 0.005587 | 0.005643 | 0.005643 |
| 2010-07-01 | 2010Q3 | 0.039028 | 0.040594 | 0.040594 |
| 2010-10-01 | 2010Q4 | 0.016405 | 0.017409 | 0.017409 |
| 2011-01-03 | 2011Q1 | 0.030926 | 0.034006 | 0.034006 |
| 2011-04-01 | 2011Q2 | 0.011325 | 0.012511 | 0.012511 |
| 2011-07-01 | 2011Q3 | 0.009810 | 0.010725 | 0.010725 |
| 2011-10-03 | 2011Q4 | 0.046087 | 0.053391 | 0.053391 |
| 2012-01-02 | 2012Q1 | 0.018174 | 0.021841 | 0.021841 |
| 2012-04-02 | 2012Q2 | 0.037051 | 0.047067 | 0.047067 |
| 2012-07-02 | 2012Q3 | 0.016763 | 0.021409 | 0.021409 |

## 비용 attribution

| scenario | commission_cost | capital_gains_tax | fx_spread_cost | dividend_withholding | total_cost |
| --- | --- | --- | --- | --- | --- |
| A_user | 0.020593 | 0.305389 | 0.000000 | 0.000000 | 0.325982 |
| B_full | 0.020102 | 0.301897 | 0.006034 | 0.088918 | 0.416951 |
| C_worst | 0.020063 | 0.301217 | 0.012046 | 0.088723 | 0.422049 |
| D_best | 0.021178 | 0.233818 | 0.000000 | 0.000000 | 0.254996 |

## 4 scenario 비교

| scenario | cagr | sharpe | max_drawdown | cagr_delta_vs_gross | sharpe_delta_vs_gross | mdd_delta_vs_gross_pp | total_cost | tax_share_of_gross_profit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Gross_I003_5 | 0.127384 | 1.172143 | -0.164077 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| A_user | 0.120137 | 1.112978 | -0.164553 | -0.007247 | -0.059165 | -0.047582 | 0.325982 | 0.049931 |
| B_full | 0.117282 | 1.088746 | -0.164553 | -0.010102 | -0.083397 | -0.047582 | 0.416951 | 0.049360 |
| C_worst | 0.117131 | 1.087447 | -0.164553 | -0.010253 | -0.084696 | -0.047582 | 0.422049 | 0.049248 |
| D_best | 0.122958 | 1.136567 | -0.164553 | -0.004426 | -0.035575 | -0.047582 | 0.254996 | 0.038229 |

## Stress 재검증

| scenario | stress | metric | value | start_date | end_date | peak_date | trough_date |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Gross_I003_5 | 2020_covid | daily_mdd | -0.164077 | 2020-02-01 | 2020-04-30 | 2020-02-20 | 2020-03-19 |
| Gross_I003_5 | 2022 | calendar_year_return | -0.146415 | 2022-01-01 | 2022-12-31 |  |  |
| Gross_I003_5 | 2025_spike_exclusion | sharpe | 1.131621 | 2010-01-04 | 2026-05-18 |  |  |
| A_user | 2020_covid | daily_mdd | -0.164553 | 2020-02-01 | 2020-04-30 | 2020-02-20 | 2020-03-19 |
| A_user | 2022 | calendar_year_return | -0.149274 | 2022-01-01 | 2022-12-31 |  |  |
| A_user | 2025_spike_exclusion | sharpe | 1.089909 | 2010-01-04 | 2026-05-18 |  |  |
| B_full | 2020_covid | daily_mdd | -0.164553 | 2020-02-01 | 2020-04-30 | 2020-02-20 | 2020-03-19 |
| B_full | 2022 | calendar_year_return | -0.151396 | 2022-01-01 | 2022-12-31 |  |  |
| B_full | 2025_spike_exclusion | sharpe | 1.069289 | 2010-01-04 | 2026-05-18 |  |  |
| C_worst | 2020_covid | daily_mdd | -0.164553 | 2020-02-01 | 2020-04-30 | 2020-02-20 | 2020-03-19 |
| C_worst | 2022 | calendar_year_return | -0.151479 | 2022-01-01 | 2022-12-31 |  |  |
| C_worst | 2025_spike_exclusion | sharpe | 1.068243 | 2010-01-04 | 2026-05-18 |  |  |
| D_best | 2020_covid | daily_mdd | -0.164553 | 2020-02-01 | 2020-04-30 | 2020-02-20 | 2020-03-19 |
| D_best | 2022 | calendar_year_return | -0.149274 | 2022-01-01 | 2022-12-31 |  |  |
| D_best | 2025_spike_exclusion | sharpe | 1.111415 | 2010-01-04 | 2026-05-18 |  |  |
| P07_gross_reference | 2020_covid | daily_mdd | -0.190961 | 2020-02-01 | 2020-04-30 | 2020-02-19 | 2020-03-19 |
| P07_gross_reference | 2022 | calendar_year_return | -0.191375 | 2022-01-01 | 2022-12-31 |  |  |
| P08_gross_reference | 2020_covid | daily_mdd | -0.234285 | 2020-02-01 | 2020-04-30 | 2020-02-19 | 2020-03-23 |
| P08_gross_reference | 2022 | calendar_year_return | -0.170427 | 2022-01-01 | 2022-12-31 |  |  |

## Subperiod 재검증

| scenario | stress | metric | value | start_date | end_date |
| --- | --- | --- | --- | --- | --- |
| Gross_I003_5 | 2010_2017 | sharpe | 1.010910 | 2010-01-04 | 2017-12-29 |
| Gross_I003_5 | 2010_2017 | cagr | 0.090521 | 2010-01-04 | 2017-12-29 |
| Gross_I003_5 | 2018_2026 | sharpe | 1.309032 | 2018-01-02 | 2026-05-18 |
| Gross_I003_5 | 2018_2026 | cagr | 0.164047 | 2018-01-02 | 2026-05-18 |
| A_user | 2010_2017 | sharpe | 0.965803 | 2010-01-04 | 2017-12-29 |
| A_user | 2010_2017 | cagr | 0.086123 | 2010-01-04 | 2017-12-29 |
| A_user | 2018_2026 | sharpe | 1.240050 | 2018-01-02 | 2026-05-18 |
| A_user | 2018_2026 | cagr | 0.154077 | 2018-01-02 | 2026-05-18 |
| B_full | 2010_2017 | sharpe | 0.937573 | 2010-01-04 | 2017-12-29 |
| B_full | 2010_2017 | cagr | 0.083431 | 2010-01-04 | 2017-12-29 |
| B_full | 2018_2026 | sharpe | 1.218236 | 2018-01-02 | 2026-05-18 |
| B_full | 2018_2026 | cagr | 0.151063 | 2018-01-02 | 2026-05-18 |
| C_worst | 2010_2017 | sharpe | 0.936292 | 2010-01-04 | 2017-12-29 |
| C_worst | 2010_2017 | cagr | 0.083309 | 2010-01-04 | 2017-12-29 |
| C_worst | 2018_2026 | sharpe | 1.216928 | 2018-01-02 | 2026-05-18 |
| C_worst | 2018_2026 | cagr | 0.150886 | 2018-01-02 | 2026-05-18 |
| D_best | 2010_2017 | sharpe | 1.002527 | 2010-01-04 | 2017-12-29 |
| D_best | 2010_2017 | cagr | 0.089677 | 2010-01-04 | 2017-12-29 |
| D_best | 2018_2026 | sharpe | 1.253438 | 2018-01-02 | 2026-05-18 |
| D_best | 2018_2026 | cagr | 0.155965 | 2018-01-02 | 2026-05-18 |

## Multi-metric framework 재평가

- Gross reference: CAGR 0.127384, Sharpe 1.172143, MDD -0.164077.
- Full cost Scenario B: CAGR 0.117282, Sharpe 1.088746, MDD -0.164553.
- Worst Scenario C: CAGR 0.117131, Sharpe 1.087447, MDD -0.164553.
- Net stress가 P07/P08 gross reference보다 우수: True.
- Core pass criteria all scenarios pass: True.
- Kill criteria triggered in any scenario: False.

## Verdict

- Verdict: P08_IEF30 production-ready 유지.
- 진행 권고: I004 candidate 유지.
- I003.6 long-history host 복귀 대기는 별도 long-history 검증 이슈로 남긴다.

## Files

- cost_scenarios.csv
- quarterly_turnover.csv
- cost_attribution.csv
- daily_nav_gross_vs_net.csv
- stress_net.csv
