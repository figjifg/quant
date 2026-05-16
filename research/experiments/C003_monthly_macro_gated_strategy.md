# C003 — Monthly macro-gated Korean equity strategy v1

## Status
planned

## What this ticket is

C-family 의 **첫 strategy backtest ticket**. C001 v2 의 Layer 1 (매크로
foundation) 을 가장 단순한 form 으로 검증.

가설: **매크로 regime favorable 일 때 한국 시장 노출, unfavorable 일
때 cash**. Holding period = 월 단위 (C002 의 monthly R² 41% 발견 반영).

이건 STRATEGY VERIFICATION ticket. 사전 등록 5-criterion verdict.
**Quarterly horizon 으로의 fallback 사전 commit** (C002 review 의
strategic conversation 결정).

## Why this design

### Monthly horizon
C002 finding:
- Daily R² 23.57% (F-Arch-1 fail)
- **Monthly R² 41.12% (F-Arch-1 PASS)**
- Quarterly R² 47.54% (PASS)
- Weekly R² 48.74% (PASS, 하지만 사용자가 "중장기" 방향 선택)

사용자가 monthly 를 primary, quarterly 를 fallback 으로 선택.

### 3개 매크로 변수 (USDKRW + VIX + DXY)
C002 monthly R² 41% 중 거의 전부가 이 3개. 추가 5개 (US 금리 3종, BAA10Y,
USDCNY) 는 marginal. 단순성 우선.

### Strategy form V1 = top-5 by 시가총액 (when ON), cash (when OFF)
B004 (c) 의 구조 그대로 차용 (이미 검증된 implementation). 단지:
- Gate signal: KOSPI 200d SMA → **3-variable macro composite**
- Rebalance frequency: daily → **monthly**

### "한 번에 한 변수 만 변경" 정신
이전 B-family 의 holding period (3-10일) 와 gate type (price-based) 둘 다 변경됨. 둘이 함께 변경되는 게 architectural pivot 의 정의. 같은 ticket 안에서 두 변경의 효과를 분리하지 않음 — 이건 architectural redesign.

## Strategy specification

### Universe (불변)
- Dynamic Top100 + 20일 거래대금 ≥ 5억 + 거래대금추정여부 = False
- 같은 universe 가 B001-B011 통해 사용됨

### Macro gate definition (사전 등록)

매월 마지막 거래일 (signal_date T_month) 에 계산:

**Signal 1 — USDKRW yoy momentum**
```
USDKRW_yoy(T) = USDKRW(T) / USDKRW(T - 252 trading days) - 1
favorable_USDKRW(T) = USDKRW_yoy(T) <= 0  (KRW 강세 또는 안정)
```

**Signal 2 — VIX regime**
```
VIX_60d_avg(T) = mean(VIX over [T-60, T])
VIX_240d_avg(T) = mean(VIX over [T-240, T])
favorable_VIX(T) = VIX_60d_avg(T) <= VIX_240d_avg(T)  (최근 60일이 장기 평균보다 낮음)
```

**Signal 3 — DXY momentum**
```
DXY_yoy(T) = DXY(T) / DXY(T - 252) - 1
favorable_DXY(T) = DXY_yoy(T) <= 0  (USD 약세 또는 안정)
```

**Composite regime score**
```
regime_score(T) = count(favorable_USDKRW, favorable_VIX, favorable_DXY)
                  in {0, 1, 2, 3}
```

**Regime ON/OFF rule** (사전 등록):
- `regime_score(T) >= 2` → **ON** (2개 또는 3개 favorable)
- `regime_score(T) <= 1` → **OFF**

이건 "majority vote" rule. **Simple 하고 사전 등록**. 추후 deepening 에서
weighted scoring 검토 가능.

### Execution (사전 등록)

- **Signal_date**: 각 월의 마지막 KRX 거래일 종가 후 (e.g., 2025-01-31)
- **Execution_date**: 다음 월의 첫 KRX 거래일 시가 (e.g., 2025-02-01 09:00)
- **Look-ahead 방지**: macro 신호는 signal_date 종가까지의 데이터만 사용

### Position management (사전 등록)

