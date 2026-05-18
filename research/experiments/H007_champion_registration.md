# H007 — H001 Champion 정식 등록 (D013 + KR carry)

## 상태
계획됨

## 이게 무슨 ticket 인가

H-family 5 sleeve 시도 후 H001 (KR carry) champion. 정식 등록.

## Carrier 정의 (사전 등록, freeze)

| 항목 | 값 |
|---|---|
| Layer 1 (ON) | D013 macro gate 그대로 |
| OFF sleeve | KR 단기금리 carry (월 환산 → 분기) |
| KR rate source | FRED IR3TIB01KRM156N (monthly annualized) |
| Sleeve formula | quarter_return = (1 + annual_rate/12)^3 - 1 |
| Universe | dynamic top 100 (D013 동일) |
| Selection | 시총 top 5 equal weight 20% (D013 동일) |
| Rebalance | 분기말 +1 거래일 시가 |
| Cost | 1.5 / 20 / 5 bps (D013 동일) |

## 보고 항목

- H001 결과 재현 확인 (+357% / 0.65 / -34%)
- D013 baseline (+254% / 0.53 / -34%) 대비 차이
- 분기별 OFF carry contribution
- H002/H003/H004/H005 와 종합 비교

## 엄격 제약

- engine.py, D013, H001 strategy 미수정
- D-G, P, H000-H005 byte-identical
- H001 결과 정확 재현 sanity check
