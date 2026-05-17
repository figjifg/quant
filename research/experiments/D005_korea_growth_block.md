# D005 — Add B7 Korea Growth block (missing-block hypothesis)

## Status
planned

## What this ticket is

ChatGPT 의 architectural critique: D001 의 6 blocks (글로벌 위험,
달러/FX, 금리, 인플레, 원자재, 한국 금리) 가 "한국을 살 직접적인 이유"
를 capture 안 함. 빠진 dimension = **한국 성장/수출/이익 사이클**.

ChatGPT 제안:
> "D001의 8개 변수는 적지 않다. 진짜 문제는 변수 개수가 아니라:
> 이 변수가 기존 변수들이 설명하지 못하는 새로운 원인을 설명하는가?"

D005 = D001 carrier + **B7 Korea Growth block 추가** (단일 architectural
change). 기존 B1-B6 보존.

## Single architectural change

| 차원 | D001 | **D005** |
|---|---|---|
| Blocks | 6 | **7** |
| Block weight | 1/6 each | **1/7 each** |
| Variables | 8 | **10** (+2 in new B7) |
| 기존 B1-B6 | as is | **unchanged** |
| Z-score window | 60mo | same |
| Threshold | composite ≥ 0 | same |
| Selection / rebalance / costs | unchanged | unchanged |

**Single architectural change**: new block addition.

## New B7 Korea Growth block (2 vars)

### B7 vars

| Var | Sign | Source | Why |
|---|---|---|---|
| KR exports yoy | +1 | fred_kr_exports.csv | 한국 수출 성장 = 외국인 매수 직접 이유 |
| OECD CLI Korea | +1 | **fred_kr_cli.csv (NEW)** | 한국 leading indicator, 글로벌 수요 → 수출 → 이익 chain |

**Block size = 2**: D003 lesson 회피 (1-var degenerate).

### Sign convention

- **KR exports yoy**: higher growth = favorable (sign +1). z-score 가
  positive → KR 수출 momentum 강함 → 외국인 매수 환경
- **OECD CLI Korea**: level (100 around trend); higher = expansion
  (sign +1). z-score positive → CLI 가 trend 평균 이상 → 경기 회복기

C-family fail history note: KR exports 가 vote 로는 -42pp fail. 그러나
factor agg 안에서 within-block averaging 하면 결과 다를 가능성. ChatGPT
framework 의 "조건부 변수" 가 아닌 "성장 block" 의 building block 으로.

### Data: OECD CLI Korea (NEW)

- FRED `KORLOLITOAASTSAM`
- Monthly, 1990-01 ~ 2026-04 (437 obs)
- "Composite Leading Indicators, Amplitude Adjusted, SA, Korea"
- 100 around trend, expansion above, contraction below
- 이미 downloaded: `research_input_data/inputs/macro_features/fred_kr_cli.csv`

### Why ISM 대신 OECD CLI Korea

- FRED ISM (NAPM) 시리즈 discontinued (license)
- OECD CLI Korea 가 더 직접적 (Korean leading, not US)
- ChatGPT 가 "ISM 또는 OECD CLI" 둘 다 추천
- 2026-04 까지 current 데이터

## Why this should work (mechanism)

### D001-D004 의 공통 패턴
- D001 6 blocks 가 글로벌 macro 환경 capture
- D002 (window), D003 (vars), D004 (sizing) 모두 fail
- **Missing dimension: "한국이 매력적인가" 자체**

### B7 의 새 정보
- Global manufacturing 회복 (CLI 상승) → KR exports 회복 → KR earnings
  → 외국인 매수
- 기존 B1-B6 의 어떤 변수와도 직접 overlap 안 됨:
  - VIX = risk-on/off (다른 channel)
  - DXY/USDKRW = currency (다른 channel)
  - US curve = 금리 (다른 channel)
  - CPI/PPI = 인플레 (다른 channel)
  - Brent = 원자재 (다른 channel)
  - KR 10y = 한국 monetary (다른 channel)
- B7 = "한국 fundamental momentum" (완전 새 dimension)

### Critical test
이 missing-block 가설이 **D-family 의 최종 architectural test**.

**PASS** = ChatGPT framework + missing-block 정당화, D-family 의 새 carrier
**FAIL** = D001 6 blocks 가 진짜 sweet spot, growth block 도 noise

## Pre-registered hypothesis

### H1-H6 inherited
- H1: 누적 net > 0
- H2: KOSPI 대비 -30pp 이내
- H3: spike (2010, 2025, 2026) ≥ 2 positive
- H4: max DD < V2 by 5pp
- H5: ≥ 8/16 positive years
- H6: net / cost-0 ≥ 0.7

### H7 (D005 missing-block 효과)
- D005 net cumulative ≥ D001 (+129.07%) → growth block 효과 있음
- 또는 Sharpe ≥ 0.48 (D001) + DD ≤ -23.67% (D001) → risk-adjusted 개선
- Sharpe ≥ 0.40 (D001 의 0.48 큰 폭 후퇴 없음)

### H8 (Subperiod robustness)
- 2010-2017 net + actual trades (D001 0% zero-trade artifact 검증)
- 2018-2026 net 유지

### H9 (Descriptive — block effect)
- B7 average score (D001 의 6 blocks 와 비교)
- B7 within-block variance (KR exports vs CLI 상관)
- Composite distribution (D001 mean -0.07, std 0.52 vs D005)
- Regime ON share (D001 22.95%)
- Trade overlap with D001

## Verdict logic (사전 등록)

