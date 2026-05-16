# C004 — Quarterly macro-gated Korean equity strategy (C003 fallback)

## Status
planned

## What this ticket is

C003 의 pre-committed fallback. C003 가 INCONCLUSIVE (3/6 literal
PASS) 로 verdict 났고, ticket 에서 사전 commit:

> "INCONCLUSIVE → C004 = quarterly horizon 재검증 (pre-committed
> fallback)"

C004 는 **C003 의 strategy 와 정확히 동일, rebalance frequency 만
quarterly 로 변경**. 단일 변수 변경 (horizon) — "한 번에 한 변수만"
discipline 정통.

## Single change from C003

| 변수 | C003 | C004 |
|---|---|---|
| Rebalance | **monthly** (월 1회) | **quarterly** (분기 1회) |
| Macro signal | USDKRW yoy + VIX 60d/240d + DXY yoy | **동일** |
| Composite rule | majority vote (≥ 2 of 3 favorable) | **동일** |
| Selection (ON) | Top-5 by 시가총액 균등 | **동일** |
| OFF | cash | **동일** |
| Universe | dynamic_top100 + 5억 + 거래대금추정여부 False | **동일** |
| Costs | 1.5 / 20 / 5 bps | **동일** |
| Period | 2010-2026 with 2016 gap | **동일** |

**Anchor**: 매 분기 마지막 거래일 (3월 말, 6월 말, 9월 말, 12월 말).
다음 분기 첫 거래일 시가에 execution.

## Hypothesis (사전 등록 — C003 와 동일한 6 criteria)

C003 와 정확히 같은 5+1 criteria. Quarterly version 으로 적용.

- H1 누적 net > 0
- H2 vs KOSPI 누적 net ≥ -30pp
- H3 spike year (2010, 2025, 2026) ≥ 2 positive
- H4 max DD < V2 max DD by ≥ 5pp (intent: V1 shallower)
- H5 ≥ 8 of 16 positive years
- H6 net / cost-0 ≥ 0.7

**추가 H7 (C004 only) — Horizon comparison**:
V1 (quarterly) cumulative net 이 V1 (C003 monthly) cumulative net
보다 **≥ +10pp 개선** 이면 horizon 이 핵심 issue 였음 확인.
**< +10pp 개선** 이면 horizon 이 핵심 아님 → selection / threshold /
macro variables 검토 필요.

## Verdict logic (사전 등록)

| 통과 | Verdict | 다음 step |
|---|---|---|
| 6/6 H1-H6 PASS + H7 ≥ +10pp | STRONG PROMOTE (quarterly) | Layer 2 (sector) 또는 macro v2 |
| 4-5/6 PASS | CONDITIONAL PROMOTE | dimension 진단 후 다음 |
| 2-3/6 PASS + H7 < +10pp | **INCONCLUSIVE** + **horizon 문제 아님** | **C005 = macro v2 deepening** OR **selection 변경** |
| 2-3/6 PASS + H7 ≥ +10pp | INCONCLUSIVE + horizon 개선됨 | C005 = quarterly + macro v2 or selection refinement |
| 0-1/6 PASS or H1 catastrophic | KILL | architecture 재고 |

이 verdict map 도 사전 commit. 결과 보고 변경 금지 (Mode C).

## Reportable metrics

C003 와 동일 + C003 vs C004 side-by-side comparison:
1. Cumulative net (16yr): V1 quarterly + V1 monthly (from C003) + V2 + V3
2. Per-year breakdown (4 variants × 16 years)
3. Cost-0 / cost paid / cost-eaten ratio
4. Max DD
5. Year-wise positive count
6. Sharpe / annualized return / vol
7. Regime ON share (quarterly basis)
8. **Trade count quarterly vs monthly** (cost saving 검증)
9. **C003 monthly vs C004 quarterly delta** per year + cumulative

## Implementation task (Codex)

C003 의 직접 reuse:
- `src/features/macro_regime.py` — 기존 daily/monthly aggregation 에
  quarterly aggregation 옵션 추가
- `src/strategies/c004_quarterly_macro_gate.py` (NEW) — C003 의 거의 복사,
  rebalance frequency 만 다름
- `src/run_experiment.py` — C004 dispatch
- `configs/backtests/c004.yaml` (NEW)
- `tests/test_c004_strategy.py` (NEW)

**Do NOT touch**:
- engine.py
- 기존 macro_factors, equity_panel loaders
- 기존 strategy modules (a001-a004, b001-b011, c003)
- 기존 features 모듈 (relative_flow, flow_ratios, regime, kospi_proxy)

기존 167+6=173 tests 다 green 유지. 새 test ~3-5 추가.

### Configuration

`configs/backtests/c004.yaml` 은 C003 의 거의 그대로, `rebalance.frequency` 만 변경:

```yaml
experiment_id: C004
# ... (C003 와 동일)
rebalance:
  frequency: quarterly
  anchor: last_trading_day  # 3월말, 6월말, 9월말, 12월말
# ... (나머지 동일)
output_dir: reports/experiments/C004_quarterly_macro_gated_strategy
```

### Completion criteria

- pytest fully green
- 3 variants 보고 + C003 monthly 와 side-by-side
- engine.py untouched
- Final message:
  - V1 quarterly cumulative net: __ % (vs C003 monthly -54.17%)
  - C003 monthly vs C004 quarterly delta: __ pp (H7 check)
  - V1 max DD: __ %, V2 max DD: __ %
  - V1 positive years: __ of 16
  - H1-H7 individual PASS/FAIL
  - Regime ON share quarterly: __ %
  - Trade count quarterly vs monthly: __ vs __ (cost saving)

### Out of scope

- ❌ Selection 변경 (top-5 mcap 그대로)
- ❌ Composite threshold 변경 (≥ 2 of 3 그대로)
- ❌ Macro variables 추가 (3개 그대로)
- ❌ Sector / stock layer
- ❌ Engine 변경

이번 ticket 의 단 하나 변경 = horizon. 다른 모든 변수 frozen.

## Result summary
DO NOT FILL until backtest complete.

## Claude review
DO NOT FILL until result files are read.
