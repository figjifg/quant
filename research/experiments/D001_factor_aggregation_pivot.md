# D001 — Factor-aggregation architecture pivot

## Status
planned

## What this ticket is

**D-family 첫 ticket**. C-family 20 ticket 후 명확한 saturation 진단 +
ChatGPT framework critique 가 동일 결론: "**composite logic 자체가
bottleneck, 변수 추가 ≠ 해결**".

C-family 의 "**≥ 2 of N count favorable**" composite 를 **factor-block
z-score aggregation** 으로 architectural pivot.

## What changes (architectural)

| 차원 | C-family (count vote) | **D-family (factor aggregation)** |
|---|---|---|
| 변수 처리 | Binary 1 vote per var | **Z-score 계산** |
| 그룹화 | Flat list, equal weight per var | **Factor block 으로 그룹** |
| Aggregation | Count favorable | **Block 평균 → composite 평균** |
| Regime decision | ≥ threshold count | **Composite ≥ 0 (above-average)** |
| Variables | 8 (C014 v11) | **Same 8** (변경 없음) |
| Selection / rebalance / etc | unchanged | unchanged |

**Variables 자체는 동일**. 단일 변수 변경 discipline 유지 — 변경되는 건
**aggregation 방식 하나**.

## Variable → Factor block mapping (사전 등록)

8 variables of C014 v11 → 6 factor blocks:

| Block | Variables | 의미 |
|---|---|---|
| **B1 Global Risk** | VIX (60d vs 240d) | 글로벌 위험 selection |
| **B2 USD / FX** | USDKRW yoy, DXY yoy | Currency / 글로벌 달러 |
| **B3 US Rates** | US 2-10y curve spread | 미국 yield curve / recession risk |
| **B4 Inflation / Fed Path** | US CPI decel, US PPI decel | Fed 정책 변수 |
| **B5 Commodity** | Brent yoy | 원자재 / inflation hint |
| **B6 Korea Specific** | KR 10y change | Korean monetary |

각 block 의 변수 개수가 다름 (1-2개 mix). Block 가중치는 등가 (각 1/6).

## Factor aggregation formula (사전 등록)

### Step 1: Variable z-score
각 변수에 대해 **rolling 5-year (60-month) z-score** 계산.
일반 형태:
```
z(var, T) = (var(T) - mean(var over [T-60mo, T])) / std(var over [T-60mo, T])
```

### Step 2: Sign-adjusted favorability score
각 변수의 favorable 방향에 따라 sign 적용:
```
fav_score(var, T) = sign * z(var, T)
where sign = +1 if higher value = favorable, -1 if lower = favorable
```

각 변수의 sign:
| Variable | Sign | Why |
|---|---|---|
| USDKRW yoy | -1 | KRW 강세 (yoy 낮음) favorable |
| VIX 60d vs 240d ratio | -1 | VIX 낮음 favorable |
| DXY yoy | -1 | USD 약세 favorable |
| US 2-10y curve | +1 | Curve steep (not inverted) favorable |
| Brent yoy | -1 | Brent 안정/하락 favorable |
| KR 10y change | -1 | KR yield 하락 favorable |
| US CPI decel | -1 | Inflation decelerating favorable |
| US PPI decel | -1 | Inflation decelerating favorable |

### Step 3: Block score (mean of in-block fav_scores)
```
block_score(B, T) = mean(fav_score(var) for var in block B)
```
B1 = z(VIX) alone (block 안 1 var). B2 = mean of z(-USDKRW), z(-DXY). 등등.

### Step 4: Composite (mean of block scores)
```
composite(T) = mean(block_score(B, T) for B in [B1...B6])
```
**Equal weight** per block (1/6 each). Weighted variant 검토는 D002+.

### Step 5: Regime ON/OFF
```
ON iff composite(T) >= 0  (above-average favorability)
OFF iff composite(T) < 0
```
**Threshold = 0** (above 5-year average favorability). Pre-registered.
Tuning 금지.

## Why this should work (mechanism explanation)

### C-family count vote 의 결함
- 8 vars 중 일부가 같은 factor (FX, inflation 등) → 같은 정보 여러 vote
- 다른 factor 의 weak signal 이 같은 factor 의 strong signal 에 overwhelm
- 새 var 추가 시 same-factor 면 redundancy, different-factor 면 marginal vote (KR3m, UNRATE, KR CPI, JGB 같은 0-contribution case)

### D-family factor aggregation 의 합리성
- 같은 factor 의 vars 가 평균 → 정보 중복 제거
- 다른 factor block 이 각각 1/6 weight → balanced view
- 새 var 추가 시 같은 block 이면 평균에 흡수, 다른 block 이면 새 block 추가 가능
- ChatGPT 의 framework critique 정확히 매칭

## Pre-registered hypothesis (D-family verdict logic)

### H1-H6 inherited (조정)
- H1: 누적 net > 0
- H2: KOSPI 대비 -30pp 이내
- H3: spike (2010, 2025, 2026) ≥ 2 positive
- H4: max DD < V2 by 5pp (literal)
- H5: ≥ 8/16 positive years
- H6: net / cost-0 ≥ 0.7

