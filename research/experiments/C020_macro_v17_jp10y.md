# C020 — Macro v17 (+ Japan 10y JGB yield)

## Status
planned

## What this ticket is

C019 USDJPY fail (-42pp, 같은 pattern). 사용자 명시: "엔달라나 일본의
ppi, 기준금리, 채권금리" — Japan series 시리즈 계속. JGB 10y yield 시도.

C020 = **C014 v11 carrier + Japan 10y JGB yield**. 9-var composite.

## Honest expectation note

지난 6 연속 fail (KR3m, UNRATE, KR CPI, KR exports, M2, USDJPY) 가
모두 같은 패턴 (independent dimension, but composite vote 시 wrong-timing
tip). ChatGPT 의 framework critique 가 정확히 가리킴: "**composite
logic 자체가 bottleneck**".

JGB 10y 도 같은 결과 예상. 그러나 사용자 명시한 Japan series 시리즈
완성 차원에서 진행. JGB fail 후 D-family pivot 정당.

## Single change

| 변수 | C014 v11 | **C020 v17** |
|---|---|---|
| Macro vars | 8 | **+ Japan 10y (9)** |
| Threshold | ≥ 2 of 8 | **≥ 2 of 9** |

## New variable

### Signal 9 — Japan 10y JGB yield change

**Mechanism (사전 commit)**:
> JGB 10y yield 은 BOJ 통화정책 + 일본 macro 환경 + 글로벌 rate 동향
> 의 종합 반영.
>
> 특히 2022-2024 BOJ YCC (yield curve control) 출구 시기 의 중요한
> regime change:
> - 2010-2015: BOJ QE, JGB yield 0% 근처
> - 2016-2022: NIRP + YCC, JGB 10y ~0%
> - 2023-2024: YCC 조정 + 종료, JGB 10y 0.5% → 1.5%+
> - 2025-2026: 추가 정상화
>
> 메커니즘 (carry trade 관점):
> - JGB yield 상승 = Japan 수익률 매력 ↑ = carry capital Japan 으로
>   회귀 → EM 부정적
> - JGB yield 하락 = carry 지속 → EM favorable
>
> US 10y yield (이미 curve 안에 있음) 와 JGB 10y 의 spread 가 사실은
> 더 직접적인 carry signal 이지만 우선 JGB 단독 검증.

**Formula** (yoy change in percentage points):
```
jp10y_yoy_change(T) = JGB10Y(T) - JGB10Y(T - 12 months)
favorable_jp10y(T) = jp10y_yoy_change(T) <= 0  (JGB yield 하락 또는 안정 = carry 지속)
```

KR 10y 와 같은 sign convention.

### Composite (9-var)

```
regime_score = count favorable in
  {USDKRW, VIX, DXY, curve, Brent, KR10y, US_CPI, US_PPI, JP10y}
ON iff score >= 2
```

## Data status

`fred_jp10y.csv` already downloaded:
- FRED `IRLTLT01JPM156N` (Long-Term Government Bond Yields, 10-year, Japan)
- Monthly, 1989-2026-04, 196 obs in window

## Hypothesis (사전 등록)

H1-H6 inherited.

### H7: JGB 10y informativeness
- V1 v17 cumulative net ≥ V1 v11 (C014) + **5pp**
- 예상: 또 fail. 그러나 confirm 필요.

### H8: Subperiod (계속)
- 2010-2017 net ≥ 0
- 2018-2026 net 유지

### H9: JGB correlations
- JGB 10y vs US 10y change (글로벌 rate sync, 예상 corr 높음)
- JGB 10y vs KR 10y change
- JGB 10y vs USDJPY (yield/yen 관계)

## Verdict logic (사전 등록)

| 통과 | Verdict | 다음 |
|---|---|---|
| H7 PASS + 두 subperiod ≥ 0 | STRONG PROMOTE | C021 = + BOJ 정책금리 또는 D-family entry |
| H7 PASS + 한쪽만 | CONDITIONAL PROMOTE | C021 진행 |
| H7 FAIL | drop, **D-family pivot 정당화** | D001 = factor-based 재설계 |

만약 JGB 도 fail 면 Japan series 시리즈 완성 (USDJPY ✗, JGB ✗, PPI/policy 데이터 issues), D-family entry 명백.

## Reportable metrics

기존 + JGB specific:
1. Full + subperiod cumulative
2. (V1 v17 - V1 v11) delta
3. JGB favorable quarters
4. JGB vs US 10y / KR 10y / USDJPY correlations (H9)
5. **2023-2024 YCC exit 시기의 JGB 신호 정성 확인**
6. H1-H7 + H8 + H9

## Implementation task

기존 pattern. macro_factors + macro_regime additive, c020 strategy,
dispatcher, config, tests.

### Configuration

```yaml
experiment_id: C020
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
    - jp10y_yoy_change  # NEW
  composite_rule: count_favorable
  on_threshold: 2  # >= 2 of 9
output_dir: reports/experiments/C020_macro_v17_jp10y
```

### Completion criteria

기존 pattern.

If ambiguity, write C020_codex_questions.md.

### Out of scope

- ❌ 다른 변수 동시 추가
- ❌ Selection / threshold / rebalance 변경

## Result summary
DO NOT FILL until backtest complete.

## Claude review
DO NOT FILL until result files are read.
