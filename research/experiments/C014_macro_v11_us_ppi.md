# C014 — Macro v11 (+ US PPI deceleration)

## Status
planned

## What this ticket is

Phase B 두 번째. C013 (US CPI) PASS + 2010-2017 큰 개선 (-21% → -8%).
US PPI 가 추가 inflation dimension (Producer side vs Consumer side)
가치 있는지 검증.

C014 = **C013 v10 carrier + US PPI**. 8-var composite.

## Single change

| 변수 | C013 v10 | **C014 v11** |
|---|---|---|
| Macro vars | 7 (incl CPI) | **+ US PPI (8)** |
| Threshold | ≥ 2 of 7 | **≥ 2 of 8** |

## New variable

### Signal 8 — US PPI deceleration

**Mechanism**:
> PPI (Producer Price Index) 는 inflation pipeline 의 upstream:
> producer → wholesale → consumer (CPI). PPI 가 CPI 의 leading
> indicator. 일반적으로 PPI 가 먼저 움직이고 CPI 가 따라옴.
>
> **CPI 와의 차이점**:
> - CPI = Fed's primary policy 변수
> - PPI = inflation pipeline 의 earlier 신호 + commodity 가격 직접
>   반영 (CPI 는 housing, services 더 큼)
>
> 가설: PPI 와 CPI 가 비슷한 방향. 둘 다 deceleration = favorable.
> 그러나 PPI 가 더 변동성 크고 commodity sensitive.
>
> Risk: PPI 와 CPI 의 correlation 이 너무 높으면 (>0.7) redundant.

**Formula** (deceleration):
```
ppi_yoy(T) = PPI(T) / PPI(T-12) - 1
ppi_decel(T) = ppi_yoy(T) - ppi_yoy(T-12)
favorable_ppi(T) = ppi_decel(T) <= 0
```

### Composite (8-var)

```
regime_score = count favorable in
  {USDKRW, VIX, DXY, curve, Brent, KR10y, CPI, PPI}
ON iff score >= 2
```

## Data status

`fred_us_ppi.csv` already downloaded (FRED PPIACO, 1913-2026 monthly).

## Hypothesis (사전 등록)

H1-H6 inherited.

### H7: PPI informativeness
- V1 v11 cumulative net ≥ V1 v10 (C013) + **5pp**

### H8: Subperiod (continue critical)
- 2010-2017 net ≥ 0 (C013 -8%, close to zero — PPI 가 push 가능?)
- 2018-2026 net ≥ 0 유지

### H9: PPI correlations
- **PPI vs CPI 상관관계** (가장 중요 — 0.7+ 면 redundant)
- PPI vs Brent (PPI 가 commodity sensitive)
- PPI vs DXY

## Verdict logic (사전 등록)

| 통과 | Verdict | 다음 |
|---|---|---|
| H7 PASS + 두 subperiod ≥ 0 | **STRONG PROMOTE + 첫 robust strategy** | C015 = US NFP (Phase B 계속) |
| H7 PASS + 한쪽만 | CONDITIONAL PROMOTE | C015 진행 |
| H7 FAIL but 2010-2017 ≥ 0 | INCONCLUSIVE + helps pre-2018 | C015 진행, PPI 유지 검토 |
| H7 FAIL + pre-2018 no change | PPI redundant w/ CPI 가능 | C015 진행, PPI dropped |
| H1 catastrophic | KILL | architecture 재고 |

어느 verdict 든 C015 진행.

## Implementation task

기존 pattern:
- ADD ppi series to macro_factors
- ADD ppi_decel signal + 8-var composite to macro_regime
- NEW c014 strategy module
- Tests + dispatcher + config

**Do NOT touch**: engine.py, existing strategy modules, existing features (except macro_regime additions).

### Configuration

```yaml
experiment_id: C014
regime:
  macro_signals:
    - usdkrw_yoy
    - vix_60d_vs_240d
    - dxy_yoy
    - us_2_10_curve
    - brent_yoy
    - kr10y_yoy_change
    - us_cpi_decel
    - us_ppi_decel  # NEW
  composite_rule: count_favorable
  on_threshold: 2  # >= 2 of 8
output_dir: reports/experiments/C014_macro_v11_us_ppi
# 나머지 동일
```

### Completion criteria

- pytest fully green (currently 205)
- engine.py untouched
- Final message:
  - V1 v11 cumulative net + cost-0 (vs C013 v10: +81.29 / +112.34)
  - Delta v11 - v10 net + cost-0 (H7)
  - Subperiod 2010-2017 V1 v11 net + cost-0 (H8, vs C013 -8.16 / -2.53)
  - Subperiod 2018-2026
  - V1 max DD, positive years, Sharpe
  - Regime ON share (C013 was 81.97 percent)
  - PPI favorable quarters
  - **PPI vs CPI correlation** (H9 most important)
  - PPI vs Brent / DXY correlations
  - H1-H7 + H8 + H9 summary

If ambiguity, write C014_codex_questions.md.

### Out of scope

- ❌ 다른 변수 동시 추가
- ❌ Selection / threshold / rebalance 변경

## Result summary
DO NOT FILL until backtest complete.

## Claude review
DO NOT FILL until result files are read.
