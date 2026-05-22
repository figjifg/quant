# X-ETF900 Final Defensive ETF Challenge

## Purpose

지피티 결정: X-ETF900의 목적은 alpha 발견이 아니라 defensive role 발견이다.

## Scope

- Bounded 1회 final test.
- X-ETF track의 마지막 테스트.
- 3 module x 8 variants = 24 total.
- X-ETF002/003/004는 각각 full 진행하지 않는다.
- Role-based pass gate로 평가한다.

## Modules

### X-ETF900-A Dual Momentum Mini

- Risk assets: SPY, QQQ, IWM, VWO, EWY, EWJ, EWZ
- Defensive assets: IEF, TLT, SHY, GLD, UUP
- Signals: 6m total return, 12m minus 1m
- Rebalance: monthly, quarterly
- Portfolio:
  - risk-on top2 / risk-off defensive top2
  - risk-on top3 / risk-off defensive top2
- Risk-on rule: risk basket median momentum > defensive basket median momentum + SPY momentum > 0
- Risk-off: defensive top assets
- Total: 2 signals x 2 rebalance x 2 portfolio = 8

### X-ETF900-B Defensive Sleeve Rotation

- Base: SPY 29%, QQQ 21%, defensive sleeve 50%
- Defensive candidates: IEF, SHY, GLD, UUP, DBC
- Signals: 6m total return, 12m minus 1m
- Rebalance: monthly, quarterly
- Portfolio:
  - defensive sleeve top1
  - defensive sleeve top2 equal weight
- Total: 2 x 2 x 2 = 8

### X-ETF900-C Risk Budget Mini

- Universe: 13 ETF primary
- Methods: inverse volatility, ERC
- Vol lookbacks: 126d, 252d
- Rebalance: monthly, quarterly
- Constraints:
  - max single ETF 25%
  - min weight 0%
  - cash/SHY fallback
  - total exposure <= 100%, no leverage
- Total: 2 methods x 2 lookbacks x 2 rebalance = 8

## Common Settings

- X-ETF001 동일 3-layer cost: gross / after-cost 30bps / after-tax 22% + KRW 2.5m exemption.
- Daily NAV in KRW.
- Common evaluation start after 12m lookback.
- Subperiod: 2011-2014, 2015-2019, 2020-2026.
- Stress: COVID 2020-02~03, 2022 full year.
- Random control: 1000 trials.
- EW13 benchmark.

## Pass Gate

### Close Entire X-ETF Track If All

1. No variant beats P08 proxy after-cost Sharpe within +0.05.
2. No variant improves MDD vs P08 proxy by >= 2pp.
3. No variant improves 2022 stress meaningfully.
4. EW13 or random explains result.
5. After-tax collapses.
6. Turnover materially higher without MDD benefit.
7. Best variant = static SHY/IEF/GLD in disguise.
8. 2 of 3 subperiods fail vs P08 proxy.

### Diagnostic Pass If All

1. MDD vs P08 proxy >= 2-3pp 개선.
2. CAGR drag vs P08 proxy <= 1.5pp.
3. After-cost Sharpe >= P08 proxy - 0.05.
4. 2022 stress 개선 clearly.
5. Random / EW13 explain X.
6. Turnover/tax acceptable.

### Deep Validation Candidate If One

1. After-cost Sharpe >= P08 proxy + 0.05.
2. MDD >= 3pp 개선 + CAGR drag <= 1pp.
3. P08_IEF30 + small X-ETF defensive sleeve = portfolio MDD >= 2pp 개선 + CAGR drag <= 1pp.

Additional requirements:

- After-tax 생존.
- Subperiods 안 깨짐.
- Static cash/GLD clone X.

## Verdict Tree

If X-ETF900 FAIL:

- Close X-ETF track entirely.
- Update closed_register.md.
- X-ETF002/003/004 별도 X.
- 사용자 의지에 따라 X-KR001 또는 X-Lab close.

If X-ETF900 PASS diagnostic:

- Open X030 deep validation with 1 surviving variant only.
- No paper / no P08 import yet.

If X-ETF900 = lower return + lower MDD variants:

- Defensive reference only; production X.
- Compare to N002-B / N001-B.
- If a simpler shadow has the same role, close.
