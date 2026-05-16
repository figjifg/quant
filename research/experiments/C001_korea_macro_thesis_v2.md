# C001 v2 — Korea macro thesis (hierarchical top-down)

## Status
v2 (replaces v1's parallel-legs structure with hierarchical layer
architecture per user input 2026-05-16)

## Why v2 (changes from v1)

v1 treated "global macro" and "industrial cycle" as parallel /
coequal legs of Story A. The user pointed out this contradicts the
classical 60/30/10 attribution (macro 60 %, sector 30 %, company 10 %
of equity return variance).

v2 reframes the architecture from **parallel** to **hierarchical**:

```
v1 (parallel — wrong):                v2 (hierarchical — correct):

Macro leg  ──┐                        Layer 1: Macro (foundation)
              ├── both → buy             ↓ (gate: macro favorable?)
Industrial ──┘                        Layer 2: Sector (refinement)
                                         ↓ (gate: sector favorable?)
                                      Layer 3: Stock (selection)
```

In v2, each layer is a **gate** for the layer below. Macro is the
foundation — if macro is unfavorable, sector and stock layers don't
fire regardless of what they would say.

**Iteration mode also changes**:
- v1: "Story A fails → switch to Story B or C"
- v2: "Macro layer v1 fails → deepen macro layer to v2 (add one
  variable)". Iteration is downward (more depth in macro), not
  sideways (different story).

This matches the user's insight: "글로벌 매크로는 중첩이 되기 쉽지
않으므로 더 해석을 고도화 할수록 더 좋은 layer 가 완성된다."

## What this ticket is

Same as v1 — thesis document, NO code, NO backtest, NO data
analysis (intentionally). Outputs of this ticket = revised narrative
+ pre-registered predictions + falsification + roadmap.

## Korean equity market structural facts (unchanged from v1)

S1. 수출 의존도 매우 높음 (~40% GDP, ~20% 가 반도체)
S2. 외국인 비중 매우 큼 (~30-35% KOSPI 시가총액, 매매 비중 30-40%)
S3. KRW 는 commodity currency 성격 (managed-floating)
S4. 글로벌 risk-on/off 의 high beta (KOSPI vs SP500 beta ~1.0-1.5)
S5. 중국 의존도 (수출 ~25% 가 중국)
S6. Cyclical earnings (반도체 사이클 3-4년)
S7. 우리 16년 데이터 관찰: 작동 연도 = 2010, 2017, 2020, 2025, 2026 —
    모두 강한 상승 + 일부 USD 약세 동반

## The hierarchical architecture (v2 core)

### Layer 1: Global Macro (foundation — project's primary deepening target)

**Purpose**: "지금 한국 시장에 자본이 유입될 macro 환경인가?"

**Output**: Binary "ON / OFF" 또는 score (-100 ~ +100).
- ON → Layer 2 권한 부여
- OFF → cash (또는 향후 short hypothesis)

**Importance**: 60% (general wisdom; 한국에서는 다를 수 있음 — C002
에서 측정).

이게 우리 project 의 **primary deepening 대상**. 다른 어떤 layer 보다
이 layer 에 가장 많은 thought 와 iteration 투입.

### Layer 2: Sector (refinement — active only when Layer 1 = ON)

**Purpose**: "한국 시장 안에서 어느 섹터가 주도하는가?"

**Output**: 1-3개 active 섹터 선택. 나머지 섹터는 underweight.

**Korean sectors with cyclical drivers**:
| 섹터 | 주요 종목 | 핵심 driver |
|---|---|---|
| 반도체 | Samsung Electronics, SK Hynix | DRAM/NAND 가격, AI 수요, 재고 사이클 |
| 자동차 | 현대차, 기아 | 미국 자동차 판매, FX (수출), EV 전환 |
| 화학/배터리 | LG화학, Samsung SDI, LG에너지솔루션 | 정유 마진, EV 수요, 인플레이션 |
| 금융 | KB금융, 신한지주, 하나금융 | 금리 phase, 부동산, NIM |
| 조선/철강 | HD현대중공업, POSCO | BDI, 글로벌 무역, 원자재 |
| IT 서비스 | NAVER, 카카오 | 광고 시장, 글로벌 빅테크 동조 |

**Importance**: 30%. Macro 가 활성화한 뒤에 의미.

### Layer 3: Stock (selection — active only when sector chosen)

**Purpose**: "선택된 섹터 안에서 어느 종목을 살까?"

**Output**: N개 종목 + 가중치.

