# V000 P08_IEF30 Adversarial Validation

Verdict: PASS

## 기준

- exact weight가 아니어도 유사 frontier가 살아남는지 확인한다.
- 이 스크립트는 P08 weight를 재최적화하지 않는다.
- D013, H001, engine.py를 수정하지 않는다.

## Baseline

- Sharpe: 1.175276
- CAGR: 0.127658
- MDD: -0.164414

## Survival Count

- Scenarios: 43
- Survivors: 43

## Worst Stress Rows

| scenario | family | frequency | rebalance_shift | SPY | QQQ | H001 | IEF | stress | total_return | cagr | vol | sharpe | max_drawdown |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ief_20% | ief_grid | Q | 0 | 0.331429 | 0.240000 | 0.228571 | 0.200000 | covid_2020 | -0.026053 | -0.104907 | 0.325615 | -0.163235 | -0.197268 |
| weight_IEF_-10% | weight_perturbation | Q | 0 | 0.322222 | 0.233333 | 0.222222 | 0.222222 | covid_2020 | -0.022575 | -0.091409 | 0.312724 | -0.137427 | -0.189474 |
| ief_25% | ief_grid | Q | 0 | 0.310714 | 0.225000 | 0.214286 | 0.250000 | covid_2020 | -0.018270 | -0.074490 | 0.296923 | -0.101639 | -0.180539 |
| weight_H001_+10% | weight_perturbation | Q | 0 | 0.263636 | 0.190909 | 0.272727 | 0.272727 | covid_2020 | -0.015393 | -0.063052 | 0.267573 | -0.099652 | -0.178806 |
| weight_IEF_-5% | weight_perturbation | Q | 0 | 0.305263 | 0.221053 | 0.210526 | 0.263158 | covid_2020 | -0.016247 | -0.066460 | 0.289563 | -0.083189 | -0.176300 |
| weight_SPY_+10% | weight_perturbation | Q | 0 | 0.354545 | 0.190909 | 0.181818 | 0.272727 | covid_2020 | -0.017730 | -0.072351 | 0.291600 | -0.101324 | -0.172608 |
| weight_H001_+5% | weight_perturbation | Q | 0 | 0.276190 | 0.200000 | 0.238095 | 0.285714 | covid_2020 | -0.013122 | -0.053944 | 0.267852 | -0.064897 | -0.171949 |
| weight_QQQ_+10% | weight_perturbation | Q | 0 | 0.263636 | 0.281818 | 0.181818 | 0.272727 | covid_2020 | -0.010137 | -0.041871 | 0.293052 | 0.005681 | -0.168755 |
| weight_SPY_+5% | weight_perturbation | Q | 0 | 0.323810 | 0.200000 | 0.190476 | 0.285714 | covid_2020 | -0.014348 | -0.058869 | 0.280898 | -0.067033 | -0.168705 |
| frequency_M | frequency | M | 0 | 0.290000 | 0.210000 | 0.200000 | 0.300000 | covid_2020 | -0.014143 | -0.058045 | 0.278424 | -0.067053 | -0.168629 |

## Files

- `adversarial_metrics.csv`
- `stress_metrics.csv`
