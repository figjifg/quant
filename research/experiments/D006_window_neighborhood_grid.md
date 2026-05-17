# D006 — Z-score window neighborhood grid (D001 robustness test)

## Status
planned

## What this ticket is

사용자 비판: "D001 의 모든 modification 이 fail 한 게 D001 의 robustness
증거가 아니라 fragile single-point optimum 의 sign 일 수 있다. 진짜
robust 검증 안 했다."

정확함. D-family 의 D002-D005 가 모두 single-point test → cliff vs
plateau 진단 안 됨. D006 = **D001 의 진짜 robustness landscape**.

## Single change

**Window neighborhood grid**:

| Window (months) | Warmup years | Effective backtest |
|---:|---:|---|
| 36 | 3 | 2013-2026 (13 years) |
| 48 | 4 | 2014-2026 (12 years) |
| **60 (D001)** | **5** | **2015-2026 (11 years)** |
| 72 | 6 | 2016-2026 (10 years) |
| 84 | 7 | 2017-2026 (9 years) |

다른 모든 D001 parameter (variables, blocks, sign, threshold, selection,
costs, rebalance) **identical**. Window 만 다섯 점.

## Robustness verdict logic (사전 등록)

**Question**: D001 의 60mo Sharpe 0.48 이 plateau 인가 cliff 인가?

| 결과 | Verdict | 해석 |
|---|---|---|
| ≥ 4 of 5 windows Sharpe ≥ 0.40 | **STRONG PLATEAU** — D001 robust | architecture 가 진짜 alpha, window 는 secondary |
| 3 of 5 windows ≥ 0.40 | PLATEAU (acceptable) | D001 의 60mo 가 sweet spot 이긴 하지만 robust |
| 2 of 5 windows ≥ 0.40 | MARGINAL | D001 partial robust; alpha 가 narrow |
| 1 of 5 (only 60mo) ≥ 0.40 | **CLIFF — D001 FRAGILE** | overfit 강한 증거; D-family champion 재평가 필요 |
| 0 of 5 (60mo includes!) ≥ 0.40 | reproducibility 검증 실패 | tech 문제 |

추가 진단:

- **Sharpe sensitivity slope**: 인접 window 차이 (예: 60→48 와 60→72 차이)
- **Net sensitivity slope**: 같은 진단을 net 으로
- **Subperiod 안정성**: 각 window 의 2010-2017 vs 2018-2026
  (36mo, 48mo 는 2010-2014 trade 가능 — D001 의 zero-trade artifact 해소)
- **Composite distribution**: 각 window 의 mean/std/% above 0
- **Regime ON share**: window 와 trade frequency 관계

## Pre-registered hypothesis

### H1: 60mo (D001) 재현
- D006-60mo Sharpe = 0.4842 (D001 정확 재현)
- 만약 다르면 implementation bug

### H7 (D006 robustness 핵심): Window cliff vs plateau
- Plateau: ≥ 3 of 5 with Sharpe ≥ 0.40 → D001 robust
- Cliff: only 60mo ≥ 0.40 → D001 fragile, overfit 증거

### H8 (subperiod stability):
- 36mo, 48mo 의 2010-2014 trade > 0 (warmup 짧음)
- 그 quarters 의 net 이 양수 여부 (D001 의 zero-trade artifact 가 사실
  은 OFF 였는지, warmup 가린 OFF 였는지 구별)

### H9 (descriptive):
- Window 와 ON share 관계 (긴 window = 안정적 z-score = 더 selective?)
- 각 window 의 max DD
- Composite distribution 변화

## What this resolves

**Plateau**:
- D001 robust → D-family conclusion valid → Layer 2 진입 정당
- D005 FAIL 의 해석 → "missing block 정말 noise"
- D002-D005 FAIL 들 = real null result

**Cliff**:
- D001 fragile → D-family champion 재평가
- D005 FAIL 의 해석 → "어떤 modification 도 cliff 라 fail 한 것뿐"
- 다음 step 재고: D-family 전체의 alpha 가 narrow 일 가능성

## Implementation task

### Scope discipline

Single change. D001 strategy 재사용, window param 만 변경.