여기서 B-family 에서 본 외국인+기관 flow 같은 micro 신호가 의미할
수 있음. 단 macro+sector 가 이미 OK 한 상황에서만. 즉 외국인+기관
flow signal 자체가 reborn 할 수도 있어 — 우리가 B-family 에서 이걸
standalone 으로 쓴 게 문제였지, signal 자체가 가치 없는 건 아닐 수도.

**Importance**: 10%. Macro+sector 가 정해진 후 의미.

---

## Layer 1 의 deepening roadmap

매크로 layer 의 iterative deepening. 한 번에 한 변수 추가.

### v1 — 단순 시작 (2 변수)
- **USDKRW yoy momentum** (KRW 방향 = 외국 자본 흐름 proxy)
- **US Fed phase** (US 3m 금리 변화율 = global liquidity)

이 두 변수만으로 16년 데이터 검증. C003 에서.

### v2 (if v1 fails) — 3 변수
- + **VIX** (글로벌 risk appetite)

이유: USDKRW + Fed 가 capture 못한 risk-on/off regime 잡기 위해.

### v3 (if v2 fails) — 4 변수
- + **DXY** (USD 전반 강도)

이유: USDKRW 가 KRW-specific 노이즈 포함할 수 있어. DXY 가 더 broad
한 USD 신호.

### v4 (if v3 fails) — 5 변수
- + **US 2-10y yield curve spread** (recession risk / term premium)

이유: yield curve 의 inversion 은 recession leading indicator. EM
risk 의 큰 변수.

### v5 (if v4 fails) — 6 변수
- + **USDCNY 또는 China PMI** (중국 환경)

이유: 한국 수출의 25% 가 중국. China-specific 신호 분리.

### v6 (if v5 fails) — 7 변수
- + **Commodity proxy** (Brent oil 또는 copper)

이유: Real economy + supply 신호. 한국이 에너지 / 원자재 수입국이라
영향 큼.

### Max 7 변수 — 그 이상은 과적합 위험
v6 까지 갔는데도 작동 안 하면 → 매크로 layer 의 structural
limitation 인정 → honest stop 또는 Layer 2 로 전환.

### Deepening 규칙 (discipline)

