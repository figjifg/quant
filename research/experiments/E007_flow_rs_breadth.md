# E007 — Flow + RS + Breadth (챔피언 후보)

## 상태
계획됨

## 이게 무슨 ticket 인가

지피티의 챔피언 후보. RS 단독 (E005) 이 최강이었고 Flow 추가 (E006) 가
오히려 약화시켰음. Breadth 가 진짜 추가 정보 줄지가 핵심 질문.

E007 = 3 변수 평균. 진단 + portfolio (통과 시).

## Breadth Score (사전 등록)

지피티 정의:
```
sector_breadth_value =
    섹터 내 외국인 순매수 양수 종목 수 / 섹터 내 전체 종목 수

sector_breadth_strict =
    섹터 내 외국인 순매수 양수 AND KOSPI 대비 상대강도 양수 종목 수 /
    섹터 내 전체 종목 수
```

기본: `sector_breadth_strict` (Flow + RS 가 모두 양수인 종목 비율)

각 종목별 outlook:
- 외국인 순매수 = stock_with_sector_daily.csv 의 foreign_net_buy_amount
- 상대강도 = stock 의 20일 누적 수익 - KOSPI 20일 누적 수익

분기말 시점에 종목별 status 계산 → 섹터별 비율

cross-sectional z-score.

thin sector (n_stocks ≤2) 는 NaN (분모 작아 noise).

## Combined Score
```
Sector Score = 평균(Flow Score, RS Score, Breadth Score)
```

## 진단 + verdict

E004-E006 와 동일 기준:
- Rank IC 평균 ≥ 0.05 AND spread t-stat ≥ 2 → 통과 + portfolio
- 통과 시 D013 ON + Top 3 (2/2/1)

기대: Breadth 가 진짜 추가 정보 = 단일 대형주 vs 섹터 전체 자금 유입 구별 → spike year 의 mismatched signal 줄일 가능성

## 산출물

- reports/experiments/E007_flow_rs_breadth/
- comparison_with_all_e.csv (E003-A vs E004 vs E005 vs E006 vs E007)
- breadth_diagnostic.csv (분기별 sector 별 breadth 값)

## 엄격 제약

- engine.py, 기존 strategy / D013 미수정
- D001-D015, E003-E006 byte-identical
- E005 패턴 (sector_mapping CSV 직접 받음)
- thin sector 처리: breadth NaN, combined NaN, Top-K 후보 제외
