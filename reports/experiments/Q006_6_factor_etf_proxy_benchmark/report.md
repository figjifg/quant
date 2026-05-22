# Q006.6 Factor ETF Proxy Benchmark

## Verdict

direct Q-family 우위 가능성은 있으나 survivor-safe universe 전 production 불가. Survivorship-safe universe가 없으면 direct Q-family는 research diagnostic이고, production path는 ETF proxy가 우선이다.

## ETF Standalone

전체 factor ETF 공통 기간의 factor ETF 최상위 Sharpe는 MTUM (0.83, CAGR 16.71%)이다. COWZ 상장일 때문에 모든 factor ETF 공통 비교는 2014가 아니라 2016-12-22 이후로 제한된다. SPY/QQQ는 같은 표에 비교 기준으로만 포함했다.

## Direct Q vs ETF

- 비교 row 수: 20
- direct_q_wins: 20
- ETF 또는 실용성 우선 판정: 0

ETF가 비슷한 경우 운용 가능성, survivor-safe exposure, 낮은 implementation risk 때문에 ETF proxy를 우선한다.

## P08_IEF30 Preview

| Sleeve | CAGR | Sharpe | MDD | Sharpe delta |
| --- | ---: | ---: | ---: | ---: |
| BASELINE | 13.01% | 1.15 | -21.42% | 0.00 |
| QUAL | 12.91% | 1.14 | -21.84% | -0.01 |
| COWZ | 12.83% | 1.15 | -20.28% | 0.00 |
| SCHD | 12.77% | 1.17 | -20.40% | 0.02 |
| VLUE | 12.86% | 1.14 | -21.15% | -0.00 |
| MTUM | 13.19% | 1.15 | -21.56% | -0.00 |
| Q002 | 13.51% | 1.17 | -21.67% | 0.03 |
| Q006 | 13.39% | 1.18 | -21.28% | 0.04 |

Best preview by Sharpe: Q006 (1.18).

## Production Gate

Direct Q-family production gate: closed. ETF proxy path: open for Q008 framework, subject to Q007-style cost/turnover validation where applicable.
