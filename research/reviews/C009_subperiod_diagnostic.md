# Diagnostic — C008 V1 v6 Subperiod Stability Analysis

## Purpose
Per C008 review recommendation. Check if Brent's +60pp cost-0
improvement is robust across the data window or driven by specific
years/sub-periods.

This is **diagnostic analysis only** — no new backtest, no new code.
Uses existing C008 equity_curve.csv and quarterly_year_breakdown.csv.

## Subperiod cumulative returns (V1 v6 net, from equity_curve)

| Period | years | V1 net cumul | V1 ann | V1 max DD | V2 cumul | V2 ann |
|---|---:|---:|---:|---:|---:|---:|
| **Full 16yr** | 14.98 | **+36.98%** | +2.12% | -71.16% | +2009.5% | +22.6% |
| **Sub 2010-2017** | 6.87 | **−26.59%** | **−4.40%** | **−48.09%** | +176.4% | +16.0% |
| **Sub 2018-2026** | 8.12 | **+86.52%** | **+7.98%** | -59.75% | +659.3% | +28.4% |
| Pre-spike (2010-2019) | 8.81 | **−57.66%** | −9.30% | -66.26% | +193.4% | +13.0% |
| Spike era (2020-2026) | 6.17 | **+228.65%** | **+21.27%** | -37.56% | +626.2% | +37.9% |

## Year-exclusion sensitivity (compound from yearly)

| Scenario | V1 cumulative |
|---|---:|
| Full (16 years) | +25.19% (yearly compound; ~+37% daily) |
| **Excluding 2020 only** | **−14.43%** |
| **Excluding 2025 only** | **−29.14%** |
| **Excluding 2020 and 2025** | **−51.57%** |
| Excluding 2020, 2025, 2026 | **−69.00%** |

## Critical findings

### Finding 1: **2010-2017 sub-period FAILS H1**
V1 v6 가 첫 8년 (2010-2017) 에서 **−26.59% 누적**. 이건 strategy 가
역사 전반에 robust 하지 않음을 의미.

전체 16년이 +37% 양수인 건 2018-2026 의 +86.52% 가 첫 반의 -27% 를
overcome 했기 때문. 진짜 균등 robust 한 strategy 였다면 두 반 모두
양수여야.

### Finding 2: **Strategy 의 양수 누적은 3 spike year 의 산물**
- 2020 빼면 −14%
- 2025 빼면 −29%
- 2020 + 2025 빼면 **−52%**
- 2020 + 2025 + 2026 빼면 **−69%**

전체 +25% (yearly compound) 의 모든 contribution 이 3년 (2020, 2025,
2026) 에서 옴. 나머지 13년 누적 ≈ −69%.

### Finding 3: Pre-spike era (2010-2019) 는 catastrophic
**−57.66% cumulative over 8.81 years**. -9.3% annualized. 거의 B-family
의 B011 -94.79% 와 비교 가능.

→ 처음 10년 동안 V1 v6 도 작동 안 했음. 마지막 6년의 spike + Brent 의 capture 만으로 표면적 양수.

### Finding 4: Cost-0 추정 sub-period (rough)
Full cost paid = 7.89% (≈ 0.5% annualized).
- 2010-2017 cost ≈ 4.0% → cost-0 ≈ -27% + 4% = **−23%**
- 2018-2026 cost ≈ 4.0% → cost-0 ≈ +87% + 4% = **+91%**

→ Cost-0 도 period-specific. 진짜 alpha 차이 +114pp between sub-periods.
"+60% cost-0 over full period" 가 misleading.

## 의미 — 정직한 해석

**옵션 1 (Optimistic)**: 2018-2026 이 modern regime, 미래 deploy 환경에 더 가까움. 2010-2017 은 different regime (post-GFC 회복, 미정상화 환경). Modern era 만 보면 strategy works.

**옵션 2 (Skeptical)**: 2010-2017 도 진짜 OOS data (16년 모두 보유). 첫 반에서 fail 하는 strategy 는 "regime-conditional alpha". 두 spike year 이 없었으면 16년 전체도 음수. 결국 B-family 의 "2025 luck" 와 같은 종류, 단지 base 만 더 좋은 case.