**Regime ON 시**:
- 매월 signal_date 의 universe 에서 **시가총액 상위 5개** 선택
- 균등 비중 (각 20%)
- 다음 월 첫 거래일 시가에 매수
- 한 달 hold (다음 signal_date 까지)

**Regime OFF 시**:
- 모든 position 청산 (다음 거래일 시가)
- 다음 month signal 까지 cash

**Regime 연속 ON 시 (rebalance)**:
- 매월 시가총액 상위 5개 재계산
- 빠진 종목 청산, 새 종목 매수
- 유지된 종목은 weight 재조정

**비용**: 1.5 / 20 / 5 bps (B-family 와 동일)

## Variants

**V1 = macro_gate_mcap (primary)**: 위 specification 그대로

**V2 = kospi_buy_and_hold (comparator)**: regime 무시, 16년 내내 cap-weighted KOSPI proxy hold

**V3 = cash (sanity)**: 0% return

V1 vs V2 = "active macro gate 가 passive 보다 나은가" 의 검증.
V1 vs V3 = "strategy 가 cash 보다 나은가" 의 sanity.

## Hypothesis (사전 등록 — 5 criteria)

V1 (macro_gate_mcap) 의 verdict logic:

**H1 — Survival**: V1 cumulative net total return > 0 over 16 years
(B011 gate-only -94.79%, B010 carrier -87.8% 와 명확히 다름)

**H2 — vs KOSPI**: V1 cumulative net ≥ V2 cumulative net − 30pp
(passive KOSPI 보다 너무 badly trail 안 함; 30pp 는 reasonable
relax — active strategy 가 cost burden 가짐)

**H3 — Spike capture**: V1 net total return positive in 2010, 2025,
2026 (3개 spike year 중 최소 2개 +)

**H4 — Drawdown protection**: V1 max drawdown < V2 max drawdown by
≥ 5pp (gate 의 핵심 목적이 drawdown 완화)

**H5 — Year robustness**: V1 positive in ≥ 8 of 16 years (B011 5/16,
B010 3/16 보다 substantial 개선)

**보조 H6 — Cost efficiency**: V1 net / V1 cost-0 ≥ 0.7 (B-family 0.4
보다 명확히 개선; monthly 의 cost 절감 효과 검증)

### Verdict 결정 (사전 등록)

| 통과 | Verdict | 다음 step |
|---|---|---|
| **6/6** | **STRONG PROMOTE** | C004 = Layer 2 (sector) 진입 또는 macro v2 deepening |
| 4-5/6 | CONDITIONAL PROMOTE | 실패 dimension 진단 후 다음 step |
| 2-3/6 | INCONCLUSIVE | C004 = quarterly horizon 재검증 (pre-committed fallback) |
| 0-1/6 | KILL | architecture 재고; project 방향 strategic 대화 |
| **H1 catastrophic fail** (V1 < -50% 누적) | **KILL** | architecture 자체 의문 |

### Fallback (사전 등록)

INCONCLUSIVE 시 → **C004 = same strategy with quarterly rebalance**.
사전 commit: 이건 "결과 보고 horizon 변경" cherry-picking 이 아니라
"C003 의 pre-committed contingency".

## Reportable metrics

For each of V1, V2, V3:
1. Cumulative net total return (16년)
2. Per-year net total return (16 cells per variant)
3. Cost-0 cumulative (raw alpha)
4. Cost paid total + cost-eaten %
5. Max drawdown
6. Trade count
7. Average holding period (regime continuation 측정)
8. Year-wise positive count (H5)
9. Annualized return, vol, Sharpe
10. **Regime state log**: 매월 regime_score, ON/OFF flag, 3개 signal value

V1 specifically:
11. Spike year (2010, 2025, 2026) capture (H3)
12. Months in ON vs OFF state per year

## Output files

- `config.yaml`, `metrics.json`
- `trades.csv` (V1 only — V2/V3 trivial)
- `equity_curve.csv` (wide: V1, V2, V3)
- `monthly_year_breakdown.csv` (16년 × 3 variants)
- `monthly_regime_log.csv` (197 months × {regime_score, ON/OFF, USDKRW_yoy, VIX_60d_avg/240d, DXY_yoy})
- `verdict_summary.csv` (H1-H6 PASS/FAIL flags)
- `report.md`

