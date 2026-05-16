# C011 — Macro v8 (+ Korean 10y treasury yield)

## Status
planned

## What this ticket is

Phase A 두 번째 ticket. C010 (copper) fail 후 Korean rates dimension
시도. 사용자 명시: "원자재랑 한국 채권 금리 쪽을 안 다뤘으니". Copper
는 fail (Brent 와 redundant), 한국 채권은 진정으로 다른 dimension
(Korean monetary policy).

C011 = **C008 v6 carrier (NOT v7, copper 제외) + KR 10y yield**. 6-var
composite (copper 자리에 KR10y 대체).

## Carrier base 명시

- **Base = C008 v6** (5 vars: USDKRW + VIX + DXY + curve + Brent)
- **NOT C010 v7** (copper 추가했지만 fail, dropped)
- Copper 는 hypothesis space 에서 dropped (corr w/ Brent 0.70 = redundant)

## Single change

| 변수 | C008 v6 | **C011 v8** |
|---|---|---|
| Macro variables | USDKRW + VIX + DXY + curve + Brent (5) | **+ KR10y (6)** |
| Composite threshold | ≥ 2 of 5 | **≥ 2 of 6** (same absolute) |
| Selection | top-5 mcap | unchanged |
| Rebalance | quarterly | unchanged |

## New variable specification

### Signal 6 — KR 10y treasury yield (Korean rates dimension)

**Mechanism (사전 글로 commit)**:
> KR 10y treasury yield 은 한국 자국 monetary 환경 + 시장의 한국 macro
> 기대값을 반영. 기존 5 변수 모두 글로벌 / US 중심:
> - USDKRW = USD/KRW pair (USD 측면 더 큼)
> - VIX = US risk
> - DXY = US 강도
> - US curve = US recession risk
> - Brent = 글로벌 commodity
>
> **KR 10y 는 진정으로 Korean-domestic dimension** — BOK 통화정책 +
> Korean 경기 기대값 + Korean fiscal 상황 + Korean credit risk
> 종합 반영. 외국인 자본 입장에서도 한국 자산 비용 (yield) 의 기준.
>
> 가설: KR 10y yield 하락 = 통화 완화 / 경기 부진 우려 / 안전자산
> 선호 — 단기는 보통 stock favorable (할인율 ↓). 상승 = 통화 긴축
> / 경기 회복 / 인플레 압력 — 일반적으로 stock 부정적 (할인율 ↑).
>
> 다만 yield 상승이 "growth recovery 신호" 일 수도 있음. 가설은
> "단기 rate ↓ = 단기 stock favorable" 의 conventional 입장.

**Formula** (yield CHANGE — return 아니라 단위 변화):
```
kr10y_yoy(T) = KR10Y(T) - KR10Y(T - 12 months)  # percentage points change
favorable_kr10y(T) = kr10y_yoy(T) <= 0  (yield 하락 또는 안정)
```

**중요**: yoy 가 RETURN ratio 아닌 CHANGE (단위: percentage points).
3.5% 에서 3.0% 면 -0.5 pp (favorable). Brent yoy 와는 다른 type.

### Composite (사전 등록)

```
regime_score(T) = count favorable in {USDKRW, VIX, DXY, curve, Brent, KR10y}
ON iff score >= 2
```

Threshold same absolute.

## Data status — Claude 가 사용자 승인 후 직접 다운로드

KR 10y data already downloaded:
- Path: `research_input_data/inputs/macro_features/fred_kr10y.csv`
- Source: FRED series `IRLTLT01KRM156N` (Long-Term Government Bond Yields,
  10-year, Korea)
- Frequency: monthly
- Coverage: 2000-10-01 ~ 2026-04-01 (196 monthly observations in 2010-2026)
- Schema: `observation_date, IRLTLT01KRM156N`

Monthly granularity 처리: copper 와 동일 패턴.

## Hypothesis (사전 등록)

H1-H6 inherited from C008.

### H7 (NEW): KR 10y informativeness
- V1 v8 cumulative net ≥ V1 v6 (C008) + **5pp** → KR 10y informative
- 0 ~ +5pp → marginal
- < 0pp → noise or wrong direction

### H8 — Subperiod robustness (continued)
- V1 v8 subperiod 2010-2017 net ≥ 0 (이게 ‼중요한 진전 지표)
- V1 v8 subperiod 2018-2026 net ≥ 0

C008 v6 의 가장 큰 약점이 2010-2017 -27%. KR 10y 같은 한국 domestic
변수가 이 시기를 개선할 가능성 가장 큼.

### H9 — KR 10y correlation
KR 10y yoy 와:
- US 10y yield change 의 상관관계 (글로벌 rate trend 와 얼마나 align)
- USDKRW yoy 상관관계 (currency vs rate)

