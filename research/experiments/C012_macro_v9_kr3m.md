# C012 — Macro v9 (+ Korean 3-month interbank rate)

## Status
planned

## What this ticket is

Phase A 세 번째 ticket. C011 (KR 10y) PASS 후 Korean rates 의 다른
curve point 시도. KR 3m (단기 시장 rate) 가 KR 10y (장기 yield) 와
다른 정보 갖는지 검증.

C012 = **C011 v8 carrier + KR 3m**. 7-var composite.

## Carrier base = C011 v8 (KR10y 포함)

KR 10y 는 C011 에서 PASS — carrier 에 유지. KR 3m 는 다른 curve point
(money market) 라 추가 정보 가능성.

## Single change

| 변수 | C011 v8 | **C012 v9** |
|---|---|---|
| Macro variables | USDKRW + VIX + DXY + curve + Brent + KR10y (6개) | **+ KR3m (7개)** |
| Composite threshold | ≥ 2 of 6 | **≥ 2 of 7** |

## New variable

### Signal 7 — KR 3-month interbank rate (Korean short-term money market)

**Mechanism (사전 commit)**:
> KR 3m 는 short-term money market rate (~BOK 정책금리에 가까움).
> KR 10y 는 장기 yield (시장 기대값 + term premium).
>
> **두 변수의 차이**:
> - KR 10y - KR 3m = Korean yield curve spread (recession indicator)
> - KR 3m 단독 = 단기 monetary stance (BOK 정책 cycle 반영)
>
> 가설: KR 3m 하락 = monetary easing = 단기 stock favorable.
> 상승 = tightening = 부정적.
>
> KR 3m 와 KR 10y 가 너무 상관 높으면 (>0.7) 추가 가치 적을 것. H9 측정.

**Formula** (change, percentage points):
```
kr3m_yoy_change(T) = KR3M(T) - KR3M(T - 12 months)
favorable_kr3m(T) = kr3m_yoy_change(T) <= 0  (단기 rate 하락 또는 안정)
```

### Composite (7-var)

```
regime_score(T) = count favorable in {USDKRW, VIX, DXY, curve, Brent, KR10y, KR3m}
ON iff score >= 2
```

## Data status

`fred_kr3m.csv` already downloaded:
- FRED `IR3TIB01KRM156N` (3-month interbank rate Korea)
- 1991-2026 monthly, 196 obs in our window

## Hypothesis (사전 등록)

H1-H6 inherited.

### H7: KR 3m informativeness
- V1 v9 cumulative net ≥ V1 v8 (C011) + **5pp** → KR 3m informative
- 0 ~ +5pp → marginal
- < 0pp → noise

### H8: Subperiod robustness
- V1 v9 subperiod 2010-2017 net 개선 (C011 -21% 보다 좋게)
- V1 v9 subperiod 2018-2026 net ≥ 0 유지

### H9: KR 3m correlations
- KR 3m yoy change vs KR 10y yoy change correlation (curve shape)
- KR 3m yoy change vs DGS3MO (US 3m) change correlation (글로벌 short rate 동조)
- 둘 다 > 0.7 면 KR 3m 가 redundant

## Verdict logic (사전 등록)

| 통과 | Verdict | 다음 step |
|---|---|---|
| H7 PASS + 두 subperiod ≥ 0 | STRONG PROMOTE (v9) + robust | **첫 robust strategy. C013 = Phase B (US CPI) 진입** |
| H7 PASS + 한쪽만 ≥ 0 | CONDITIONAL PROMOTE | C013 = Phase B 진입, KR 3m 유지 |
| H7 FAIL (< +5pp) but pre-2018 개선 | INCONCLUSIVE | C013 = Phase B, KR 3m 유지 검토 |
| H7 FAIL + pre-2018 no change | KR 3m redundant | C013 = Phase B, KR 3m dropped |
| H1 catastrophic | KILL | architecture 재고 |

어느 경우든 C013 진행 (Phase B 진입). KR 3m 의 carrier 채택 여부만 결정.

## Reportable metrics

C011 pattern + KR 3m specific:
1. Full + subperiod cumulative (net, cost-0)
2. (V1 v9 - V1 v8) per-year delta
3. KR 3m favorable quarters
4. KR 3m - KR 10y change correlation (H9)
5. KR 3m - US 3m (DGS3MO) change correlation
6. KR 3m - BOK policy 변화 시기 정성 비교 (있으면)
7. H1-H7 + H8/H9 summary

## Implementation task

### Scope discipline

Touch (additive):
- `src/data/macro_factors.py` — ADD kr3m series spec
- `src/features/macro_regime.py` — ADD kr3m_yoy_change signal + 7-var
  composite (preserve all existing variants)
- `src/strategies/c012_quarterly_macro_v9.py` (NEW)
- `src/run_experiment.py` — C012 dispatch
- `configs/backtests/c012.yaml` (NEW)
- `tests/test_macro_factors_loading.py` — ADD kr3m loading test
- `tests/test_macro_regime.py` — ADD kr3m signal test
- `tests/test_c012_strategy.py` (NEW)

**Do NOT touch**:
- engine.py
- 기존 strategy modules (a001-a004, b001-b011, c003-c011)
- 기존 features 모듈 except macro_regime additions
- research_input_data/

### Configuration

```yaml
experiment_id: C012
# (C011 와 동일 except)
regime:
  macro_signals:
    - usdkrw_yoy
    - vix_60d_vs_240d
    - dxy_yoy
    - us_2_10_curve
    - brent_yoy
    - kr10y_yoy_change
    - kr3m_yoy_change  # NEW
  composite_rule: count_favorable
  on_threshold: 2  # >= 2 of 7

selection:
  type: market_cap_top_n
  n: 5

output_dir: reports/experiments/C012_macro_v9_kr3m
```

### Completion criteria

Final message reports:
- V1 v9 cumulative net + cost-0 (vs C011 v8: +55.00 net, +83.35 cost-0)
- Delta v9 - v8 net + cost-0 (H7)
- Subperiod 2010-2017 V1 v9 net + cost-0 (H8 — vs C011 v8 -21.48% / -15.84%)
- Subperiod 2018-2026 V1 v9 net + cost-0
- V1 max DD, positive years, Sharpe, annualized
- Regime ON share (vs C011 86.89%)
- KR 3m favorable quarters
- KR 3m vs KR 10y correlation (H9)
- KR 3m vs US 3m correlation (H9)
- H1-H7 + H8 + H9 summary

If ambiguity, write to research/experiments/C012_codex_questions.md and stop.

### Out of scope

- ❌ 다른 매크로 변수 동시 추가
- ❌ Selection, threshold, rebalance 변경
- ❌ Copper, USDCNY (둘 다 이미 dropped)

## Result summary
DO NOT FILL until backtest complete.

## Claude review
DO NOT FILL until result files are read.
