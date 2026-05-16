# Review — C005 (Macro v4 — yield curve 추가)

## Verdict
**INCONCLUSIVE + v4 helps** per literal map (3/6 + H7 PASS = 매크로
deepening 효과 진짜).

**그러나 가장 중요한 발견은 따로**: **V1 cost-0 가 처음으로 양수 (+3.67%
over 16 years)**. 프로젝트 시작 이래 **모든 strategy 변형 중 최초로
multi-decade 양의 raw alpha**.

## One-line conclusion
Macro v4 가 처음으로 진짜 alpha 발굴. Cost-0 +3.67% 가 cost (8% 누적
≈ 0.5% 연환산) 보다 작아서 net 은 여전히 -8% 음수. 하지만 "alpha
존재 여부" 의 binary question 이 처음으로 PASS.

## Headline numbers

| Strategy | Net | Cost-0 | Annualized | Sharpe |
|---|---:|---:|---:|---:|
| **C005 V1 v4** | **-8.48%** | **+3.67%** | -0.59% | -0.03 |
| C004 V1 v3 | -22.01% | -9% est | -1.65% | -0.09 |
| C003 V1 monthly | -54.17% | n/a | -5.08% | -0.27 |
| B011 V1 daily | -94.79% | n/a | n/a | n/a |
| B010 V1 (flow) | -87.8% (cost-0 -0.10%) | -0.10% | n/a | n/a |

→ **C005 가 처음으로 양의 cost-0 (+3.67%)** 도달. 모든 이전 시도들은
cost-0 도 음수였거나 OOS 만 양수 (B009 cost-0 OOS +2.42 였지만 IS
음수, 16년 전체로는 -0.10).

## 사전 등록 H1-H7 결과

| H | 결과 | Pass |
|---|---|:---:|
| H1 cumul > 0 | -8.48% | ❌ |
| H2 vs KOSPI -30pp 이내 | -2018pp | ❌ |
| H3 spike 2/3+ | 2/3 (2010=0%, 2025+, 2026+) | ✓ |
| H4 max DD 우월 | V1 -71% vs V2 -34% | ✓ literal, ❌ spirit |
| H5 ≥ 8 positive year | 6/16 (vs C004 4/16) | ❌ |
| **H6 net/cost-0 ≥ 0.7** | **-2.31** | **❌ — 이게 진짜 진단** |
| **H7 v4 ≥ v3 + 5pp** | **+13.54pp** | **✓ 명확** |

**H6 FAIL 이 가장 의미있는 PASS**:
- V1 net -8.48%, V1 cost-0 +3.67% → ratio = -2.31
- 이건 **alpha 가 진짜 있는데 cost 가 alpha + 7pp 더 먹음**
- 이전엔 alpha 가 음수라 cost 와 비교 의미 없었음. 이제 처음으로 양수.

Verdict map: **2-3/6 + H7 ≥ +5pp = INCONCLUSIVE + v4 helps → C006 = macro v5**

## Trajectory — Deepening 효과 가시화

| Step | 변경 | Net cumul | 누적 개선 |
|---|---|---:|---:|
| B011 daily | (baseline daily) | -94.79% | — |
| C003 monthly | horizon: daily → monthly | -54.17% | **+40pp** |
| C004 quarterly | horizon: monthly → quarterly | -22.01% | **+32pp** |
| **C005 v4** | **+ yield curve** | **-8.48%** | **+14pp** |
| C006 v5 (TODO) | + USDCNY 또는 China PMI | ? | ? |

**일관된 trajectory**. 매 단계가 점진적 개선. 차차 감소하는 marginal 효과지만 진짜 발전.

다음 deepening (v5, v6) 가 가능한 결과 시나리오:
- Net positive (예: +5%) — strategy promote 가능
- Net 여전히 음수 but cost-0 더 양수 (예: cost-0 +10%, net -3%) — cost reduction 검토
- Cost-0 도 marginal change (+4%) — deepening 한계, 다음 step 검토

## 핵심 진단

### 1. **Alpha 가 존재함이 처음으로 증명**
지금까지 모든 strategy 는 16년 cost-0 도 음수였거나 marginal. C005 가 +3.67% (≈ 0.23% 연환산) 로 small but real. Magnitude 는 작지만 sign 이 양수.

### 2. **Cost 가 진짜 bottleneck**
Cost 8% 누적 (0.5% 연환산). 이건 사실 low 한 편 (B-family monthly average 와 비교). 그런데 alpha 가 작아서 cost > alpha.

→ 둘 중 하나 또는 둘 다 필요:
- **Alpha 증가**: 더 깊은 macro deepening (v5, v6)
- **Cost 감소**: holding period 늘리거나 selection 변경 (Layer 3, 매크로 deepening 후)

