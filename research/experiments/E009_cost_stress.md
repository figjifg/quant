# E009 — E007 비용 stress

## 상태
계획됨

## 이게 무슨 ticket 인가

E007 (사전 등록 챔피언 후보) 의 비용 stress. E008 에서 Top 4 가
더 좋게 나왔지만 사전 등록은 E007 (Top 3). 일관성 유지.

## 비용 시나리오

D018 와 동일:
- base (1.5/20/5 bps)
- 2x (3.0/40/10)
- 3x (4.5/60/15)
- extra_slippage (1.5/20/15)

## 판정

- 3x 비용에도 D013 (+254%) 보다 못해도 큰 폭 후퇴 없으면 OK
- 모든 시나리오 누적 ≥ 0 + 샤프 ≥ 0.20 → 통과

## 산출물

- reports/experiments/E009_cost_stress/
- cost_stress_summary.csv

## 엄격 제약

- E007 carrier 그대로 (Flow+RS+Breadth, Top 3)
- 비용만 변경
- D001-D015, E003-E008 byte-identical
