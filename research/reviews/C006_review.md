# Review — C006 (Macro v5 — USDCNY 추가)

## Verdict
**H7 FAIL by -11.19pp** (severe). Per pre-registered C006 verdict map:
"2-3/6 + H7 < +5pp → deepening 한계 신호 → **C007 = Layer 3 selection
재고 정당**".

**중요 결론**: 매크로 deepening 이 v4 에서 효과적으로 saturated.
**C005 v4 가 best macro carrier**. C006 의 USDCNY 추가는 net 도 cost-0
도 둘 다 후퇴시킴.

## One-line conclusion
USDCNY 가 USDKRW 와 correlation 0.50 으로 redundant 아닌 별도 변수임에도
composite 에 추가하니 net -11pp, cost-0 -12pp **둘 다 후퇴**. Macro
layer 의 deepening 효과 한계 명확히. **C005 v4 가 최선 carrier**, 다음
step 은 Layer 3 (selection).

## Headline numbers — Trajectory reversal

| Step | 변경 | Net cumul | Cost-0 cumul | Cumul 변화 |
|---|---|---:|---:|---:|
| B011 daily | (baseline) | -94.79% | n/a | — |
| C003 monthly | horizon ↑ | -54.17% | n/a | +40pp |
| C004 quarterly | horizon ↑↑ | -22.01% | -9% est | +32pp |
| **C005 v4** | **+ yield curve** | **-8.48%** | **+3.67%** ⭐ | **+14pp** |
| **C006 v5** | **+ USDCNY** | **-19.67%** | **-8.39%** | **-11pp** ⚠ |

→ Trajectory **reverses**. **C005 v4 가 local optimum**. v5 추가는 substantial 후퇴.

### 사전 등록 H1-H7 결과

| H | 결과 | Pass |
|---|---|:---:|
| H1 cumul > 0 | -19.67% | ❌ |
| H2 vs KOSPI | -2029pp | ❌ |
| H3 spike 2/3+ | 2/3 (2010=0%) | ✓ |
| H4 max DD | literal | ✓ |
| H5 ≥ 8 positive | 7/16 (slight up) | ❌ |
| H6 net/cost-0 ≥ 0.7 | 2.35 (literal, two-negatives meaningless) | ✓ literal |
| **H7 v5 ≥ v4 + 5pp** | **−11.19pp** | **❌ severe fail** |

3/6 + **H7 SEVERE FAIL** = "deepening 한계 신호".

## H8 보조 진단 — USDCNY-USDKRW 상관관계

**0.4953** (moderate, < 0.7). 두 변수가 완전 중복은 아님. USDCNY 자체가 별도 dimension 갖긴 함.

그런데도 composite 에 추가하면 net 도 cost-0 도 worse. 이게 의미:
- USDCNY 가 **independent dimension** 이지만
- 그 dimension 이 **wrong direction 신호** 를 일부 시기에 보냄
- 또는 **regime ON 결정에 noise 만 추가** 함

## 왜 USDCNY 가 harmful 했나 — 가설

### 1. 5 변수 composite + "≥ 2 of 5" threshold 의 effect

| Threshold | 효과 |
|---|---|
| v4: ≥ 2 of 4 (50%) | regime ON share 64% |
| v5: ≥ 2 of 5 (40%) | regime ON share 67% (+3pp) |

ON share 가 +3pp 만 증가 (대규모 변화 아님). 그런데 net -11pp 후퇴. 즉 ON share 자체 변화는 작지만 **wrong-timing 으로 진입한 경우가 많아짐**.

### 2. USDCNY 의 mechanism mismatch
가설: "CNY 약세 = 한국 export 약화". 실제 데이터 패턴:
- 2010-2014: CNY trend 강세 (USDCNY 하락) — favorable
- 2015 onwards: more 변동 — mixed signal
- 2022-2024: CNY 약세 (USDCNY 상승) — unfavorable
- USDCNY favorable 27/57 (47%) — 거의 50/50

이 patterns 가 KOSPI 의 실제 driver 와 align 잘 안 됨. 2025 spike year 에서 USDCNY 가 어떤 신호 보냈는지 quarterly_regime_log 확인 필요.

### 3. **결정적 학습**: 변수 추가 자체가 alpha 보장 아님
v3 → v4 (+yield curve): +14pp 개선
v4 → v5 (+USDCNY): -11pp 후퇴

→ **각 변수의 incremental value 가 점진 감소 → eventually 음수**. Classical "diminishing then negative returns" 패턴. Macro v4 = 4 변수가 우리 데이터 / 한국 시장 / quarterly horizon 의 **right capacity**.

