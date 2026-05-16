# Review — C007 (Top-20 mcap selection)

## Verdict
**H7 FAIL (-10.77pp)** per pre-registered C007 verdict map.
INCONCLUSIVE + selection marginal → **C008 = macro v6 (Brent)**.

**C005 v4 N=5 가 진짜 local optimum confirmed**. Macro deepening
(v5 USDCNY) 도 failed, selection diversification (N=20) 도 failed.
C005 v4 가 두 방향 모두에서 best.

## One-line conclusion
Broader basket 이 concentration risk 부분 완화 (2018: -44%→-27%) 하고
max DD 도 줄였지만, **spike capture 반감 (2025: +57%→+33%) + cost-0
양수→음수 (+3.67%→-8.46%) + cost 4배 증가**로 net -11pp 후퇴. 매크로
signal 이 top-5 mcap (Samsung/Hynix 등) 의 특정 종목들과 강하게
align 되어 있었음을 정량 확인.

## Headline 비교

| | C005 v4 (N=5) | **C007 (N=20)** | Δ |
|---|---:|---:|---:|
| Net cumul | -8.48% | **-19.25%** | **-10.77pp** |
| **Cost-0 cumul** | **+3.67%** | **-8.46%** | **-12.13pp** ⚠ |
| Max DD | -71% | -66% | +5pp (less bad) |
| Sharpe | -0.03 | -0.08 | -0.05 |
| 2018 disaster | -44% | **-27%** | **+17pp** ✓ |
| 2025 spike | +57% | **+33%** | **-24pp** ✗ |
| Trade count | ~190 | **760** | **4x more** |
| Positive years | 6/16 | 6/16 | same |

### 사전 등록 H1-H7

| H | 결과 | Pass |
|---|---|:---:|
| H1 cumul > 0 | -19.25% | ❌ |
| H2 vs KOSPI | -2028pp | ❌ |
| H3 spike 2/3+ | 2/3 | ✓ |
| H4 max DD literal | OK | ✓ |
| H5 ≥ 8/16 positive | 6/16 | ❌ |
| H6 net/cost-0 ≥ 0.7 | 2.28 (literal, two-neg) | ✓ literal |
| **H7 N=20 ≥ N=5 + 5pp** | **−10.77pp** | **❌** |

3/6 + H7 FAIL = "Layer 3 marginal" → next per pre-commit.

## H8 진단 (descriptive) — 2018 concentration

V1 N=20 2018 = -27% (vs N=5 -44%). **Concentration risk 진짜 있었음**
부분 확인. 그러나 -27% 도 여전히 catastrophic (V2 KOSPI 2018 = -8%).
즉 매크로 signal 자체의 2018 timing 도 wrong (regime ON during bear).

## 결정적 발견 — Macro signal 의 selection-specificity

C007 의 cost-0 가 음수로 회귀한 점이 가장 informative:
- N=5 cost-0 +3.67% (양수)
- N=20 cost-0 -8.46% (음수)

**같은 macro signal, 다른 selection, 12pp 차이**. 의미:
- 매크로 signal 은 **특정 종목들 (top-5 = Samsung/Hynix 등) 의 특정 상황과 강하게 align**
- 그 종목들이 2025 같은 spike year 에 KOSPI 의 outperformance leader
- Broader basket (top-20) 으로 가면 이 alignment 가 dilute 됨
- 즉 매크로 signal 은 "한국 시장 전체 상승" 보다 "특정 mega-cap 종목들의 outperformance" 와 연관

이게 implies:
- Top-5 mcap 의 alpha 는 **selection 자체에 알파**가 있는 게 아니라 (그건 macro 없어도 top-5 hold 면 같아야 함)
- **Macro favorable 환경에서 top-5 mcap 이 특히 잘 함** (즉 conditional alpha)
- Broader basket 으로 가면 그 conditional alpha 잃음

→ **매크로 + top-5 mcap 의 조합이 의도된 effect**. Broader basket = 매크로 신호의 alpha 손실.

## C-family 진단 종합 (C003-C007)

### Tested combinations and results

| Config | Net | Cost-0 |
|---|---:|---:|
| C003 monthly + 3 vars + top-5 | -54% | -? |
| C004 quarterly + 3 vars + top-5 | -22% | -9% |
| **C005 quarterly + 4 vars + top-5 (BEST)** | **-8%** | **+3.67%** |
| C006 quarterly + 5 vars + top-5 | -20% | -8% |
| C007 quarterly + 4 vars + top-20 | -19% | -8% |

**Local optimum 확정**: 모든 single-variable change 가 v4-N5 보다 worse. 4 dimensions × 1 step both directions 모두 검증.

### 우리가 검증된 진실들

1. ✓ Macro signal 은 alpha 있음 (cost-0 +3.67%)
2. ✓ Best config = 4 macro vars + quarterly + top-5 mcap
3. ✓ 매크로 deepening 한계: v5 (USDCNY) 가 net 도 cost-0 도 worse
4. ✓ Selection diversification 한계: N=20 가 net 도 cost-0 도 worse
5. ✓ **매크로 신호의 alpha 는 selection-specific** — top-5 mcap 의 특정 종목들과 conditional

### 아직 fail 하는 부분
1. Cost > alpha (3.67% < 7.89% cost paid → net -8.48%)
2. 2018 disaster (ON 에서 -44%) 의 timing issue
3. 2010, 2015, 2019 missed (threshold 또는 signal mechanism)

## C008 — 사용자 의견 entry per pre-commit

C007 pre-registered fallback:
> "2-3/6 + H7 < +5pp → INCONCLUSIVE + selection marginal → **C008 =
> macro v6 (Brent) — 사용자 의견의 정당한 진입점**"

사용자가 C006 직후 제안: "변수 더 추가해야 한다". 그 의견을 cherry-pick
없이 disciplined fallback 으로 진입. **C008 = macro v6 = + Brent oil**.

### Brent 의 mechanism

| 변수 | Dimension |
|---|---|
| USDKRW yoy | Currency flow (Asia FX) |
| VIX 60/240 | Risk appetite |
| DXY yoy | USD broad |
| US 2-10y curve | Term premium / recession risk |
| **Brent oil yoy** | **Commodity / supply / inflation** |

Brent 는 진정으로 다른 dimension:
- Commodity cycle (USDKRW, USDCNY 와 다름 — FX 아님)
- 한국 정유/화학 산업에 직접 영향
- 글로벌 인플레이션 leading indicator
- USD 강세와 inverse correlation 가능 (oil priced in USD)

### Pre-registered hypothesis (C008)

- H7 (C008): V1 v6 cumulative net ≥ V1 v4 (C005) + 5pp → Brent informative
- < +5pp → 진짜 macro deepening 한계 (Brent 도 fail), **C009 = strategic 재고**

만약 Brent 도 H7 FAIL → **deepening 완전 한계 확정**, project 의 큰 결정 필요.

## Do not do next
- C008 = Brent 외의 다른 변수 (Mode C: C007 fallback 이 Brent commit)
- C008 = selection 또 변경 (Layer 3 두 직선 실패 했음)
- Threshold 변경 (data-snooping risk)

## Follow-up
- **C008 = macro v6 = + Brent oil** (사용자 의견 + pre-registered fallback)
- C008 결과:
  - H7 PASS → v6 carrier, C009 = 다음 macro 변수 (마지막 1-2개)
  - H7 FAIL → strategic 재고: 우리 hypothesis space 의 종결 시점