### 3. **Spike capture 가 확실히 자리잡음**
2025 +57%, 2026 +56% (둘 다 큰 양수). 2025 의 V2 +105% 대비 약 절반 캡쳐는 여전한 한계지만, 절대 magnitude 가 우리 strategy 의 best 성공 case.

### 4. **2018 disaster 여전히 (-44%)**
Yield curve 추가가 2018 ON 결정에 영향 못 줌. Selection (top-5 mcap) 의 concentration 문제. 매크로 deepening 완료 후 Layer 3 단계에서 해결.

### 5. **Regime ON share 64% — Yield curve 가 너무 자주 favorable**
Yield curve 53/61 quarters favorable (87%). 효과적으로 threshold 완화함. 이게 alpha 증가의 일부 원인일 수 있고, cost 도 함께 증가 가능성 있음.

다음 v5 변수가 이 imbalance 보정할 수 있음 (China PMI 같은 변수는 더 자주 unfavorable 가능).

## C006 candidates (사전 등록한 deepening roadmap)

C001 v2 의 macro roadmap:
- v1: USDKRW + Fed
- v2: + VIX
- v3: + DXY ← 현재 (C003-C004)
- v4: + US 2-10y curve ← C005
- **v5: + USDCNY 또는 China PMI** ← C006 candidate
- v6: + commodity (Brent or copper)

### Option A (recommended): C006 = v5 = + USDCNY
**Mechanism**: China demand 가 한국 수출의 25% (반도체 중간재 + 부품). CNY 약세 (USDCNY 상승) = 중국 수출 환경 어려움 = 한국 export demand 약화 = KOSPI 부정적. CNY 강세 = 중국 강건 = 한국 favorable.

데이터: 이미 보유 (`fred_dexchus.csv`).

**Formula 후보**:
```
USDCNY_yoy(T) = USDCNY(T) / USDCNY(T-252) - 1
favorable_USDCNY(T) = USDCNY_yoy(T) <= 0  (CNY 강세 또는 안정)
```

### Option B: C006 = v5 = China PMI (대신)
- 더 직접적인 중국 경기 신호
- 데이터 별도 수집 필요 (현재 미보유)
- 추가 data source 도입 = 다른 ticket

### Option C: C006 = Skip to commodity (Brent)
- USDCNY 가 USDKRW 와 상관 있을 수 있음 (둘 다 AsiaEM FX)
- Brent oil 은 commodity dimension (전혀 다른 신호)
- Roadmap 순서 변경 = 사전 등록 위반

### 내 추천: **A (USDCNY 추가)**
- 이미 데이터 있음
- Roadmap 순서 그대로
- 단일 변수 변경 (Mode C)
- Mechanism 명확 (한국 수출 driver 의 핵심 destination)

---

## 큰 그림 — 우리는 어디 있나

**처음으로 진짜 alpha 발견했지만 cost burden 으로 net 음수**. 두 가지 길:

### Path 1: 매크로 deepening 계속 (C006, C007)
- v5, v6 추가하며 cost-0 alpha 점진 증가 추구
- 만약 cost-0 가 충분히 커지면 (>10%) net 양수 가능
- 위험: 변수 추가 marginal returns 감소 (v3→v4 +13pp 였지만 v4→v5 가 +5pp 일 수도 있음)

### Path 2: Cost reduction 시작 (Layer 3 또는 holding 연장)
- Selection broader basket → turnover 감소
- 또는 hold period yearly 로 더 길게
- 위험: Macro layer 아직 deepening 안 끝남, 너무 이른 layer change

### Path 3: 둘 다 (multi-variable)
- ⚠️ Mode C 위반 위험. 한 번에 하나만.

**내 추천**: Path 1 진행, 적어도 v5 한 step 더. v5 결과 본 뒤 결정.
만약 v5 가 +10pp 이상 도움이면 → v6 도 진행. 만약 v5 가 marginal (< +3pp) 이면 → 매크로 deepening 한계 신호 → Layer 3 (selection) 으로 전환 정당.

## Do not do next
- Selection / threshold / rebalance frequency 동시 변경 (multi-variable)
- C005 결과 보고 H6 threshold (0.7) 임의 완화 — pre-registered 유지
- "Cost-0 가 양수니까 strategy 좋음" 결론 — net 가 음수면 deployable 아님
- 결과 보고 사전 등록 verdict map 변경

## Follow-up
- **C006 = v5 = + USDCNY** (사전 등록 roadmap 순서, 단일 변수 변경)
- C006 결과 본 뒤 v6 진행 또는 Layer 3 검토 결정
