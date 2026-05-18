# H000 D013 OFF Regime Diagnostics

## A. OFF regime statistics

- OFF quarters: 38 (62.30%)
- ON quarters: 23 (37.70%)
- Average OFF duration: 7.60 quarters
- Longest OFF streak: 24 quarters
- ON/OFF transitions: 9

## B. Return distribution

- OFF KOSPI quarterly return mean: 0.023508; median: 0.027999; positive: 71.05%
- ON KOSPI quarterly return mean: 0.093509; median: 0.085529; positive: 73.91%
- OFF USDKRW quarterly change mean: 0.010417; OFF USDKRW yoy mean: 0.026192
- OFF US 10y quarterly change mean: 3.57 bps
- OFF KR short-rate quarterly carry mean: 0.006678

## C. Missed rally / avoided crash

- OFF and KOSPI > +10%: 4 quarters
- OFF and KOSPI < -10%: 3 quarters
- ON and KOSPI < -10%: 1 quarters

## D. Sleeve candidate OFF returns

- USDKRW mean yoy during OFF: 0.026192
- US 10y mean quarterly change during OFF: 3.57 bps
- KR short-rate mean quarterly carry during OFF: 0.006678
- D013 virtual cash baseline during OFF: 0.000000

## E. KOSPI inverse diagnostic

- Simple OFF short mean: -0.023508; std: 0.067292; positive: 28.95%
- Conclusion: not_positive_expected_value

## Verdict

- OFF character: sideways with bipolar tails
- Sleeve priority: H003 KR short-rate carry 1순위, H001 USDKRW 2순위, H005 defensive/static sleeve 3순위, H002 Treasury 4순위, H004 Gold는 H000 제외 데이터라 H004 단계에서 별도 검증입니다.
- H006 KOSPI inverse: OFF 평균 KOSPI가 양수라 단순 inverse/short의 기대값은 음수입니다. H006 KOSPI inverse는 sleeve 후보 가치가 낮습니다. 이 진단은 decay와 ETF 비용을 제외한 H000 범위의 1차 필터입니다.

## Metadata

- No new backtest was run.
- D013 strategy and existing D/E/F/G/P family outputs were not modified.
- Gold is excluded in H000 per current task instruction.
- KOSPI return source: krx_market_breadth_kospi_2010_2026.csv cap_weighted_return, compounded by quarter.
- USDKRW and US 10y source: FRED files aligned to latest observation on or before each D013 quarterly signal_date.
- KR short-rate source: fred_kr_short_rate.csv; monthly annualized rates converted to monthly carry and compounded by quarter.
