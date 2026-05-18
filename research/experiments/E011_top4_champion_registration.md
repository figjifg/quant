# E011 — E008 Top 4 정식 챔피언 후보 등록

## 상태
계획됨

## 이게 무슨 ticket 인가

E008 의 Top-K 격자에서 Top 4 (+297% / 0.57) 가 D013 (+254% / 0.53)
명확히 넘음. 그러나 사후 발견 — 사전 등록 외. D-family 의 D011 →
D013 패턴 (사후 finding → 정식 ticket → 견고성 검증) 적용.

E011 = Top 4 정식 baseline 등록 + 보고. E012 (견고성) 와 E013
(시기 분할) 별도.

## Carrier 정의 (사전 등록, freeze)

| 항목 | 값 |
|---|---|
| Layer 1 | D013 (10 vars, 5 blocks, 60mo, threshold -0.2) |
| Layer 2 score | Flow + RS + Breadth (E007 동일) |
| Top-K | **4** (E007 의 3 변경) |
| Allocation | **2 / 1 / 1 / 1** (E008 정의 동일) |
| Rebalance | 분기 |
| Universe | dynamic top 100 |
| Sector mapping | E001-rev freeze |
| Portfolio size | 5 종목 count-matched 유지 |
| Cost | 1.5 / 20.0 / 5.0 bps |

## E011 보고 항목

- 누적 수익 / 비용 0
- 샤프 / 최대 손실폭 / 양의 수익 연도 수
- 거래 횟수 / turnover
- E008 K=4 결과 정확 재현 확인 (+297% / 0.57 / -41%)
- D013 (+254% / 0.53 / -34%) 와 비교
- E007 (+232% / 0.48 / -40%) 와 비교
- 분기별 매수 sector 분포

## 엄격 제약

- engine.py, 기존 strategy 미수정
- D001-D015, E003-E010 byte-identical
- E007 strategy 재사용, Top 4 만 변경
- E008 의 K=4 결과 정확 재현 검증
