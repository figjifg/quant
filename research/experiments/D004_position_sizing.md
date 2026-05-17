# D004 — Position sizing on D001 (composite magnitude → exposure)

## Status
planned

## What this ticket is

D001 carrier 위 단일 architectural 변경: **binary ON/OFF → continuous
exposure based on composite magnitude**.

D001 의 한계:
- Composite = +0.1 이든 +2.0 이든 같은 100% exposure
- Composite 의 magnitude 정보를 활용 못함
- 약한 신호에도 full risk
- ChatGPT framework 권장: composite 의 strength 를 size 로 활용

D004 = D001 그대로 + position sizing layer.

## Single architectural change

| 차원 | D001 | **D004** |
|---|---|---|
| Regime gate | binary (ON if composite ≥ 0) | **continuous (sized by composite)** |
| Total exposure | 100% on ON quarters | **scaled by composite magnitude** |
| Per-stock weight | 20% (5 stocks equal) | **20% × exposure_scalar** |
| Variables / blocks / window | same (8 vars, 6 blocks, 60mo) | same |
| Selection / rebalance / costs | unchanged | unchanged |

**Single architectural change**: regime gating → sizing.

## Sizing function (사전 commit, 변경 금지)

```
exposure_scalar(composite) =
  0.0                       if composite ≤ 0
  composite / k             if 0 < composite ≤ k
  1.0                       if composite > k

where k = 1.0  (사전 등록, tuning 금지)
```

**왜 k=1.0?**:
- D001 composite distribution: mean -0.07, std 0.52
- +1σ ≈ +0.45, +2σ ≈ +0.97
- k=1.0 → ~+2σ 이상 에서 full exposure
- Conservative — 강한 macro favorability 에서만 full risk

**대안 검토 안 함 (단일변수 변경 discipline)**:
- Tiered (50/75/100) — discrete cliff, 임의 cutoff
- Sigmoid — 추가 parameter
- 다른 k 값 — D005+ 에서 sensitivity 검토 가능

## Per-stock weight implementation

5 stocks 선택 후 (D001 과 동일 selection logic):
```
weight_per_stock(T) = (1 / 5) × exposure_scalar(composite(T)) = 0.20 × exposure_scalar(T)
cash_weight(T) = 1.0 - 5 × weight_per_stock(T) = 1.0 - exposure_scalar(T)
```

예시:
- Composite +1.5 → exposure 1.0 → 각 stock 20%, cash 0% (D001 과 동일)
- Composite +0.6 → exposure 0.6 → 각 stock 12%, cash 40%
- Composite +0.3 → exposure 0.3 → 각 stock 6%, cash 70%
- Composite -0.1 → exposure 0 → all cash (D001 과 동일)

Long-only, cash filler, no leverage. CLAUDE.md positioning 규칙 준수.

## Why this should help (mechanism)

### D001 의 implicit assumption
모든 ON quarter 가 동일한 alpha 확률. 그러나 composite 가 +2σ 인
quarter 와 +0.1 인 quarter 가 같은 size 면 비효율.

### D004 의 logic
- 강한 신호 quarters → full exposure → 큰 winners 잡음
- 약한 신호 quarters → 작은 exposure → 작은 losses 만
- Composite magnitude 와 forward returns 의 정 상관 가정
  → risk-adjusted return 개선

