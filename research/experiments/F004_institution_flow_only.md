# F004 — Stock institution flow only

## 상태
계획됨

## 이게 무슨 ticket 인가

F003의 종목 단위 외국인 수급 실험을 기관 수급으로 대체한다. Layer 3에서
기관의 종목별 누적 순매수가 외국인 수급보다 강한 단기/분기 리밸런싱
carrier인지 확인한다.

## 변수 정의 (사전 등록)

```
institution_flow_20(stock, T) =
    stock 기관 순매수금액 20일 합 / stock 거래대금 20일 합

institution_flow_60(stock, T) =
    stock 기관 순매수금액 60일 합 / stock 시가총액(T)

Stock Institution Flow Score =
    zscore_within_sector(평균(institution_flow_20, institution_flow_60))
```

cross-sectional z-score는 같은 sector 내 종목끼리 계산한다.

## 결측 처리

종목별 기관 매매 결측은 대체하지 않는다. `institution_net_buy_amount`,
`traded_value`, `market_cap` 중 필요한 rolling window에 결측이 있거나
분모가 0 이하이면 해당 종목의 raw score를 NaN으로 둔다. NaN 종목은
진단의 유효 표본과 portfolio 후보에서 제외한다.

현재 panel의 종목별 기관 매매 결측은 외국인과 같은 행에서 발생하는 구조다.
실행 입력 `data/processed/stock_with_sector_daily.csv` 기준
`institution_net_buy_amount` 결측은 17,128 / 402,198행(4.2586%)이며
`foreign_net_buy_amount`와 byte-for-byte 같은 결측 위치다. 원천 panel별로는
2010-2016 구간 130,797 / 1,093,386행(11.9626%), 2017-2024 구간 0%,
2018-2024 구간 0%, 2025-2026 KRX 구간 1,228 / 172,543행(0.7117%)이다.
따라서 기관 결측은 외국인과 동일하게 처리하되, 현재 실행 입력의 실제
결측률은 9.5%가 아니라 4.2586%로 기록한다. 결측 정책은 F003과 동일하게
"미대체, 후보 제외"로 고정한다.

## 두 carrier 위 portfolio

### F004-A: D013 direct + Stock institution flow top 5
- D013 ON 분기에 universe 전체에서 stock institution flow score 상위 5 종목
- 비교: F001-A (시총 top 5), F003-A (Stock foreign flow)

### F004-B: E014 + Stock institution flow within sector
- D013 ON + E014 Top 4 sector
- 각 sector 내에서 stock institution flow top → 2/1/1/1 분배
- 비교: F001-B (sector 내 시총 top), F003-B (Stock foreign flow)

## 진단

### A. Rank IC
- 각 분기말의 stock institution flow score와 다음 분기 stock 수익률의 Spearman correlation
- D013 direct: universe-wide IC
- E014: within-sector IC
- 평균 IC, t-stat

### B. Top-Bottom spread
- D013 direct: universe top 5 vs bottom 5 forward return
- E014: 각 sector 내 top vs bottom

### C. Portfolio metrics
- carrier uplift vs F001
- F003 Stock foreign flow 대비 누적수익/Sharpe/MDD 비교

## 사전 등록 verdict

| 결과 | 판정 |
|---|---|
| 두 carrier 모두 baseline uplift + IC t-stat ≥ 2 | surprise pass |
| 한 carrier 만 통과 | weak |
| 둘 다 미통과 | stock-level institution Flow 단독 약함 |

## 산출물

- reports/experiments/F004_institution_flow_only/
- A_d013_direct/ (portfolio + diagnostics)
- B_e014/ (portfolio + diagnostics)
- ic_diagnostics.csv
- carrier_comparison.csv
- report.md

## 엄격 제약

- engine.py, 기존 strategy 미수정
- D001-D015, E003-E015, F002, F003 byte-identical
- 새 코드: src/features/stock_institution_flow_score.py
- 새 strategy: src/strategies/f004_institution_flow_d013_direct.py, src/strategies/f004_institution_flow_e014.py
- DO NOT use future data: signal quarter-end T uses stock flow and denominators through T; execution is T+1 or later
