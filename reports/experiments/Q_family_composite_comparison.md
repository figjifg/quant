# Q-family Composite Comparison

## 종합 표

| Experiment | Sleeve | CAGR | Sharpe | MDD | Excess CAGR vs SPY | IR | Top30 turnover | Q1-Q4 long-short |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Q002 | Quality only | 19.56% | 1.08 | -27.77% | 4.80% | 0.84 | 14.85% | -0.94% |
| Q003 | Value only | 18.70% | 1.11 | -28.53% | 3.95% | 0.59 | 11.35% | -1.22% |
| Q004 | Shareholder Yield only | 17.82% | 1.11 | -30.80% | 3.06% | 0.38 | 12.63% | -1.38% |
| Q005 | Quality + Value | 19.41% | 1.09 | -30.08% | 4.65% | 0.80 | 15.20% | -0.72% |
| Q006 | Quality + Value + Shareholder Yield | 19.03% | 1.13 | -28.38% | 4.27% | 0.66 | 16.49% | -1.18% |
| SPY | Benchmark | 14.76% |  |  | 0.00% |  |  |  |

## Subperiod 일관성

| Experiment | 2010_2015 excess | 2016_2020 excess | 2021_2026 excess | Positive subperiods |
| --- | ---: | ---: | ---: | ---: |
| Q002 | 5.38% | 8.63% | 0.94% | 3/3 |
| Q003 | 4.61% | 7.35% | 0.27% | 3/3 |
| Q004 | 0.36% | 5.56% | 2.47% | 3/3 |
| Q005 | 6.96% | 7.55% | 0.34% | 3/3 |
| Q006 | 4.51% | 6.39% | 2.04% | 3/3 |

## Verdict ranking

1. Q002 Quality only: Excess CAGR 4.80%, Sharpe 1.08, IR 0.84.
2. Q005 Quality + Value: Excess CAGR 4.65%, Sharpe 1.09, IR 0.80.
3. Q006 Quality + Value + Shareholder Yield: Excess CAGR 4.27%, Sharpe 1.13, IR 0.66.
4. Q003 Value only: Excess CAGR 3.95%, Sharpe 1.11, IR 0.59.
5. Q004 Shareholder Yield only: Excess CAGR 3.06%, Sharpe 1.11, IR 0.38.

## 다음 step

- Q007 cost validation으로 turnover, 세금, 수수료, 슬리피지를 별도 검증한다.
- Q-family는 별도 US individual-stock fundamental sleeve이며 `P08_IEF30`을 직접 promote하지 않는다.
- 모든 Q002-Q006 결과는 현재 survivor universe 기반이므로 survivorship bias 한계를 유지한다.
