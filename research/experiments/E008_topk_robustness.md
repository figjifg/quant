# E008 — Top-K 견고성 (E007 carrier)

## 상태
계획됨

## 이게 무슨 ticket 인가

E007 (Flow+RS+Breadth) 가 Layer 2 의 chamipon 후보 (+232%, 샤프 0.48).
사전 등록 Top 3, 그러나 Top-K 흔들기 견고함 검증 필요.

지피티 좋은 결과 패턴: Top 2 OK / Top 3 BEST / Top 4 OK / Top 5 weaker
나쁜 결과: Top 3 만 좋고 나머지 무너짐

## Top-K 후보 (사전 등록)

| K | sector 분배 (count-matched 5 종목) |
|---:|---|
| 2 | 3 / 2 |
| 3 (E007) | 2 / 2 / 1 |
| 4 | 2 / 1 / 1 / 1 |
| 5 | 1 / 1 / 1 / 1 / 1 |

## 사전 등록 견고성 판정

| 결과 | 판정 |
|---|---|
| 4 중 3 이상 샤프 ≥ 0.40 + 누적 ≥ +150% | **튼튼한 안정 구간** |
| 2 중 만 통과 | 어중간 |
| Top 3 만 통과 (다른 K 는 0.30 미만) | **절벽 — 과최적화 의심** |

## 산출물

- reports/experiments/E008_topk_robustness/
- 각 K 별 결과
- grid_summary.csv

## 엄격 제약

- engine, 기존 strategy / D013 미수정
- D001-D015, E003-E007 byte-identical
- E007 carrier (Flow+RS+Breadth) 그대로, K 만 변경
- sandbox pandas 없으면 직접 실행 OK
