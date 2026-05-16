# C008 — Macro v6 (+ Brent oil) — commodity dimension

## Status
planned

## What this ticket is

C007 의 pre-registered fallback. C007 (selection N=20) 도 fail 한 뒤
사용자 의견 (매크로 더 추가) 이 commit 된 fallback 으로 진입.

C008 = **C005 v4 carrier + Brent oil** 추가. 5-var composite.

## Why Brent (사용자 의견 + roadmap)

C001 v2 macro deepening roadmap:
- v1: USDKRW + Fed
- v2: + VIX
- v3: + DXY ← C003-C004
- v4: + US 2-10y curve ← **C005 (BEST)**
- v5: + USDCNY ← C006 (regressed, dropped)
- **v6: + commodity (Brent or copper)** ← C008

USDCNY 는 hypothesis space 에서 drop (regression). Brent 는 진정으로
다른 dimension 으로 entry.

### Brent 의 mechanism (사전 글로 commit)

**기존 4 변수 모두 finance dimension**:
- USDKRW = currency flow (Asia FX)
- VIX = risk appetite (sentiment)
- DXY = USD broad (FX)
- US curve = term premium (rates)

**Brent = real economy / commodity dimension** — 진정으로 orthogonal:
- 한국은 oil 100% 수입 → 정유/화학 sector 직접 영향
- 글로벌 demand cycle proxy (oil demand = global growth)
- Inflation leading indicator
- USD 강세와 일반 inverse correlation (oil priced in USD)

**Formula 가설**:
```
brent_yoy(T) = Brent(T) / Brent(T-252) - 1
favorable_brent(T) = brent_yoy(T) <= 0  (oil 가격 안정 또는 하락)
```

**가설 mechanism**: Oil 가격 상승 = 한국 수입 인플레이션 + 정유 마진
compression + 글로벌 demand overheat → 한국 주식 부정적. Oil 안정/
하락 = 정유 마진 회복 + 인플레이션 안정 → 한국 주식 favorable.

Caveat: Oil 가격 상승이 글로벌 demand 강함 신호 (commodity reflation)
일 수도 있어 양면적. 단순 yoy 부호로 시작.

## Single change from C005 v4 carrier

| 변수 | C005 v4 carrier | **C008 변경** |
|---|---|---|
| Macro variables | USDKRW + VIX + DXY + curve (4개) | **+ Brent (5개)** |
| Composite threshold | ≥ 2 of 4 | **≥ 2 of 5** (same absolute count) |
| Selection | top-5 mcap | unchanged |
| Rebalance | quarterly | unchanged |
| 기타 | unchanged | unchanged |

**C006 는 v4 + USDCNY 였고, C008 은 v4 + Brent**. C006 와 다른 새 5번째 변수.

## Data status — Claude 가 사용자 승인 후 직접 다운로드 완료

Brent 데이터 already downloaded:
- Path: `research_input_data/inputs/macro_features/fred_brent.csv`
- Source: FRED series `DCOILBRENTEU` (Crude Oil Prices: Brent Europe)
- Coverage: 1987-05-20 ~ 2026-05-11 (4267 rows in 2010-2026 window)
- Schema: `observation_date, DCOILBRENTEU` (date + value)
- 무료, 무인증

Codex 의 남은 작업: loader 확장 + 6-var (다른 5개) composite 추가.

## Hypothesis (사전 등록)

H1-H6 from C005 그대로 +

### H7 (NEW): Brent informativeness
- V1 v6 (= C005 v4 + Brent) cumulative net ≥ V1 v4 (C005) + **5pp** → informative
- 0 ~ +5pp → marginal
- < 0pp → noise (USDCNY case 같음)

### H8 (descriptive): Brent-USDKRW yoy correlation
Brent yoy 와 USDKRW yoy 의 시계열 상관관계 측정. > 0.5 면 partial overlap. < 0.3 면 진짜 독립 dimension.

## Verdict logic (사전 등록)

| 통과 | Verdict | 다음 step |
|---|---|---|
| 6/6 H1-H6 + H7 PASS | STRONG PROMOTE (v6 = v4 + Brent) | C009 = 다음 layer (sector data 수집) 또는 holding 변경 |
| 4-5/6 + H7 PASS | CONDITIONAL PROMOTE | dimension 진단 후 다음 |
| 2-3/6 + H7 ≥ +5pp | INCONCLUSIVE + Brent helps | C009 = 다른 commodity (copper) 또는 selection 보강 |
| **2-3/6 + H7 < +5pp** | **deepening 진짜 한계** | **C009 = strategic 재고 — 우리 hypothesis space 끝**  |
| 0-1/6 or catastrophic | KILL | architecture 재고 |

