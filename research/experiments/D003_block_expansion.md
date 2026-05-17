# D003 — Block expansion with within-block averaging

## Status
planned

## What this ticket is

사용자 통찰: ChatGPT 의 block framework 의 핵심은 "같은 theme 의
변수들을 within block 으로 모아 평균 → robust factor score" 인데,
**D001 의 6 blocks 중 4개가 1-variable degenerate** 라서 within-block
averaging 의 실효가 발휘 안 됨.

D003 = **block 확장 + within-block averaging 실효화**.

C-family 의 rejected 변수 중 **theme + sign 이 깔끔하게 맞는 것만**
within-block 에 추가. 새 vote 아닌 block refinement 로.

## Single architectural change

| 차원 | D001 | **D003** |
|---|---|---|
| Blocks | 6 (geography mix) | **5 (theme-pure)** |
| Variables | 8 | **13** |
| Mean vars/block | 1.3 | **2.6** |
| Within-block averaging 실효 | 2/6 blocks | **4/5 blocks** |
| Z-score window | 60mo | same (60mo) |
| Threshold | composite ≥ 0 | same |
| Sign convention | per-var | same per-var |
| Selection / rebalance / costs | unchanged | unchanged |

**Single architectural change**: block 구조.

## New block structure (사전 등록)

### B1 Global Risk (2 vars)
| Var | Sign | Why |
|---|---|---|
| VIX 60d/240d ratio | -1 | 낮음 favorable (risk-on) |
| USDJPY yoy | +1 | yen 약세 (carry active) = risk-on |

### B2 USD/FX (3 vars)
| Var | Sign | Why |
|---|---|---|
| USDKRW yoy | -1 | KRW 강세 favorable |
| DXY yoy | -1 | USD 약세 favorable |
| USDCNY yoy | -1 | CNY 강세 favorable (Asian FX 연동) |

### B3 Rates (4 vars)
| Var | Sign | Why |
|---|---|---|
| US 2-10y curve | +1 | Steep favorable |
| KR 10y change | -1 | Yield 하락 favorable (B6에서 이동) |
| KR 3m change | -1 | Yield 하락 favorable |
| JGB 10y change | -1 | 글로벌 rates 하락 = EM favorable |

### B4 Inflation (3 vars)
| Var | Sign | Why |
|---|---|---|
| US CPI decel | -1 | 인플레 감속 favorable |
| US PPI decel | -1 | 동일 |
| KR CPI decel | -1 | 동일 (한국 인플레 감속도 favorable) |

### B5 Commodity (1 var)
| Var | Sign | Why |
|---|---|---|
| Brent yoy | -1 | 안정/하락 favorable |

(Copper 는 mechanism 반대 — Brent inflation hint vs Copper 성장
hint. 같은 block 평균하면 cancel out → 제외.)

## Variables intentionally NOT added (정직하게)

| Var | 제외 이유 |
|---|---|
| Copper | Brent 와 sign 반대 (-1 vs +1 mechanism) → block 평균 의미 상실 |
| US M2 | Inflation block sign 반대; Liquidity 단독 block 하면 degenerate |
| UNRATE | Labor 단독, fit theme 없음 |
| KR exports | Activity 단독, fit theme 없음 |

→ 향후 D-family 에서 separate block weight 또는 stage-based architecture
로 검토 가능. D003 에서는 깔끔한 theme block 만.

## Sign convention 통일

모든 sign-adjusted fav_score(var) = sign * z(var) 가 **"environment
favorability"** 라는 동일 해석. Block 평균이 의미 있음.

## Factor aggregation formula (D001 와 동일)

```
z(var, T) = (var(T) - mean over [T-60mo, T]) / std over [T-60mo, T]
fav_score(var, T) = sign * z(var, T)
block_score(B, T) = mean(fav_score(var) for var in B)
composite(T) = mean(block_score(B, T) for B in [B1...B5])
ON iff composite(T) >= 0
```

5 blocks → composite = mean of 5 block scores (equal weight per block,
1/5 each).

## Why this should work (mechanism explanation)

