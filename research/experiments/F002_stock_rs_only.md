# F002 — Stock RS only (Layer 3 1순위 변수, sector-relative)

## 상태
계획됨

## 이게 무슨 ticket 인가

Layer 2 finding: RS 가 메인 알파. Layer 3 1순위 변수 = 종목 단위 RS.
지피티 권장: **sector-relative** (KOSPI 대비 아닌).

## 변수 정의 (사전 등록)

```
stock_rs_20(stock, T) =
    stock 20일 누적 수익 - 그 종목 소속 sector 20일 누적 수익

stock_rs_60(stock, T) =
    stock 60일 누적 수익 - 그 종목 소속 sector 60일 수익

Stock RS Score = zscore_within_sector(평균(stock_rs_20, stock_rs_60))
```

cross-sectional z-score 는 같은 sector 내 종목 끼리. (Stock-level cross
sector 가 아니라 sector-internal ranking 가 더 자연스러움).

## 두 carrier 위 portfolio

### F002-A: D013 direct + Stock RS top 5
- D013 ON 분기에 universe 전체에서 stock RS score 상위 5 종목 (cross-section)
- 비교: F001-A (시총 top 5)

### F002-B: E014 + Stock RS within sector
- D013 ON + E014 Top 4 sector
- 각 sector 내에서 stock RS top → 2/1/1/1 분배
- 비교: F001-B (sector 내 시총 top)

## 진단 (Layer 2 패턴, 약간 완화)

### A. Rank IC
- 각 분기말의 stock RS score 와 다음 분기 stock 수익률 의 Spearman correlation
- D013 direct: universe-wide IC
- E014: within-sector IC (sector 내 비교)
- 평균 IC, t-stat

### B. Top-Bottom spread
- D013 direct: universe top 5 vs bottom 5 forward return
- E014: 각 sector 내 top vs bottom

### C. Portfolio metrics (vs baseline)
- carrier uplift (누적/Sharpe/MDD vs F001)

## 사전 등록 verdict

| 결과 | 판정 |
|---|---|
| 두 carrier 모두 baseline uplift + IC t-stat ≥ 2 | 통과, F003 진행 |
| 한 carrier 만 통과 | weak — 어느 쪽에서 진행 |
| 둘 다 미통과 | RS 종목 단위 약함, F003 fallback |

지피티 기준: IC ≥ 0.02 약함, 0.03 양호, 0.05 강함.

## 산출물

- reports/experiments/F002_stock_rs_only/
- A_d013_direct/ (portfolio + diagnostics)
- B_e014/ (portfolio + diagnostics)
- ic_diagnostics.csv
- carrier_comparison.csv
- report.md

## 엄격 제약

- engine, 기존 strategy 미수정
- D001-D015, E003-E015 byte-identical
- 새 코드: src/features/stock_rs_score.py (sector-relative)
- 외국인/기관 매매 결측 9.5% — F002 는 가격 만 사용해서 영향 없음
- 종목별 sector 매핑은 sector_mapping_loader 재사용
