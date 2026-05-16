# Review — C004 (Quarterly macro-gated strategy)

## Verdict
**CONDITIONAL PROMOTE per literal verdict map (4/6 + H7 PASS)**.
**Honest interpretation**: 단지 "horizon 변경이 효과 있음 확인" 정도.
Strategy 는 여전히 누적 -22% 음수.

## One-line conclusion
Quarterly 가 monthly 보다 +32pp 명확히 개선 (H7 PASS). 그러나 여전히
누적 -22% (cash -0% 보다 못함). Selection (top-5 mcap) 의 본질적
weakness 가 horizon 변경으로 안 고쳐짐.

## Headline numbers

### V1 quarterly vs C003 monthly vs others

| Strategy | 16년 누적 net | Sharpe | Max DD |
|---|---:|---:|---:|
| **C004 V1 quarterly** | **-22.01%** | -0.09 | -74.73% |
| C003 V1 monthly | -54.17% | -0.27 | -73.47% |
| B011 V1 daily gate-only | -94.79% | n/a | -98.04% |
| B010 V1 (flow carrier) | -87.8% | n/a | n/a |
| Cash | 0% | — | 0% |

→ **Horizon 정교화 trajectory 명확**: daily → monthly → quarterly 각 step 마다 ~40pp 개선. 그러나 cash 도 못 이김.

### 사전 등록 6+1 verdict

| # | 조건 | 결과 | Pass |
|---|---|---:|:---:|
| H1 | 누적 > 0 | -22% | ❌ |
| H2 | KOSPI 대비 -30pp 이내 | -2031pp | ❌ |
| H3 | spike ≥ 2/3 | 2/3 (2010=0%, 25/26+) | ✓ |
| H4 | max DD 우월 | V1 -75 vs V2 -34 | ✓ literal, ❌ spirit |
| H5 | ≥ 8/16 positive | 4/16 | ❌ |
| H6 | net/cost-0 ≥ 0.7 | 1.43 | ✓ literal, meaningless |
| **H7** | **quarterly ≥ monthly + 10pp** | **+32pp** | **✓ 명확** |

Literal 4/6 + H7 = CONDITIONAL PROMOTE.
Honest: 1/6 (H3) + H7 만 truly meaningful PASS.

---

## 가장 중요한 발견 — 2025 spike capture 가 dramatic 개선

| Year | C003 monthly | C004 quarterly | delta |
|---|---:|---:|---:|
| 2025 (spike) | **+12.68%** | **+56.70%** | **+44pp** |
| 2024 | -5.22% | +9.80% | +15pp |
| 2026 (partial) | +24.19% | +26.86% | +3pp |
| 2020 (V) | +22.95% | +12.20% | -11pp (monthly 더 나음) |
| 2018 (bear ON disaster) | -44.47% | -41.76% | +3pp (둘 다 disaster) |
| 2011 | -13.21% | -19.80% | -7pp |

**핵심 메커니즘**: Quarterly hold 가 **spike 환경에서 추세를 계속 타게 함**. Monthly rebalance 는 spike 중간에 regime change 로 빠져나갈 수 있음.

2020 V-recovery 는 반대로 monthly 가 더 빠르게 적응. 즉 **trade-off**: quarterly 가 sustained trend 에 좋고, monthly 가 빠른 regime change 에 좋음.

---

## 그래도 still fail — 왜?

### 1. **Selection 문제 (top-5 mcap 집중)** — 가장 큰 weakness
2018 -42% disaster 가 horizon 바뀌어도 거의 그대로 (-44% → -42%). **5종목 집중 risk** 가 macro gate 와 무관하게 작용. 이건 horizon 으로 못 고침.

### 2. **2010, 2015, 2017, 2019, 2022 missed**
이 해들도 monthly 와 거의 같음. Macro composite "≥ 2 of 3" threshold 가 너무 strict. VIX 가 높은 시기 (post-crisis recovery 초입) 를 일관되게 놓침.

### 3. 좋은 spike year 도 still under-perform vs KOSPI
2025 V1 quarterly +57% 인데 V2 KOSPI proxy +105%. 좋은 시기에 도 절반 가량만 capture.

### 4. 본질적 trade-off — 못 잡은 게 vs 못 피한 게
- Spike year 일부 캡쳐 (+12% ~ +57%)
- 정상 년 entirely missed (0%)
- Bad year 일부 회피 (2022 +0% vs V2 -18%)
- Bad year 일부 catastrophic (2018 -42% vs V2 -8%)

평균하면 못 잡은 가 / 못 피한 게 > 캡쳐한 거. 누적 음수.

---

## C-family 의 진단 — 우리 무엇을 배웠나

