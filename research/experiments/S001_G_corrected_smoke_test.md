# S001-G Corrected Smoke Test

## 목적

W001에서 수리한 한국 개별주 backtest utility layer로 S000의 핵심 단기 평균회귀 신호를 1회 corrected smoke 재실행한다.

## 범위

- Infrastructure QA only.
- S-family continuation이 아니며 alpha를 살리기 위한 파라미터 수정은 금지한다.
- S000 결과는 재활용하지 않고 비교 대상으로만 사용한다.

## 신호

- `r1d_lt_m3_hold1`
- `r1d_lt_m3_hold3`
- `r1d_lt_m3_hold5`

## 사전 등록 PASS gate

1. KRX trading calendar는 local equity panel의 날짜에서만 추출한다.
2. signal_date T는 T close 이후 사용 가능하며 execution_date는 T+1 이후여야 한다.
3. adjusted OHLC alias를 통해 return을 계산한다.
4. `거래대금추정여부 == True` 행은 headline에서 제외한다.
5. 거래대금 0, missing OHLC, 관리/정지 status 행은 제외한다.
6. limit-up/down open 행은 execution 불가로 본다.
7. sleeve NAV는 10억 원 capital, no leverage로 계산한다.
8. 비용은 round trip 30 bps와 매도 증권거래세 18 bps를 적용한다.
9. random placebo는 signal date별 event 수를 맞춘다.
10. duplicate signal, impossible return, entry/exit lineage sanity check를 자동 실행한다.
11. 기존 D013/H001/P08 산출물은 수정하지 않는다.
12. 결과 판정은 사전 정의한 null/mild/strong gate만 사용한다.

## Verdict rule

- Null/weak: gross < 1% 또는 Sharpe < 1.5 또는 placebo edge 없음 → S-family permanently CLOSED.
- Mild positive: gross 1-3%, Sharpe 1.5-3.0, placebo edge 있음 → diagnostic only, no paper.
- Strong: gross > 3%, Sharpe > 3.0, placebo clear edge → 새 S2-family preregistration 필요.
