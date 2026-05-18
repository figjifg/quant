# H004 — Gold sleeve (KODEX 132030)

## 상태
계획됨

## 이게 무슨 ticket 인가

지피티 framework H004. H000 에서 FRED gold spot 없어 별도 처리.
pykrx 로 KODEX 골드선물(H) 132030 ETF 사용 가능 확인 → H004 진행.

## Sleeve 정의

- D013 ON: 기존 D013 top 5
- D013 OFF: KODEX 132030 매수 (KRW 기반 헤지 ETF)
- ETF inception 2010-10-01 → 2010-Q1, Q2, Q3 (inception 전) cash fallback

## 데이터

- KODEX 132030 가격: research_input_data/inputs/macro_features/krx_kodex_gold_132030.csv
- 3844 rows, 2010-10-01 ~ 2026-05-18
- 종가 사용 (분기말 close)

## ETF inception bias 처리 (사전 등록)

- 2010-Q1, Q2, Q3: KODEX 132030 없음 → 그 분기 cash (return 0)
- 2010-Q4 부터 gold ETF 사용

## 사전 등록 verdict

- 누적 D013 baseline (+254%) 보다 개선
- Sharpe ≥ 0.53 유지 또는 개선
- Gold sleeve max DD ≤ 15% (Gold 변동성 높을 가능성)
- 2022 (인플레 + 금리 급등) 시기 gold 영향 확인
- H001 (KR carry, +357% / 0.65) 와 비교

## 산출물

- reports/experiments/H004_gold_sleeve/
- portfolio metrics
- baseline_comparison.csv (D013, H001, H004)
- gold_return_decomposition.csv (분기별 ETF return)
- regime_breakdown.csv (rate-rise vs rate-fall 시기)
- inception_handling_log.csv (2010 cash fallback 명시)
- report.md (verdict + H-family final champion 비교)

## 엄격 제약

- D013 strategy 미수정 (ON byte-identical)
- engine.py 미수정
- D-G, P, H000-H003, H005 byte-identical
- ETF 가격 = 종가 (분기말 시점)
- KRW 기반 ETF 이므로 USDKRW 환산 불필요