### B-family vs C-family 의 비교
| | B-family (단기 매매) | C-family (중장기 매크로 gate) |
|---|---|---|
| 16년 누적 worst | -94.79% (B011) | -22.01% (C004) |
| 16년 누적 best | -87.8% (B010) | -54.17% (C003) → -22.01% (C004) |
| Cost 부담 | 매우 큼 | 1/3 수준 |
| Mechanism | "5일 flow signal" (weak) | "macro regime gate" (informative but rough) |
| 주요 weakness | Regime conditional + 단기 noise | Selection 집중 + threshold conservative |

→ C-family 가 B-family 보다 명확히 개선. 그러나 둘 다 viable strategy 아님.

### Confirmed 진실들
1. **매크로 horizon (monthly+) 이 옳음** — daily 보다 명백히 신호 강함
2. **매크로 signal 자체가 정보 갖음** — regime ON share 42% 이 의미있는 timing 보여줌
3. **Selection 단계가 진짜 weakness** — top-5 mcap 의 집중 risk 가 macro 이점 상쇄
4. **Threshold (≥ 2 of 3) 가 너무 conservative** — 좋은 시기 일부 놓침

### 아직 모르는 것
1. **Macro v2 (변수 추가) 가 도움 될지** — 현재 3개 외에 추가 변수가 differential 가치
2. **Selection 변경 (broader basket, ETF style)** 가 얼마나 도움될지
3. **Threshold 완화 (≥ 1 of 3) + Selection 변경** 의 결합 효과

---

## C005 candidates (Mode C — 사전 등록 결정 필요)

### Option A: Selection 변경 (단일 변수)
**가설**: Top-5 mcap 의 집중 risk 가 핵심 issue. 더 broad basket (예: cap-weighted top-20 또는 합성 KOSPI ETF proxy) 으로 변경.

- 한 변수 변경 (selection only)
- Macro signal 그대로 유지
- 2018 disaster 같은 case 의 risk 감소
- Spike capture 도 더 잘 될 가능성 (mcap 가 spike 의 일부만 잡았던 것)

### Option B: Macro v2 deepening (단일 변수)
**가설**: 3 macro 변수가 충분하지 않다. C001 v2 의 deepening roadmap 따라 4번째 변수 추가.

- Roadmap v2 = + VIX (이미 있음) — wait, VIX 는 이미 v1 에 있어서 사실은 v3 (+DXY) 만 추가됐다고 봐야 함
- 정확히는 우리 macro v1 이 (USDKRW + VIX + DXY) 인데, roadmap v1 는 (USDKRW + Fed) 였음. 우리가 사실 이미 v3 를 한 것.
- 다음 deepening = v4 = + US 2-10y yield curve

### Option C: Threshold 변경 (단일 변수)
**가설**: ≥ 2 of 3 이 너무 strict. ≥ 1 of 3 으로 완화하면 좋은 시기를 더 잡음.

- 한 변수 변경 (threshold only)
- Macro signal 그대로
- Selection 그대로
- **위험**: ON share 너무 커지면 cash 효과 사라지고 bad year 들 fully exposed

### Option D: 결합 (multi-variable change)
**가설**: 진짜 문제는 두 가지 (selection + threshold) 동시. 함께 변경 필요.

- ⚠️ Multi-variable change. "한 번에 한 변수" discipline 위반.
- 만약 진행하면 사전 등록 정당화 필요.

### 내 추천: **Option A (Selection 변경) 먼저**

이유:
1. **가장 큰 실패 source 가 selection** — 2018 -42% 가 단일 사건으로 누적 손실의 큰 부분
2. **단일 변수 변경** — Mode C discipline 정확히 따름
3. **Hypothesis 명확** — "concentration risk 감소가 catastrophic loss 감소" 예측
4. **2025 spike capture 도 개선 가능** — 광범위 basket 이 더 많은 winning stocks 포함
5. Selection 변경의 가장 단순한 form = "synthetic KOSPI proxy hold" (V2 와 동일). 만약 V1 변경 후 사실상 V2 (KOSPI BH) 가 되면 → "결국 macro gate 가 substantial value 못 더함" 결론 가능. 깨끗한 진단.

### 추천 안 함: Option C (Threshold)
같은 데이터에서 threshold 변경은 본질적으로 "regime score 분포 다시 보고 cut-off 조정" = data-snooping risk 큼. 신중해야 함.

---

## 결정 요청

다음 4가지 중:

1. **C005 = Selection 변경** — top-5 mcap → broader basket (내 추천)
2. **C005 = Macro v4 (yield curve 추가)** — 사전 등록 macro deepening roadmap
3. **C005 = Threshold 변경** — ≥ 2 → ≥ 1, ON share 증가 시도
4. **잠시 멈춤 — strategic 재고**

또는 더 큰 redesign 필요 시:
5. **Strategy form 자체 재고** — gate + 단일 holding 구조 자체가 한계