## Implementation task (Codex)

Read C001 v2, C002 review, B004 (c) implementation (src/strategies/
b004_regime_gate.py) for the reusable patterns.

### Scope discipline

Touch (additive):
- `src/features/macro_regime.py` (NEW) — 위 3 signal + composite score
  를 daily/monthly 시계열로 계산
- `src/strategies/c003_monthly_macro_gate.py` (NEW) — orchestrate V1
  (macro_gate_mcap), V2 (kospi_buy_and_hold), V3 (cash)
- `src/run_experiment.py` — `experiment_id == "C003"` dispatch
- `configs/backtests/c003.yaml` (NEW)
- `tests/test_macro_regime.py` (NEW) — regime 계산의 no-look-ahead
- `tests/test_c003_strategy.py` (NEW) — sanity

**Do NOT touch**:
- `src/backtest/engine.py` — should not need any change. Verify with
  `git diff src/backtest/engine.py` empty.
- 기존 role 함수, 기존 strategy module, src/features/ 의 기존 모듈

### Engine reuse vs new code

월 단위 rebalance 는 daily engine 으로 처리 가능:
- Signal 만 매월 마지막일에 fire (다른 날은 no signal)
- 기존 engine 의 exit_on_gate_off 비슷한 메커니즘으로 regime OFF 시 일괄 exit
- 또는 monthly anchor 의 단순 wrapper

B004 (c) 의 exit_on_gate_off + B011 의 mcap selection 그대로 재사용.
Gate dates 만 새 macro composite 으로 정의.

### Configuration

`configs/backtests/c003.yaml`:

```yaml
experiment_id: C003
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
regime:
  macro_signals: [usdkrw_yoy, vix_60d_vs_240d, dxy_yoy]
  composite_rule: majority_vote
  on_threshold: 2  # >= 2 of 3 favorable
selection:
  type: market_cap_top_n
  n: 5
costs:
  commission_bps: 1.5
  tax_bps_sell:   20.0
  slippage_bps:   5.0
rebalance:
  frequency: monthly
  anchor: last_trading_day
variants:
  - macro_gate_mcap        # V1
  - kospi_buy_and_hold     # V2
  - cash                   # V3
output_dir: reports/experiments/C003_monthly_macro_gated_strategy
```

### Order of work

Commit (Claude commits) after each green-test boundary.

1. `src/features/macro_regime.py` + tests (regime 정확성 + no-look-ahead)
2. `src/strategies/c003_monthly_macro_gate.py` + dispatcher + config
3. `tests/test_c003_strategy.py` (synthetic mini-panel sanity)
4. Run C003 real-panel
5. Verify engine.py untouched

### Completion criteria

- pytest fully green (currently 167)
- All 3 variants reported in metrics.json
- engine.py untouched (git diff empty)
- Final message reports:
  - V1 cumulative net (16yr): __ percent
  - V2 KOSPI BH cumulative: __ percent (caveat: cap-weighted dynamic top-100 survivor-biased; for proper context, also note B011's V1 gate-only-mcap = -94.79%)
  - V1 max DD: __ percent ; V2 max DD: __ percent
  - V1 positive years: __ of 16
  - V1 in 2010 / 2025 / 2026: __ / __ / __ (H3)
  - V1 net / V1 cost-0 ratio: __ percent (H6)
  - V1 annualized return: __ percent ; Sharpe: __
  - Regime ON share over 16 years: __ percent

If any ambiguity, write to `research/experiments/C003_codex_questions.md` and stop.

### Out of scope

- ❌ Sector layer (그건 다음 ticket)
- ❌ Stock-level signals (B-family flow signals 등)
- ❌ Different macro variable sets (그건 macro v2 deepening)
- ❌ Different rebalance frequencies (monthly 만, quarterly 는 fallback ticket)
- ❌ Engine changes
- ❌ Position sizing 변화 (균등만)

## Result summary
DO NOT FILL until backtest complete.

## Claude review
DO NOT FILL until result files are read.
