# C005 — Macro v4 (US yield curve 추가)

## Status
planned

## What this ticket is

C001 v2 의 macro layer **deepening roadmap 의 v3 → v4 step**.
C004 (quarterly + 3 macro) 가 H7 PASS (horizon 효과 확인) 했지만
누적 -22% 로 still fail. C004 review 의 진단: macro signal 자체가
아직 informative 하지만 **3 변수로 글로벌 매크로 읽기는 너무 sparse**.

C005 = 단일 변수 변경. 매크로 v3 → v4. **US 2-10y yield curve
spread** 추가.

## Single change from C004

| 변수 | C004 (v3) | **C005 (v4)** |
|---|---|---|
| Macro variables | USDKRW + VIX + DXY (3개) | **+ US 2-10y curve (4개)** |
| Composite threshold | ≥ 2 of 3 favorable | **≥ 2 of 4 favorable** (same absolute count) |
| Rebalance | quarterly | **quarterly** (unchanged) |
| Selection | top-5 by 시가총액 | **top-5 by 시가총액** (unchanged — Layer 3) |
| Universe | dynamic_top100 + 5억 + estimated False | unchanged |
| Costs | 1.5 / 20 / 5 bps | unchanged |
| Period | 2010-2026 with 2016 gap | unchanged |

**한 변수 변경** (Layer 1 deepening). Layer 3 (selection) 는 macro
layer 가 perfected 될 때까지 손 안 댐.

## New variable specification

### Signal 4 — US 2-10y yield curve spread

**Mechanism (사전 글로 commit)**:
> Yield curve inversion (단기 금리 > 장기 금리) 은 historically
> recession leading indicator (US 1980s, 2000, 2007, 2019, 2022-2023
> 모두 inversion 후 recession 발생). Recession 가 위험자산 (한국
> 포함) 매도 압력. Steepening curve (장기 금리 가 단기보다 가파르게
> 상승) 는 growth 기대 회복 → 위험자산 매수 환경. 기존 3 변수
> (USDKRW = currency flow, VIX = risk appetite, DXY = USD broad) 와
> **다른 dimension (term premium / recession risk)** 을 cover.

**Formula**:
```
curve_spread(T) = US 10y rate(T) - US 2y rate(T)
favorable_curve(T) = curve_spread(T) > 0  (즉 not inverted)
```

데이터: 이미 보유 (`fred_dgs2.csv`, `fred_dgs10.csv`).

### Composite (사전 등록)

```
regime_score(T) = count of favorable in {USDKRW, VIX, DXY, curve}
                  in {0, 1, 2, 3, 4}

ON iff regime_score >= 2
OFF iff regime_score <= 1
```

