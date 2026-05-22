# Q006.5 + Q006.6 Combined Verdict

## 결론

Q-family 결과는 흥미롭지만 factor alpha로 확정할 수 없다. Q006.5에서 survivor 99종목 equal-weight가 SPY를 CAGR +5.18%p 이겼고, Q4 bottom bucket도 SPY 대비 평균 +2.26%p였다. 이는 alpha의 상당 부분이 factor 자체보다 survivor universe bias에서 왔을 가능성을 강하게 시사한다.

Direct Q-family는 research diagnostic이며 production X. Survivorship-safe universe가 없으면 ETF proxy production path를 우선한다.

## Bias Audit 요약

| 항목 | 결과 | 해석 |
| --- | ---: | --- |
| Survivor 99 EW excess CAGR vs SPY | +5.18%p | universe bias 큼 |
| Market-cap top30 excess CAGR vs SPY | +0.12%p | 단순 mega-cap top30만으로 Q 성과를 설명하긴 어려움 |
| Q002 random30 excess percentile | 50.9% | random survivor 30 중앙값 수준 |
| Q006 random30 excess percentile | 39.1% | random survivor 30보다 낮음 |
| Q002 Mag7 제외 CAGR delta | -1.64%p | 일부 의존도 있음 |
| Q006 Mag7 제외 CAGR delta | -2.93%p | Mag7 영향 큼 |
| Q002 Top20 contribution share | 77.59% | 기여 집중도 높음 |
| Q006 Top20 contribution share | 66.92% | 기여 집중도 높음 |

Verdict: factor alpha 진짜 여부는 미확정. 현재 결과는 survivor concentration과 일부 Mag7/상위 contributor 의존도를 포함한다.

## ETF Proxy 요약

Direct Q002/Q006는 ETF별 공통 기간 비교에서 factor ETF를 모두 이겼다(`direct_q_wins` 20/20). 하지만 이 우위는 survivor universe에서 나온 diagnostic 결과이므로 production promote 근거로 쓰지 않는다.

전체 factor ETF 공통 기간은 COWZ 때문에 2016-12-22부터 시작한다. 이 구간에서 factor ETF 중 MTUM이 Sharpe 0.83, CAGR 16.71%로 가장 높았다.

P08_IEF30 preview에서는 SPY 10%를 ETF/Q sleeve로 대체했을 때:
- SCHD: Sharpe +0.02, MDD +1.03%p 개선, CAGR -0.25%p
- COWZ: Sharpe +0.00, MDD +1.14%p 개선, CAGR -0.18%p
- MTUM: CAGR +0.18%p, Sharpe -0.00, MDD -0.14%p
- Direct Q006: Sharpe +0.04, CAGR +0.38%p이나 survivor diagnostic이라 production X

## Next Step

Q007 cost validation은 direct Q-family production 검증이 아니라, Q008 결합 framework를 위한 비용/turnover sanity check로만 진행 가능하다.

Q008 framework는 명확하다: P08_IEF30 baseline에 factor ETF proxy sleeve를 10% 단위로 결합하고, SPY 차감 방식으로 gross preview를 net/cost-aware validation으로 확장한다. Direct Q002/Q006 sleeve는 비교용 diagnostic으로 남기고 production 후보에는 올리지 않는다.

## Production Gate Status

- Direct Q-family: closed. Survivorship-safe universe 없이는 production 불가.
- ETF proxy: open. Q008 후보로 SCHD/COWZ/MTUM 중심 검증 가능.
- Q007/Q008 전제: Q-family 결과를 "factor alpha 확정"으로 해석하지 않는다.
- 결정문 적용: `Q002 + Q006 dual candidate`는 research candidate로 유지하되, survivorship-safe X이면 ETF proxy production prefer.
