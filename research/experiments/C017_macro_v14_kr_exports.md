# C017 — Macro v14 (+ Korean Exports growth)

## Status
planned

## What this ticket is

Phase C 두 번째. C016 KR CPI fail (US CPI corr 0.83 redundant).
한국 specific 이되 inflation 외 dimension 시도: **한국 수출 성장률**.

한국 수출 = 반도체 + 자동차 + 화학 등 manufacturing 의 직접 지표.
KOSPI 의 가장 fundamental driver 중 하나 (한국 GDP 의 ~40% 가 수출).

C017 = **C014 v11 carrier + KR Exports yoy growth**. 9-var composite.

## Single change

| 변수 | C014 v11 | **C017 v14** |
|---|---|---|
| Macro vars | 8 | **+ KR exports (9)** |
| Threshold | ≥ 2 of 8 | **≥ 2 of 9** |

## New variable

### Signal 9 — Korean Exports yoy growth

**Mechanism (사전 commit)**:
> 한국 = export 중심 경제 (GDP 의 ~40% 수출). 한국 수출 ≈ 글로벌
> manufacturing demand × 한국 경쟁력. KOSPI 시가총액 ~25% 가 반도체
> (Samsung + Hynix) 인데 이들이 수출의 큰 비중.
>
> 외국인이 한국 시장 보는 view:
> - 수출 호조 → 한국 기업 이익 호조 → KOSPI favorable
> - 수출 부진 → 한국 기업 이익 부진 → KOSPI 부정적
>
> 기존 macro 변수들 (FX, rates, inflation, commodity) 와 다른 dimension:
> **real economy / Korean fundamental**. CPI/PPI 는 가격 측면, KR 수출
> 은 quantity 측면.

**Formula** (yoy growth):
```
exports_yoy(T) = exports(T) / exports(T - 12) - 1
favorable_kr_exports(T) = exports_yoy(T) >= 0  (성장 또는 보합)
```

**Sign**: growth 가 favorable. Brent (가격 안정/하락 favorable) 와
반대 방향이지만 fundamental 신호라 자연스럽다.

### Composite (9-var)

```
regime_score = count favorable in
  {USDKRW, VIX, DXY, curve, Brent, KR10y, US_CPI, US_PPI, KR_exports}
ON iff score >= 2
```

## Data status

`fred_kr_exports.csv` already downloaded:
- FRED `XTEXVA01KRM664S` (Korea Exports of Goods, Value)
- Monthly, 1957-2026-03 (195 obs in window)
- Schema: observation_date, XTEXVA01KRM664S

## Hypothesis (사전 등록)

H1-H6 inherited from C014.

### H7: KR Exports informativeness
- V1 v14 cumulative net ≥ V1 v11 (C014) + **5pp**

### H8: Subperiod (계속 critical, pre-2018 -8% 정체)
- 2010-2017 net ≥ 0
- 2018-2026 net 유지

### H9: KR Exports correlations
- KR Exports yoy vs Brent yoy correlation (commodity → demand pass-through)
- KR Exports yoy vs USDKRW correlation (export competitiveness via FX)
- KR Exports yoy vs US CPI/PPI correlation

## Verdict logic (사전 등록)

| 통과 | Verdict | 다음 |
|---|---|---|
| H7 PASS + 두 subperiod ≥ 0 | STRONG PROMOTE | C018 = next variable (Phase C 계속 또는 D) |
| H7 PASS + 한쪽만 | CONDITIONAL PROMOTE | C018 진행 |
| H7 FAIL + pre-2018 ≥ 0 | INCONCLUSIVE + helps pre-2018 | C018, exports 유지 |
| H7 FAIL + pre-2018 no change | exports redundant or low-info | C018, exports dropped |
| H1 catastrophic | KILL | architecture 재고 |

## Implementation task

기존 pattern. macro_factors + macro_regime additive, new strategy
module, dispatcher, config, tests.

### Configuration

```yaml
experiment_id: C017
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
    - kr_exports_yoy  # NEW
  composite_rule: count_favorable
  on_threshold: 2  # >= 2 of 9
output_dir: reports/experiments/C017_macro_v14_kr_exports
```

### Completion criteria

- pytest fully green (currently 221)
- engine.py untouched
- Final message:
  - V1 v14 net + cost-0 (vs C014 v11)
  - Delta v14 - v11 net + cost-0 (H7)
  - Subperiod 2010-2017 + 2018-2026 (H8)
  - V1 max DD, positive years, Sharpe, annualized
  - Regime ON share
  - KR exports favorable quarters
  - KR exports vs Brent / USDKRW / US CPI / US PPI 상관관계 (H9)
  - H1-H7 + H8 + H9 summary

If ambiguity, write C017_codex_questions.md.

### Out of scope

- ❌ 다른 변수 동시 추가
- ❌ Selection / threshold / rebalance / engine 변경

## Result summary
DO NOT FILL until backtest complete.

## Claude review
DO NOT FILL until result files are read.
