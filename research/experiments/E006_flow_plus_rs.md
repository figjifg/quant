# E006 — Flow + RS 결합

## 상태
계획됨

## 이게 무슨 ticket 인가

E004 (Flow 단독) FAIL — 외국인 수급 lagging
E005 (RS 단독) PASS — 가격 모멘텀 sector 선택력 있음 (Rank IC 0.16)

E006 = 두 변수 결합. Flow 의 lagging 이 RS 와 결합 시 보완되는가?
또는 noise 추가 만 되는가?

## 변수 정의 (사전 등록)

```
Sector Score = 평균(Flow Score, RS Score)

Flow Score = E004 동일
RS Score = E005 동일
```

cross-sectional z-score 는 이미 각 component 에 적용됨.
단순 평균.

## 진단 (E004/E005 와 동일 구조)

Rank IC, Top-Bottom spread, subperiod, spike year.

verdict:
- Rank IC 평균 ≥ 0.05 AND spread t-stat ≥ 2 → 통과 + portfolio
- 미통과 → portfolio skip

기대: Flow 의 lagging 효과로 noise 증가 가능. RS 단독 (Rank IC 0.16)
보다 약화 가능성 vs 향상 가능성.

## 포트폴리오 (진단 통과 시)

- D013 macro gate ON 분기 → Sector Score Top 3
- 2/2/1 분배

## 산출물

- reports/experiments/E006_flow_plus_rs/
- E005 와 동일 구조 + comparison_with_e003_e004_e005.csv

## 엄격 제약

- DO NOT modify engine, 기존 strategy 모듈
- D001-D015, E003, E004, E005 byte-identical
- 새 코드: src/features/sector_combined_score.py (또는 sector_flow_score, sector_rs_score reuse), src/strategies/e006_flow_plus_rs.py
- look-ahead 방지
