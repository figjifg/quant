# C016 — Macro v13 (+ Korean CPI deceleration)

## Status
planned

## What this ticket is

**Phase C 첫 ticket** — 한국 specific 지표. C015 UNRATE fail 후
한국 inflation 시도. BOK 정책 결정의 primary 변수, 한국 시장의 가장
domestic macro driver 중 하나.

C016 = **C014 v11 carrier + KR CPI deceleration**. 9-var composite.

## Carrier base = C014 v11

C015 UNRATE fail (0 contribution), C012 KR 3m fail, C010 copper fail.
모두 carrier 에서 dropped. C014 v11 (8 vars) 가 best.

## Single change

| 변수 | C014 v11 | **C016 v13** |
|---|---|---|
| Macro vars | 8 | **+ KR CPI decel (9)** |
| Threshold | ≥ 2 of 8 | **≥ 2 of 9** |

## New variable

### Signal 9 — Korean CPI yoy deceleration

**Mechanism**:
> 한국 CPI 는 BOK 정책결정의 primary 변수. US CPI 와 다른 점:
> - US CPI = US Fed 정책 → 글로벌 자본 흐름 → EM 영향
> - KR CPI = BOK 정책 → KRW + 한국 시장 직접 영향
>
> 한국 inflation 하락 = BOK dovish 가능 → KRW 약세 위험 but 한국
> 시장 favorable (소비/투자 환경 개선).
>
> US CPI 와 부분 상관 가능 (글로벌 supply chain inflation 공유). H9
> 측정.

**Formula** (이미 yoy 인 시리즈의 deceleration):
```
kr_cpi_yoy(T) = FRED 시리즈 값 (이미 yoy growth rate)
kr_cpi_decel(T) = kr_cpi_yoy(T) - kr_cpi_yoy(T - 12)
favorable_kr_cpi(T) = kr_cpi_decel(T) <= 0
```

US CPI 와 같은 sign convention (declining favorable).

### Composite (9-var, including KR CPI)

```
regime_score = count favorable in
  {USDKRW, VIX, DXY, curve, Brent, KR10y, US_CPI, US_PPI, KR_CPI}
ON iff score >= 2
```

## Data status

`fred_kr_cpi.csv` already downloaded:
- FRED `KORCPALTT01CTGYM` (Korea CPI yoy growth rate)
- Monthly, 2010-01 ~ 2025-04 (184 obs)
- **Caveat**: 2025-05 ~ 2026-05 데이터 없음 (FRED 가 업데이트 안 함).
  마지막 4 quarters 에서 KR CPI 신호 unavailable. Codex 가 handling
  명시 (해당 quarter 에서 favorable = False 또는 composite 에서 제외).

## Hypothesis (사전 등록)

H1-H6 inherited.

### H7: KR CPI informativeness
- V1 v13 cumulative net ≥ V1 v11 (C014) + **5pp**

### H8: Subperiod (계속)
- 2010-2017 net ≥ 0 (현 C014 -8%)
- 2018-2026 net 유지

### H9: KR CPI correlations
- **KR CPI vs US CPI correlation** (가장 중요 — corr 0.7+ 면 redundant)
- KR CPI vs Brent correlation (oil → KR inflation pass-through)

## Verdict logic (사전 등록)

| 통과 | Verdict | 다음 |
|---|---|---|
| H7 PASS + 두 subperiod ≥ 0 | STRONG PROMOTE | C017 = + 한국 PMI 또는 수출 (Phase C 계속) |
| H7 PASS + 한쪽만 | CONDITIONAL PROMOTE | C017 진행 |
| H7 FAIL + pre-2018 ≥ 0 | INCONCLUSIVE + helps pre-2018 | C017, KR CPI 유지 |
| H7 FAIL + pre-2018 no change | KR CPI redundant w/ US CPI 가능 | C017, KR CPI dropped |
| H1 catastrophic | KILL | architecture 재고 |

어느 verdict 든 C017 진행.

## Reportable metrics

기존 + KR CPI specific:
1. Full + subperiod cumulative net + cost-0
2. (V1 v13 - V1 v11) per-year delta
3. KR CPI favorable quarters (out of available 60 quarters with data)
4. KR CPI vs US CPI 상관관계 (H9)
5. KR CPI vs Brent 상관관계
6. **Data gap handling**: 2025-Q2 이후의 missing KR CPI 처리 명시
7. H1-H7 + H8 + H9 summary

## Implementation task

기존 pattern:
- ADD kr_cpi series spec
- ADD kr_cpi_decel signal + 9-var-with-kr-cpi composite to macro_regime
- NEW c016 strategy module
- Tests + dispatcher + config

**Missing data handling**: 시리즈 끝 (2025-04) 이후의 quarter 에서:
- favorable_KR_CPI(T) = False (안전한 default — 정보 없으면 ON 신호 안 줌)
- 또는 composite 에서 KR CPI 제외 (위 quarter 만)

Codex 가 사전 등록한 방식 명시.

### Configuration

```yaml
experiment_id: C016
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
    - kr_cpi_decel  # NEW
  composite_rule: count_favorable
  on_threshold: 2  # >= 2 of 9
output_dir: reports/experiments/C016_macro_v13_kr_cpi
```

### Completion criteria

- pytest fully green (currently 215)
- engine.py untouched
- Final message: V1 v13 net + cost-0, subperiod, max DD, positive years,
  Sharpe, KR CPI favorable quarters, KR CPI vs US CPI corr (H9 critical),
  KR CPI vs Brent corr, **data gap handling summary**, H1-H7+H8/H9.

If ambiguity, write C016_codex_questions.md.

### Out of scope

- ❌ 다른 변수 동시 추가
- ❌ Selection / threshold / rebalance 변경
- ❌ Engine 변경

## Result summary
DO NOT FILL until backtest complete.

## Claude review
DO NOT FILL until result files are read.
