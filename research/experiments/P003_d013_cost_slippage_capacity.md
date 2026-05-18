# P003 — D013 cost / slippage / capacity stress

## 상태
계획됨

## 이게 무슨 ticket 인가

P002 에서 D013 가 시점 차이 (1-2일 지연) 에는 robust 지만 unfavorable
fill 에 취약. P003 = 더 현실적 슬리피지 + 비용 + capacity 시나리오.

## 시나리오 (사전 등록)

### A. Cost stress (D018 보다 더 보수적)

| 시나리오 | commission | tax | slippage |
|---|---:|---:|---:|
| base | 1.5 | 20 | 5 |
| 3x | 4.5 | 60 | 15 |
| 5x | 7.5 | 100 | 25 |
| 10x | 15 | 200 | 50 |

### B. Slippage 별도 stress
- base + 5 bps slippage
- base + 10 bps slippage
- base + 20 bps slippage

### C. Capacity curve (운용금액 별 market impact)
- 5 종목 × 분기 리밸런싱 portfolio
- 운용금액 별 = 각 종목 매수 금액
- 일 평균 거래대금 대비 매수 비중 % 별
- Market impact = sqrt(주문/거래대금) × constant
- 운용금액: 1억, 5억, 10억, 30억, 50억, 100억, 300억, 500억, 1000억

각 운용금액 별:
- 평균 주문/거래대금 비중
- impact bps 추정
- 누적 수익 (impact 반영)

## 사전 등록 pass 기준

### A Cost stress
- 5x 비용에서 누적 ≥ +100%
- 10x 비용에서 누적 ≥ 0% (손실 아니어야)

### B Slippage
- +20 bps slippage 에서 누적 ≥ +100%

### C Capacity curve
- 운용금액 100억 까지 누적 ≥ +150%
- 운용금액 1000억 에서 누적 ≥ 0%
- capacity threshold (누적 +100% 이상 가능한 max AUM) 보고

## 산출물

- reports/experiments/P003_d013_cost_slippage_capacity/
- A_cost_stress/
- B_slippage/
- C_capacity_curve/
- summary.csv (모든 시나리오 비교)
- capacity_curve.png (가능하면) 또는 csv
- report.md (verdict + capacity 추정)

## 엄격 제약

- engine.py 미수정 (가능하면; 비용 multiplier 만 변경)
- D013 carrier 정의 변경 X
- D001-D015, E003-E015, F002-F012, G000-G002, P001-P002 byte-identical
- Market impact 계산: 단순 모델 (sqrt(participation) × constant) 사용
