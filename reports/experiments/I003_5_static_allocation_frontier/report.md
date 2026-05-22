# I003.5 — Static Allocation Frontier

## 방법

- I001.6/I003과 동일한 daily NAV 재구성: quarterly rebalance + daily mark-to-market.
- D013/H001 strategy와 `engine.py`는 수정하지 않았다.
- Grid의 새 best 후보는 final 승격하지 않고 multi-metric balance만 평가한다.
- 2022 stress는 binary pass/fail이 아니라 penalty로 반영했다.
- 기간: 2010-01-04부터 2026-05-18까지.
- USDKRW latest observation used: 2026-04-24 at 1476.47.

## Frontier shape (단조 vs plateau)

- A frontier: plateau/비단조 frontier: 일부 구간에서 Sharpe 또는 MDD 개선이 둔화.
- B frontier: 단조 frontier: IEF 증가에 따라 Sharpe/MDD는 개선되고 CAGR은 하락.

### I003.5-A P07-style IEF frontier

| candidate | weights | cagr | sharpe | max_drawdown | positive_years |
| --- | --- | --- | --- | --- | --- |
| A01_QQQ70_H00130_IEF00 | QQQ70/H00130 | 0.179699 | 1.131242 | -0.252425 | 16 |
| A02_QQQ60_H00130_IEF10 | QQQ60/H00130/IEF10 | 0.163865 | 1.172466 | -0.219741 | 16 |
| A03_P07_QQQ50_H00130_IEF20 | QQQ50/H00130/IEF20 | 0.147724 | 1.210984 | -0.199070 | 16 |
| A04_QQQ40_H00130_IEF30 | QQQ40/H00130/IEF30 | 0.131292 | 1.234846 | -0.178219 | 16 |
| A05_QQQ30_H00130_IEF40 | QQQ30/H00130/IEF40 | 0.114586 | 1.220351 | -0.157187 | 16 |
| A06_QQQ20_H00130_IEF50 | QQQ20/H00130/IEF50 | 0.097622 | 1.134645 | -0.135972 | 16 |

### I003.5-B P08-style IEF frontier

| candidate | weights | cagr | sharpe | max_drawdown | positive_years |
| --- | --- | --- | --- | --- | --- |
| B01_SPY46_QQQ34_H00120_IEF00 | SPY46/QQQ34/H00120 | 0.167101 | 1.070409 | -0.272948 | 16 |
| B02_P08_SPY40_QQQ30_H00120_IEF10 | SPY40/QQQ30/H00120/IEF10 | 0.154328 | 1.109627 | -0.234285 | 16 |
| B03_SPY34_QQQ26_H00120_IEF20 | SPY34/QQQ26/H00120/IEF20 | 0.141254 | 1.146777 | -0.195824 | 16 |
| B04_SPY29_QQQ21_H00120_IEF30 | SPY29/QQQ21/H00120/IEF30 | 0.127384 | 1.172143 | -0.164077 | 16 |
| B05_SPY23_QQQ17_H00120_IEF40 | SPY23/QQQ17/H00120/IEF40 | 0.113757 | 1.172469 | -0.140925 | 16 |

## Rebalance frequency 효과

- 아래 4 후보 모두 monthly/quarterly/semiannual/annual로 재계산했다.
- P07의 성과가 특정 rebalance 주기 artifact인지 확인하는 진단이다.

| portfolio | frequency | cagr | sharpe | max_drawdown |
| --- | --- | --- | --- | --- |
| P07 | monthly | 0.147454 | 1.220910 | -0.197181 |
| P08 | monthly | 0.154205 | 1.112518 | -0.238099 |
| P07_IEF30 | monthly | 0.130883 | 1.246581 | -0.176060 |
| P08_IEF30 | monthly | 0.126825 | 1.172563 | -0.170476 |
| P07 | quarterly | 0.147724 | 1.210984 | -0.199070 |
| P08 | quarterly | 0.154328 | 1.109627 | -0.234285 |
| P07_IEF30 | quarterly | 0.131292 | 1.234846 | -0.178219 |
| P08_IEF30 | quarterly | 0.127384 | 1.172143 | -0.164077 |
| P07 | semiannual | 0.147833 | 1.207448 | -0.200331 |
| P08 | semiannual | 0.154496 | 1.109207 | -0.234285 |
| P07_IEF30 | semiannual | 0.131224 | 1.230112 | -0.179186 |
| P08_IEF30 | semiannual | 0.127002 | 1.168701 | -0.164077 |
| P07 | annual | 0.149089 | 1.211621 | -0.198715 |
| P08 | annual | 0.155599 | 1.113068 | -0.234285 |
| P07_IEF30 | annual | 0.132374 | 1.234121 | -0.177939 |
| P08_IEF30 | annual | 0.127930 | 1.171900 | -0.164077 |

