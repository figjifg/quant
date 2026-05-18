# E014 — RS+Breadth Top 4 정식 챔피언 등록 (마지막 Layer 2 승격)

## 상태
계획됨

## 이게 무슨 ticket 인가

E012 score ablation 에서 발견: **RS+Breadth Top 4 (+362% / 0.63) > Flow+RS+Breadth Top 4 (+297% / 0.57)**.

이건 임의의 새 변수 추가 아니라 **Flow 제거라는 구조적 단순화**:
- E004 Flow only: 실패
- E006 Flow+RS: RS 희석
- E007 Flow+RS+Breadth: portfolio 개선 (Breadth 가 false positive 거름)
- E012 RS+Breadth: Flow 제거가 최강 — 일관

지피티 평가: "단순 chasing 아닌 구조적 finding, 마지막 정식 승격 가치 있음".

E014 = **Layer 2 의 마지막 정식 등록**. E015 후 Layer 3 진입.

## Carrier 정의 (사전 등록, freeze)

| 항목 | 값 |
|---|---|
| Layer 1 | D013-L1-FROZEN |
| Layer 2 score | **RS + Breadth** (Flow 제거) |
| Top-K | 4 |
| Allocation | 2 / 1 / 1 / 1 |
| Rebalance | 분기 |
| Universe | dynamic top 100 |
| Sector mapping | E001-rev snapshot |
| Portfolio size | 5 종목 count-matched |
| Cost | 1.5 / 20 / 5 bps |

## 보고 항목

- E012 RS+Breadth Top 4 결과 정확 재현 (+362% / 0.63 / -36%)
- D013 (+254% / 0.53 / -34%) 와 비교
- E011 (+297% / 0.57 / -41%) 와 비교
- 분기별 매수 sector + 종목

## 엄격 제약

- engine, 기존 strategy 미수정
- D001-D015, E003-E013 byte-identical
- 새 코드 최소화 (sector_combined_score 의 weights 파라미터 이용)
