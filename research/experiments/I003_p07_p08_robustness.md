# I003 — P07/P08 robustness 동시 검증

## 상태
계획됨

## 목적

I003은 P07과 P08의 final freeze가 아니라, 두 후보 주변의 coarse structural
robustness plateau를 확인하는 audit이다. 새 P09를 찾지 않고, grid의 새 best
weight를 final 후보로 승격하지 않는다.

지피티 결정문:

> P07 = performance candidate (QQQ50/H001 30/IEF 20)
> P08 = structural diversification candidate (SPY40/QQQ30/H001 20/IEF 10)
> 둘 다 I003 robustness 동시 검증. final freeze X. 새 P09 찾기 X.
> I003 은 P07/P08 plateau 확인 목적, coarse structural robustness 만.

## 고정 후보

- P07: QQQ 50 / SPY 0 / H001 30 / IEF 20.
- P08: SPY 40 / QQQ 30 / H001 20 / IEF 10.

## 계산 방식

- I001.6 daily NAV 방식과 동일하게 계산한다.
- ETF close는 USDKRW로 KRW 환산한다.
- H001은 기존 `reports/experiments/H001_kr_short_rate_sleeve/equity_curve.csv`
  의 `net_value`를 그대로 사용한다.
- 공통 calendar는 ETF와 H001 source date의 union calendar로 두고, 휴일 차이는
  component NAV forward-fill로 처리한다.
- 분기 첫 관측일에 target weight로 rebalance하고, 분기 내에는 daily
  mark-to-market으로 weight drift를 허용한다.
- metric은 daily return 기준 Sharpe, Sortino, Volatility, CAGR, daily MDD,
  calendar-year 양의 수익 연도이다.

## 사전 등록 grid

### I003-A P07-style IEF grid

H001 30 / SPY 0 고정:

- QQQ70 / H001 30 / IEF 0
- QQQ60 / H001 30 / IEF 10
- QQQ50 / H001 30 / IEF 20 (= P07)
- QQQ40 / H001 30 / IEF 30

### I003-B P08-style IEF grid

H001 20 / SPY:QQQ ≈ 4:3:

- SPY 46 / QQQ 34 / H001 20 / IEF 0
- SPY 40 / QQQ 30 / H001 20 / IEF 10 (= P08)
- SPY 34 / QQQ 26 / H001 20 / IEF 20
- SPY 29 / QQQ 21 / H001 20 / IEF 30

### I003-C SPY inclusion test

Total US 50 / H001 30 / IEF 20 고정:

- QQQ 50 / SPY 0 / H001 30 / IEF 20 (= P07)
- QQQ 40 / SPY 10 / H001 30 / IEF 20
- QQQ 35 / SPY 15 / H001 30 / IEF 20
- QQQ 30 / SPY 20 / H001 30 / IEF 20
- QQQ 25 / SPY 25 / H001 30 / IEF 20

## Stress tests

- 2020 COVID stress: 2020-02부터 2020-04 peak-to-trough daily MDD, recovery
  date, QQQ/SPY/H001/IEF component contribution.
- 2022 rate-shock: 2022 calendar-year KRW return, QQQ와 IEF 동시 손실 영향,
  P07 vs P08의 IEF 20% vs 10% 차이.
- 2021-2022 drawdown: 2021 peak부터 2022 또는 2023 trough까지 daily MDD 시기와
  길이.
- Subperiod split: 2010-2017, 2018-2026 Sharpe/CAGR/MDD.
- US long-history core stress: 가능할 때만 QQQ/SPY/IEF local history로
  2000-2002 dot-com stress를 계산한다. H001은 2010 이전 재현하지 않는다.
  local data가 부족하면 network 없이 skip한다.
- Contribution attribution: P07/P08에 대해 QQQ, SPY, H001, IEF return
  contribution, rebalance effect, USDKRW FX contribution.

## 사전 등록 verdict rules

- P07 wins (daily Sharpe + 2022 stress + long-history): P07 promote.
- P07 loses 2022 OR long-history: P08 또는 P08-like prefer.
- 둘 다 가까움: structural robustness + explainability 우선.
- Grid의 새 weights는 절대 final 승격하지 않는다.

## 산출물

`reports/experiments/I003_p07_p08_robustness/` 아래에 생성한다.

- `grid_a_p07_style.csv`
- `grid_b_p08_style.csv`
- `grid_c_spy_inclusion.csv`
- `covid_stress_2020.csv`
- `rate_shock_stress_2022.csv`
- `subperiod_split.csv`
- `us_long_history_stress.csv`
- `contribution_attribution_p07.csv`
- `contribution_attribution_p08.csv`
- `daily_metrics_all_candidates.csv`
- `report.md`

## report.md 필수 섹션

- Grid plateau 확인 (P07/P08 주변이 안정적인가?)
- 2020 stress 결과 (P07 vs P08)
- 2022 stress 결과 (P07 vs P08, IEF 효과)
- Long-history stress (US core만, P07-like의 dot-com 취약성)
- Subperiod 결과
- Contribution attribution
- 최종 verdict (P07 promote / P08 prefer / 둘 다 후보 유지)
- I002 진행 권고 또는 I004 final candidate registration 직접

## 엄격 제약

- D013, H001 strategy 미수정.
- `engine.py` 미수정.
- 기존 D-H, P, I000-I001.6 모든 결과 byte-identical.
- 새 audit script만 추가한다.
- 외부 network 금지.
- Weight optimization 금지. Coarse grid와 사전 등록 후보만 사용한다.
- Grid의 새 best 후보 final 승격 금지.
