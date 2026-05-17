# D009 — ChatGPT holistic Layer 1 design (Path B: full carrier swap)

## Status
planned

## What this ticket is

D-family 의 incremental "add 1 variable" 접근이 saturation 에 도달.
User insight:
- Layer 1 의 한계는 layer 자체의 본질적 제약 → 너무 조급해 X
- 변수 1개씩 추가는 한계
- **Story-coherent 한 design 자체가 가치 있음**
- ChatGPT 의 holistic design 으로 alternative carrier test

D009 = **D001 의 incremental evolution 가 아닌 full carrier swap** —
ChatGPT 의 framework 를 그대로 구현. 만약 D001 와 "크게 나쁘지 않다면
(comparable Sharpe)" 그게 더 나은 carrier 일 수 있음 (story 가 깔끔하기에).

## What changes (architectural)

D001 (incremental) vs **D009 (holistic)**:

| Block | D001 | **D009** |
|---|---|---|
| B1 Risk | VIX | **VIX + BAA10Y credit spread** |
| B2 USD/FX | USDKRW, DXY | USDKRW, DXY (same) |
| B3 Rates | US 2-10y curve | **US 10y real yield + US 2-10y curve** |
| B4 Inflation | US CPI decel, US PPI decel | **Brent + 10y breakeven** |
| B5 Commodity | Brent | (merged into B4) |
| B6 Korea | KR 10y change | (removed — replaced by growth) |
| **B5 NEW Growth** | — | **OECD CLI Korea + KR exports** |

Final: **5 blocks, 10 variables, 2 vars per block** (perfectly symmetric).

## Why this is the right test

User 의 framing:
1. D-family 가 "여러 지표 = 문제 생김" + "우리만의 이상적 layer 발견"
2. 하나씩 변수 더하는 한계 도달
3. ChatGPT 의 story-driven design 으로 holistic 비교

D009 = ChatGPT framework 전체 test. 비교 대상은:
- D001 (incremental 8 vars, 6 blocks, mostly degenerate)
- D009 (holistic 10 vars, 5 blocks, all 2-var multi)

If D009 ≈ D001 → **adopt D009 for story coherence** (cleaner mechanism)
If D009 ≫ D001 → ChatGPT framework 본질적 개선
If D009 ≪ D001 → D001's specific 8 vars 가 진짜 매력

## D009 variable specification (사전 등록)

### B1 Global Risk
| Var | Sign | Source | Why |
|---|---|---|---|
| VIX 60d/240d ratio | -1 | fred_vix.csv | 위험회피 spike |
| BAA10Y credit spread (level z) | -1 | fred_baa10y_spread.csv | 신용시장 stress |

(주: BAMLH0A0HYM2 (진짜 HY OAS) 는 FRED 가 2023-05 이후만 제공 →
BAA10Y 를 IG/credit stress proxy 로 사용. ChatGPT 의 HY OAS intent
와 부분 일치 — 둘 다 credit spread widening = stress.)

### B2 USD/FX
| Var | Sign | Source | Why |
|---|---|---|---|
| DXY yoy | -1 | fred_dxy.csv | USD 강세 EM 부정 |
| USDKRW yoy | -1 | fred_dexkous_usdkrw.csv | KRW 약세 한국 부정 |

(주: Fed Broad Dollar Index 도 download 가능 (TWEXBGSMTH) 하지만 DXY
유지 — D001 와 직접 비교 위해 currency dimension 변경 최소화.)

### B3 US Rates
| Var | Sign | Source | Why |
|---|---|---|---|
| US 10y real yield (level z) | -1 | fred_us_10y_real.csv (NEW) | 실질 discount rate, 위험자산 핵심 |
| US 2-10y curve | +1 | fred_dgs2/10.csv | 경기/정책 cycle |

(ChatGPT 핵심 권장 — CPI/PPI 대신 real yield + curve 가 forward-
looking 가격기반 지표.)

### B4 Inflation
| Var | Sign | Source | Why |
|---|---|---|---|
| Brent yoy | -1 | fred_brent.csv | 에너지/비용 inflation |
| 10y breakeven inflation (level z) | -1 | fred_us_breakeven_10y.csv (NEW) | 시장 기대 inflation |

(ChatGPT 권장 — raw CPI/PPI 는 후행적, breakeven 은 forward.)