| 결과 | Verdict | 다음 |
|---|---|---|
| H7 PASS (net ≥ +129%) + Sharpe ≥ 0.40 + pre-2018 ≥ 0 | **STRONG PROMOTE D005** | D006 = ChatGPT 의 path B (full variable replacement) 검토 |
| H7 PASS Sharpe-only (risk improvement) | CONDITIONAL | D006 = additional growth var 검토 |
| H7 marginal (±5pp) | INCONCLUSIVE | D006 = OECD CLI alone test 또는 KR exports alone test (어느 var driver) |
| H7 FAIL + Sharpe drop | growth block 도 noise | **D-family 종료**, Layer 2 진입 |
| H7 FAIL + Sharpe 유지 | benign 확장 | Layer 2 진입 후 D005 carrier 검토 |

## Reportable metrics

기존 + D005 specific:
1. Full + subperiod cumulative net + cost-0
2. (D005 - D001) per-year delta + cumulative delta
3. Max DD, positive years, Sharpe, annualized
4. **B7 average score** (D001's 6 blocks 와 함께)
5. **B7 within-block variance** (KR exports z vs CLI z correlation)
6. **KR exports yoy & OECD CLI yoy time series** (quarterly samples)
7. Composite distribution (D001 vs D005 mean/std/% above 0)
8. Regime ON share (D001 22.95%)
9. Trade overlap with D001 (Jaccard, quarter level)
10. **D005 가 D001 와 다른 trade quarters**: D005 ON / D001 OFF 와 D005 OFF / D001 ON
11. H1-H9 summary

## Implementation task

### Scope discipline

Touch (additive):
- `src/data/macro_factors.py` — ADD OECD CLI loading spec (read
  fred_kr_cli.csv, column KORLOLITOAASTSAM)
- `src/features/macro_regime.py` — config 만 변경 가능
  (factor_aggregation_composite 가 이미 yaml-driven 가능)
- `src/strategies/d005_korea_growth.py` (NEW) — d001 clone
- `src/run_experiment.py` — D005 dispatch
- `configs/backtests/d005.yaml` (NEW) — 7 blocks
- `tests/test_d005_strategy.py` (NEW)

**Do NOT touch**:
- `src/backtest/engine.py`
- 기존 strategy modules (a001-a004, b001-b011, c003-c020, d001-d004)
- D001/D002/D003/D004 reproducibility byte-identical
- 기존 features 모듈 (관련 macro_factors 추가는 additive only)
- `research_input_data/` 의 기존 파일

### Variables / signs

```
B7 = Korea Growth
  - kr_exports_yoy (sign +1)  # higher growth favorable
  - kr_cli_value  (sign +1)   # higher CLI favorable (level vs trend)
```

**Note**: OECD CLI 가 level 기반 indicator (around 100). Z-score 가
60mo rolling 으로 계산되면 자연스럽게 "최근 60mo 평균 대비 상대 위치"
가 됨. Yoy 또는 diff 전처리 불필요.

### Configuration

`configs/backtests/d005.yaml`:

```yaml
experiment_id: D005
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
    # B1-B6 D001 그대로
    - name: global_risk
      vars:
        - {name: vix_60d_vs_240d, sign: -1}
    - name: usd_fx
      vars:
        - {name: usdkrw_yoy, sign: -1}
        - {name: dxy_yoy,    sign: -1}
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
    # B7 NEW
    - name: korea_growth
      vars:
        - {name: kr_exports_yoy, sign: +1}
        - {name: kr_cli_value,   sign: +1}

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

output_dir: reports/experiments/D005_korea_growth_block
```

### Completion criteria

- pytest fully green (currently 253)
- 3 variants in metrics.json + cost-0 diagnostic
- engine.py untouched
- D001/D002/D003/D004 byte-identical reproducibility (SHA-256 check)
- Final message reports:
  - V1 D005 cumulative net + cost-0 (vs D001 +129.07 / +139.71)
  - Delta D005 - D001 net + cost-0
  - V1 D005 vs C014 v11 (+111.36 / +148.39)
  - Subperiod 2010-2017 V1 D005 net + cost-0 + trade count
  - 2010-2014 trade count
  - Subperiod 2018-2026 V1 D005 net + cost-0
  - V1 max DD (D001 -23.67%), positive years (D001 4), Sharpe (D001 0.48), annualized (D001 5.69%)
  - Regime ON share (D001 22.95%)
  - **B7 Korea Growth average score** (vs D001's 6 blocks: US rates -0.74, Commodity -0.25, Korea -0.21, Global risk -0.16, Inflation -0.01, USD/FX +0.05)
  - **B7 within-block: KR exports z vs CLI z correlation, mean, std of each**
  - Composite distribution: mean, std, % above 0 (D001 was -0.07, 0.52, 43%)
  - Trade overlap with D001 (Jaccard, quarter level)
  - **D005 ON / D001 OFF quarters** (B7 이 새로 추가한 ON quarters)
  - **D005 OFF / D001 ON quarters** (B7 이 OFF 만든 quarters)
  - H1-H9 summary

If ambiguity, write D005_codex_questions.md.

### Out of scope

- ❌ 기존 B1-B6 변경 (D001 그대로)
- ❌ Z-score window 변경
- ❌ Threshold 변경
- ❌ Position sizing
- ❌ Block weight tuning
- ❌ 다른 변수 추가 (US HY OAS, real yield, MSCI 등은 D006+)
- ❌ Variable replacement (CPI/PPI/KR10y 교체는 ChatGPT path B, D006+)
- ❌ Selection / rebalance / costs 변경

## Result summary
DO NOT FILL until backtest complete.

## Claude review
DO NOT FILL until result files are read.