### D001 의 한계 진단
- 6 blocks 중 4개 (Global Risk, US Rates, Commodity, Korea) 가
  1-variable → within-block averaging 의 효과 0
- 사실상 6-block 으로 보이지만 **information-wise 는 8개 변수의
  equal weight 평균과 유사**
- ChatGPT framework 의 within-block 의 진가 미발휘

### D003 의 architectural 개선
- 4/5 blocks 가 multi-var → within-block 평균 효과 실효
- C-family 에서 vote 로 fail 한 변수들 (USDCNY 0.50 corr,
  KR CPI 0.83 corr, KR 3m 0.81 corr, JGB neutral) 이 **vote 가 아니라
  block refinement** 로 들어감 → wrong-direction tip 위험 제거
- Block 내 평균 → noise 감소, signal 강화 (특히 Rates block 4 vars
  의 평균은 단일 curve 보다 robust)

### Critical test
이 architecture 가 **C-family vote logic 의 실패가 변수 잘못이
아니라 architecture 잘못** 임을 증명. PASS면 framework 정당화.
FAIL면 변수 자체의 한계 확인.

## Pre-registered hypothesis

### H1-H6 inherited
- H1: 누적 net > 0
- H2: KOSPI 대비 -30pp 이내
- H3: spike (2010, 2025, 2026) ≥ 2 positive
- H4: max DD < V2 by 5pp
- H5: ≥ 8/16 positive years
- H6: net / cost-0 ≥ 0.7

### H7 (D003 architecture-specific): Block expansion 효과
- D003 net cumulative ≥ D001 (+129.07%) → block 확장 net 효과 있음
- 또는 Sharpe ≥ D001 (0.48) + DD ≤ D001 (-23.67%) → risk-adjusted 개선
- Sharpe ≥ 0.40 (D001 의 0.48 큰 폭 후퇴 없음)

### H8 (Subperiod robustness)
- 2010-2017 net (D001 0% zero-trade vs D003 actual trades)
- 2018-2026 net 유지

### H9 (Descriptive — block effect 진단)
- Block 별 average score, std, % positive (D001 vs D003 비교)
- Within-block variance (D001 의 1-var blocks 와 D003 의 multi-var
  blocks 의 noise 차이)
- Composite distribution (mean, std, % above 0)
- Regime ON share (D001 22.95%)
- Trade count, overlap with D001

## Verdict logic (사전 등록)

| 결과 | Verdict | 다음 |
|---|---|---|
| H7 PASS + Sharpe ≥ 0.40 + pre-2018 ≥ 0 | **STRONG PROMOTE D003** | D004 = position sizing on D003 carrier |
| H7 PASS + Sharpe ≥ 0.40 + pre-2018 < 0 | CONDITIONAL — modern era 효과 | D004 진행 |
| H7 marginal (±5pp) | INCONCLUSIVE | D004 = position sizing on D001 carrier |
| H7 FAIL + Sharpe drop | block 확장 noise 증가 | D001 8 vars 가 sweet spot |
| H7 FAIL + Sharpe 유지 | benign expansion | D004 진행, D003 carrier 검토 |

## Reportable metrics

기존 + D003 specific:
1. Full + subperiod cumulative net + cost-0
2. (D003 - D001) per-year delta + (D003 - D001) cumulative delta
3. **Block 별 평균 score 5개** (D001 6개와 비교)
4. **Within-block variance** (vars per block 의 평균 std)
5. Composite 분포 (D001 mean -0.0682, std 0.5174 와 비교)
6. Regime ON share, max DD, Sharpe, annualized
7. **Trade overlap with D001** (Jaccard) — 얼마나 다른 trade
8. H1-H7 + H8 + H9 summary

## Implementation task

### Scope discipline

Touch (additive):
- `src/features/macro_regime.py` — factor_aggregation_composite 가 이미
  yaml-driven block 구조 받음 → 코드 변경 없음 또는 minimal
  (config 추가 변수의 mapping 만)
- `src/data/macro_factors.py` — KR CPI, USDCNY, KR 3m, JGB 10y 의
  feature spec 추가 (이미 있을 수도 있음, 확인)