---

## C-family 학습 종합

### Confirmed 진실들
1. ✓ **Macro horizon 이 옳음** (daily → quarterly 명확)
2. ✓ **Macro signal carries real alpha** (C005 cost-0 +3.67%)
3. ✓ **Variable diminishing returns 있음** (v3→v4 +14pp, v4→v5 -11pp)
4. ✓ **4 변수 (USDKRW + VIX + DXY + yield curve) 가 optimal macro carrier**
5. ✓ **Cost 가 alpha 보다 큰 게 net negative 의 원인** (C005 cost-0 +3.67% vs cost paid +7.89%)

### 핵심 발견 (이번 ticket)
1. **Macro deepening 의 saturation 검증 완료** — v5 가 v4 보다 worse 라는 명확한 신호
2. **v4 = 최적 macro carrier confirmed** — 더 이상의 매크로 variable 추가 안 해야
3. **Pre-registered fallback 작동** — Mode C discipline 의 가치 다시 확인. 결과 보고 임의 변경 안 했음

### 아직 남은 issue
1. **2018 disaster (-44%)** — selection 단계 (top-5 mcap) 의 concentration 문제. v5/v6 추가로 안 고침
2. **2010, 2015, 2019 missed** — threshold 문제, 가능
3. **Cost > alpha 의 본질** — alpha 증가 한계 → cost 감소 필요

---

## C007 의 결정적 다음 step — **Layer 3 (selection) 진입**

C006 의 pre-registered verdict 가 명확하게 가리킴: **deepening 한계, Layer 3 재고 정당**.

**Carrier = C005 v4** (4 변수 macro composite, quarterly, top-5 mcap selection). 이 위에서 single variable change.

### C007 candidates

### Option A: Selection 변경 — broader basket
**가설**: Top-5 mcap 의 concentration risk 가 핵심 문제 (2018 -44% disaster). Broader basket 으로 risk 분산.

후보:
- **A1**: Top-20 mcap 균등 (5 → 20 종목, 4배 분산)
- **A2**: KOSPI200 ETF proxy (실효 100+ 종목 cap-weighted)
- **A3**: Universe 전체 cap-weighted (broadest)

### Option B: Selection 변경 — sector-aware
**가설**: 매크로 favorable 환경에서도 sector 별 다른 성과. Sector diversification 필요.

- Sector data 추가 수집 필요 → 별도 ticket
- 더 복잡, prerequisite 필요

### Option C: Holding period 변경
**가설**: Quarterly 도 너무 짧음. Yearly hold 가 cost 더 줄임.

- 단순 변경
- 단점: Macro signal 변화 lag 큼

### Option D: Threshold 변경
**가설**: "≥ 2 favorable" 가 너무 conservative. ≥ 1 로 완화하면 좋은 시기 더 잡음.

- Data-snooping risk (이미 결과 본 후 threshold 변경)
- Pre-registered 영역 외

### 내 추천: **A (Selection 변경)**, A2 (KOSPI200 ETF proxy) 또는 A1 (top-20)

이유:
1. **Pre-registered fallback 그대로** — C006 verdict map 의 "Layer 3 (selection) 재고" 정확히 매칭
2. **2018 disaster 진단과 align** — concentration risk 는 단일 가장 큰 손실 source
3. **Single variable change** — selection 만 변경, 다른 모든 frozen
4. **결정적 진단** — A2 (KOSPI200) 가 V1 v4 와 같으면 → macro gate 의 selection-independent value 확인. 명확히 다르면 → selection 이 진짜 issue.

A1 (top-20) vs A2 (KOSPI200) 의 선택:
- A1: 단순 (top-N mcap, 같은 selection 메커니즘 with N=20)
- A2: 정통 indexing approach, 더 broad
- 둘 다 의미 있는 hypothesis. A1 추천 (가장 단순한 변경: N=5→N=20 만).

## Do not do next
- C007 = macro v6 (Brent) — pre-registered verdict 가 Layer 3 진입 가리킴. Macro 더 deepening 은 약속 위반
- Selection + threshold 동시 변경 (multi-variable)
- C005 v4 의 carrier 가 변경됨을 결과 보고 변경

## Follow-up
- **C007 = Selection 변경** (A1: top-5 → top-20 mcap, single variable change)
- C007 결과:
  - 명확히 좋음 (예: 누적 +5% 이상 개선) → A2 (KOSPI200 ETF) 또는 sector layer 진행
  - 비슷 → selection 도 한계, holding period 변경 또는 strategy 재고
  - 더 나쁨 → unexpected, 진단 필요
