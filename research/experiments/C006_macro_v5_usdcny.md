# C006 — Macro v5 (USDCNY 추가)

## Status
planned

## What this ticket is

C001 v2 macro deepening roadmap의 v4 → v5 step. C005 가 첫 양의
cost-0 alpha (+3.67%) 달성. 이 trajectory 가 deepening 더 가치
있는지 한 step 더 확인.

C006 = 단일 변수 변경. 매크로 v4 → v5. **USDCNY** (중국 환율) 추가.

## Single change from C005

| 변수 | C005 (v4) | **C006 (v5)** |
|---|---|---|
| Macro variables | USDKRW + VIX + DXY + curve (4개) | **+ USDCNY (5개)** |
| Composite threshold | ≥ 2 of 4 favorable | **≥ 2 of 5 favorable** (same absolute count) |
| Rebalance | quarterly | quarterly (unchanged) |
| Selection | top-5 by 시가총액 | top-5 by 시가총액 (unchanged) |
| Universe / costs / period | unchanged | unchanged |

**한 변수 변경**. Layer 1 deepening 계속.

## New variable specification

### Signal 5 — USDCNY yoy momentum (China demand layer)

**Mechanism (사전 글로 commit)**:
> 한국 수출의 약 25% 가 중국 (반도체 중간재 + 부품 + 화학 원료).
> CNY 약세 (USDCNY 상승) = 중국의 import 능력 약화 + 한국 수출 단가
> 압박 → 한국 export demand 위축 → KOSPI 부정적. CNY 강세 (USDCNY
> 하락) = 중국 강건 + 수입 활발 → 한국 수출 호조 → KOSPI 긍정적.
>
> 기존 4 변수 (USDKRW currency flow, VIX risk, DXY USD broad, curve
> term premium) 와 **다른 dimension**: China-specific demand environment.
>
> Caveat: USDCNY 와 USDKRW 는 Asia FX 로 일부 상관관계 가능 (둘 다
> USD 강도 반영). 그러나 USDCNY 는 China policy 와 무역 환경의 더
> 직접적 신호. C006 의 결과에서 이 둘의 incremental contribution
> 측정.

**Formula**:
```
USDCNY_yoy(T) = USDCNY(T) / USDCNY(T - 252 trading days) - 1
favorable_USDCNY(T) = USDCNY_yoy(T) <= 0  (CNY 강세 또는 안정)
```

데이터: 이미 보유 (`fred_dexchus.csv`).

### Composite (사전 등록)

```
regime_score(T) = count of favorable in {USDKRW, VIX, DXY, curve, USDCNY}
                  in {0, 1, 2, 3, 4, 5}

ON iff regime_score >= 2
OFF iff regime_score <= 1
```

Same absolute threshold "≥ 2". Variable 추가가 threshold 완화와
confound 되지 않도록.

## Hypothesis (사전 등록)

C005 의 H1-H6 그대로 + 새 H7:

- H1 누적 net > 0
- H2 vs KOSPI 누적 net ≥ -30pp
- H3 spike (2010, 2025, 2026) ≥ 2 positive
- H4 max DD < V2 max DD by ≥ 5pp
- H5 ≥ 8 of 16 positive years
- H6 net / cost-0 ≥ 0.7

**새 H7 (C006 only) — USDCNY informativeness**:
- V1 v5 cumulative net ≥ V1 v4 (C005) cumulative + **5pp** → informative
- 0pp ~ +5pp → marginal
- < 0pp → noise

**보조 H8 (descriptive only — not for verdict)**:
USDCNY 와 USDKRW 의 yoy 시계열 상관관계 측정 (보고만, 사전 등록 verdict 영향 없음). Correlation > 0.7 면 두 변수 중복 dimension 가능성 진단.

## Verdict logic (사전 등록)

| 통과 | Verdict | 다음 step |
|---|---|---|
| 6/6 H1-H6 + H7 PASS | STRONG PROMOTE (v5) | C007 = macro v6 (Brent) or Layer 2 |
| 4-5/6 + H7 PASS | CONDITIONAL PROMOTE | dimension 진단 후 |
| 2-3/6 + H7 ≥ +5pp | INCONCLUSIVE + v5 helps | C007 = macro v6 |
| 2-3/6 + H7 < +5pp | INCONCLUSIVE + v5 marginal | **deepening 한계 신호** — C007 = Layer 3 (selection) 검토 정당 |
| 0-1/6 or H1 catastrophic | KILL | architecture 재고 |