- `src/strategies/d003_block_expansion.py` (NEW) — d001 clone
- `src/run_experiment.py` — D003 dispatch
- `configs/backtests/d003.yaml` (NEW) — 5 blocks, 13 vars 사전 등록
- `tests/test_d003_strategy.py` (NEW)

**Do NOT touch**:
- `src/backtest/engine.py`
- 기존 strategy modules (a001-a004, b001-b011, c003-c020, d001, d002)
- D001/D002 reproducibility 보존
- 기존 features 모듈 (관련 macro_factors 변경은 additive only)
- `research_input_data/`

### Variables 와 data 파일

이미 모두 존재:
- USDKRW: fred_dexkous_usdkrw.csv
- VIX: fred_vix.csv
- DXY: fred_dxy.csv
- USDJPY: fred_jpy.csv (C019)
- USDCNY: fred_dexchus.csv
- US 2y, 10y: fred_dgs2.csv, fred_dgs10.csv
- KR 10y: fred_kr10y.csv
- KR 3m: fred_kr3m.csv
- JGB 10y: fred_jp10y.csv (C020)
- US CPI: fred_us_cpi.csv
- US PPI: fred_us_ppi.csv
- KR CPI: fred_kr_cpi.csv
- Brent: fred_brent.csv

데이터 다운로드 필요 없음. 모두 read-only.

### Configuration

`configs/backtests/d003.yaml`:

```yaml
experiment_id: D003
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
        - {name: vix_60d_vs_240d, sign: -1}
        - {name: usdjpy_yoy,     sign: +1}
    - name: usd_fx
      vars:
        - {name: usdkrw_yoy, sign: -1}
        - {name: dxy_yoy,    sign: -1}
        - {name: usdcny_yoy, sign: -1}
    - name: rates
      vars:
        - {name: us_2_10_curve,    sign: +1}
        - {name: kr10y_yoy_change, sign: -1}
        - {name: kr3m_yoy_change,  sign: -1}
        - {name: jp10y_yoy_change, sign: -1}
    - name: inflation
      vars:
        - {name: us_cpi_decel,  sign: -1}
        - {name: us_ppi_decel,  sign: -1}
        - {name: kr_cpi_decel,  sign: -1}
    - name: commodity
      vars:
        - {name: brent_yoy, sign: -1}

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

output_dir: reports/experiments/D003_block_expansion
```

### Completion criteria

- pytest fully green (currently 246)
- 3 variants in metrics.json + cost-0 diagnostic
- engine.py untouched
- D001 reproducibility (existing test 그대로 pass)
- D002 reproducibility (existing test 그대로 pass)
- Final message reports:
  - V1 D003 cumulative net + cost-0 (vs D001 +129.07 / +139.71)
  - V1 D003 vs C014 v11 (+111.36 / +148.39)
  - Delta D003 - D001 net + cost-0
  - **Subperiod 2010-2017 V1 D003 net + cost-0 + trade count**
  - **2010-2014 trade count**
  - Subperiod 2018-2026 V1 D003 net + cost-0
  - V1 max DD (D001 was -23.67%)
  - V1 positive years (D001 was 4)
  - Sharpe (D001 was 0.48)
  - Annualized
  - Regime ON share (D001 was 22.95%)
  - **Block 별 평균 score 5개** (D001 6개 와 비교)
  - **Within-block average std** (multi-var blocks 의 var 분산)
  - Composite distribution (mean, std, % above 0; D001 was -0.07, 0.52, 43%)
  - Trade overlap with D001 (Jaccard)
  - H1-H9 summary

If ambiguity, write D003_codex_questions.md.

### Out of scope

- ❌ Z-score window 변경
- ❌ Threshold 변경
- ❌ Position sizing
- ❌ Risk circuit breaker
- ❌ Block weights tuning (등가)
- ❌ M2, UNRATE, KR exports, Copper 추가 (다음 ticket 검토)
- ❌ Selection / rebalance / costs 변경

## Result summary
DO NOT FILL until backtest complete.

## Claude review
DO NOT FILL until result files are read.
