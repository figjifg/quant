# D008 — Out-of-time subperiod split (era-specific vs robust alpha)

## Status
planned

## What this ticket is

D006 (window plateau) + D007 (threshold MARGINAL) 가 D001 의 parameter
robustness 검증. 그러나 **temporal robustness** (시간상 generalize 하는지)
미검증. 가장 중요한 미해결 질문:

> D001 의 alpha 가 진짜 architecture 에서 나오는가, 아니면 2015-2026
> 의 특정 era 에 운 좋게 align 한 것인가?

D008 = **fixed-parameter D001 strategy 를 multiple temporal splits 에
적용, 각 subperiod 의 metrics 비교**. 같은 strategy 가 IS / OOS 에서
유사 성과 → architecture real; OOS 만 무너짐 → era-specific.

## What we already know

D001 effective trading: **2015-2026** (60mo warmup from 2010-01 means
no signals before 2015-01).

Existing D001 subperiod (per pre-registered C-family logic):
- 2010-2017: 0% (zero trades due warmup)
- 2018-2026: +129.07%

→ 위 2분할은 너무 거칠음. 실제로 trading 한 11년 (2015-2026) 안에서
의 안정성이 핵심 질문.

## Single change

기존 D001 strategy 그대로. 새 strategy 코드 거의 없음. **분석 단위**가
변경:

| Subperiod scheme | 의도 |
|---|---|
| **Scheme A**: 2015-2020 vs 2021-2026 | COVID 전/후 split (5-6년씩) |
| **Scheme B**: 2015-2019 vs 2020-2026 | Pre-COVID 5년 vs COVID-after 7년 |
| **Scheme C**: 2015-2021 vs 2022-2026 | 5-6년 train / 4-5년 OOS |
| **Per-year**: 2015, 2016, ..., 2026 | 연도별 Sharpe 안정성 |
| **Rolling 3yr**: 2015-2017, 2016-2018, ... | rolling window Sharpe 안정성 |

3 splits + per-year + rolling 가 다른 각도에서 같은 질문.

## Robustness verdict logic (사전 등록)

**Per Subperiod Sharpe**:

| OOS Sharpe (vs IS Sharpe ~0.5) | Verdict | 해석 |
|---:|---|---|
| ≥ 0.40 | **STRONG GENERALIZATION** | Architecture 진짜 alpha |
| 0.30 ~ 0.40 | ACCEPTABLE | Real alpha with some era effect |
| 0.20 ~ 0.30 | MARGINAL | Mixed — partial generalization |
| 0.10 ~ 0.20 | WEAK | Era-specific 우려 |
| < 0.10 또는 negative | **OOS COLLAPSE** | Era-specific (overfit on time) |

**Combined**: 3 scheme 중 **2 이상이 ACCEPTABLE+** → 안정 alpha.
3 scheme 모두 MARGINAL 또는 worse → era-specific 의심.

**Per-year stability**:
- Sharpe std across years 가 작음 (variance < mean) → 안정
- Specific year 가 dominant (예: 2020 만 +50%, 나머지 다 0%) → era-specific
- Positive years 의 distribution

## Pre-registered hypothesis

### H1: D001 재현 (sanity)
- D008 의 full-period D001 metrics = D001 보고된 값 정확 재현
- Sharpe 0.4842, Net +129.07%

### H7 (D008 OOS 핵심): Temporal robustness
- Scheme A IS (2015-2020) Sharpe vs OOS (2021-2026) Sharpe
- Scheme B IS (2015-2019) Sharpe vs OOS (2020-2026) Sharpe
- Scheme C IS (2015-2021) Sharpe vs OOS (2022-2026) Sharpe
- 적어도 2 scheme 의 OOS Sharpe ≥ 0.30 (ACCEPTABLE+)

### H8 (per-year stability)
- 각 연도의 trade count, return, Sharpe
- Sharpe std 가 small (mean Sharpe 보다 낮음)
- 최소 절반 이상의 연도가 net positive

### H9 (descriptive)
- Trade 시점 분포 — clustering 있는지
- Spike years (2020 COVID rebound, 2025/26 rally) 의 contribution
- 만약 D001 의 alpha 가 2-3 spike year 만에서 나오면 era-specific 강함

## What this resolves

**STRONG / ACCEPTABLE generalization**:
- D001 architecture 진짜 alpha capture
- 시간 차원에서도 robust
- D-family conclusion (D001 = champion) FULLY validated
- Layer 2 진입 with high confidence

