# C019 — Macro v16 (+ USDJPY / 엔 캐리 trade signal)

## Status
planned

## What this ticket is

사용자 의견: "**앤 캐리 트레이드라는 용어도 있는 만큼 외국인이 시장에
들어옴에 있어서는 엔달라나 일본의 ppi, 기준금리, 채권금리** 데이터들이
중요"

D-family pivot 전 마지막 C-family 시도. **USDJPY = 엔 carry trade 의
direct indicator**, 글로벌 risk-on/off 와 EM 자본 흐름의 잘 알려진
driver.

C019 = **C014 v11 carrier + USDJPY yoy**. 9-var composite.

## Single change

| 변수 | C014 v11 | **C019 v16** |
|---|---|---|
| Macro vars | 8 | **+ USDJPY (9)** |
| Threshold | ≥ 2 of 8 | **≥ 2 of 9** |

## New variable

### Signal 9 — USDJPY yoy momentum (엔 carry trade)

**Mechanism (사전 commit)**:
> **엔 carry trade 메커니즘**: 글로벌 투자자가 저금리 JPY 차입 → 고금리
> 자산 (EM 포함) 투자. Yen 약세 시 carry trade 활성화, yen 강세 시
> carry unwind 와 risk-off.
>
> - USDJPY 상승 (yen 약세) = carry trade active = risk-on = EM/Korea 자본 유입 → favorable
> - USDJPY 하락 (yen 강세) = carry unwind = risk-off = EM 자본 회수 → 부정적
>
> 역사적 사례:
> - 2008 GFC: USDJPY 110 → 90 급락 (carry unwind), 글로벌 risk-off
> - 2012-2015 Abenomics: yen 의도적 약세, EM 일부 영향
> - 2022-2024 Fed-BOJ divergence: USDJPY 110 → 160, 큰 carry trade
>
> 기존 변수와 차이:
> - DXY (broad USD index) 안에 JPY 비중 ~14% — 부분 overlap
> - 그러나 USDJPY 의 specific role (carry funding currency) 은 unique
> - DXY 와의 corr 측정 후 redundancy 판단

**Formula** (yoy ratio, INVERSE sign vs USDKRW):
```
usdjpy_yoy(T) = USDJPY(T) / USDJPY(T - 252 trading days) - 1
favorable_usdjpy(T) = usdjpy_yoy(T) >= 0  (yen weakening favorable)
```

**Sign convention 주의**: USDKRW 는 yoy ≤ 0 (KRW 강세) favorable.
USDJPY 는 yoy ≥ 0 (yen 약세) favorable. 둘 다 currency 이지만 역할
다름:
- KRW = 한국 asset 매수 cost
- JPY = funding currency (carry trade)

### Composite (9-var)

```
regime_score = count favorable in
  {USDKRW, VIX, DXY, curve, Brent, KR10y, US_CPI, US_PPI, USDJPY}
ON iff score >= 2
```

## Data status

`fred_jpy.csv` already downloaded:
- FRED `DEXJPUS` (Japan / US Foreign Exchange Rate, yen per USD)
- **Daily** frequency (다른 monthly 변수와 다름)
- 1971-2026, 4266 obs in window

## Hypothesis (사전 등록)

H1-H6 inherited.

### H7: USDJPY informativeness
- V1 v16 cumulative net ≥ V1 v11 (C014) + **5pp**

### H8: Subperiod (계속)
- 2010-2017 net ≥ 0
- 2018-2026 net 유지

### H9: USDJPY correlations
- **USDJPY vs DXY correlation** (가장 중요 — DXY 안에 JPY 비중)
- USDJPY vs USDKRW correlation (Asian FX 연동)
- USDJPY vs VIX correlation (carry unwind = VIX spike?)

## Verdict logic (사전 등록)

| 통과 | Verdict | 다음 |
|---|---|---|
| H7 PASS + 두 subperiod ≥ 0 | STRONG PROMOTE | C020 = + Japan 10y JGB (Japan 시리즈 추가) |
| H7 PASS + 한쪽만 | CONDITIONAL PROMOTE | C020 진행 |
| H7 FAIL + pre-2018 ≥ 0 | INCONCLUSIVE | C020, USDJPY 유지 검토 |
| H7 FAIL + pre-2018 no change | USDJPY redundant w/ DXY 가능 | C020, USDJPY dropped |
| H1 catastrophic | KILL | architecture 재고 |

어느 경우든 C020 진행 (사용자 명시: Japan 시리즈 (PPI, 기준금리, JGB) 모두 시도).

## Reportable metrics

기존 + USDJPY specific:
1. Full + subperiod cumulative net + cost-0
2. (V1 v16 - V1 v11) per-year delta
3. USDJPY favorable quarters
4. **USDJPY vs DXY correlation** (H9 KEY)
5. USDJPY vs USDKRW correlation
6. USDJPY vs VIX correlation
7. **2008/2020/2022 carry trade phase 별 USDJPY 신호 정성 확인**
8. H1-H7 + H8 + H9

## Implementation task

기존 pattern. macro_factors + macro_regime additive, c019 strategy,
dispatcher, config, tests.

### Configuration

```yaml
experiment_id: C019
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
    - usdjpy_yoy  # NEW
  composite_rule: count_favorable
  on_threshold: 2  # >= 2 of 9
output_dir: reports/experiments/C019_macro_v16_usdjpy
```

### Completion criteria

기존 pattern.

If ambiguity, write C019_codex_questions.md.

### Out of scope

- ❌ 다른 변수 동시 추가
- ❌ Selection / threshold / rebalance 변경

## Result summary
DO NOT FILL until backtest complete.

## Claude review
DO NOT FILL until result files are read.
