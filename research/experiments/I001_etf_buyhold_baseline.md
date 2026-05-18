# I001 — ETF buy-and-hold baseline (KRW 환산)

## 상태
계획됨

## 이게 무슨 ticket 인가

I000 통과. I001 = 각 ETF 단순 buy-and-hold baseline.
다음 I002 (macro gate 적용) 의 비교 기준 + ETF 별 raw profile 확인.

## Backtest 정의

- 각 ETF 단순 buy-and-hold (2010-01-04 ~ 2026-05-18)
- KRW 환산 (USDKRW 변동 포함)
- 분기말 rebalance 없음 (단순 보유)
- 비용 무시 (baseline 단순)

## 보고 항목 (각 9 ETF + D013 + H001)

| Carrier | 누적 net | CAGR | Sharpe | MDD | 양의 수익 연도 |
|---|---:|---:|---:|---:|---:|
| QQQ buy-hold | +1757% | ? | ? | ? | ? |
| SPY buy-hold | +896% | ? | ? | ? | ? |
| ... |
| D013 | +254% | 8.0% | 0.53 | -34% | 7 |
| H001 | +357% | ? | 0.65 | -34% | ? |

비교 핵심:
- 절대 수익: QQQ 압도
- Risk-adjusted (Sharpe): D013 vs QQQ
- MDD: US 주식 vs D013
- 양의 수익 연도: 균일성

## 사전 등록 verdict

I001 = 진단 baseline. PROCEED 조건:
- 9 ETF 모두 KRW 환산 backtest 완료
- D013/H001 와 정량 비교 가능
- I002 (macro gate) 의 baseline 으로 사용 가능

## 산출물

- reports/experiments/I001_etf_buyhold_baseline/
- baseline_metrics.csv (각 9 ETF + D013 + H001)
- equity_curves.csv (분기 단위)
- mdd_attribution.csv (각 ETF 의 max drawdown 시기)
- year_returns.csv (각 ETF 연도별)
- report.md (정직한 비교 + I002 진행 권고)

## 엄격 제약

- D013, H001 strategy 미수정
- engine.py 가능하면 미수정 (buy-and-hold 단순)
- 새 코드: src/audit/i001_etf_baseline.py
- 외부 network X (이미 download 완료)
- sandbox pandas 없으면 직접 실행 OK
