# D007 — Composite threshold neighborhood grid (D001 robustness, second axis)

## Status
planned

## What this ticket is

D006 가 window dimension 의 plateau (48-84mo Sharpe 0.47-0.48) 를
입증. D001 의 robust 가 진짜인지 확인하려면 **threshold dimension**
도 plateau 인지 확인 필요. 두 축 모두 plateau 면 D001 architecture
strong evidence.

D007 = **threshold grid** {-0.2, -0.1, 0, +0.1, +0.2}. 다른 D001
parameter 모두 identical.

## Single change

**Threshold neighborhood grid**:

| Threshold | 의미 | 예상 ON share |
|---:|---|---:|
| -0.2 | ~mean 이상 (덜 selective) | ~50% |
| -0.1 | ~half-mean 이상 | ~47% |
| **0 (D001)** | ~ above-average favorability | **22.95%** |
| +0.1 | 위쪽 selective | ~35% |
| +0.2 | 강한 favorability 만 (~+0.8σ) | ~25% |

(% 예상값은 D001 composite dist mean -0.22, std 0.53 기준)

다른 모든 D001 parameter (8 vars, 6 blocks, sign, **60mo window**,
selection, costs, rebalance) **identical**.

## Robustness verdict logic (사전 등록)

| 결과 | Verdict | 해석 |
|---|---|---|
| ≥ 4 of 5 Sharpe ≥ 0.40 | **STRONG PLATEAU** — threshold 도 robust | D001 가 두 축 모두 plateau → 진짜 robust |
| 3 of 5 ≥ 0.40 | PLATEAU acceptable | D001 의 0 가 sweet spot, 그러나 robust |
| 2 of 5 ≥ 0.40 | MARGINAL | threshold 에 narrow | 
| 1 of 5 (only 0) ≥ 0.40 | **CLIFF — D001 threshold-fragile** | 비록 window robust 라도 threshold fragile = D001 overfit on this axis |
| 0 of 5 | reproducibility 문제 | tech 문제 |

Combined with D006:
- D006 STRONG PLATEAU + D007 STRONG PLATEAU → D001 진짜 architecture
- D006 STRONG + D007 CLIFF → D001 partial robust, threshold 조심
- D006 STRONG + D007 PLATEAU → D001 robust 확인

## Pre-registered hypothesis

### H1: threshold 0 (D001) 재현
- D007-0 Sharpe = 0.4842 (D001 정확 재현)
- 만약 다르면 implementation bug

### H7 (D007 robustness): Threshold cliff vs plateau
- Plateau: ≥ 3 of 5 with Sharpe ≥ 0.40
- Cliff: only 0 ≥ 0.40

### H8 (descriptive):
- Threshold 별 ON share, trade count, max DD
- Threshold 와 Sharpe slope
- Threshold -0.1, -0.2 의 추가 OFF→ON quarters 가 hit rate 어떤지
- Threshold +0.1, +0.2 의 OFF 만든 quarters 의 D001 forward return

## Implementation task

D006 와 거의 동일 pattern. Strategy 가 이미 parameterized.

Touch (additive):
- `src/strategies/d007_threshold_grid.py` (NEW) — D001 logic with
  parameterized threshold; 5 variants
- `src/run_experiment.py` — D007 dispatch
- `configs/backtests/d007.yaml` (NEW)
- `tests/test_d007_strategy.py` (NEW)

**Reuse**:
- factor_aggregation_composite 의 threshold param

**Do NOT touch**:
- engine.py
- 기존 strategy modules (a001-a004, b001-b011, c003-c020, d001-d006)
- D001-D006 byte-identical reproducibility
- research_input_data/

### Configuration

`configs/backtests/d007.yaml`:

```yaml
experiment_id: D007
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
  z_score_window_months: 60      # D001 fixed
  on_threshold_grid: [-0.2, -0.1, 0.0, 0.1, 0.2]
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

variants_per_threshold:
  - factor_macro_gate_mcap

fixed_baselines:
  - kospi_buy_and_hold
  - cash

output_dir: reports/experiments/D007_threshold_neighborhood_grid
```

### Completion criteria

- pytest fully green (currently 265)
- engine.py untouched
- D001-D006 byte-identical reproducibility
- **D007-0 Sharpe = 0.4842** (D001 reproduce)
- Each of 5 thresholds: full metrics + subperiod
- Final message reports:
  - **Grid table**: threshold | net | cost-0 | Sharpe | Max DD | positive years | annualized | ON share | trade count | 2010-2017 net | 2018-2026 net
  - Verdict per pre-registered
  - 0 threshold reproduce D001
  - Sharpe sensitivity slopes (0 → -0.1 delta, 0 → +0.1 delta)
  - 각 threshold composite distribution (D001 reproducibility check)
  - Combined with D006 verdict (2-axis robustness summary)

If ambiguity, write D007_codex_questions.md.

### Out of scope

- ❌ Window grid (D006 done)
- ❌ 변수 변경
- ❌ Block 변경
- ❌ Sizing
- ❌ Selection / costs / rebalance 변경

## Result summary
DO NOT FILL until backtest complete.

## Claude review
DO NOT FILL until result files are read.