### Critical assumption
**Composite magnitude 가 forward return magnitude 와 정 상관** 인가?
이게 사실이면 sizing 이 도움. 사실 아니면 (composite 가 just "ON/OFF
indicator") sizing 은 그냥 averaging — 보호는 좋아도 alpha 손실.

## Pre-registered hypothesis

### H1-H6 inherited
- H1: 누적 net > 0
- H2: KOSPI 대비 -30pp 이내
- H3: spike (2010, 2025, 2026) ≥ 2 positive
- H4: max DD < V2 by 5pp
- H5: ≥ 8/16 positive years
- H6: net / cost-0 ≥ 0.7

### H7 (D004 sizing 효과): 핵심 가설
- D004 Sharpe ≥ D001 (0.48) → sizing 이 risk-adjusted 개선
- 또는 D004 net ≥ D001 (+129.07%) → sizing 이 net 개선
- Max DD ≤ D001 (-23.67%) → sizing 이 protective
- **두 가지 다 충족 → STRONG**

### H8 (Composite magnitude predictive power)
- D004 ON 분기 평균 exposure: 너무 낮으면 (예: < 0.3) k=1.0 가 너무
  보수적
- D004 가 D001 trades 와 같은 quarters 에서 다른 (작은) returns 면
  composite magnitude predictive 함을 시사

### H9 (Descriptive — sizing 분포)
- Exposure scalar 분포: mean, std, % at 0%, % at 100%, % partial
- Per-year cumulative exposure (regime ON share × avg exposure)
- D001 vs D004 trade overlap, return diff per overlapping quarter

## Verdict logic (사전 등록)

| 결과 | Verdict | 다음 |
|---|---|---|
| Sharpe ≥ 0.48 AND Net ≥ +129% | **STRONG PROMOTE** | D-family 완성, Layer 2 진입 |
| Sharpe ≥ 0.48 AND Net < +129% | CONDITIONAL — risk improvement | D005 = k tuning 또는 alternate sizing |
| Sharpe < 0.48 AND Net ≥ +129% | unexpected — net 개선 but variance ↑ | 검토 |
| Sharpe < 0.48 AND Net < +129% | **KILL D004** — sizing 가설 fail | D005 = D001 그대로 + Layer 2 진입 |

## Reportable metrics

기존 + D004 specific:
1. Full + subperiod cumulative net + cost-0
2. (D004 - D001) per-year delta + cumulative delta
3. Max DD, positive years, Sharpe, annualized
4. **Exposure scalar 분포** (mean, std, %=0, %=1, % partial)
5. **Per-year average exposure on ON quarters**
6. **Per-quarter exposure scalar 와 forward return scatter** (H8)
7. Trade overlap with D001 (quarter-level, since same ON quarters
   but different sizes)
8. **Quarters where D004 had partial exposure: avg return 비교**
9. Composite 분포 (D001 reproducibility check, should be identical)
10. H1-H9 summary

## Implementation task

### Scope discipline

Touch (additive only):
- `src/features/macro_regime.py` — ADD exposure_scalar function
  (composite → scalar, k=1.0 hardcoded for D004; D001's regime_on
  preserved)
- `src/strategies/d004_position_sizing.py` (NEW) — D001 clone + sizing
- `src/run_experiment.py` — D004 dispatch
- `configs/backtests/d004.yaml` (NEW)
- `tests/test_d004_strategy.py` (NEW)

**Engine 변경**:
- `src/backtest/engine.py` 변경이 필요하면 **사용자에게 보고 후 결정**
  - 만약 engine 이 이미 per-stock weight 지원 → 변경 불필요
  - 만약 engine 이 equal-weight only assumes → 변경 필요할 가능성
- 만약 변경 필요 → Codex 가 `D004_codex_questions.md` 에 정확히 어떤
  modification 필요한지 작성하고 stop

**Do NOT touch**:
- 기존 strategy modules (a001-a004, b001-b011, c003-c020, d001, d002, d003)
- D001/D002/D003 reproducibility byte-identical 보존
- 기존 features 모듈 (macro_regime 의 기존 functions 보존, additive only)
- `research_input_data/`

### Cash handling

Cash position 의 daily return = 0 (risk-free rate 안 적용, 단순 cash).
KRW 보유 가정. Equity 가 마이너스여도 cash 부분이 보호.

### Configuration

`configs/backtests/d004.yaml`:

```yaml
experiment_id: D004
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
  z_score_window_months: 60
  on_threshold: 0.0
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

sizing:                          # NEW
  function: linear
  k: 1.0                         # composite ≥ k → 100%
  composite_floor: 0.0           # composite ≤ floor → 0%

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

variants:
  - factor_macro_sized_mcap
  - kospi_buy_and_hold
  - cash

output_dir: reports/experiments/D004_position_sizing
```

### Completion criteria

- pytest fully green (currently 250)
- 3 variants in metrics.json + cost-0 diagnostic
- D001/D002/D003 byte-identical reproducibility
- engine.py 변경 시: 사용자 보고 후만, 그리고 D001/D002/D003 모두
  reproduce
- Final message reports:
  - V1 D004 cumulative net + cost-0 (vs D001 +129.07 / +139.71)
  - Delta D004 - D001 net + cost-0
  - V1 max DD (D001 -23.67%), Sharpe (D001 0.48), annualized (D001 5.69%)
  - Positive years (D001 4)
  - **Exposure scalar 분포: mean, std, % at 0, % at 100, % partial**
  - **D004 ON quarters 의 평균 exposure**
  - **D001 ON quarters 와 D004 partial-exposure quarters 의 return 비교**
  - Subperiod 2010-2017, 2018-2026 net + cost-0
  - Trade count (quarters with non-zero exposure)
  - H1-H9 summary

If ambiguity, write D004_codex_questions.md.

### Out of scope

- ❌ k 값 변경 (D005+)
- ❌ 다른 sizing function (sigmoid, tiered)
- ❌ Block structure 변경 (D001 그대로)
- ❌ Z-score window 변경
- ❌ Threshold 변경
- ❌ Leverage / short
- ❌ Selection / rebalance / costs 변경

## Result summary
DO NOT FILL until backtest complete.

## Claude review
DO NOT FILL until result files are read.
