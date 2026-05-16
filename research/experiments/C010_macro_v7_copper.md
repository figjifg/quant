# C010 — Macro v7 (+ Copper) — industrial commodity dimension

## Status
planned

## What this ticket is

C008 의 deepening 후속. 사용자가 명시: "원자재랑 한국 채권 금리 쪽을
안 다뤘으니 그 두 개를 해보는게 좋겠네". Phase A 의 첫 ticket.

C010 = **C008 v6 carrier + Copper**. 6-var composite.

## Single change from C008 v6 carrier

| 변수 | C008 v6 carrier | **C010 v7** |
|---|---|---|
| Macro variables | USDKRW + VIX + DXY + curve + Brent (5개) | **+ Copper (6개)** |
| Composite threshold | ≥ 2 of 5 favorable | **≥ 2 of 6 favorable** (same absolute count) |
| Rebalance | quarterly | unchanged |
| Selection | top-5 mcap | unchanged |
| 기타 | unchanged | unchanged |

## New variable specification

### Signal 6 — Copper yoy momentum (industrial commodity)

**Mechanism (사전 글로 commit)**:
> Copper 는 "Dr. Copper" 로 알려진 글로벌 manufacturing demand 의
> leading indicator. Brent (energy) 와 다른 commodity 측면: industrial
> demand. 한국은 manufacturing/export 중심 경제 (반도체 + 자동차 +
> 화학) 로 copper 가격이 글로벌 산업 사이클의 직접 proxy. 중국은 세계
> 최대 copper 수입국이고 한국 export destination 의 #1 — China demand
> 가 copper 가격에 반영.
>
> 가설: Copper yoy ≤ 0 (가격 안정 또는 하락) = 글로벌 manufacturing
> cooling / supply 안정. 그러나 deflation 위험 가능. Copper yoy > 0
> (가격 상승) = manufacturing 활발 / commodity inflation. 한국 수출
> 호조 신호.

**Caveat**: Brent 와 다르게 copper 는 inverse 가설 가능. Industrial
upturn = copper 상승 = 한국 favorable. 그래서 **반대 부호 가설**:

```
copper_yoy(T) = Copper(T) / Copper(T - 12 months) - 1
favorable_copper(T) = copper_yoy(T) > 0  (가격 상승 = industrial demand 회복)
```

Brent 와 반대 부호 (Brent 는 하락이 favorable, copper 는 상승이 favorable).
두 commodity 가 서로 다른 메커니즘 capture.

### Composite (사전 등록)

```
regime_score(T) = count favorable in {USDKRW, VIX, DXY, curve, Brent, copper}
                  in {0..6}

ON iff regime_score >= 2
OFF iff regime_score <= 1
```

Same absolute threshold "≥ 2".

## Data status — Claude 가 사용자 승인 후 직접 다운로드

Copper data already downloaded:
- Path: `research_input_data/inputs/macro_features/fred_copper.csv`
- Source: FRED series `PCOPPUSDM` (Global price of Copper, USD/tonne)
- Frequency: **monthly** (other macro vars are daily)
- Coverage: 1992-01-01 ~ 2026-03-01 (195 monthly observations in 2010-2026 window)
- Schema: `observation_date, PCOPPUSDM`

**Monthly granularity caveat**: quarterly anchor 가 quarter-end 인데
copper 는 monthly. 가장 가까운 month-end 값 사용. 또는 quarter-end
바로 이전 또는 같은 달 값. Codex 가 명시.

## Hypothesis (사전 등록)

H1-H6 inherited from C008 카리어 +

### H7 (NEW): Copper informativeness
- V1 v7 cumulative net ≥ V1 v6 (C008) + **5pp** → copper informative
- 0 ~ +5pp → marginal
- < 0pp → noise

### H8 — Subperiod robustness (NEW for C010+, lesson from C009)
- V1 v7 sub-period (2010-2017) net cumulative ≥ 0
- V1 v7 sub-period (2018-2026) net cumulative ≥ 0
- 둘 다 양수 = robust strategy
- 한쪽만 양수 = period-specific
- 이건 hard threshold 가 아니라 descriptive. 결과 보고 평가.

### H9 — Copper-Brent correlation
Copper yoy 와 Brent yoy 의 상관관계 (descriptive). > 0.7 = 중복
dimension. < 0.3 = 진짜 독립.

## Verdict logic (사전 등록)

| 통과 | Verdict | 다음 step |
|---|---|---|
| H1 + H7 + 4-5/6 PASS + 두 subperiod ≥ 0 | **STRONG PROMOTE (v7) + robust** | C011 = + 한국 채권 (Phase A 계속) |
| H1 + H7 PASS + subperiod 한쪽만 ≥ 0 | CONDITIONAL PROMOTE | C011 = + 한국 채권 (계속 deepening) |
| H7 PASS but H1 FAIL | INCONCLUSIVE (Brent 보다 marginal alpha) | C011 진행 |
| H7 FAIL (< +5pp) | Copper 가 informative 아님 | C011 진행 (다음 dimension 시도) |
| H1 catastrophic | KILL | architecture 재고 |

