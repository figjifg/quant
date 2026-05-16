# C013 — Macro v10 (+ US CPI 인플레이션 deceleration)

## Status
planned

## What this ticket is

**Phase B 첫 ticket**. Phase A 종료 (KR 10y adopted, copper + KR 3m
dropped). 사용자 명시: "외국인이라 불리는 이들이 참고할 만한 데이터
들" — US 경제 지표.

US CPI = Fed 의사결정의 primary 변수. 외국인 자본의 EM allocation
결정의 중심 driver.

C013 = **C011 v8 carrier + US CPI deceleration**. 7-var composite.

## Carrier base = C011 v8

C012 의 KR 3m fail 로 carrier 그대로 유지.

## Single change

| 변수 | C011 v8 | **C013 v10** |
|---|---|---|
| Macro vars | 6 (incl KR10y) | **+ US CPI yoy decel (7)** |
| Threshold | ≥ 2 of 6 | **≥ 2 of 7** |

## New variable

### Signal 7 — US CPI inflation deceleration

**Mechanism (사전 글로 commit)**:
> US CPI 가 Fed 의사결정의 primary 변수. 외국인 EM 자본 흐름의 가장 큰
> driver:
> - CPI 인플레이션 가속 → Fed hawkish (긴축 빠르게) → EM 자본 회수 →
>   한국 부정적
> - CPI 인플레이션 감속 → Fed dovish 기대 → EM 자본 유입 → 한국
>   favorable
>
> 기존 6 변수 모두 가격/금리/sentiment dimension. CPI 는 **inflation
> dynamics 의 직접 신호** — 진정으로 다른 dimension.
>
> 가설: CPI yoy 감속 = stock favorable (Fed dovish path 기대).
> 가속 = unfavorable.

**Formula** (yoy deceleration):
```
cpi_yoy(T) = CPI(T) / CPI(T-12 months) - 1  # 인플레이션율
cpi_decel(T) = cpi_yoy(T) - cpi_yoy(T-12 months)  # yoy 의 yoy 변화
favorable_cpi(T) = cpi_decel(T) <= 0  (인플레이션 감속 또는 안정)
```

**상대 측정**. 절대 threshold 사용 안 함 (시대마다 inflation regime
다름 — 1970s vs 2010s vs 2022).

### Composite (7-var, NOT including KR 3m or copper)

```
regime_score(T) = count favorable in
  {USDKRW, VIX, DXY, curve, Brent, KR10y, CPI_decel}
ON iff score >= 2
```

## Data status

`fred_us_cpi.csv` already downloaded:
- FRED `CPIAUCSL` (CPI All Urban Consumers SA)
- 1947-2026 monthly, 196 obs in window
- Schema: observation_date, CPIAUCSL

## Hypothesis (사전 등록)

H1-H6 inherited.

### H7: US CPI deceleration informativeness
- V1 v10 cumulative net ≥ V1 v8 (C011) + **5pp**
- < +5pp → marginal or noise

### H8: Subperiod robustness (계속 critical)
- 2010-2017 net ≥ 0 (**이게 진짜 진전 지표** — 현 C011 -21%)
- 2018-2026 net ≥ 0 유지 (현 +97%)

### H9: CPI correlation
- CPI yoy vs curve change correlation
- CPI yoy vs USDKRW correlation
- CPI yoy vs Brent correlation (Brent → inflation pass-through)
- > 0.7 면 redundant

## Verdict logic (사전 등록)

| 통과 | Verdict | 다음 step |
|---|---|---|
| H7 PASS + 두 subperiod ≥ 0 | STRONG PROMOTE (v10) — **첫 진짜 robust** | C014 = + US PPI (Phase B 계속) |
| H7 PASS + 한쪽만 ≥ 0 | CONDITIONAL PROMOTE | C014 진행 |
| H7 FAIL + 2010-2017 개선 | INCONCLUSIVE | C014 진행, CPI 유지 검토 |
| H7 FAIL + pre-2018 no change | CPI redundant | C014 진행, CPI dropped |
| H1 catastrophic | KILL | architecture 재고 |

## Reportable metrics

기존 pattern + CPI specific:
1. Full + subperiod cumulative net + cost-0
2. (V1 v10 - V1 v8) per-year delta
3. CPI favorable quarters
4. CPI vs other macro 상관관계 (H9)
5. 2008-2009 GFC 시기, 2022 inflation spike 시기 의 CPI 신호 정성 진단
6. H1-H7 + H8 + H9 summary

## Implementation task

### Scope discipline

Touch (additive):
- `src/data/macro_factors.py` — ADD US CPI series spec (monthly)
- `src/features/macro_regime.py` — ADD cpi_decel signal + 7-var-with-cpi
  composite (NOT with copper or kr3m). Preserve all variants.
- `src/strategies/c013_quarterly_macro_v10.py` (NEW)
- `src/run_experiment.py` — C013 dispatch
- `configs/backtests/c013.yaml` (NEW)
- `tests/test_macro_factors_loading.py` — ADD CPI loading
- `tests/test_macro_regime.py` — ADD CPI deceleration test
- `tests/test_c013_strategy.py` (NEW)

**Do NOT touch**:
- engine.py, existing strategy modules, existing features (except
  macro_regime additions)
- research_input_data/

### Configuration

```yaml
experiment_id: C013
regime:
  macro_signals:
    - usdkrw_yoy
    - vix_60d_vs_240d
    - dxy_yoy
    - us_2_10_curve
    - brent_yoy
    - kr10y_yoy_change
    - us_cpi_decel  # NEW
  composite_rule: count_favorable
  on_threshold: 2  # >= 2 of 7
output_dir: reports/experiments/C013_macro_v10_us_cpi
# 나머지 동일
```

### Completion criteria

Final message reports:
- V1 v10 cumulative net + cost-0 (vs C011 v8: +55.00 net, +83.35 cost-0)
- Delta v10 - v8 net + cost-0 (H7)
- Subperiod 2010-2017 + 2018-2026 (H8) net + cost-0
- V1 max DD, positive years, Sharpe
- CPI favorable quarters
- CPI vs Brent / curve / USDKRW / other 상관관계 (H9)
- 2022 inflation spike 시기의 ON/OFF 가 어떻게 변했나
- H1-H7 + H8 + H9 summary

If ambiguity, write C013_codex_questions.md and stop.

### Out of scope

- ❌ 다른 매크로 변수 동시 추가
- ❌ Selection, threshold, rebalance 변경
- ❌ Copper, USDCNY, KR3m (모두 dropped)

## Result summary
DO NOT FILL until backtest complete.

## Claude review
DO NOT FILL until result files are read.
