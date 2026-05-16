# Review — C002 (Macro layer foundation)

## Verdict
**F-Arch-1 TRIGGERED** per pre-registered C001 v2 logic. Macro R²
(full period) = 23.57 %, below the 30 % threshold for the hierarchical
architecture premise.

Per Mode C: the verdict stands. Past commitments (C001 v2's
hierarchy + threshold) are not retroactively softened. The
architecture's foundation premise — "macro is ~60 % of Korean
equity variance" — is empirically NOT supported at the
pre-registered strict threshold.

**Strategic conversation required before C003.** Multiple paths
forward exist; user choice needed.

## One-line conclusion
8개 macro 변수가 KOSPI 일별 수익률의 약 24%만 explain. 그 중 대부분이
USDKRW + DXY 의 FX 신호에서 옴. 나머지 76% 는 sector + idiosyncratic
인데 한국 sector 지수 데이터 없어 분리 불가. F-Arch-1 사전 등록된
threshold 30% 아래로 명확히 떨어짐.

## Headline numbers

### Variance decomposition R² by period

| Window | n_obs | Macro R² | Sector R² | Idiosyncratic |
|---|---:|---:|---:|---:|
| **Full (2010-2026)** | 3,478 | **23.57 %** | deferred | **76.43 %** |
| Sub (2010-2017) | 1,707 | 28.76 % | deferred | 71.24 % |
| Sub (2018-2026) | 1,771 | **23.14 %** | deferred | **76.86 %** |

→ Macro share **declining over time** (28.76 % → 23.14 %).
→ F-Arch-1 (30 % threshold) triggered in full period and recent sub-period.

### Regression coefficients (full period)

By absolute size, the macro explanation is **dominated by FX**:

| Variable | Coefficient | Magnitude rank |
|---|---:|:---:|
| **USDKRW (dexkous_usdkrw_ret)** | **-0.669** | **#1** |
| **DXY (dxy_ret)** | **-0.377** | **#2** |
| USDCNY (dexchus_usdcny_ret) | +0.167 | #3 |
| VIX (vix_ret) | -0.037 | small |
| BAA10Y spread | -0.020 | small |
| US 3m rate Δ | +0.018 | small |
| US 10y rate Δ | -0.009 | small |
| US 2y rate Δ | +0.004 | smallest |

**관찰**: 매크로 explanation 의 거의 전부가 두 FX 변수 (KRW, DXY).
나머지 6개 변수 (US 금리 3종, VIX, credit spread, CNY) 는 합쳐도
KOSPI variance 의 marginal contribution.

→ "Macro layer" 라기보다 사실상 "**FX layer**". User 가 Option 3
진단에서 발견한 USDKRW 패턴이 regression 으로 정량 확인됨.

### Recent sub-period reinforces FX dominance

2018-2026 에서 USDKRW coefficient = **-0.80** (full 평균 -0.67 보다
더 강함), DXY = -0.40. FX 의 KOSPI 설명력이 더 커진 시기.

## Why 24% (not 60%)? — 3 possible reasons

### 1. Sector data missing (가능성 매우 큼)
Sector 지수 (반도체, 자동차, 화학 등) 데이터가 우리 repo 에 없음.
한국에서 반도체가 KOSPI 시가총액 ~25% 이고 사이클이 큰 driver 이므로
sector R² 가 상당히 클 가능성. 만약 sector 가 30-40% 면 macro + sector
합쳐서 50-65% 로 user reframing 의 macro+sector hierarchy 와 비슷.

→ Idiosyncratic 76% 중 상당 부분이 실제로는 unmeasured sector variance.

### 2. KOSPI 가 외국 매크로보다 자체 dynamics 가 더 강함
20-30 거래일 단위로 보면 외국 매크로 영향이 작고, 한국 specific
event (정책, 단일 종목 news, 외국인 단발 매수 등) 가 큰 driver. 한국
시장이 generally 외국 매크로에 follow 한다는 wisdom 이 daily 수준
에서는 약화될 수 있음.

### 3. OLS daily regression 의 한계
- Daily granularity 에서는 noise 큰 portion 차지 → R² 낮게 측정
- Non-linear 관계 (예: regime breakdown) OLS 가 capture 못함
- Lagged effect (예: 미국 매크로 영향이 1-3 거래일 후 한국에 나타남)
  지금 lag 1 로만 측정, 더 긴 lag 가 더 explain 할 수 있음
- 월별 또는 주별 단위로 가면 R² 가 더 높을 가능성 있음

## What this means for the project

### Strict interpretation (Mode C)
F-Arch-1 triggered → C001 v2 의 hierarchical architecture 의 premise
(macro 가 foundation) 가 검증 안 됨 → **architecture 재설계 필요**.