### B5 Growth
| Var | Sign | Source | Why |
|---|---|---|---|
| OECD CLI Korea (level z) | +1 | fred_kr_cli.csv (D005에서 download) | 한국 leading indicator |
| KR exports yoy | +1 | fred_kr_exports.csv | 한국 수출 활동 |

(ChatGPT 의 missing block — Korea growth/activity dimension.)

## What's intentionally OUT (정직)

| 변수 | 이유 |
|---|---|
| US CPI | Replaced by breakeven (ChatGPT 권장) |
| US PPI | Replaced by breakeven |
| KR 10y | Replaced by KR exports (activity > monetary for foreign-buy) |
| SOX 상대강도 | Nasdaq proprietary, FRED 없음 |
| MSCI Korea/EM ratio | MSCI proprietary, FRED 없음 |
| ISM Manufacturing | FRED 가 2016년 이후 discontinued; OECD CLI 로 대체 |
| Fed Broad Dollar | DXY 유지 (currency 변경 최소화) |

## Factor aggregation (D001 와 동일)

- Z-score: 60-month rolling (D006 plateau 확인)
- Sign-adjusted favorability
- Block score = within-block mean
- Composite = mean of block scores (1/5 per block)
- ON iff composite >= 0 (D007 plateau 확인 됨)

기존 factor_aggregation_composite 그대로 사용. **D009 는 variable set
swap 만**, aggregation logic 완전 같음.

## Pre-registered hypothesis

### H1-H6 inherited
- H1: 누적 net > 0
- H2: KOSPI 대비 -30pp 이내
- H3: spike (2010, 2025, 2026) ≥ 2 positive
- H4: max DD < V2 by 5pp
- H5: ≥ 8/16 positive years (D001 도 fail 한 기준; descriptive 만)
- H6: net / cost-0 ≥ 0.7

### H7 (D009 holistic vs D001)
- D009 net cumulative comparison: vs D001 (+129.07%)
- D009 Sharpe comparison: vs D001 (0.4842)

User criteria: "**성과가 크게 나쁘지 않다면** 그걸 가져가는 것도 나쁘지
않겠다" — 핵심.

Verdict:
- D009 Sharpe ≥ 0.55 → **STRONG ADOPT** (ChatGPT framework 더 우수)
- D009 Sharpe 0.40-0.55 → **COMPARABLE — adopt for story coherence**
- D009 Sharpe 0.30-0.40 → MARGINAL ALTERNATIVE — story 가치 vs 성과 손실 trade-off
- D009 Sharpe < 0.30 → **D001 유지** (story 보다 성과 우선)

### H8 (Subperiod stability — D008 lesson)
- 2025 spike year contribution (D001 의 59.4% 와 비교)
- 만약 D009 가 spike concentration 낮으면 (예: < 40%) → 더 균일 alpha
- 만약 더 높으면 (예: > 70%) → 더 spike-dependent

### H9 (Block scores 진단)
- 각 block 의 평균 score
- Block 간 contribution dispersion
- Variable z-scores 시계열 (real yield 의 2022-2024 spike, breakeven 의 inflation expectation 등 정성 확인)

## Verdict logic (사전 등록)

| Sharpe | Net vs D001 | Verdict | 다음 |
|---:|---:|---|---|
| ≥ 0.55 | ≥ +129% | **STRONG ADOPT D009** | D009 = new carrier; D010 = D009 robustness (D006/D007/D008 재현) |
| 0.40-0.55 | varies | **COMPARABLE — ADOPT D009** | story 우수, D010 = robustness |
| 0.30-0.40 | varies | MARGINAL | story 가치 검토; user 결정 |
| < 0.30 | varies | KEEP D001 | D-family 종료, Layer 2 진입 |

## Reportable metrics

기존 + D009 specific:
1. Full + subperiod cumulative net + cost-0
2. (D009 - D001) per-year delta + cumulative delta
3. Max DD, positive years, Sharpe, annualized, ON share
4. **Block 별 평균 score 5개** (D001 의 6개와 mechanism 비교)
5. **Variable z-score time series** (real yield, breakeven, CLI, KR exports — 새 vars)
6. **D009 2025 contribution %** (D001 59.4% 와 비교 — spike dependency)
7. Composite distribution (D001 mean -0.22, std 0.53 vs D009)
8. Trade overlap with D001 (quarter level Jaccard)
9. **D009 ON / D001 OFF quarters** + **D009 OFF / D001 ON quarters**
10. H1-H9 summary