**Threshold = "≥ 2 of 4"** (same absolute count as C003/C004's "≥ 2 of
3"). Rationale: "최소 2개 favorable" minimum 약속 유지. 단순 majority
vote (≥ 3 of 4) 는 너무 strict (ON share 감소 위험). Loose (≥ 1 of 4)
는 다른 ticket 에서 threshold deepening 시 별도 검토.

→ Same absolute threshold 가 **threshold change 와 variable addition 의 confounding 회피**.

## Hypothesis (사전 등록)

C004 의 H1-H6 그대로 + 새 H7:

- H1 누적 net > 0
- H2 vs KOSPI 누적 net ≥ -30pp
- H3 spike year (2010, 2025, 2026) ≥ 2 positive
- H4 max DD < V2 max DD by ≥ 5pp (intent: V1 shallower; literal sign convention 주의)
- H5 ≥ 8 of 16 positive years
- H6 net / cost-0 ≥ 0.7

**새 H7 (C005 only) — Yield curve informativeness**:
V1 (v4 = quarterly + 4 vars) cumulative net 이 V1 (C004 v3 = quarterly + 3 vars) cumulative net 보다:
- **≥ +5pp 개선** → yield curve 가 informative addition
- **0pp ~ +5pp** → marginal contribution
- **< 0pp** → yield curve 가 noise 또는 wrong direction

## Verdict logic (사전 등록)

| 통과 | Verdict | 다음 step |
|---|---|---|
| 6/6 H1-H6 PASS + H7 ≥ +5pp | STRONG PROMOTE (v4 → carrier) | C006 = Layer 2 진입 또는 macro v5 |
| 4-5/6 + H7 ≥ +5pp | CONDITIONAL PROMOTE | dimension 진단 후 다음 |
| 2-3/6 + H7 ≥ +5pp | INCONCLUSIVE + v4 helps | C006 = macro v5 (다음 변수 추가) |
| 2-3/6 + H7 < +5pp | INCONCLUSIVE + v4 marginal | C006 = strategic 재고 (macro deepening 한계?) |
| 0-1/6 or H1 catastrophic | KILL | architecture 재고 |

이 verdict map 사전 commit. 결과 보고 변경 금지 (Mode C).

## Reportable metrics

C004 와 동일 + v3 vs v4 side-by-side:
1. Cumulative net (16yr): V1 v4 + V1 v3 (from C004) + V2 + V3
2. Per-year breakdown (4 variants × 16 years)
3. Cost-0 / cost paid / cost-eaten ratio
4. Max DD
5. Year-wise positive count
6. Sharpe / annualized return / vol
7. Regime ON share (quarterly basis)
8. **C004 v3 vs C005 v4 delta** per year + cumulative
9. **Per-quarter regime log**: 4 signal values + composite score + ON/OFF
10. **Yield curve specific stats**: spread time series stats, how many quarters inverted

## Implementation task (Codex)

### Scope discipline

Touch (additive):
- `src/features/macro_regime.py` — ADD `curve_spread` signal computation
  and update `composite_score` to support 4-variable variant (don't
  break 3-variable variant; both should be available)
- `src/strategies/c005_quarterly_macro_v4.py` (NEW) — clone of
  `c004_quarterly_macro_gate.py` with composite config pointing to
  4 signals
- `src/run_experiment.py` — `experiment_id == "C005"` dispatch
- `configs/backtests/c005.yaml` (NEW)
- `tests/test_macro_regime.py` — ADD yield curve test cases (no
  look-ahead, correct formula)
- `tests/test_c005_strategy.py` (NEW) — sanity

**Do NOT touch**:
- `src/backtest/engine.py` — verify `git diff src/backtest/engine.py`
  empty
- Existing strategy modules (a001-a004, b001-b011, c003, c004)
- `src/features/relative_flow.py`, `flow_ratios.py`, `regime.py`,
  `kospi_proxy.py`
- `src/data/macro_factors.py` — 이미 dgs2/dgs10 loaded
- `research_input_data/`

### Configuration

`configs/backtests/c005.yaml`:

```yaml
experiment_id: C005
# panels, market_breadth_csv, macro_data_dir, period, universe,
# costs, rebalance: 모두 C004 와 동일

regime:
  macro_signals:
    - usdkrw_yoy
    - vix_60d_vs_240d
    - dxy_yoy
    - us_2_10_curve  # NEW
  composite_rule: count_favorable
  on_threshold: 2  # >= 2 of 4 favorable

# selection, variants: 동일
output_dir: reports/experiments/C005_macro_v4_yield_curve
```

### Completion criteria

- pytest fully green (currently 177)
- 3 variants in metrics.json
- C005 V1 quarterly numbers + C004 V1 quarterly side-by-side comparison
- engine.py untouched
- Final message reports:
  - V1 v4 cumulative net: __ percent
  - C004 V1 v3 cumulative for reference: -22.01 percent
  - Delta (v4 - v3): __ pp (H7 check, threshold ≥ +5pp)
  - V1 max DD: __ percent
  - V1 positive years: __ of 16
  - V1 in 2010 / 2025 / 2026 net: __ / __ / __ (H3)
  - V1 annualized return: __ percent, Sharpe: __
  - Regime ON share: __ percent (v3 was 42.62%)
  - Yield curve favorable quarters: __ of 66 (vs inverted)
  - H1-H7 PASS/FAIL summary

If any ambiguity, write to `research/experiments/C005_codex_questions.md` and stop.

### Out of scope

- ❌ Selection 변경 (top-5 mcap 그대로, Layer 3)
- ❌ Composite threshold 변경 (≥ 2 absolute, not majority)
- ❌ 다른 macro variables 추가 (이번엔 yield curve 만)
- ❌ Sector layer (Layer 2)
- ❌ Engine 변경

이번 ticket 의 단 하나 변경 = yield curve 추가. 다른 모든 변수 frozen.

## Result summary
DO NOT FILL until backtest complete.

## Claude review
DO NOT FILL until result files are read.
