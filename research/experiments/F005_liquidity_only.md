# F005 — Stock liquidity / participation only

## 상태
계획됨

## 이게 무슨 ticket 인가

F001-F004 이후 Layer 3 단독 stock selector로 거래대금/회전율 관심도 증가가
독립 알파인지 확인한다. Prior는 liquidity가 단독 알파라기보다 confirmation
성격일 가능성이 높다는 쪽이다. 그래도 단독 baseline으로 확인한다.

## 변수 정의 (사전 등록)

```
liquidity_change(stock, T) =
    stock 최근 20일 평균 거래대금 / stock 최근 120일 평균 거래대금

turnover(stock, t) =
    traded_value(stock, t) / market_cap(stock, t)

turnover_change(stock, T) =
    stock 최근 20일 평균 turnover / stock 최근 120일 평균 turnover

Stock Liquidity Score =
    zscore_within_sector(평균(liquidity_change, turnover_change))
```

cross-sectional z-score는 같은 sector 내 종목끼리 계산한다.

## 결측 처리

F000 확인 기준 현재 실행 입력의 거래대금 결측은 0%이므로 별도 대체는 하지
않는다. `traded_value`, `market_cap` 중 필요한 rolling window에 결측이 있거나
분모가 0 이하이면 해당 종목의 raw score를 NaN으로 둔다. NaN 종목은 진단의
유효 표본과 portfolio 후보에서 제외한다.

## 두 carrier 위 portfolio

### F005-A: D013 direct + Stock liquidity top 5
- D013 ON 분기에 universe 전체에서 stock liquidity score 상위 5 종목
- 비교: F001-A, F002-A, F003-A, F004-A

### F005-B: E014 + Stock liquidity within sector
- D013 ON + E014 Top 4 sector
- 각 sector 내에서 stock liquidity top → 2/1/1/1 분배
- 비교: F001-B, F002-B, F003-B, F004-B

## 진단

### A. Rank IC
- 각 분기말의 stock liquidity score와 다음 분기 stock 수익률의 Spearman correlation
- D013 direct: universe-wide IC
- E014: within-sector IC
- 평균 IC, t-stat

### B. Top-Bottom spread
- D013 direct: universe top 5 vs bottom 5 forward return
- E014: 각 sector 내 top vs bottom

### C. Portfolio metrics
- carrier uplift vs F001
- F002/F003/F004 대비 누적수익/Sharpe/MDD 비교

## 사전 등록 verdict

| 결과 | 판정 |
|---|---|
| 두 carrier 모두 baseline uplift + IC t-stat ≥ 2 | surprise pass |
| 한 carrier 만 통과 | weak |
| 둘 다 미통과 | liquidity 단독 약함 |

## 산출물

- reports/experiments/F005_liquidity_only/
- A_d013_direct/ (portfolio + diagnostics)
- B_e014/ (portfolio + diagnostics)
- ic_diagnostics.csv
- carrier_comparison.csv
- report.md

## 엄격 제약

- engine.py, 기존 strategy 미수정
- D001-D015, E003-E015, F002-F004 byte-identical
- 새 코드: src/features/stock_liquidity_score.py
- 새 strategy: src/strategies/f005_liquidity_d013_direct.py, src/strategies/f005_liquidity_e014.py
- DO NOT use future data: signal quarter-end T uses stock liquidity, turnover, and market cap through T; execution is T+1 or later
