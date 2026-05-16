# C015 — Macro v12 (+ US Unemployment Rate)

## Status
planned

## What this ticket is

Phase B 세 번째. C013 (CPI) + C014 (PPI) 둘 다 PASS, 누적 trajectory
strong (+37 → +55 → +81 → +111). Pre-2018 -8% 여전 (CPI/PPI 가 2010-2017
은 미해결).

US labor market 신호가 진정으로 새 dimension (Fed 의 dual mandate 중
하나, 고용 측면) — pre-2018 환경 capture 가능성.

C015 = **C014 v11 carrier + US Unemployment Rate**. 9-var composite.

## Single change

| 변수 | C014 v11 | **C015 v12** |
|---|---|---|
| Macro vars | 8 | **+ UNRATE (9)** |
| Threshold | ≥ 2 of 8 | **≥ 2 of 9** |

## New variable

### Signal 9 — US Unemployment Rate yoy change

**Mechanism (사전 commit)**:
> US 실업률은 Fed의 dual mandate (price stability + employment) 의
> employment side. CPI 와 함께 Fed 정책의 primary 변수.
>
> 외국인 EM 자본의 결정 view:
> - **UNRATE 상승 → 노동 시장 약화 → Fed dovish path → EM 자본 유입**
>   = 한국 favorable
> - UNRATE 하락 → 노동 시장 강세 → Fed hawkish path → EM 자본 회수
>   = 한국 unfavorable
>
> 기존 CPI/PPI 는 inflation 측면, UNRATE 는 employment 측면. Fed
> 양면 of mandate. 진정으로 다른 dimension.
>
> Note: 'unemployment 상승 = stock favorable' 은 counter-intuitive.
> 단기 macro view 에서 unemployment 상승 = Fed easing 예상 = 위험
> 자산 (EM 포함) favorable 의 정통 관점. 다만 recession 우려가 너무
> 크면 안 좋을 수도. 우리 dataset 의 16년 검증으로 sign 정확성 확인.

**Formula** (yoy CHANGE, percentage points; INVERSE sign vs others):
```
unrate_yoy_change(T) = UNRATE(T) - UNRATE(T - 12 months)
favorable_unrate(T) = unrate_yoy_change(T) >= 0  (실업률 yoy 상승)
```

**중요**: INVERSE sign — Brent/CPI/PPI 는 declining 이 favorable,
unrate 는 rising 이 favorable. Copper 도 같은 inverse 였음.

### Composite (9-var)

```
regime_score = count favorable in
  {USDKRW, VIX, DXY, curve, Brent, KR10y, CPI, PPI, UNRATE}
ON iff score >= 2
```

## Data status

`fred_us_unrate.csv` already downloaded (FRED UNRATE, monthly, 1948+).

## Hypothesis (사전 등록)

H1-H6 inherited.

### H7: UNRATE informativeness
- V1 v12 cumulative net ≥ V1 v11 (C014) + **5pp**

### H8: Subperiod (계속 critical, pre-2018 -8% 여전)
- 2010-2017 net ≥ 0 (UNRATE 가 pre-2018 의 weak labor market 환경 capture
  가능성)
- 2018-2026 net 유지

### H9: UNRATE correlations
- UNRATE yoy_change vs CPI yoy correlation
- UNRATE yoy_change vs curve correlation
- UNRATE yoy_change vs USDKRW correlation

## Verdict logic (사전 등록)

| 통과 | Verdict | 다음 |
|---|---|---|
| H7 PASS + 두 subperiod ≥ 0 | **STRONG PROMOTE + 첫 robust!** | C016 = Phase C (한국 specific) 진입 |
| H7 PASS + 한쪽만 | CONDITIONAL PROMOTE | C016 진행 |
| H7 FAIL + pre-2018 ≥ 0 | INCONCLUSIVE + pre-2018 fix | C016, UNRATE 유지 |
| H7 FAIL + pre-2018 no fix | UNRATE redundant | C016, UNRATE dropped |
| H1 catastrophic | KILL | architecture 재고 |

어느 경우든 C016 진행.

## Reportable metrics

기존 pattern + UNRATE specific:
1. Full + subperiod cumulative net + cost-0
2. (V1 v12 - V1 v11) per-year delta
3. UNRATE favorable quarters
4. UNRATE vs CPI / DXY / USDKRW correlations (H9)
5. H1-H7 + H8 + H9 summary

## Implementation task

기존 pattern (additive macro_regime + new strategy module).

### Configuration

```yaml
experiment_id: C015
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
    - us_unrate_change  # NEW
  composite_rule: count_favorable
  on_threshold: 2  # >= 2 of 9
output_dir: reports/experiments/C015_macro_v12_us_unrate
# 나머지 동일
```

### Completion criteria

- pytest fully green (currently 210)
- engine.py untouched
- Final message: V1 v12 net + cost-0, subperiod, max DD, positive years,
  Sharpe, UNRATE correlations, H1-H7+H8/H9.

If ambiguity, write C015_codex_questions.md.

### Out of scope

- ❌ 다른 변수 동시 추가
- ❌ Selection / threshold / rebalance 변경
- ❌ Engine 변경

## Result summary
DO NOT FILL until backtest complete.

## Claude review
DO NOT FILL until result files are read.
