# I003.5 — Static Allocation Frontier

## 상태

계획 및 실행 요청됨.

## 지피티 결정문

> Do not freeze P08, do not promote P07, do not promote IEF30.
> I003 = monotonic frontier finding, not plateau.
> 2022 rule too binary -> stress penalty.
> Static frontier 정리 먼저, I002 macro gate 미루기.

## 목적

I003.5는 P07/P08 주변의 static allocation frontier를 사전 등록 grid로
정리한다. 목표는 highest Sharpe 후보를 자동 승격하는 것이 아니라, Sharpe,
CAGR, MDD, 2022 stress, long-history stress, 설명 가능성을 함께 본
multi-metric balance로 I004 등록 후보를 좁히는 것이다.

Grid의 새 best 후보는 final 후보로 승격하지 않는다. P07, P08,
P07-style IEF30, P08-style IEF30은 비교 anchor로만 사용한다.

## 계산 방식

- I001.6/I003 daily NAV 방식과 동일하게 계산한다.
- ETF close는 USDKRW로 KRW 환산한다.
- H001은 기존 `reports/experiments/H001_kr_short_rate_sleeve/equity_curve.csv`
  의 `net_value`를 그대로 사용한다.
- 공통 calendar는 ETF와 H001 source date의 union calendar로 두고, 휴일 차이는
  component NAV forward-fill로 처리한다.
- 기본 frontier는 quarterly rebalance로 계산한다.
- Rebalance frequency robustness는 monthly, quarterly, semiannual, annual을
  별도 계산한다.
- Weight optimization은 하지 않는다. 아래 사전 등록 grid만 계산한다.

## 사전 등록 grid

### I003.5-A P07-style IEF frontier

H001 30 / SPY 0 고정:

- QQQ70 / H001 30 / IEF 0
- QQQ60 / H001 30 / IEF 10
- QQQ50 / H001 30 / IEF 20 (= P07)
- QQQ40 / H001 30 / IEF 30
- QQQ30 / H001 30 / IEF 40
- QQQ20 / H001 30 / IEF 50

### I003.5-B P08-style IEF frontier

H001 20 / SPY:QQQ ≈ 4:3:

- SPY46 / QQQ34 / H001 20 / IEF 0
- SPY40 / QQQ30 / H001 20 / IEF 10 (= P08)
- SPY34 / QQQ26 / H001 20 / IEF 20
- SPY29 / QQQ21 / H001 20 / IEF 30
- SPY23 / QQQ17 / H001 20 / IEF 40

## Rebalance frequency robustness

대상 4 후보:

- P07
- P08
- P07-style IEF30
- P08-style IEF30

Frequency:

- monthly
- quarterly
- semiannual
- annual

각 조합에 대해 daily Sharpe, MDD, CAGR을 산출한다.

## Stress tests

- 2020 COVID: 모든 frontier 후보의 daily MDD와 recovery date.
- 2022 full-year: 모든 frontier 후보의 KRW return과 component contribution.
- 2021-2022 drawdown: 4 주요 후보의 peak-to-trough, MDD, length.
- 2025 spike exclusion: 2025 calendar year 제외 누적 Sharpe/MDD/CAGR.
- Subperiod: 2010-2017 vs 2018-2026, 모든 frontier 후보.

## Long-history stress

US core만 계산한다. H001은 2010 이전 재현하지 않고 KR cash flat proxy로 둔다.

- yfinance 추가 download 시도는 승인됨.
- Target tickers: QQQ, SPY, IEF, TLT, GLD.
- 다운로드 위치: `research_input_data/inputs/global_etf/yf_*_long.csv`.
- Test portfolios:
  - QQQ 100
  - SPY 100
  - QQQ/SPY 50/50
  - QQQ50/IEF50
  - QQQ40/SPY10/IEF50
  - SPY40/QQQ30/IEF30 (P08 proxy without H001)
- 핵심 시기: 2000-2002 dot-com, 2008 GFC.
- Metrics: Sharpe, MDD, CAGR. USD 기준 허용, KRW 환산 가능한 시기는 별도 가능.
- Network 실패 또는 yfinance 미설치 시 skip하고 사유를 명시한다.

## Contribution attribution

대상:

- P07
- P08
- P07-style IEF30
- P08-style IEF30

분해 항목:

- QQQ
- SPY
- H001
- IEF
- FX estimate
- rebalance effect

기간:

- 2010-2017
- 2018-2026

## 사전 등록 decision rule

- Highest Sharpe 자동 선택 금지.
- CAGR < 12% 후보는 defensive portfolio로 분류하고 global growth 후보로 보지 않는다.
- MDD > -25%는 warning으로 표시한다.
- Daily Sharpe >= 1.15 후보를 선호한다.
- 2022 stress에서 P07 vs P08 차이 >= 5pp이면 significant로 본다.
- Long-history에서 QQQ-heavy가 catastrophic이면 SPY 포함 후보를 선호한다.
- 비슷한 후보는 structurally robust하고 explainable한 후보를 우선한다.
- 2022 rule은 binary pass/fail이 아니라 stress penalty로 반영한다.
- Static frontier 정리 이후 I004 final candidate registration을 검토하고,
  macro gate(I002)는 뒤로 미룬다.

## 산출물

`reports/experiments/I003_5_static_allocation_frontier/` 아래에 생성한다.

- `frontier_a_p07_style.csv`
- `frontier_b_p08_style.csv`
- `rebalance_frequency.csv`
- `stress_2020_covid.csv`
- `stress_2022_rate_shock.csv`
- `stress_2021_2022_drawdown.csv`
- `spike_exclusion_2025.csv`
- `subperiod_split.csv`
- `long_history_us_core.csv`
- `contribution_attribution.csv`
- `daily_metrics_all_candidates.csv`
- `report.md`

## report.md 필수 섹션

- Frontier shape (단조 vs plateau)
- Rebalance frequency 효과 (P07의 rebalance loss artifact 여부)
- 2022 vs COVID stress trade-off
- Long-history 결과
- Multi-metric 최종 후보 선정
- Champion candidate 추천 및 근거
- I004 final candidate registration 진행 또는 I003.6 long-history 별도 진행

## 엄격 제약

- D013, H001 strategy 미수정.
- `engine.py` 미수정.
- 기존 D-H, P, I000-I003 모든 결과 byte-identical.
- 새 audit script와 새 long-history data만 추가한다.
- yfinance 다운로드는 승인됨. 실패 시 skip한다.
- Weight optimization 금지.
- Grid의 새 best 후보 final 승격 금지.
- Multi-metric balance는 Sharpe, CAGR, MDD, 2022, long-history,
  explainability로 판단한다.