## 2022 vs COVID stress trade-off

- P07 2022 KRW return: -0.191375.
- P08 2022 KRW return: -0.170427.
- P07/P08 2022 차이: 0.020948.

### 2020 COVID

| candidate | daily_mdd | recovery_date | QQQ_return_contribution | SPY_return_contribution | H001_return_contribution | IEF_return_contribution |
| --- | --- | --- | --- | --- | --- | --- |
| A03_P07_QQQ50_H00130_IEF20 | -0.190961 | 2020-05-20 | -0.109810 | 0.000000 | -0.095786 | 0.014635 |
| A04_QQQ40_H00130_IEF30 | -0.162948 | 2020-05-18 | -0.088536 | 0.000000 | -0.096535 | 0.022124 |
| B02_P08_SPY40_QQQ30_H00120_IEF10 | -0.234285 | 2020-06-05 | -0.072933 | -0.115994 | -0.058068 | 0.012710 |
| B04_SPY29_QQQ21_H00120_IEF30 | -0.164077 | 2020-05-25 | -0.046224 | -0.073420 | -0.064152 | 0.019719 |

### 2022 rate shock

| candidate | calendar_year_return_krw | QQQ_return_contribution | SPY_return_contribution | H001_return_contribution | IEF_return_contribution |
| --- | --- | --- | --- | --- | --- |
| A03_P07_QQQ50_H00130_IEF20 | -0.191375 | -0.149948 | 0.000000 | -0.024727 | -0.016700 |
| A04_QQQ40_H00130_IEF30 | -0.171102 | -0.120880 | 0.000000 | -0.024701 | -0.025521 |
| B02_P08_SPY40_QQQ30_H00120_IEF10 | -0.170427 | -0.090945 | -0.054644 | -0.016444 | -0.008394 |
| B04_SPY29_QQQ21_H00120_IEF30 | -0.146415 | -0.064288 | -0.039792 | -0.016426 | -0.025908 |

### 2021-2022 drawdown

| portfolio | peak_date | trough_date | peak_to_trough_mdd | drawdown_length_days | recovery_date |
| --- | --- | --- | --- | --- | --- |
| P07 | 2021-12-28 | 2022-12-28 | -0.199070 | 365 | 2023-08-08 |
| P08 | 2021-12-28 | 2022-12-28 | -0.176765 | 365 | 2023-06-28 |
| P07_IEF30 | 2021-12-28 | 2022-12-28 | -0.178219 | 365 | 2023-08-31 |
| P08_IEF30 | 2021-12-28 | 2022-12-28 | -0.152250 | 365 | 2023-06-30 |

## Long-history 결과

- long-history files missing after yfinance attempt: QQQ, SPY, IEF

| status | reason |
| --- | --- |
| skipped | long-history files missing after yfinance attempt: QQQ, SPY, IEF |

## 2025 spike exclusion

| candidate | cagr | sharpe | max_drawdown | mdd_peak_date | mdd_trough_date |
| --- | --- | --- | --- | --- | --- |
| A03_P07_QQQ50_H00130_IEF20 | 0.147724 | 1.133353 | -0.199070 | 2021-12-28 | 2022-12-28 |
| A04_QQQ40_H00130_IEF30 | 0.131292 | 1.128987 | -0.178219 | 2021-12-28 | 2022-12-28 |
| B02_P08_SPY40_QQQ30_H00120_IEF10 | 0.154328 | 1.099733 | -0.234285 | 2020-02-19 | 2020-03-23 |
| B04_SPY29_QQQ21_H00120_IEF30 | 0.127384 | 1.131621 | -0.164077 | 2020-02-20 | 2020-03-19 |

## Subperiod split