**Mode C honest 해석**: **Subperiod stability test failed**. C008 의 +37% 는 robust 한 strategy 가 아니라 spike-year-conditional 알파의 cumulative effect.

## 무엇이 진짜 진전이었나

C008 의 결과가 useless 한가? **No**. 정직하게 평가하면:

1. **C005 v4 vs C008 v6 비교 자체는 valid**: Brent 추가가 같은 데이터에서 단방향 개선 (+45pp). Mechanism 도 명확.
2. **Modern era (2018-2026) 에서는 strategy works**: +86% over 8 years, Sharpe 약 +0.7 (이건 추정).
3. **Brent 가 진짜 informative variable**: 다른 매크로 변수와 orthogonal, recovery 환경 capture.
4. **그러나 "16년 robust alpha"** 는 **NOT achieved**.

## C-family 의 honest 결론

| | 사용자 stated 목표 | C008 V1 v6 |
|---|---|---|
| "지수 상회" | 16년 견고하게 KOSPI 정도 | 첫 8년 -27%, 다음 8년 +87% (불균등) |
| "큰 스파이크 따라가기" | spike 환경 잘 캡쳐 | ✓ 2020, 2025, 2026 좋은 캡쳐 |
| "moderate outperformance" | 매 연도 작은 + | ✗ 6/16 양수 연도만 |

→ **"Spike capture" 목표는 부분적으로 만족**. "**지수 상회**" 와 "**moderate outperformance**" 는 아직 만족 안 됨.

## 다음 step 의 시나리오 (사용자 결정 필요)

### Scenario A: 2010-2017 fix 시도
**가설**: 더 추가 매크로 변수 (예: copper, 한국 정책금리, China PMI) 가 pre-2018 환경 capture 가능.

- 위험: USDCNY (C006) 같은 fail 가능
- 기회: 새 dimension 이 pre-2018 환경 capture 가능
- C001 v2 deepening roadmap 다음 step (v7 = + copper)

### Scenario B: Modern era only 인정 + Layer 2/3 진입
**가설**: 2018-2026 의 +87% 가 진짜라 인정. Layer 2 (sector) 진입으로 modern era 성능 더 개선.

- 위험: Modern era 성능도 lucky 일 수도
- 기회: 더 정교한 layer 가 robust performance 의 더 큰 그림 줄 수도
- "Strategy works in modern era" 라는 가정 수용

### Scenario C: 정직한 결론 / project conclusion
**가설**: 16년 robust strategy 가 우리 hypothesis space 에서 안 만들어짐.

- C-family 의 발견 정리, 한계 인정
- 깨끗한 research 결과 문서화
- 사용자 stated 목표 ("지수 상회") 와 데이터 결과의 honest gap 인정

### Scenario D: 더 큰 redesign
**가설**: 한 가지 strategy 가 16년 견고하기 어려움. Multi-strategy / regime-adaptive 가 필요.

- 큰 architecture change
- 위험: 또 다른 16-experiment cycle
- 기회: real 한 robust strategy

## 내 추천 — **사용자와 strategic 대화 필요**

이건 결정적 분기점. 4 시나리오 모두 정당하고 trade-off 다름. 단순 next ticket 보다 **strategic discussion** 가 옳음.

내 lean: **Scenario C 또는 A**. 
- C 이유: 우리 hypothesis space 의 한계가 명확히 드러남. Honest conclusion 도 valid output.
- A 이유: Brent 가 진짜 도움 됐으니 한 더 step 시도 정당.

B 와 D 는 신중. B = "modern era 인정" 이 premature 일 수 있음. D = 큰 risk.

## 결정 요청

이건 ticket 결정보다 **strategic conversation**. 4가지 시나리오 중 어느 방향이 너의 본질적 우선순위 / 인내심 / 시간 투자 의지와 맞는지.

- 1. **A: macro v7 (+ copper) 시도** — 한 더 step
- 2. **B: Modern era 인정 + Layer 2 sector 진입** — 다음 layer
- 3. **C: 정직한 결론 / project conclusion**
- 4. **D: Multi-strategy redesign**
- 5. 다른 방향 / 잠시 멈춤