Touch (additive):
- `src/strategies/d006_window_grid.py` (NEW) — D001 logic with
  parameterized window; runs 5 variants
- `src/run_experiment.py` — D006 dispatch (runs 5 windows in sequence)
- `configs/backtests/d006.yaml` (NEW) — grid 정의
- `tests/test_d006_strategy.py` (NEW) — 60mo 가 D001 정확 재현 확인

**Reuse**:
- `src/features/macro_regime.py` — z-score window 가 이미 parameter
  (D002 work 에서 추가됨), 변경 불필요
- `src/data/macro_factors.py` — D001 변수 그대로

**Do NOT touch**:
- `src/backtest/engine.py`
- 기존 strategy modules (a001-a004, b001-b011, c003-c020, d001-d005)
- D001-D005 reproducibility byte-identical
- `research_input_data/`

### Configuration

`configs/backtests/d006.yaml`:

```yaml
experiment_id: D006
panels:
  - research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv
  - research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv
  - research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv
  - research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv
panel_date_filters:
  research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv:
    end: 2017-12-31
market_breadth_csv: research_input_data/inputs/macro_features/krx_market_breadth_kospi_2010_2026.csv
macro_data_dir: research_input_data/inputs/macro_features/
period:
  start: 2010-01-04
  end:   2026-05-04
  exclude_calendar_years: [2016]
universe:
  require_dynamic_top100: true
  min_avg_traded_value_20d: 5_000_000_000
  exclude_estimated_flag_rows: true
strategy:
  lookback: 5
  max_positions: 5

regime:
  aggregation: factor_z_score
  on_threshold: 0.0
  # window_grid 가 핵심
  z_score_window_grid: [36, 48, 60, 72, 84]
  # D001 blocks 그대로
  blocks:
    - name: global_risk
      vars:
        - {name: vix_60d_vs_240d, sign: -1}
    - name: usd_fx
      vars:
        - {name: usdkrw_yoy, sign: -1}
        - {name: dxy_yoy, sign: -1}
    - name: us_rates
      vars:
        - {name: us_2_10_curve, sign: 1}
    - name: inflation
      vars:
        - {name: us_cpi_decel, sign: -1}
        - {name: us_ppi_decel, sign: -1}
    - name: commodity
      vars:
        - {name: brent_yoy, sign: -1}
    - name: korea
      vars:
        - {name: kr10y_yoy_change, sign: -1}

selection:
  type: market_cap_top_n
  n: 5

rebalance:
  frequency: quarterly
  anchor: last_trading_day

costs:
  commission_bps: 1.5
  tax_bps_sell:   20.0
  slippage_bps:   5.0

variants_per_window:
  - factor_macro_gate_mcap

# 추가 baseline (전 grid 와 비교용, 한 번만)
fixed_baselines:
  - kospi_buy_and_hold
  - cash

output_dir: reports/experiments/D006_window_neighborhood_grid
```

### Completion criteria

- pytest fully green (currently 260)
- engine.py untouched
- D001-D005 byte-identical reproducibility (SHA-256 across 50+ files)
- **D006-60mo Sharpe = 0.4842** (D001 정확 재현 검증)
- Each of 5 windows: full metrics.json + variant outputs
- Final message reports:
  - **Grid table**: window | net | cost-0 | Sharpe | Max DD | positive years | annualized | ON share | trade count | 2010-2017 net | 2018-2026 net
  - **Verdict per pre-registered**: cliff (1/5), marginal (2/5), plateau (3/5), strong plateau (≥4/5)
  - Sharpe sensitivity slopes
  - 각 window 의 composite distribution (mean, std, % above 0)
  - 36mo, 48mo 의 2010-2014 trade count + return (warmup-artifact 확인)

If ambiguity, write D006_codex_questions.md.

### Out of scope

- ❌ Threshold grid (D007 candidate)
- ❌ 변수 변경
- ❌ Block 변경
- ❌ Sizing
- ❌ Selection / costs / rebalance 변경

## Result summary
DO NOT FILL until backtest complete.

## Claude review
DO NOT FILL until result files are read.
