# N006 Shadow Promotion Rule

Status: rule for interpreting N002-B and N001-B shadow portfolios.

## 정직한 해석

N002-B와 N001-B는 `P08_IEF30`의 즉시 대체 전략이 아니다. 두 후보는 stress
diversifier shadow이며, live allocation 변경 권한을 갖지 않는다. 목적은
drawdown budget을 초과하는 환경에서 사전에 정한 방어 sleeve가 실제로 비용을
정당화하는지 확인하는 것이다.

## 4분기 평가 항목

| 항목 | 질문 |
|---|---|
| MDD 개선 | 같은 기간 `P08_IEF30` 대비 drawdown이 반복적으로 낮았는가 |
| CAGR drag | 방어 sleeve 비용이 사전에 허용한 sacrifice 안에 있었는가 |
| Stress day | 급락일과 급반등일에 행동이 설명 가능한가 |
| 2022/rate shock | IEF 손실 구간에서 방어 효과가 있었는가 |
| Equity crash | COVID/GFC proxy형 하락에서 손실 완화가 있었는가 |
| 운영성 | 세금, 환전, 상품 제약이 live에서 감당 가능한가 |

## 승격 금지 사유

- 단순 최근 수익률 우위.
- 금 가격 상승.
- 현금 보유가 심리적으로 편안함.
- 뉴스 불안.
- 특정 한 달의 drawdown 우위.
- `P08_IEF30` drawdown 중 즉흥적 손실 회피.

## 승격 가능 조건

승격 검토는 아래 조건을 모두 만족할 때만 가능하다.

- 사전 drawdown budget 초과가 확인됨.
- 4분기 paper에서 shadow가 명확히 우월함.
- return sacrifice가 숫자로 명시되고 사용자가 수용함.
- stress window별 MDD 개선이 단일 사건에만 의존하지 않음.
- 세금과 환전 비용 반영 후에도 결론이 유지됨.

승격은 새 ticket으로만 진행한다. 기존 `P08_IEF30` live pilot 도중 임의 교체는
금지한다.