### H7 (D001 architecture-specific): Factor aggregation 효과
- D001 net cumulative ≥ C014 v11 (+111.36%) + **5pp** → factor 가 count 보다 나음
- 0 ~ +5pp → marginal architectural improvement
- < 0pp → factor aggregation worse → architectural pivot 실패

### H8 (subperiod robustness): pre-2018 핵심
- 2010-2017 net ≥ 0 (가장 중요한 진전 지표; C014 v11 -8.16%)
- 2018-2026 net 유지 (C014 +130%)

### H9 (descriptive): regime ON share + composite distribution
- D001 regime ON share (C014 was 83.61%)
- Composite 분포 (mean, std, % positive over 16 years)
- Block scores 의 각 block 별 average contribution

## Verdict logic (사전 등록)

| 통과 | Verdict | 다음 |
|---|---|---|
| H7 PASS + 두 subperiod ≥ 0 | **STRONG PROMOTE D001** — 진짜 robust strategy | D002 = position sizing 또는 Layer 2 |
| H7 PASS + 한쪽만 | CONDITIONAL PROMOTE | D002 = block weight tuning 또는 다른 refinement |
| H7 marginal (-5 ~ +5pp) | INCONCLUSIVE | D002 = factor weighting 시도 |
| H7 FAIL (< -5pp) | factor aggregation 도 fail | **strategic 재고** — hypothesis space 한계 인정 |
| H1 catastrophic | KILL | architecture 전면 재고 |

## Reportable metrics

기존 + D001 specific:
1. Full + subperiod cumulative net + cost-0
2. (D001 - C014 v11) per-year delta
3. **Composite 시계열** (quarter별 값) — distribution 분석
4. **Block 별 평균 score** (어느 block 이 driver 였나)
5. Regime ON share + distribution of composite scores
6. **D001 vs C014 v11 trade overlap** (얼마나 다른 trade)
7. Max DD, positive years, Sharpe, annualized
8. H1-H7 + H8 + H9

## Implementation task

### Scope discipline

Touch (additive):
- `src/features/macro_regime.py` — ADD factor_aggregation_composite
  function. Existing count-favorable composites preserve (모든 C-family
  실험 재현 가능 유지).
- `src/strategies/d001_factor_aggregation.py` (NEW) — clone of c014
  pattern 그러나 factor_aggregation_composite 사용
- `src/run_experiment.py` — `experiment_id == "D001"` dispatch
- `configs/backtests/d001.yaml` (NEW)
- `tests/test_macro_regime.py` — ADD factor aggregation test
  (z-score 정확성, no-look-ahead, sign convention)
- `tests/test_d001_strategy.py` (NEW)

**Do NOT touch**:
- `src/backtest/engine.py`
- 기존 strategy modules (a001-a004, b001-b011, c003-c020)
- 기존 features 모듈 (relative_flow, flow_ratios, regime, kospi_proxy,
  기존 macro_regime functions)
- `research_input_data/`

### Z-score implementation note

Z-score 의 critical decision:
- Rolling window: **60 months (5 years)**
- Insufficient data 시 (warmup): NaN, gate 는 OFF (안전한 default)
- Look-ahead 방지: T 시점의 z-score 는 [T-60mo, T] 사용, **T 자체 포함 OK** (sample 의 가장 마지막 점)
- Standard deviation 0 시 (degenerate): z-score 0 (neutral)

### Configuration

`configs/backtests/d001.yaml`:

```yaml
experiment_id: D001
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
  aggregation: factor_z_score    # NEW (vs count_favorable)
  z_score_window_months: 60
  on_threshold: 0.0              # composite >= 0
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

variants:
  - factor_macro_gate_mcap
  - kospi_buy_and_hold
  - cash

output_dir: reports/experiments/D001_factor_aggregation_pivot
```

### Completion criteria

- pytest fully green (currently 239)
- 3 variants in metrics.json + cost-0 diagnostic
- engine.py untouched
- Final message reports:
  - V1 D001 cumulative net + cost-0 (vs C014 v11: +111.36 / +148.39)
  - Delta D001 - C014 v11 net + cost-0 (H7, threshold >= +5pp)
  - **Subperiod 2010-2017 V1 D001 net + cost-0 (H8 — KEY; C014 was -8.16 / -2.53)**
  - Subperiod 2018-2026 V1 D001 net + cost-0
  - V1 max DD, positive years, Sharpe, annualized
  - Regime ON share (C014 was 83.61 percent)
  - **Composite 분포: mean, std, percent of quarters above 0** (regime distribution)
  - **Block 별 평균 score** (each of 6 blocks)
  - Trade overlap with C014 v11 (얼마나 다른 trade 선택)
  - H1-H7 + H8 + H9 summary

If ambiguity, write to research/experiments/D001_codex_questions.md and stop.

### Out of scope for D001

- ❌ Position sizing (그건 D002)
- ❌ Risk circuit breaker (D003)
- ❌ Block weights tuning (D002)
- ❌ 새 macro variables (D-family later 또는 stay at 8)
- ❌ Selection / rebalance / costs 변경
- ❌ Stage-based structure (D004)
- ❌ Engine 변경

## Result summary
DO NOT FILL until backtest complete.

## Claude review
DO NOT FILL until result files are read.