| candidate | period | cagr | sharpe | max_drawdown | mdd_length_days |
| --- | --- | --- | --- | --- | --- |
| A03_P07_QQQ50_H00130_IEF20 | 2010_2017 | 0.101045 | 1.098869 | -0.075050 | 70 |
| A03_P07_QQQ50_H00130_IEF20 | 2018_2026 | 0.193880 | 1.324199 | -0.199070 | 365 |
| A04_QQQ40_H00130_IEF30 | 2010_2017 | 0.088322 | 1.096048 | -0.063742 | 69 |
| A04_QQQ40_H00130_IEF30 | 2018_2026 | 0.173920 | 1.364610 | -0.178219 | 365 |
| B02_P08_SPY40_QQQ30_H00120_IEF10 | 2010_2017 | 0.111335 | 0.987301 | -0.114783 | 175 |
| B02_P08_SPY40_QQQ30_H00120_IEF10 | 2018_2026 | 0.196841 | 1.217889 | -0.234285 | 33 |
| B04_SPY29_QQQ21_H00120_IEF30 | 2010_2017 | 0.090521 | 1.010910 | -0.064949 | 62 |
| B04_SPY29_QQQ21_H00120_IEF30 | 2018_2026 | 0.164047 | 1.307825 | -0.164077 | 28 |

## Contribution attribution

| portfolio | period | component | target_weight | return_contribution | fx_contribution_estimate |
| --- | --- | --- | --- | --- | --- |
| P07 | 2010_2017 | QQQ | 0.500000 | 0.960869 | -0.130082 |
| P07 | 2010_2017 | SPY | 0.000000 | 0.000000 | -0.000000 |
| P07 | 2010_2017 | H001 | 0.300000 | 0.121444 | 0.000000 |
| P07 | 2010_2017 | IEF | 0.200000 | 0.074207 | -0.020000 |
| P07 | 2010_2017 | FX_estimate_total |  | -0.150082 | -0.150082 |
| P07 | 2010_2017 | rebalance_effect |  | -0.193588 |  |
| P07 | 2010_2017 | total | 1.000000 | 1.156520 | -0.150082 |
| P07 | 2018_2026 | QQQ | 0.500000 | 2.026787 | 0.927269 |
| P07 | 2018_2026 | SPY | 0.000000 | 0.000000 | 0.000000 |
| P07 | 2018_2026 | H001 | 0.300000 | 1.225312 | 0.000000 |
| P07 | 2018_2026 | IEF | 0.200000 | 0.156924 | 0.085283 |
| P07 | 2018_2026 | FX_estimate_total |  | 1.012551 | 1.012551 |
| P07 | 2018_2026 | rebalance_effect |  | -0.239911 |  |
| P07 | 2018_2026 | total | 1.000000 | 3.409024 | 1.012551 |
| P08 | 2010_2017 | QQQ | 0.300000 | 0.595172 | -0.078049 |
| P08 | 2010_2017 | SPY | 0.400000 | 0.605696 | -0.078667 |
| P08 | 2010_2017 | H001 | 0.200000 | 0.084403 | 0.000000 |
| P08 | 2010_2017 | IEF | 0.100000 | 0.037509 | -0.010000 |
| P08 | 2010_2017 | FX_estimate_total |  | -0.166716 | -0.166716 |
| P08 | 2010_2017 | rebalance_effect |  | -0.116185 |  |
| P08 | 2010_2017 | total | 1.000000 | 1.322780 | -0.166716 |
| P08 | 2018_2026 | QQQ | 0.300000 | 1.249557 | 0.556361 |
| P08 | 2018_2026 | SPY | 0.400000 | 1.308244 | 0.492458 |
| P08 | 2018_2026 | H001 | 0.200000 | 0.859845 | 0.000000 |
| P08 | 2018_2026 | IEF | 0.100000 | 0.083777 | 0.042641 |
| P08 | 2018_2026 | FX_estimate_total |  | 1.091460 | 1.091460 |
| P08 | 2018_2026 | rebalance_effect |  | -0.072023 |  |
| P08 | 2018_2026 | total | 1.000000 | 3.501422 | 1.091460 |
| P07_IEF30 | 2010_2017 | QQQ | 0.400000 | 0.741480 | -0.104065 |
| P07_IEF30 | 2010_2017 | SPY | 0.000000 | 0.000000 | -0.000000 |
| P07_IEF30 | 2010_2017 | H001 | 0.300000 | 0.115649 | 0.000000 |
| P07_IEF30 | 2010_2017 | IEF | 0.300000 | 0.108291 | -0.030000 |
| P07_IEF30 | 2010_2017 | FX_estimate_total |  | -0.134065 | -0.134065 |
| P07_IEF30 | 2010_2017 | rebalance_effect |  | -0.175125 |  |
| P07_IEF30 | 2010_2017 | total | 1.000000 | 0.965420 | -0.134065 |
| P07_IEF30 | 2018_2026 | QQQ | 0.400000 | 1.509793 | 0.741815 |
| P07_IEF30 | 2018_2026 | SPY | 0.000000 | 0.000000 | 0.000000 |
| P07_IEF30 | 2018_2026 | H001 | 0.300000 | 1.101510 | 0.000000 |
| P07_IEF30 | 2018_2026 | IEF | 0.300000 | 0.217282 | 0.127924 |
| P07_IEF30 | 2018_2026 | FX_estimate_total |  | 0.869739 | 0.869739 |
| P07_IEF30 | 2018_2026 | rebalance_effect |  | -0.314791 |  |
| P07_IEF30 | 2018_2026 | total | 1.000000 | 2.828585 | 0.869739 |
| P08_IEF30 | 2010_2017 | QQQ | 0.210000 | 0.394189 | -0.054634 |
| P08_IEF30 | 2010_2017 | SPY | 0.290000 | 0.417334 | -0.057034 |
| P08_IEF30 | 2010_2017 | H001 | 0.200000 | 0.078143 | 0.000000 |
| P08_IEF30 | 2010_2017 | IEF | 0.300000 | 0.107676 | -0.030000 |
| P08_IEF30 | 2010_2017 | FX_estimate_total |  | -0.141668 | -0.141668 |
| P08_IEF30 | 2010_2017 | rebalance_effect |  | -0.113884 |  |
| P08_IEF30 | 2010_2017 | total | 1.000000 | 0.997342 | -0.141668 |
| P08_IEF30 | 2018_2026 | QQQ | 0.210000 | 0.781847 | 0.389453 |
| P08_IEF30 | 2018_2026 | SPY | 0.290000 | 0.842430 | 0.357032 |
| P08_IEF30 | 2018_2026 | H001 | 0.200000 | 0.723437 | 0.000000 |
| P08_IEF30 | 2018_2026 | IEF | 0.300000 | 0.219479 | 0.127924 |
| P08_IEF30 | 2018_2026 | FX_estimate_total |  | 0.874409 | 0.874409 |
| P08_IEF30 | 2018_2026 | rebalance_effect |  | -0.237885 |  |
| P08_IEF30 | 2018_2026 | total | 1.000000 | 2.567193 | 0.874409 |