각 deepening step 마다:
1. **한 변수만 추가** (한 번에 둘 이상 추가 금지)
2. **추가 변수의 mechanism 사전 글로 commit** ("이게 왜 macro 의
   missing dimension 인가")
3. **기존 변수와의 상관관계 사전 측정** (corr ≥ 0.7 이면 중복 dimension
   이므로 추가 안 함, 다른 변수 선택)
4. **추가 변수의 falsification 조건 명시** ("이 변수가 alpha 에 기여
   안 한다는 증거는 무엇")
5. **각 deepening 의 결과 인정** (모드 C): v1 verdict 가 fail 이라도
   v1 의 verdict 는 변경 안 함, v2 가 새 시도

---

## Layer 1 v1 의 사전 등록 predictions

매크로 v1 (USDKRW + US Fed 의 2 변수) 로 시작. 검증은 C003 에서.

**P1 (USDKRW 단일)**: 
- 측정: 특정 day T 에서 USDKRW 252거래일 변화율 ("yoy") 계산
- 가설: yoy ≤ 0% (KRW 강세) 일 때 → 향후 252 거래일 KOSPI 수익률
  평균 ≥ +10%
- 가설: yoy ≥ +5% (KRW 큰 약세) 일 때 → 향후 252 거래일 KOSPI 수익률
  평균 ≤ 0%

**P2 (Fed phase)**:
- 측정: US 3m 금리의 252거래일 변화 (Δrate)
- 가설: Δrate < 0 (금리 하락 cycle) 일 때 → KOSPI 향후 252거래일 평균
  +5% 이상
- 가설: Δrate > +1.0% (강한 긴축) 일 때 → KOSPI 향후 252거래일 평균 ≤ 0%

**P3 (combined, the core hypothesis)**:
- 측정: P1 양수 조건 AND P2 양수 조건 동시 만족
- 가설: 두 조건 동시 만족 시 → 향후 252거래일 KOSPI 평균 ≥ +20%
  (single-leg 보다 strictly 큼)

**P4 (XOR — only one leg)**:
- 한 조건만 만족 시 → 향후 252거래일 KOSPI 평균 -5% ~ +10% (중립)

**P5 (neither)**:
- 두 조건 모두 실패 시 → 향후 252거래일 KOSPI 평균 ≤ 0%

이 5개의 predictions 가 macro layer v1 의 전체 평가.

---

## Layer 1 의 사전 등록 falsification

**Layer 1 v1 의 verdict 결정 (C003 에서 적용)**:

**PASS** (모두 만족):
- P1 양수 조건 시 KOSPI 평균 ≥ +10% (관측치 ≥ 3개 필요)
- P1 음수 조건 시 KOSPI 평균 ≤ 0% (관측치 ≥ 3개 필요)
- P2 양수 조건 시 KOSPI 평균 ≥ +5% (관측치 ≥ 3개 필요)
- P2 음수 조건 시 KOSPI 평균 ≤ 0% (관측치 ≥ 3개 필요)
- P3 의 조건 만족 시 KOSPI 평균 strictly P1, P2 단독보다 큼

**FAIL** (즉 v1 깨짐 → v2 로 deepening):
- 위 PASS 조건 중 셋 이상 fail
- OR: P1, P2 의 sign 이 hypothesis 와 정반대로 나옴 (예: KRW 약세
  시기에 KOSPI 강세)

**INCONCLUSIVE** (관측치 부족):
- 어느 조건의 sample size < 3개 (16년에 충분히 발생 안 함) → 정량
  결론 어렵, 정성 분석 + v2 로 진행

### 전체 thesis 의 falsification (구조적)

위 layer-내 falsification 와 별개로, **architecture 자체의 falsification**:

**F-Arch-1**: C002 의 variance decomposition 에서 매크로 R² < 30% →
60/30/10 가설 한국에서 깨짐 → architecture 재설계 필요 (매크로가
foundation 이 아닐 수도)

**F-Arch-2**: 매크로 v1-v7 까지 모두 fail → 매크로 layer 가 한국
시장 driver 아님 → top-down 가설 자체 깨짐 → 정직한 stop

**F-Arch-3**: 매크로 v3+ 시점에서 추가 변수와 기존 변수 모두 corr
≥ 0.7 → 매크로의 truly independent dimension 이 부족 → 다른 layer
로 전환

---

## C002 의 첫 작업: variance decomposition

이게 v2 에서 새로 추가된 부분. 너의 reframing 의 premise (60/30/10)
를 한국에서 검증.

### Variance decomposition methodology

**Step 1**: KOSPI 일별 수익률 데이터 (2010-2026)
- market_breadth 의 cap_weighted_return (cumulative) 또는 가능하면
  진짜 KOSPI total return

**Step 2**: 매크로 변수 (이미 가진 것 + 새로 수집한 것)
- USDKRW, US 3m rate, [v2-v6 의 추가 변수들 모두]

**Step 3**: 섹터 proxy
- KOSPI 안의 섹터 분류가 없으면 — universe 의 종목들을 자체적으로
  KIS 또는 외부 분류로 grouping (이건 별도 effort 필요할 수도)
- 또는 단순화: 시가총액 상위 10개 종목의 sector grouping

**Step 4**: Regression / variance decomposition
- KOSPI return = α + β_macro * macro_factors + β_sector * sector_returns + ε
- 각 leg 의 R² contribution 계산
- 결과: macro % + sector % + idiosyncratic %

### 결과 해석
- macro 가 60% 근처 → user reframing 강하게 확인 → architecture 진행
- macro 가 40-50% → architecture 조정 (sector 가 더 중요)
- macro 가 20-30% 또는 그 이하 → architecture 재설계

이게 C002 의 첫 deliverable. 그 결과 보고 매크로 layer 의 detailed
predictions 정량화 진행.

---

## Story B, C 의 처지

v1 에서 alternative 로 유지했던 Story B (post-crisis recovery) 와
Story C (USDKRW 단일) 는 v2 에서 어떻게?

**Story B**: Macro layer 안의 한 특별 case 로 흡수. Post-crisis
recovery 는 macro 의 "regime change" detector 의 한 형태. v2-v6 의
deepening 에서 자연히 cover 가능. 별도 story 로 유지 안 함.

**Story C**: USDKRW 단일 가설 = macro v1 의 P1 단독 (Fed 없이). 만약
P2 (Fed) 가 P1 (USDKRW) 에 비해 add value 거의 없음을 발견하면 →
de facto Story C 채택 (v1 의 simpler 형태). 별도 story 로 유지 안 함.

이렇게 두 alternative 가 deepening 의 부분 case 로 흡수됨. v2 의
구조가 더 단단한 이유.

---

## 데이터 needs (v2 재정렬)

### 보유 (즉시)
- USDKRW (FRED) — Layer 1 v1 의 P1
- US 3m rate (FRED) — Layer 1 v1 의 P2
- equity panels — Layer 3 stock
- market_flow — Layer 3 stock (flow signal)
- market_breadth — Layer 1 의 KOSPI proxy + sector breadth
- KOSPI200 선물 — Layer 1 의 derivative signal (옵션)
- Global futures (SP500/NASDAQ/Nikkei/Russell) — Layer 1 의 cross-asset

### HIGH priority 수집 (Layer 1 deepening 용)
| 데이터 | Version 적용 | Source (예상) |
|---|---|---|
| VIX 시계열 | v2 | FRED (VIXCLS) 무료 |
| DXY 시계열 | v3 | FRED 또는 ICE 무료 |
| US 2y, 10y 국채 수익률 | v4 | FRED (DGS2, DGS10) 무료 |
| USDCNY | v5 | FRED (DEXCHUS) 무료 |
| China PMI (Caixin 또는 NBS) | v5 | 발표 시 시점 조심 |
| HY spread (US high yield - treasury) | v2-v3 | FRED (BAMLH0A0HYM2) |
| Brent oil 또는 copper | v6 | FRED 또는 데이터 vendor |

대부분 FRED 무료. C002 에서 일괄 수집.

### MED priority (Layer 2 sector 용 — 나중)
- DRAM spot 가격 (TrendForce)
- BDI (Baltic Exchange)
- 한국 월별 수출 (KOSTAT)

### LOW priority (Layer 3 stock 용)
- 이미 보유 (equity panels)

---

## C-family roadmap (v2)

- **C001 v2 (this)**: hierarchical thesis + macro deepening roadmap
- **C002**: variance decomposition (architecture 검증) + macro
  데이터 수집 + macro v1 predictions 정량화
- **C003**: macro v1 검증 (P1-P5 적용, PASS/FAIL/INCONCLUSIVE)
- **C004**: (if v1 fail) macro v2 (VIX 추가) 검증
- **C005, C006, ...**: continue deepening as needed
- **C00N (macro verified)**: Layer 2 (sector) 진입
- **C00M (sector verified)**: Layer 3 (stock) 진입, B-family 의 signal
  들이 여기서 redeemed 될 수도
- **C00L (전체 verified)**: True OOS / forward 검증

각 step 의 verdict 가 명확. Deepening 또는 honest stop 결정 명확.

---

## Honest 우려 (v2 update)

v1 에서 짚은 5가지 + v2 새 우려:

6. **"60/30/10" 은 일반론** — 한국 시장에서 정확한 비율은 C002 에서
   측정해야. 잘못된 premise 위에 architecture 쌓을 수 있음.

7. **매크로 변수도 상관 가능** — USDKRW 와 DXY 는 강한 상관. v2-v6
   deepening 에서 사전 상관관계 측정 + 중복 dimension 회피 필수.

8. **Iterative deepening 도 과적합 위험 있음** — 매크로 v1 fail 후
   v2 로 가는 것이 본질적으로 "결과 보고 변수 추가" 임. 이걸 막는 건
   사전 등록된 mechanism 과 falsification. discipline 매우 중요.

9. **Layer-내 vs cross-layer 의 분리** — Layer 1 검증과 Layer 2/3
   는 sequential. Layer 1 not verified 시 Layer 2/3 시작 금지.
   이 sequential 약속을 어기지 말 것.

---

## What this ticket is NOT (unchanged from v1)
- ❌ 백테스트
- ❌ 새 코드
- ❌ Strategy 설계
- ❌ Predictions 의 정량 검증 (그건 C003)

## What this ticket IS (updated)
- ✓ Hierarchical architecture 의 사전 등록
- ✓ Macro layer deepening roadmap (v1-v7)
- ✓ Predictions 와 falsification 의 layer-별 명시
- ✓ Architecture 자체의 falsification 조건 (F-Arch-1, 2, 3)
- ✓ 데이터 needs 의 layer-별 mapping
- ✓ C-family roadmap

---

## 사용자 입력 받고 진행

C002 작성 시작해도 되는지, 또는 C001 v2 에 추가 조정 필요한지.
v2 의 hierarchical 구조 + macro deepening roadmap 이 너의 reframing
의 정신을 정확히 반영하는지 확인 요청.

만약 OK 면 → C002 작성 (variance decomposition + 매크로 데이터 수집
계획 + predictions 정량화)