**MARGINAL / WEAK generalization**:
- D001 alpha 가 부분적으로 era-specific
- Layer 2 (stock signal) 가 raw signal source 로 더 중요
- D001 = macro filter (correct OFF 잘 함), Layer 2 = positive alpha

**OOS COLLAPSE**:
- D001 의 high Sharpe 는 era-specific 우연
- Strategy 재고
- Conservative interpretation: D001 도 alpha 없음, just buy-and-hold equivalent

## Implementation task

### Scope

새 backtest 없음. 기존 D001 outputs (trades.csv, equity_curve.csv,
quarterly_year_breakdown.csv) 를 analyze.

또한 D001 strategy 를 restricted period 에서 직접 다시 run 해서
isolated subperiod Sharpe 정확히 계산 — 단순 트레이드 slicing 보다 정확
(starting capital, compounding 정확 반영).

Touch (additive):
- `src/strategies/d008_subperiod_analysis.py` (NEW) — D001 logic
  with parameterized backtest start/end; runs 6 instances
  (full + Scheme A IS, A OOS, B IS, B OOS, C IS, C OOS)
- `src/run_experiment.py` — D008 dispatch
- `configs/backtests/d008.yaml` (NEW) — subperiod schemes
- `tests/test_d008_strategy.py` (NEW)
- `src/reporting/subperiod_analyzer.py` (NEW or extension) — per-year
  + rolling 3yr Sharpe from existing equity curve

**Do NOT touch**:
- `src/backtest/engine.py`
- 기존 strategy modules (D001-D007)
- D001-D007 byte-identical reproducibility
- `research_input_data/`

### Configuration

`configs/backtests/d008.yaml`:

```yaml
experiment_id: D008
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

# Subperiod schemes (z-score window 는 항상 60mo 사용하되, 트레이딩만
# subperiod 안에서 제한; 즉 IS 의 시작 시점에 이미 60mo z-score 있어야 함)
subperiods:
  - name: full
    start: 2010-01-04
    end:   2026-05-04
  - name: scheme_a_is   # 2015-2020 (COVID 직전까지)
    start: 2015-01-01
    end:   2020-12-31
  - name: scheme_a_oos  # 2021-2026 (COVID 후)
    start: 2021-01-01
    end:   2026-05-04
  - name: scheme_b_is   # 2015-2019 pre-COVID
    start: 2015-01-01
    end:   2019-12-31
  - name: scheme_b_oos  # 2020-2026 COVID+after
    start: 2020-01-01
    end:   2026-05-04
  - name: scheme_c_is   # 2015-2021
    start: 2015-01-01
    end:   2021-12-31
  - name: scheme_c_oos  # 2022-2026
    start: 2022-01-01
    end:   2026-05-04

variants:
  - factor_macro_gate_mcap

per_year_analysis: true
rolling_3yr_sharpe: true

output_dir: reports/experiments/D008_oos_subperiod_split
```

### Z-score timing 주의

**중요**: 모든 subperiod 의 trading 시작 시점에서, 60mo rolling z-score
가 valid 해야 함 (즉 2015-01 시작 = 2010-01 ~ 2014-12 의 historical
data 필요). Subperiod 가 trading 만 제한; z-score 계산은 항상 historical
look-back 유지.

이건 look-ahead 가 아님 — t 시점의 z-score 는 [t-60mo, t] 만 사용.

### Completion criteria

- pytest fully green (currently 269)
- engine.py untouched
- D001-D007 byte-identical reproducibility
- D008 full-period results 가 D001 정확 재현
- Final message reports:
  - **Subperiod table**: subperiod | start | end | trades | net | Sharpe | annualized | MaxDD | pos_years
  - **IS vs OOS comparison (3 schemes)**: IS Sharpe / OOS Sharpe, IS net / OOS net, ratio
  - **Per-year breakdown**: year | trades | net | Sharpe | MaxDD
  - **Rolling 3yr Sharpe** time series (단순 line)
  - **Verdict per pre-registered**: STRONG / ACCEPTABLE / MARGINAL / WEAK / COLLAPSE
  - Spike year contribution (2020, 2025 if exist) 의 share of total return

If ambiguity, write D008_codex_questions.md.

### Out of scope

- ❌ 새 parameter tuning
- ❌ Walk-forward parameter selection (이건 D009 candidate)
- ❌ Bootstrap (D009 candidate)
- ❌ 변수 / block 변경

## Result summary
DO NOT FILL until backtest complete.

## Claude review
DO NOT FILL until result files are read.