사전 commit. 결과 보고 변경 금지.

## Reportable metrics

C005 와 동일 + v4 vs v5 comparison + USDCNY-USDKRW 상관관계:
1. Cumulative net + cost-0 (16yr): V1 v5 + V1 v4 (from C005) + V2 + V3
2. Per-year breakdown (4 variants × 16 years)
3. (V1 v5 − V1 v4) per-year delta
4. **Regime ON share** (vs v4 64%)
5. **USDCNY favorable quarters** (sample size 측정)
6. **USDCNY-USDKRW 상관관계** (H8 descriptive)
7. Max DD, Sharpe, hit rate
8. Cost paid total + cost-eaten %
9. Year-wise positive count

## Implementation task (Codex)

### Scope discipline

Touch (additive):
- `src/features/macro_regime.py` — ADD `usdcny_yoy` signal + 5-var
  composite support (preserve 3/4-var for backward compat)
- `src/strategies/c006_quarterly_macro_v5.py` (NEW) — clone of c005
  with config pointing to 5 signals
- `src/run_experiment.py` — `experiment_id == "C006"` dispatch
- `configs/backtests/c006.yaml` (NEW)
- `tests/test_macro_regime.py` — ADD USDCNY signal test (formula
  correctness, no look-ahead)
- `tests/test_c006_strategy.py` (NEW) — sanity

**Do NOT touch**:
- `src/backtest/engine.py`
- 기존 strategy modules (a001-a004, b001-b011, c003-c005)
- 기존 features 모듈 (relative_flow, flow_ratios, regime,
  kospi_proxy)
- 기존 macro_factors loader (이미 USDCNY = dexchus_usdcny 로딩됨)
- `research_input_data/`

### Configuration

`configs/backtests/c006.yaml`:

```yaml
experiment_id: C006
# panels, market_breadth_csv, macro_data_dir, period, universe,
# costs, rebalance: 모두 C005 와 동일

regime:
  macro_signals:
    - usdkrw_yoy
    - vix_60d_vs_240d
    - dxy_yoy
    - us_2_10_curve
    - usdcny_yoy  # NEW
  composite_rule: count_favorable
  on_threshold: 2  # >= 2 of 5

selection:
  type: market_cap_top_n
  n: 5
variants:
  - macro_gate_mcap
  - kospi_buy_and_hold
  - cash
output_dir: reports/experiments/C006_macro_v5_usdcny
```

### Completion criteria

- pytest fully green (currently 182)
- 3 variants in metrics.json + cost-0 diagnostic
- engine.py untouched
- Final message:
  - V1 v5 cumulative net: __ percent
  - V1 v5 cost-0 cumulative: __ percent (vs C005 v4 cost-0 +3.67 percent)
  - C005 V1 v4 cumulative for reference: -8.48 percent
  - Delta v5 - v4 (net): __ pp (H7 check)
  - Delta v5 - v4 (cost-0): __ pp (보조 진단)
  - V1 max DD: __ percent
  - V1 positive years: __ of 16
  - V1 in 2010 / 2025 / 2026: __ / __ / __ (H3)
  - V1 annualized return: __ percent, Sharpe: __
  - Regime ON share: __ percent (v4 was 64 percent)
  - USDCNY favorable quarters: __ of __
  - **USDCNY-USDKRW 상관관계 (yoy 시계열)**: __ (H8 descriptive)
  - H1-H7 PASS/FAIL summary

If any ambiguity, write to `research/experiments/C006_codex_questions.md` and stop.

### Out of scope

- ❌ Selection 변경 (top-5 mcap, Layer 3)
- ❌ Threshold 변경 (≥ 2 absolute)
- ❌ Rebalance frequency 변경
- ❌ Other macro variables 동시 추가 (이번엔 USDCNY 만)
- ❌ Sector layer (Layer 2)
- ❌ Engine 변경

## Result summary
DO NOT FILL until backtest complete.

## Claude review
DO NOT FILL until result files are read.
