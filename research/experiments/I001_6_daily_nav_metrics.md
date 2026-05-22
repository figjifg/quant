# I001.6 — Daily NAV metric standardization

## 상태
계획됨

## 이게 무슨 ticket 인가

I003 robustness로 진행하기 전에 production risk metric 기준을 일별 NAV로
통일한다. I001.5 portfolio 조합표는 분기 수익률 기반 metric을 사용했고,
QQQ Sharpe가 직접 일별 계산값과 다르게 나타났다. 특히 MDD는 분기말 수익률로
계산하면 장중/월중 drawdown을 과소평가할 수 있다.

핵심 결정문:

> I001.6 metric standardization / daily NAV reconstruction (먼저).
> I003 robustness 전 metric 기준 통일 필수.
> QQQ Sharpe 직접 계산 1.018 vs codex 분기 단위 1.211 차이.
> production risk metric 은 반드시 일별 NAV.
> 특히 MDD: 분기말 수익률로 MDD 계산 시 장중/월중 drawdown 과소평가.

## Backtest / audit 정의

- 기간: 2010-01-04부터 2026-05-18까지 사용 가능한 일별 data.
- 대상:
  - 9 ETF buy-hold: SPY, QQQ, IWM, SHY, IEF, TLT, GLD, UUP, DBC.
  - D013: `reports/experiments/D013_d009_threshold_minus_0p2/equity_curve.csv`.
  - H001: `reports/experiments/H001_kr_short_rate_sleeve/equity_curve.csv`.
  - I001.5 사전 등록 8 portfolios: P01-P08.
- ETF NAV: Yahoo ETF close를 USDKRW로 KRW 환산한 daily NAV.
- D013/H001 NAV: 기존 equity curve의 net value를 그대로 사용한다.
- 공통 calendar: ETF, D013, H001 component date의 union calendar를 사용하고,
  휴일 차이는 component NAV forward-fill로 처리한다.

## Portfolio daily NAV 계산 방식

- 사전 등록 weights만 사용한다.
- Quarterly rebalance 시점에 weights를 reset한다.
- 분기 내에는 component daily price/NAV 변동을 그대로 mark-to-market하며,
  rebalance 사이 weights는 drift한다.
- Weight optimization은 하지 않는다.

## Metric 표준화

- Sharpe: `daily_return.mean() / daily_return.std() * sqrt(252)`.
- MDD: daily NAV peak-to-trough.
- CAGR: `(1 + total_return) ** (1 / years) - 1`.
- 양의 수익 연도: calendar year 기준.
- Volatility: `daily_return.std() * sqrt(252)`.
- Sortino: `daily_return.mean() / downside_std * sqrt(252)`.

## 비교 항목

- Quarterly vs Daily metric 비교표:
  - 같은 carrier의 I001.5 quarterly metric과 I001.6 daily metric을 비교한다.
  - 차이가 큰 metric, 특히 MDD와 Sharpe를 강조한다.
- 주요 비교 대상:
  - P01_QQQ_100, P02_SPY_100, P03_QQQ50_SPY50.
  - P06_SPY35_QQQ35_H00130.
  - P07_QQQ50_H00130_IEF20.
  - P08_SPY40_QQQ30_H00120_IEF10.
  - H001, D013.
  - 9 ETF buy-hold.

## 산출물

- `reports/experiments/I001_6_daily_nav_metrics/daily_nav_by_portfolio.csv`
- `reports/experiments/I001_6_daily_nav_metrics/daily_metrics.csv`
- `reports/experiments/I001_6_daily_nav_metrics/quarterly_vs_daily_metrics.csv`
- `reports/experiments/I001_6_daily_nav_metrics/mdd_drawdown_paths.csv`
- `reports/experiments/I001_6_daily_nav_metrics/report.md`

## report.md 필수 항목

- QC 결과: quarterly metric과 daily metric 차이, 특히 MDD/Sharpe.
- P08 daily MDD가 I001.5의 -16.56%와 얼마나 다른지.
- QQQ Sharpe daily vs 분기 중 어느 값이 production 기준인지.
- 최종 daily 기준 metric 표.
- P08 일별 NAV 그래프 묘사 및 큰 drawdown 시기.
- I003 진행 권고 또는 P08 demote 권고.

## 엄격 제약

- D013, H001 strategy 미수정.
- `engine.py` 미수정.
- D-H, P, I000-I001.5 모든 결과 byte-identical.
- 새 audit script만 추가한다.
- 외부 network 금지.
- Weight optimization 금지.
- 사전 등록 weights만 사용.