**Note**: 사용자 명시 "지치기 전까지 계속". H7 FAIL 도 KILL 아니라 다음 variable 진행. Multi-experiment roadmap.

## Reportable metrics

C008 와 동일 + v6 vs v7 + 2010-2017 / 2018-2026 subperiod 별:
1. Cumulative net + cost-0 (16yr full)
2. Cumulative net + cost-0 (2010-2017 subperiod)
3. Cumulative net + cost-0 (2018-2026 subperiod)
4. Per-year breakdown (incl C008 v6 column)
5. (V1 v7 − V1 v6) per-year delta
6. Max DD, Sharpe (full + subperiods)
7. Copper favorable quarters
8. **Copper-Brent yoy correlation** (H9)
9. **Copper-USDKRW yoy correlation** (보조)
10. Regime ON share

## Implementation task (Codex)

### Scope discipline

Touch (additive):
- `src/data/macro_factors.py` — ADD copper series spec to FRED_SERIES
  (filename='fred_copper.csv', fred_series='PCOPPUSDM', frequency='monthly')
- `src/features/macro_regime.py` — ADD copper_yoy signal + 6-var
  composite. **Note inverse sign (favorable iff > 0)**. Preserve 3/4/5-var.
- `src/strategies/c010_quarterly_macro_v7.py` (NEW) — clone of c008 with
  config pointing to 6 signals
- `src/run_experiment.py` — `experiment_id == "C010"` dispatch
- `configs/backtests/c010.yaml` (NEW)
- `tests/test_macro_factors_loading.py` — ADD copper loading test
  (monthly schema handling)
- `tests/test_macro_regime.py` — ADD copper signal test (inverse
  favorability, monthly-to-quarterly alignment, no look-ahead)
- `tests/test_c010_strategy.py` (NEW) — sanity

**Subperiod reporting infrastructure** (NEW for C010+):
- Strategy module should output subperiod_breakdown.csv with V1
  cumulative for 2010-2017 vs 2018-2026 (use existing equity_curve)

**Do NOT touch**:
- `src/backtest/engine.py`
- 기존 strategy modules (a001-a004, b001-b011, c003-c008)
- 기존 features 모듈 (relative_flow, flow_ratios, regime, kospi_proxy)
- `research_input_data/` (copper csv 이미 있음)

### Monthly-to-quarterly alignment 가이드

Copper 는 monthly (다른 변수는 daily). Quarter-end signal_date T 에서:
- Copper(T) = T 시점 가장 가까운 직전 month-end (또는 같은 달) value
- Copper(T - 252 trading days) = ~1년 전 시점의 가장 가까운 month-end
- No look-ahead: T 이후 month 값 사용 금지

### Configuration

`configs/backtests/c010.yaml`:

```yaml
experiment_id: C010
# panels, market_breadth_csv, macro_data_dir, period, universe,
# costs, rebalance: 모두 C008 와 동일

regime:
  macro_signals:
    - usdkrw_yoy
    - vix_60d_vs_240d
    - dxy_yoy
    - us_2_10_curve
    - brent_yoy
    - copper_yoy  # NEW (inverse sign: favorable iff > 0)
  composite_rule: count_favorable
  on_threshold: 2  # >= 2 of 6

selection:
  type: market_cap_top_n
  n: 5

variants:
  - macro_gate_mcap
  - kospi_buy_and_hold
  - cash
output_dir: reports/experiments/C010_macro_v7_copper
```

### Completion criteria

- pytest fully green (currently 188)
- 3 variants in metrics.json + cost-0 diagnostic
- engine.py untouched
- Final message:
  - V1 v7 cumulative net: __ percent
  - V1 v7 cost-0 cumulative: __ percent (vs C008 v6 cost-0 +59.82 percent)
  - C008 V1 v6 cumulative reference: +36.98 percent
  - Delta v7 - v6 net: __ pp (H7, threshold >= +5pp)
  - Delta v7 - v6 cost-0: __ pp
  - **Subperiod 2010-2017 V1 v7 net: __ percent (H8)**
  - **Subperiod 2018-2026 V1 v7 net: __ percent (H8)**
  - V1 max DD: __ percent
  - V1 positive years: __ of 16
  - V1 in 2010 / 2025 / 2026: __ / __ / __ percent
  - V1 annualized return: __ percent, Sharpe: __
  - Regime ON share: __ percent (v6 was 80 percent)
  - Copper favorable quarters: __ of __
  - **Copper-Brent yoy correlation: __ (H9)**
  - Copper-USDKRW yoy correlation: __
  - H1-H7 + H8/H9 summary

If ambiguity (especially around monthly-quarterly alignment), write
to research/experiments/C010_codex_questions.md and stop.

### Out of scope

- ❌ 다른 매크로 변수 동시 추가 (이번엔 copper 만)
- ❌ Selection 변경
- ❌ Threshold 변경
- ❌ Rebalance frequency 변경
- ❌ Engine 변경

## Result summary
DO NOT FILL until backtest complete.

## Claude review
DO NOT FILL until result files are read.
