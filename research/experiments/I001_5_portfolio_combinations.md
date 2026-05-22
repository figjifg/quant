# I001.5 — Portfolio combination baseline

## 상태
계획됨

## 이게 무슨 ticket 인가

I001-QC에서 QQQ KRW buy-and-hold 누적 수익률이 정확히 재확인되었다.
I002 macro gate로 가기 전에, H001(D013 + KR carry)이 QQQ/SPY 중심
core portfolio의 Sharpe 또는 MDD를 개선하는지 단순 조합 baseline으로 확인한다.

핵심 질문:

> QQQ buy-and-hold가 우월하면, H001이 QQQ/SPY 중심 portfolio의 Sharpe / MDD를 개선하는가?

## Backtest 정의

- 기간: 2010-01-04부터 2026-05-18까지 사용 가능한 공통 분기.
- 리밸런스: 분기 단위. 각 분기 수익률은 component KRW return × 사전 등록 weight의 합.
- H001 분기 return: `reports/experiments/H001_kr_short_rate_sleeve/equity_curve.csv`.
- D013 분기 return: `reports/experiments/D013_d009_threshold_minus_0p2/equity_curve.csv`.
- ETF 분기 return: `research_input_data/inputs/global_etf/yf_*.csv`를 USDKRW로 KRW 환산.
- 비용: ETF baseline은 ticket 정의상 비용 무시. H001/D013은 기존 산출물의 net value 사용.

## 사전 등록 portfolio combinations

| Portfolio | Weights |
|---|---|
| P01_QQQ_100 | 100% QQQ |
| P02_SPY_100 | 100% SPY |
| P03_QQQ50_SPY50 | 50% QQQ + 50% SPY |
| P04_QQQ50_H00150 | 50% QQQ + 50% H001 |
| P05_SPY50_H00150 | 50% SPY + 50% H001 |
| P06_SPY35_QQQ35_H00130 | 35% SPY + 35% QQQ + 30% H001 |
| P07_QQQ50_H00130_IEF20 | 50% QQQ + 30% H001 + 20% IEF |
| P08_SPY40_QQQ30_H00120_IEF10 | 40% SPY + 30% QQQ + 20% H001 + 10% IEF |

## 보고 항목

- 9 ETF buy-hold + D013 + H001 + 8 portfolios = 19행 비교표.
- 누적 net, CAGR, 분기 annualized Sharpe, 분기 MDD, 양의 수익 연도.
- Sharpe, MDD, CAGR ranking.
- H001 추가가 Sharpe 또는 MDD를 개선하는지 비교.
- Treasury(IEF) 추가 효과.

## 사전 등록 verdict

- H001이 QQQ 단독 또는 SPY 단독 대비 Sharpe/MDD를 개선하는지 숫자로 판정한다.
- I002 macro gate보다 risk-controlled core 조합이 먼저 필요한지 숫자로 권고한다.
- 전략 성과의 연구적 해석은 별도 review에서 다룬다.

## 산출물

- `reports/experiments/I001_5_portfolio_combinations/portfolio_metrics.csv`
- `reports/experiments/I001_5_portfolio_combinations/equity_curves_by_portfolio.csv`
- `reports/experiments/I001_5_portfolio_combinations/year_returns_by_portfolio.csv`
- `reports/experiments/I001_5_portfolio_combinations/correlation_matrix.csv`
- `reports/experiments/I001_5_portfolio_combinations/report.md`

## 엄격 제약

- D013, H001 strategy 미수정.
- `engine.py` 미수정.
- D-H, P, I000-I001 byte-identical.
- 단순 weighted combination만 사용. 최적화 금지.
- 위 사전 등록 weights 그대로 사용.
- 외부 network 금지.
- 새 코드: `src/audit/i001_5_portfolio_combinations.py`.
