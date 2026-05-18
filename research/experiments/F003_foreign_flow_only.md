# F003 — Stock foreign flow only

## 상태
계획됨

## 이게 무슨 ticket 인가

Layer 2의 Flow 단독은 lagging 성격이 강했지만, 종목 단위에서는 다를 수
있다. 개별 종목의 외국인 누적 매집, 패시브 수급, 특정 종목 집중 수급이
sector aggregate보다 먼저 나타나는지 확인한다.

## 변수 정의 (사전 등록)

```
foreign_flow_20(stock, T) =
    stock 외국인 순매수금액 20일 합 / stock 거래대금 20일 합

foreign_flow_60(stock, T) =
    stock 외국인 순매수금액 60일 합 / stock 시가총액(T)

Stock Foreign Flow Score =
    zscore_within_sector(평균(foreign_flow_20, foreign_flow_60))
```

cross-sectional z-score는 같은 sector 내 종목끼리 계산한다.

## 결측 처리

종목별 외국인 매매 결측은 대체하지 않는다. `foreign_net_buy_amount`,
`traded_value`, `market_cap` 중 필요한 rolling window에 결측이 있거나
분모가 0 이하이면 해당 종목의 raw score를 NaN으로 둔다. NaN 종목은
진단의 유효 표본과 portfolio 후보에서 제외한다.

## 두 carrier 위 portfolio

### F003-A: D013 direct + Stock foreign flow top 5
- D013 ON 분기에 universe 전체에서 stock foreign flow score 상위 5 종목
- 비교: F001-A (시총 top 5), F002-A (Stock RS)

### F003-B: E014 + Stock foreign flow within sector
- D013 ON + E014 Top 4 sector
- 각 sector 내에서 stock foreign flow top → 2/1/1/1 분배
- 비교: F001-B (sector 내 시총 top), F002-B (Stock RS)

## 진단

### A. Rank IC
- 각 분기말의 stock foreign flow score와 다음 분기 stock 수익률의 Spearman correlation
- D013 direct: universe-wide IC
- E014: within-sector IC
- 평균 IC, t-stat

### B. Top-Bottom spread
- D013 direct: universe top 5 vs bottom 5 forward return
- E014: 각 sector 내 top vs bottom

### C. Portfolio metrics
- carrier uplift vs F001
- F002 Stock RS 대비 누적수익/Sharpe/MDD 비교

## 사전 등록 verdict

| 결과 | 판정 |
|---|---|
| 두 carrier 모두 baseline uplift + IC t-stat ≥ 2 | surprise pass |
| 한 carrier 만 통과 | weak |
| 둘 다 미통과 | stock-level Flow 단독 약함 |

지피티 권장 prior: Layer 2의 Flow가 단독으로 약했으므로 종목 단위도 약할
가능성이 크다. 통과하면 surprise로 본다.

## 산출물

- reports/experiments/F003_foreign_flow_only/
- A_d013_direct/ (portfolio + diagnostics)
- B_e014/ (portfolio + diagnostics)
- ic_diagnostics.csv
- carrier_comparison.csv
- report.md

## 엄격 제약

- engine.py, 기존 strategy 미수정
- D001-D015, E003-E015, F002 byte-identical
- 새 코드: src/features/stock_foreign_flow_score.py
- 새 strategy: src/strategies/f003_foreign_flow_d013_direct.py, src/strategies/f003_foreign_flow_e014.py
- DO NOT use future data: signal quarter-end T uses stock flow and denominators through T; execution is T+1 or later
