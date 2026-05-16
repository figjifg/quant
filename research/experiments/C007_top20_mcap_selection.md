# C007 — Selection 변경 (top-5 → top-20 mcap)

## Status
planned

## What this ticket is

C006 의 pre-registered fallback. C006 H7 SEVERE FAIL (-11pp) 로
macro deepening 한계 도달. C006 ticket commit:

> "2-3/6 + H7 < +5pp → deepening 한계 신호 → C007 = Layer 3
> (selection) 재고 정당"

C007 = 처음으로 **Layer 3 (selection) 변경**. Carrier 의 다른 모든 변수
frozen, selection 의 단일 parameter (N) 만 변경.

## Why now (사용자 의견 vs pre-registered fallback 의 honest tension)

사용자는 매크로 더 추가 (예: Brent) 가 자연스러운 다음 step 이라고
의견. 그 의견에 일리 있음:
- USDCNY 가 USDKRW 와 partial overlap (corr 0.50) — 사실 비슷한 dimension
- Brent oil 은 완전 다른 dimension (commodity, supply, inflation)
- USDCNY 의 fail 이 "macro deepening 전체 fail" 의미 아닐 수 있음

그러나 우리 Mode C discipline:
- C006 ticket 의 fallback 이 "Layer 3 재고" 로 사전 commit
- C001 v2 roadmap 의 deepening 종료 후 next layer 진입이 architecture
- USDCNY 결과 보고 "다른 macro 변수 시도" 는 cherry-pick risk (선택적 reinterpretation)

**우리 약속**: C007 = Layer 3 selection. 만약 결과 marginal 이면 **그
때 macro v6 (Brent) 시도 정당화 가능** (실패가 명확한 후의 horizontal
exploration, pre-commit 위반 아님).

## Single change from C005 v4 carrier

**Carrier base = C005 v4** (4 macro vars, quarterly, NOT C006 의 v5)

| 변수 | C005 v4 carrier | **C007 변경** |
|---|---|---|
| Macro variables | USDKRW + VIX + DXY + curve (4개) | unchanged |
| Composite threshold | ≥ 2 of 4 favorable | unchanged |
| Rebalance | quarterly | unchanged |
| **Selection** | **top-5 by 시가총액** | **top-20 by 시가총액** |
| Universe / costs / period | unchanged | unchanged |

**한 변수 변경**: selection N 만 5 → 20. 다른 모든 frozen.

## Why top-20 specifically (not top-10 or KOSPI200)

- **N=20 = 4x 분산** (5 → 20). 의미있는 분산 효과
- **N=10 은 너무 incremental** — 차이 확연히 안 보일 수 있음
- **KOSPI200 (extreme)** 은 다음 escalation 후보 — A1 (top-20) 결과 보고 결정
- Quant 관행에서 top-quintile (20%) 흔히 사용

## New hypothesis specific to C007

### H7 (NEW): Selection diversification 효과

V1 N=20 cumulative net ≥ V1 N=5 (C005 v4) cumulative + **5pp** →
diversification 가치 있음
- 0 ~ +5pp → marginal
- < 0pp → 분산이 alpha 도 함께 diluted

### H8 (보조 descriptive): 2018 disaster 의 변화

V1 N=20 의 2018 net total return.
- 2018 V1 N=5 = -44%
- 만약 N=20 의 2018 이 -20% 이내 → concentration risk 가 진짜 issue
- -30% 이상 여전 → 다른 issue (macro signal 의 2018 timing 자체 wrong)

## H1-H6 inherited from C005

- H1 누적 > 0
- H2 vs KOSPI -30pp 이내
- H3 spike 2/3+
- H4 max DD < V2 by 5pp+ (literal)
- H5 ≥ 8/16 positive
- H6 net / cost-0 ≥ 0.7

## Verdict logic (사전 등록)

