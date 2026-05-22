# Q006.5 Bias & Benchmark Audit

## 목적

Q002/Q006의 초과성과가 진짜 factor alpha인지, 현재 99종목 survivor universe와 mega-cap/sector concentration에서 온 것인지 검증한다.

## 사전 등록 audit

1. Survivor universe equal-weight benchmark: 99종목 equal-weight quarterly rebalance를 SPY와 비교한다.
2. Random 30 simulation: 고정 seed로 99종목 중 random 30 equal-weight를 1000회 생성하고 CAGR/Sharpe/Excess CAGR 분포에서 Q002/Q006 percentile을 측정한다.
3. Market-cap top 30 benchmark: SEC filed shares와 execution-date price로 추정한 분기말 시총 기준 top 30 equal-weight를 SPY/Q002/Q006과 비교한다.
4. Sector exposure: Q002/Q006 분기 sector weight를 survivor universe equal-weight 및 시총 top30 proxy와 비교한다.
5. Magnificent 7 exclusion: AAPL, MSFT, GOOGL, AMZN, META, NVDA, TSLA 제외 후 기존 Q002/Q006 signal score에서 top30을 재선정한다.
6. Top contributor attribution: Q002/Q006 NAV 기여도를 종목별로 분해하고 상위 5/10/20 집중도 및 2020-2026 vs 2010-2019 기여를 측정한다.
7. Q1/Q2/Q3/Q4 bucket returns vs SPY: 각 quartile NAV와 SPY excess를 비교한다.

## 제약

- 기존 Q002/Q006 결과와 D/H/P/I/T/O/N/K/J 결과는 수정하지 않는다.
- `src/backtest/engine.py`, D013, H001, P08_IEF30 strategy는 수정하지 않는다.
- 외부 network를 사용하지 않는다.
- 이 audit는 survivor universe 한계를 정직하게 표시하며 Q-family production promote 근거로 사용하지 않는다.