**중요**: 만약 Brent 도 fail 면 macro v5 (USDCNY), v6 (Brent) 둘 다 못한 게 됨. 즉 **C005 v4 가 진짜 global optimum** 일 가능성 매우 큼. **C009 = strategic 재고** 의 의미: 현 hypothesis space (single 매크로 gate + mcap selection + quarterly) 의 한계 인정 후 더 큰 redesign (예: sector layer 데이터 수집, fundamentally different alpha class, project 결론).

## Reportable metrics

C005 와 동일 + v4 vs v6 비교:
1. Cumulative net + cost-0 (16yr): V1 v6 + V1 v4 + V2 + V3
2. Per-year breakdown (v6 yearly, v6-v4 delta)
3. Max DD, Sharpe, hit rate
4. Cost paid + cost-eaten %
5. Year-wise positive count
6. **Brent favorable quarters** (sample size)
7. **Brent-USDKRW yoy 상관관계 (H8 descriptive)**
8. **Brent-VIX 상관관계** (보조: oil shock = risk-off correlation 측정)

## Implementation task (Codex)

### Scope discipline

Touch (additive):
- `src/data/macro_factors.py` — ADD Brent series spec to FRED_SERIES
  list (Claude 가 이미 fred_brent.csv 다운로드 완료)
- `src/features/macro_regime.py` — ADD `brent_yoy` signal + 5-var
  composite (USDKRW + VIX + DXY + curve + Brent). USDCNY 미포함.
  Backward compat: 3/4-var composites preserved.
- `src/strategies/c008_quarterly_macro_v6.py` (NEW) — clone of
  c005 with config pointing to 5 signals (USDKRW + VIX + DXY +
  curve + brent)
- `src/run_experiment.py` — `experiment_id == "C008"` dispatch
- `configs/backtests/c008.yaml` (NEW)
- `tests/test_macro_factors_loading.py` — ADD Brent loading test
- `tests/test_macro_regime.py` — ADD Brent signal test (formula,
  no-look-ahead)
- `tests/test_c008_strategy.py` (NEW) — sanity

**Do NOT touch**:
- `src/backtest/engine.py`
- 기존 strategy modules (a001-a004, b001-b011, c003-c007)
- 기존 features 모듈 (relative_flow, flow_ratios, regime, kospi_proxy)
- `research_input_data/` (Brent CSV 이미 있음, 수정 안 함)

### Configuration

`configs/backtests/c008.yaml`:

```yaml
experiment_id: C008
# panels, market_breadth_csv, macro_data_dir, period, universe,
# costs, rebalance: 모두 C005 와 동일

regime:
  macro_signals:
    - usdkrw_yoy
    - vix_60d_vs_240d
    - dxy_yoy
    - us_2_10_curve
    - brent_yoy  # NEW; USDCNY excluded (regressed)
  composite_rule: count_favorable
  on_threshold: 2  # >= 2 of 5

selection:
  type: market_cap_top_n
  n: 5  # C005 v4 N=5

variants:
  - macro_gate_mcap
  - kospi_buy_and_hold
  - cash
output_dir: reports/experiments/C008_macro_v6_brent
```

### Completion criteria

- pytest fully green (currently 185)
- engine.py untouched
- Final message:
  - V1 v6 cumulative net: __ percent
  - V1 v6 cost-0 cumulative: __ percent (vs C005 v4 cost-0 +3.67 percent)
  - C005 V1 v4 cumulative for reference: -8.48 percent
  - Delta v6 - v4 net: __ pp (H7, threshold >= +5pp)
  - Delta v6 - v4 cost-0: __ pp
  - V1 max DD: __ percent
  - V1 positive years: __ of 16
  - V1 in 2010 / 2025 / 2026: __ / __ / __ percent (H3)
  - V1 annualized return: __ percent, Sharpe: __
  - Regime ON share: __ percent (v4 was 64 percent)
  - Brent favorable quarters: __ of __
  - Brent-USDKRW yoy correlation: __ (H8 descriptive)
  - Brent-VIX correlation: __ (supplementary)
  - H1-H7 PASS/FAIL summary

If ambiguity, write to research/experiments/C008_codex_questions.md and stop.

### Out of scope

- ❌ USDCNY 다시 시도 (C006 에서 fail 확인)
- ❌ Selection 변경 (C007 에서 fail 확인)
- ❌ Threshold 변경
- ❌ Rebalance frequency 변경
- ❌ 다른 commodity (copper 등) 동시 추가
- ❌ Sector layer

## Result summary
DO NOT FILL until backtest complete.

## Claude review
DO NOT FILL until result files are read.