| 통과 | Verdict | 다음 step |
|---|---|---|
| 6/6 H1-H6 + H7 PASS | STRONG PROMOTE (N=20 carrier) | C008 = 다음 layer (sector 또는 holding 연장) |
| 4-5/6 + H7 ≥ +5pp | CONDITIONAL PROMOTE | dimension 진단 후 다음 |
| 2-3/6 + H7 ≥ +5pp | INCONCLUSIVE + selection helps | C008 = A2 (KOSPI200 ETF) 또는 다른 selection |
| 2-3/6 + H7 < +5pp | INCONCLUSIVE + selection marginal | C008 = **macro v6 (Brent)** — 사용자 의견의 정당한 진입점 |
| 0-1/6 or catastrophic | KILL | architecture 재고 |

**중요 약속**: C007 결과 H7 < +5pp 면 → C008 = macro v6 (Brent).
사용자 의견의 disciplined entry. 결과 보고 변경 아닌, 사전 commit.

## Reportable metrics

C005 와 동일 + N=5 vs N=20 비교:
1. Cumulative net + cost-0 (16yr): V1 N=20 + V1 N=5 (from C005) + V2 + V3
2. Per-year breakdown (4 variants × 16 years)
3. **(V1 N=20 − V1 N=5) per-year delta** — 매 연도 selection 변경 효과
4. **2018 disaster 의 변화 (H8)** — concentration risk 진단
5. **2025 spike capture 의 변화** — broader basket 이 spike 도 dilute 하는지
6. Max DD, Sharpe, hit rate
7. Cost paid + cost-eaten %
8. Year-wise positive count
9. Average holding period (rebalance 시 turnover 측정)

## Implementation task (Codex)

### Scope discipline

Touch (additive):
- `src/strategies/c007_top20_mcap.py` (NEW) — clone of `c005_quarterly_macro_v4.py`
  with selection N=5 → 20
- `src/run_experiment.py` — `experiment_id == "C007"` dispatch
- `configs/backtests/c007.yaml` (NEW)
- `tests/test_c007_strategy.py` (NEW) — sanity that N=20 selection
  picks correct top-20 by mcap

**Do NOT touch**:
- `src/backtest/engine.py`
- 기존 strategy modules (a001-a004, b001-b011, c003-c006)
- `src/features/macro_regime.py` (macro signal 동일)
- `src/features/` 기타 모듈
- `src/data/macro_factors.py`
- `research_input_data/`

### Configuration

`configs/backtests/c007.yaml`:

```yaml
experiment_id: C007
# panels, market_breadth_csv, macro_data_dir, period, universe,
# costs, rebalance: 모두 C005 와 동일

regime:
  macro_signals:
    - usdkrw_yoy
    - vix_60d_vs_240d
    - dxy_yoy
    - us_2_10_curve  # 4-var, same as C005 v4 (NOT C006)
  composite_rule: count_favorable
  on_threshold: 2

selection:
  type: market_cap_top_n
  n: 20  # <-- CHANGED from 5

variants:
  - macro_gate_mcap
  - kospi_buy_and_hold
  - cash
output_dir: reports/experiments/C007_top20_mcap_selection
```

### Completion criteria

- pytest fully green (currently 184)
- 3 variants in metrics.json + cost-0 diagnostic
- engine.py untouched
- Final message:
  - V1 N=20 cumulative net: __ percent
  - V1 N=20 cost-0 cumulative: __ percent (vs C005 N=5 cost-0 +3.67 percent)
  - C005 V1 N=5 cumulative for reference: -8.48 percent
  - Delta N=20 - N=5 net: __ pp (H7 check, threshold >= +5pp)
  - Delta N=20 - N=5 cost-0: __ pp (supplementary)
  - 2018 V1 N=20 net: __ percent (vs C005 N=5 -44 percent) (H8)
  - 2025 V1 N=20 net: __ percent (vs C005 N=5 +57 percent)
  - V1 max DD: __ percent
  - V1 positive years: __ of 16
  - V1 annualized return: __ percent, Sharpe: __
  - Trade count quarterly: __ (cost burden 측정; N=20 means more positions per rebalance)
  - H1-H7 PASS/FAIL summary

If ambiguity, write to research/experiments/C007_codex_questions.md and stop.

### Out of scope

- ❌ Macro variables 변경 (C005 v4 그대로)
- ❌ Threshold 변경
- ❌ Rebalance frequency 변경
- ❌ Sector layer
- ❌ Engine 변경

## Result summary
DO NOT FILL until backtest complete.

## Claude review
DO NOT FILL until result files are read.