## Multi-metric 최종 후보 선정

- Highest Sharpe 자동 선택은 하지 않았다.
- CAGR < 12%는 defensive portfolio로 분류한다.
- MDD가 -25% 이하이면 warning으로 표시한다.
- Daily Sharpe >= 1.15, 2022 stress, long-history, frequency robustness, explainability를 함께 점수화했다.

| portfolio | score | sharpe | cagr | max_drawdown | return_2022 | covid_mdd | reasons |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P08_IEF30 | 7 | 1.172143 | 0.127384 | -0.164077 | -0.146415 | -0.164077 | Sharpe>=1.15; CAGR>=12%; MDD within warning line; 2022 resilient; frequency robust |
| P07_IEF30 | 5 | 1.234846 | 0.131292 | -0.178219 | -0.171102 | -0.162948 | Sharpe>=1.15; CAGR>=12%; MDD within warning line; 2022 mild penalty; frequency robust |
| P07 | 5 | 1.210984 | 0.147724 | -0.199070 | -0.191375 | -0.190961 | Sharpe>=1.15; CAGR>=12%; MDD within warning line; 2022 mild penalty; frequency robust |
| P08 | 3 | 1.109627 | 0.154328 | -0.234285 | -0.170427 | -0.234285 | CAGR>=12%; MDD within warning line; 2022 mild penalty; frequency robust |

## Champion candidate 추천 + 근거

- Verdict: P08_IEF30는 stress-balance 진단 leader이나 final promote 금지; P07/P08 anchor를 유지; 2022 P07/P08 차이는 5pp 미만.
- 이 추천은 grid best 승격이 아니며, IEF30 후보는 diagnostic leader여도 final promote하지 않는다.
- 진행 권고: I003.6에서 long-history만 별도 재시도 후 I004 등록.

## Files

- frontier_a_p07_style.csv
- frontier_b_p08_style.csv
- rebalance_frequency.csv
- stress_2020_covid.csv
- stress_2022_rate_shock.csv
- stress_2021_2022_drawdown.csv
- spike_exclusion_2025.csv
- subperiod_split.csv
- long_history_us_core.csv
- contribution_attribution.csv
- daily_metrics_all_candidates.csv