C003 (macro v1 predictions 검증) 를 진행하기 전에 architecture
재고가 옳음.

### Nuanced interpretation
- Macro R² 가 0% 가 아닌 24%
- 그 24% 가 매우 robust 한 한 가지 driver (FX) 에 집중
- USDKRW 자체는 강한 explanatory power 갖음
- 그래도 "60% foundation" 은 아님

### The honest situation
세 가지 사실 모두 인정:
1. F-Arch-1 strict threshold 깨짐 (24% < 30%)
2. 하지만 24% 가 무의미한 noise 가 아니라 USDKRW-driven robust signal
3. Sector data 부족으로 "왜 76% 가 unexplained 인가" 진단 어려움

→ Action 결정은 user 의 strategic 선택.

## 4가지 가능 다음 단계

### Option A: F-Arch-1 strict 인정 → 매크로 layer 폐기
- Macro 가 foundation 이라는 hypothesis 깨짐
- 다른 architecture 시도 (예: stock-level 부터 시작 — 사실상 B-family 로 회귀)
- 또는 정직한 project 종료

### Option B: 약화된 macro layer 로 진행
- "Macro 가 24% explainer 이고 그 중 USDKRW 가 dominant" 을 사실로 인정
- C003 진행하되 architecture 가 "weak macro gate + 다른 layer 필요"
  임을 명시
- C003 의 결과 본 후 sector / stock layer 다시 보강

### Option C: Sector data 수집 → variance decomposition 재실행
- 한국 KOSPI 섹터 지수 데이터 추가 수집 (KIS/Bloomberg/직접 구성)
- C002 의 sector deferred 부분 채워서 full decomposition
- 그 후 architecture 재평가
- **장점**: 진짜 macro/sector/idio 비율 알 수 있음
- **단점**: 1-2 ticket 시간 + 새 데이터 수집

### Option D: 방법론 정교화
- Lagged regression (US 매크로 → 한국 1-3일 lag)
- Rolling window R² (시간에 따라 변하는 explanation)
- 월별/주별 granularity (daily noise 줄임)
- 비선형 / regime-dependent 측정

## 내 추천 — Option C → Option B/D 조합

논리:
1. **F-Arch-1 trigger 는 sector deferred 라는 caveat 가 본질적**.
   76% 의 idiosyncratic 중 얼마가 진짜 stock-specific 인지 sector
   variance 인지 모르고서는 architecture 결정 불가.
2. 사용자 reframing 의 핵심 (60/30/10) 은 macro+sector 합쳐서 90%
   까지인데, 우리는 sector 부분을 측정 안 함.
3. Sector 데이터 추가가 best 1-2 ticket 시간이고 다른 모든 결정의
   foundation 이 됨.
4. Sector 데이터 후 매크로+sector 합쳐서 50% 이상이면 → user
   reframing 부분 확인 → Option B 로 진행 (weak macro 인정하되 layered)
5. 매크로+sector 합쳐서도 30% 미만이면 → Option A (architecture
   진짜 깨짐) → 정직한 재고

순서:
- **C003 = 한국 sector 지수 데이터 수집 + full hierarchical 재검증**
- 결과 본 후 C004 = macro v1 predictions 검증 (Option B) 또는
  architecture 재설계 (Option A)

## 솔직한 caveat 들

1. **30% threshold 자체가 pre-registered 했지만 somewhat arbitrary**.
   24% vs 30% 의 차이가 정말 architecture 깨는 의미인가 vs 약간
   under인 의미인가 — 사실 미묘함.
2. **하지만 pre-registered 약속을 임의 완화하는 게 더 큰 risk**.
   Mode C 정신상 24% < 30% 면 trigger 인정.
3. **Sector 데이터 없이 결론 내리는 게 가장 큰 weakness**. C002 의
   진정한 limitation.

## Predictions P1-P5 quantification (Task 3)

`research/strategy_thesis/C002_predictions_quantified.md` 작성 완료
(126 lines). Exact formulas + bootstrap methodology + sample size
estimates. F-Arch-1 trigger 와 무관하게 quantification 작업 자체는
완료. 만약 C003 가 macro v1 predictions 검증으로 가면 이 doc 즉시
사용 가능. 만약 architecture 재고로 가면 doc 은 dormant 으로 유지.

## 다음 단계 결정 요청

1. **C003 = sector 데이터 수집 후 full decomposition** (내 추천)
2. **C003 = macro v1 predictions 검증 (Option B, weak macro 로 진행)**
3. **Project 재고 — macro layer 가 foundation 아니라는 게 명백하면 어떻게?**
4. 다른 방향

이 결정에 따라 C-family 의 전체 방향 갈림.
