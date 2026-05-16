# C018 — Macro v15 (+ US M2 money supply growth)

## Status
planned

## What this ticket is

C017 KR exports fail (-42pp, wrong direction). Phase C Korean
variables exhausted (3 dropped: KR CPI 0, KR exports -42, prior KR3m 0).

Pivot: **Fed liquidity dimension**. 직접적인 monetary 환경 변수. 기존
8 vars 모두 가격/금리/sentiment dimension. **Liquidity 는 다른 channel**.

C018 = **C014 v11 carrier + US M2 yoy growth**. 9-var composite.

## Single change

| 변수 | C014 v11 | **C018 v15** |
|---|---|---|
| Macro vars | 8 | **+ US M2 (9)** |
| Threshold | ≥ 2 of 8 | **≥ 2 of 9** |

## New variable

### Signal 9 — US M2 yoy growth

**Mechanism (사전 commit)**:
> US M2 money supply 는 Fed liquidity 의 가장 직접 척도. QE 시기
> (2009-2014, 2020-2021) M2 폭증, QT 시기 (2022-2024) M2 감속.
>
> 메커니즘:
> - M2 성장 가속 → 글로벌 liquidity 확장 → risk asset (EM 포함) 매수
>   → 한국 favorable
> - M2 성장 감속 → liquidity 축소 → EM 자본 회수 → 한국 부정적
>
> 기존 변수와 다른 dimension:
> - CPI/PPI = 가격 측면
> - Curve / KR10y = 금리 측면
> - VIX/USDKRW/DXY = sentiment/FX 측면
> - Brent = commodity
> - **M2 = pure liquidity 양적 측면**
>
> 특히 **2010-2014 QE 시기**의 환경 capture 가능성 — pre-2018 -8%
> 의 가장 큰 chance.

**Formula** (yoy growth):
```
m2_yoy(T) = M2(T) / M2(T - 12 months) - 1
favorable_m2(T) = m2_yoy(T) >= 0.05  (연 5% 이상 성장 = expansionary)
```

**Threshold 5%**: M2 growth 의 long-run average 가 ~5-7%. 5% 이상 =
expansionary. Pre-register. Tuning 금지.

또는 simpler: `favorable iff m2_yoy >= m2_yoy(T-12 months)` (가속)
Let me use the absolute threshold (5%) for simpler interpretation.
가속 보다 절대 수준이 macro story 와 더 align.

### Composite (9-var, NOT including failed variables)

```
regime_score = count favorable in
  {USDKRW, VIX, DXY, curve, Brent, KR10y, US_CPI, US_PPI, US_M2}
ON iff score >= 2
```

## Data status

`fred_us_m2.csv` already downloaded:
- FRED `M2SL` (M2 Money Stock SA)
- Monthly, 1959-2026-03 (195 obs)

## Hypothesis (사전 등록)

H1-H6 inherited.

### H7: US M2 informativeness
- V1 v15 cumulative net ≥ V1 v11 (C014) + **5pp**

### H8: Subperiod (가장 중요 — QE era 2010-2014 capture 가능성)
- 2010-2017 net ≥ 0 (현 C014 -8%)
- 2018-2026 net 유지

### H9: M2 correlations
- M2 vs US CPI decel
- M2 vs curve
- M2 vs USDKRW

## Verdict logic (사전 등록)

기존 pattern 동일. H7 PASS면 carrier 채택, FAIL면 dropped + C019 진행.

## Reportable metrics

기존 + M2 specific:
1. Full + subperiod cumulative
2. (V1 v15 - V1 v11) per-year delta
3. M2 favorable quarters
4. M2 yoy 시계열 (QE / QT 시기 분포)
5. M2 correlations (H9)
6. H1-H7 + H8 + H9

## Implementation task

기존 pattern. macro_factors + macro_regime additive, c018 strategy
module, dispatcher, config, tests.

### Configuration

```yaml
experiment_id: C018
regime:
  macro_signals:
    - usdkrw_yoy
    - vix_60d_vs_240d
    - dxy_yoy
    - us_2_10_curve
    - brent_yoy
    - kr10y_yoy_change
    - us_cpi_decel
    - us_ppi_decel
    - us_m2_yoy  # NEW
  composite_rule: count_favorable
  on_threshold: 2  # >= 2 of 9
output_dir: reports/experiments/C018_macro_v15_us_m2
```

### Completion criteria

기존 pattern. Final message reports H7/H8/H9 + M2 specific.

If ambiguity, write C018_codex_questions.md.

### Out of scope

- ❌ 다른 변수 동시 추가
- ❌ Selection / threshold / rebalance 변경

## Result summary
DO NOT FILL until backtest complete.

## Claude review
DO NOT FILL until result files are read.