## Verdict logic (사전 등록)

| 통과 | Verdict | 다음 step |
|---|---|---|
| H7 PASS + 두 subperiod ≥ 0 | **STRONG PROMOTE (v8)** | C012 = + 한국 정책금리 (Phase A 마무리) |
| H7 PASS + 한쪽만 ≥ 0 | CONDITIONAL PROMOTE | C012 진행 |
| H7 FAIL (< +5pp) but 2010-2017 ≥ 0 | INCONCLUSIVE + KR 10y helps pre-2018 | C012 진행, KR 10y 유지 검토 |
| H7 FAIL + 2010-2017 still < 0 | KR 10y 가 informative 아님 | C012 진행, KR 10y dropped |
| H1 catastrophic (cumul < -20%) | KILL signal candidate | architecture 재고 |

Per user directive: 어느 경우든 C012 진행. KR 10y 만 carrier 채택 여부가 결정사항.

## Reportable metrics

C010 pattern 동일 + KR 10y 특정:
1. Full + subperiod cumulative net + cost-0
2. Per-year breakdown + (v8 - v6) delta
3. KR 10y favorable quarters
4. **KR 10y - US 10y yield change correlation** (H9)
5. **KR 10y - USDKRW correlation**
6. Max DD, Sharpe (full + subperiod)
7. Regime ON share
8. H1-H7 + H8/H9 summary

## Implementation task (Codex)

### Scope discipline

Touch (additive):
- `src/data/macro_factors.py` — ADD kr10y series spec (filename=
  'fred_kr10y.csv', fred_series='IRLTLT01KRM156N', frequency='monthly')
- `src/features/macro_regime.py` — ADD kr10y_yoy signal + 6-var-with-
  kr10y composite. **Note**: yoy is CHANGE in percentage points,
  not return ratio. favorable iff ≤ 0 (yield declining/stable).
  6-var composite 가 v7 (with copper) 와 다름. Preserve all variants.
- `src/strategies/c011_quarterly_macro_v8.py` (NEW) — clone of c008
  with 6-var-with-kr10y config (no copper)
- `src/run_experiment.py` — `experiment_id == "C011"` dispatch
- `configs/backtests/c011.yaml` (NEW)
- `tests/test_macro_factors_loading.py` — ADD kr10y loading test
- `tests/test_macro_regime.py` — ADD kr10y signal test (change formula,
  no look-ahead, monthly-quarterly alignment)
- `tests/test_c011_strategy.py` (NEW)

**Do NOT touch**:
- engine.py, existing strategy modules (a001-a004, b001-b011, c003-c010),
  existing features modules (relative_flow, flow_ratios, regime,
  kospi_proxy)
- research_input_data/ (kr10y csv 이미 있음)

### Configuration

`configs/backtests/c011.yaml`:

```yaml
experiment_id: C011
# panels, market_breadth_csv, macro_data_dir, period, universe,
# costs, rebalance: 모두 C008/C010 와 동일

regime:
  macro_signals:
    - usdkrw_yoy
    - vix_60d_vs_240d
    - dxy_yoy
    - us_2_10_curve
    - brent_yoy
    - kr10y_yoy_change  # NEW; copper excluded (dropped)
  composite_rule: count_favorable
  on_threshold: 2  # >= 2 of 6

selection:
  type: market_cap_top_n
  n: 5

variants:
  - macro_gate_mcap
  - kospi_buy_and_hold
  - cash
output_dir: reports/experiments/C011_macro_v8_kr10y
```

### Completion criteria

Final message reports:
- V1 v8 cumulative net: __ percent (vs C008 v6 +36.98%)
- V1 v8 cost-0 cumulative: __ percent (vs +59.82%)
- Delta v8 - v6 net: __ pp (H7)
- Delta v8 - v6 cost-0: __ pp
- **Subperiod 2010-2017 V1 v8 net: __ percent (H8 — most important)**
- **Subperiod 2018-2026 V1 v8 net: __ percent**
- Subperiod cost-0 둘 다
- V1 max DD, Sharpe
- KR 10y favorable quarters
- KR 10y change vs US 10y change correlation
- KR 10y vs USDKRW correlation
- H1-H7 + H8/H9 summary

If ambiguity, write to research/experiments/C011_codex_questions.md and stop.

### Out of scope

- ❌ Copper (dropped per C010 fail)
- ❌ 다른 매크로 변수 동시 추가
- ❌ Selection, threshold, rebalance, engine 변경

## Result summary
DO NOT FILL until backtest complete.

## Claude review
DO NOT FILL until result files are read.
