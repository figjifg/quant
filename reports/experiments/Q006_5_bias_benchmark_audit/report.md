# Q006.5 Bias & Benchmark Audit

## Verdict

universe bias 비중이 크다. Q-family 결과는 현재 99개 survivor universe diagnostic이며 production 후보가 아니다.

## Universe Bias

| Benchmark | CAGR | Sharpe | MDD | Excess CAGR vs SPY |
| --- | ---: | ---: | ---: | ---: |
| Survivor 99 EW | 19.94% | 1.15 | -32.49% | 5.18% |
| SPY | 14.76% | 0.91 | -33.72% | 0.00% |

## Random 30 Percentile

Random 30 median excess CAGR: 4.76%.

| Strategy | CAGR percentile | Excess CAGR percentile | Sharpe percentile |
| --- | ---: | ---: | ---: |
| Q002_candidate | 50.9% | 50.9% | 26.4% |
| Q006_candidate | 39.1% | 39.1% | 51.0% |

## Mega-cap Benchmark

Market-cap top30 excess CAGR vs SPY: 0.12%. 이 값이 Q002/Q006와 가까우면 mega-cap concentration 설명력이 크다.

## Sector / Mag 7

- Sector exposure CSV는 Q002/Q006, survivor EW proxy, market-cap top30 proxy 분기 sector weight를 기록한다. 실제 SPY sector breakdown 파일은 없어서 외부 추정 없이 별도 산출하지 않았다.
- Q002 Mag7 제외 CAGR delta: -1.64%
- Q006 Mag7 제외 CAGR delta: -2.93%

## Contributor Concentration

| Strategy | Top bucket | Share of total gain |
| --- | --- | ---: |
| Q002 | TOP_20_CONCENTRATION | 77.59% |
| Q002 | TOP_10_CONCENTRATION | 55.50% |
| Q002 | TOP_5_CONCENTRATION | 33.14% |
| Q006 | TOP_20_CONCENTRATION | 66.92% |
| Q006 | TOP_10_CONCENTRATION | 48.73% |
| Q006 | TOP_5_CONCENTRATION | 32.02% |

## Quartile vs SPY

평균 Q4 excess vs SPY: 2.26%. Bucket별 평균 excess: Q1=1.19%, Q2=0.46%, Q3=0.82%, Q4=2.26%.

## Production Gate

Direct Q-family는 survivor-safe universe가 없으므로 production X. Q007/Q008 진행 여부는 Q006.6 ETF proxy 결과와 함께 판단한다.