## Implementation task

### Scope discipline

Touch (additive):
- `src/data/macro_factors.py` — ADD US 10y real yield, breakeven,
  BAA10Y spread feature specs (some may exist; verify)
- `src/features/macro_regime.py` — config 만 변경, factor_aggregation
  이미 yaml-driven
- `src/strategies/d009_chatgpt_holistic.py` (NEW) — D001 clone w/
  different blocks
- `src/run_experiment.py` — D009 dispatch
- `configs/backtests/d009.yaml` (NEW)
- `tests/test_d009_strategy.py` (NEW)

**Do NOT touch**:
- `src/backtest/engine.py`
- 기존 strategy modules (a001-a004, b001-b011, c003-c020, d001-d008)
- D001-D008 byte-identical reproducibility
- 기존 feature 함수들 (관련 macro_factors 추가는 additive only)
- `research_input_data/` 기존 파일

### Data files needed (모두 이미 in research_input_data/)

- fred_vix.csv ✓
- fred_baa10y_spread.csv ✓
- fred_dxy.csv ✓
- fred_dexkous_usdkrw.csv ✓
- fred_dgs2.csv, fred_dgs10.csv ✓
- fred_us_10y_real.csv (NEW, just downloaded)
- fred_brent.csv ✓
- fred_us_breakeven_10y.csv (NEW, just downloaded)
- fred_kr_cli.csv (D005 download)
- fred_kr_exports.csv ✓

### Configuration

`configs/backtests/d009.yaml`:

```yaml
experiment_id: D009
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
  blocks:
    - name: global_risk
      vars:
        - {name: vix_60d_vs_240d,    sign: -1}
        - {name: baa10y_spread_level, sign: -1}
    - name: usd_fx
      vars:
        - {name: usdkrw_yoy, sign: -1}
        - {name: dxy_yoy,    sign: -1}
    - name: us_rates
      vars:
        - {name: us_10y_real_level, sign: -1}
        - {name: us_2_10_curve,     sign: +1}
    - name: inflation
      vars:
        - {name: brent_yoy,           sign: -1}
        - {name: us_breakeven_level,  sign: -1}
    - name: growth
      vars:
        - {name: kr_cli_value,    sign: +1}
        - {name: kr_exports_yoy,  sign: +1}

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
  - factor_macro_gate_mcap
  - kospi_buy_and_hold
  - cash

output_dir: reports/experiments/D009_chatgpt_holistic_design
```

### Completion criteria

- pytest fully green (currently 275)
- 3 variants in metrics.json + cost-0 diagnostic
- engine.py untouched
- D001-D008 byte-identical reproducibility
- Final message reports:
  - V1 D009 cumulative net + cost-0 (vs D001 +129.07 / +139.71)
  - Delta D009 - D001 net + cost-0
  - V1 max DD (D001 -23.67%), positive years (D001 4), Sharpe (D001 0.48), annualized (D001 5.69%)
  - Regime ON share (D001 22.95%)
  - **Block 별 평균 score 5개** (D001 6개 와 함께)
  - **Variable z-score statistics**: mean, std, % above 0 for each of 10 vars
  - **2025 contribution % of total return** (D001 was 59.4%)
  - Composite distribution: mean, std, % above 0 (D001 -0.22, 0.53, 43.75%)
  - Trade overlap with D001 (quarter-level Jaccard)
  - D009 ON / D001 OFF and D009 OFF / D001 ON quarter counts
  - Per-year breakdown (D008 style)
  - H1-H9 summary
  - **Verdict per pre-registered**: STRONG ADOPT / COMPARABLE ADOPT / MARGINAL / KEEP D001

If ambiguity, write D009_codex_questions.md.

### Out of scope

- ❌ Robustness grid (window/threshold) — D010 if D009 adopted
- ❌ Subperiod isolation — D010 if D009 adopted
- ❌ 추가 변수 (SOX, MSCI 등 — proprietary)
- ❌ Selection / costs / rebalance 변경
- ❌ Sizing

## Result summary
DO NOT FILL until backtest complete.

## Claude review
DO NOT FILL until result files are read.
