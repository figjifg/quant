# C001 — Korea macro thesis v1 (top-down 첫 시도)

## Status
draft (thesis only, NO data testing yet)

## What this ticket is

C-family 의 첫 ticket. C 는 "top-down thesis-driven" approach 를 의미.
B-family 의 bottom-up feature engineering 종료 후 (B011 verify fail
이후) 의 새 출발점.

**이 ticket 의 산출물은 글 한 편**. 코드 없음, 백테스트 없음, 데이터
분석 없음 (의도적으로). 다음 ticket 들에서 thesis 의 predictions 을
정량 검증.

## Why top-down approach now (B-family 와의 본질적 차이)

| B-family (bottom-up) | C-family (top-down) |
|---|---|
| 데이터 (5일 flow) 에서 시작 | Thesis (macro 환경) 에서 시작 |
| "이 신호로 alpha 만들 수 있을까" | "왜 한국 시장이 alpha 를 만드는가" |
| 27 변형 시도, 한 가지 신호 안에서 | 검증 가능한 predictions 도출 후 검증 |
| 작동/안 작동 binary 결과 | 어느 부분이 살아있고 어느 부분이 깨졌는지 진단 |
| 결과 보고 다음 변형 시도 | 결과 보고 thesis 수정 또는 폐기 |
| 데이터 끼워 맞추기 위험 | Narrative confirmation bias 위험 |

B-family 가 27번의 시도로 한 가지 진실을 가르쳐줬어: **alpha 가 "왜
존재해야 하는가" 의 답이 없으면 어떤 변형도 그저 운에 의존하게 됨**.
C-family 는 그 "왜" 를 먼저 답하고 시작.

## 한국 주식 시장의 구조적 사실 (관찰, 의견 아님)

Thesis 를 만들기 전에 부정할 수 없는 사실들부터 정리:

### S1. 수출 의존도가 매우 높다
- 한국 GDP 중 수출 비중 ~40% (미국 ~10%, 일본 ~15% 대비 매우 높음)
- 수출의 ~20% 가 반도체 (DRAM + NAND + 시스템반도체)
- KOSPI 시가총액 상위: Samsung Electronics (~15-20% 비중), SK Hynix
  (~5-7%). 합쳐 KOSPI 의 ~25% 가 반도체.
- 따라서 KOSPI 수익은 **글로벌 반도체 사이클** + **글로벌 무역 환경**
  과 깊이 연결.

### S2. 외국인 비중이 매우 크다
- KOSPI 시가총액 중 외국인 보유 ~30-35%
- 외국인 매매 비중 (일별) 종종 30-40%
- 외국인은 long-only 가 아니며 (헤지펀드, ETF rebalance 등) 단기
  variance 큼
- 따라서 **외국인 자금 유입/유출 의 단기 driver 가 큰 영향**

### S3. KRW 는 자유 변동에 가깝지만 통제됨
- 한국은행이 dramatic FX 변동 시 개입
- KRW 는 위험자산 (commodity currency 성격) 으로 분류됨
- USD 강세 → EM 자금 회수 → KRW 약세 → 외국인 한국 주식 매도
- 따라서 **USDKRW 방향 = 외국인 자금 유입/유출 의 leading or
  coincident 지표**

### S4. 한국 시장은 글로벌 risk-on / risk-off 의 high beta
- VIX 상승 → EM 매도 → 한국 시장 큰 폭 하락
- VIX 하락 → EM 매수 → 한국 시장 큰 폭 상승
- KOSPI vs SP500 beta 일반적으로 1.0-1.5

### S5. 중국 의존도
- 한국 수출의 ~25% 가 중국 (반도체 중간재 + 부품)
- 중국 경기 부진 → 한국 수출 부진 → KOSPI underperform
- 동시에 지정학적 긴장 (사드, 한한령 등) 의 영향도 큼

### S6. Cyclical earnings
- 반도체 산업은 사이클이 명확함 (보통 3-4년)
- DRAM/NAND 가격은 spot 시장에서 관찰 가능
- 반도체 가격 상승 = Samsung/Hynix 이익 급증 = KOSPI 상승
- 반도체 가격 하락 = 이익 감소 = KOSPI 침체

### S7. 우리 데이터의 관찰 (B003-B011 에서)
- 작동한 연도들 = 2010, 2017, 2020, 2025, 2026 (5개)
- 모두 KOSPI 강한 상승 + 일부는 USD 약세 동반
- 우연이 아니라 패턴

---

## 후보 Story 들 (3개, 경쟁 narrative)

### Story A: "두 다리 (Global macro + Industrial cycle) 가 모두 작동할 때"

**메커니즘**:
한국 시장의 outperform 은 **두 개의 독립 driver** 가 동시에 양수일
때 발생.

1. **Global macro 다리** — USD 약세 + US 금리 안정/하락 + 글로벌
   risk-on (VIX 안정). 이 환경에서 EM 으로 자본 유입, 한국이 그 중
   가장 큰 수혜자 중 하나.

2. **Industrial cycle 다리** — 반도체 가격 상승 사이클. Samsung +
   Hynix 의 이익 급증. 이게 KOSPI 의 ~25% 를 직접 끌어올림. 또한
   국내 자금도 이쪽으로 따라옴.

두 다리가 동시에 강하면 → "Korea outperform" 환경 → 외국인 + 기관
flow 도 강하게 양수 (그래서 우리 B-family signal 이 이 시기에 작동
한 것). 한 다리만 작동하면 → 중립 또는 마일드 → 우리 signal 불충분.
두 다리 모두 죽어있으면 → underperform → 어떤 long-only 도 손해.

**왜 이게 16년 데이터를 잘 설명하는가**:
- 2010: post-GFC, USD 약세 + 반도체 회복 → 두 다리 ✓
- 2011-2015: 다양한 macro 환경, 반도체는 mostly 약함 → 한 다리 또는
  둘 다 부족
- 2017: USD 약세 (DXY 큰 하락) + 반도체 super-cycle 시작 → 두 다리
  ✓ (gate-only 도 작동)
- 2018-2019: 미중 무역전쟁 + 반도체 cycle 끝남 → 한 다리 죽음
- 2020: COVID 후 USD 약세 + 반도체 수요 폭발 → 두 다리 ✓
- 2021: USD 강세 시작 + 반도체 후반부 + 한국 정부 부동산 정책 등
  → 다리 부분 죽음
- 2022: USD 초강세 + 반도체 침체 → 두 다리 모두 죽음
- 2023: USD 안정 + 반도체 회복 신호 → 다리 살아나기 시작 (실제로 우리
  carrier 2023 손실 비교적 작음 −1.5%, gate-only 도 비교적 덜 손해)
- 2024: USD 큰 강세 (yoy +14.5%) + 반도체 ambiguous → 다리 부족
- 2025: USD 약세 전환 + 반도체 + AI 수요 → 두 다리 ✓✓ (super strong)
- 2026 (부분): 연속

**Predictions**:
- P1: USDKRW yoy < 0% (KRW 강세) → 12개월 후 KOSPI return 평균 양수
- P2: DRAM spot 가격 3개월 상승 트렌드 → 6개월 후 KOSPI return
  평균 양수
- P3: P1 AND P2 동시 만족 → KOSPI 12개월 후 return ≥ +15%
- P4: P1 또는 P2 만 만족 (XOR) → KOSPI return 중립 (-5% ~ +10%)
- P5: 둘 다 만족 안 함 → KOSPI return 평균 음수 또는 0

**Falsification (Story A 가 틀렸음을 증명하는 것)**:
- F1: USDKRW yoy ≥ +5% (KRW 큰 약세) 이면서 12개월 후 KOSPI +20%
  이상이 한 번 이상 발생 → Story A 의 macro 다리 가설 깨짐
- F2: DRAM 가격 12개월 하락 트렌드인데 KOSPI 같은 12개월 +20% 이상
  → 반도체 다리 가설 깨짐
- F3: 두 다리 모두 죽었는데 (P1 음수 + P2 음수) KOSPI +10% 이상 →
  Story A 전체 깨짐
- F4: 두 다리 모두 살아있는데 (P1 양수 + P2 양수) KOSPI 음수 →
  Story A 전체 깨짐

### Story B: "Post-crisis Recovery 단일 사이클"

**메커니즘**: 한국 시장은 high-beta 회복 시장. 글로벌 위기 직후 V자
회복 단계 (할인율 압축 + cyclical 이익 회복 + 외국 자본 panic 후
re-entry) 에서만 강세. 그 외 기간은 underperform.

이게 단일 leg story 라 단순. 위기 = 2008-2009 (GFC), 2020 (COVID),
2022 (Fed 긴축). 위기 직후 = 2010, 2020 (H2), 2023-2026 (cumulative).

**Predictions**:
- P1: KOSPI 12개월 drawdown ≥ -30% 발생 → 그 후 12-24개월 KOSPI
  outperform (recovery)
- P2: 위기 후 첫 회복 연도가 가장 강함 (subsequent years 약해짐)

**Falsification**:
- F1: 위기 (KOSPI -30%) 직후 24개월 안에 회복 안 함 → Story B 깨짐
- F2: 위기 없는 안정 환경에서 KOSPI +20% 이상 → Story B 의 "회복기만"
  가설 깨짐 (2017 같은 해가 이에 해당? 2017 은 KOSPI 큰 상승, 직전
  위기는 2016 brexit 정도 — 위기라기엔 약함)

### Story C: "단순 USDKRW 단일 지표"

**메커니즘**: KRW 방향이 한국 시장의 모든 것을 결정. 다른 모든 변수
(반도체 가격, 미 금리, VIX 등) 는 USDKRW 와 상관관계 있어서 사실상
같은 정보. KRW 강세 = 외국 자본 유입 = KOSPI 상승. 끝.

**Predictions**:
- P1: USDKRW 5일 변화율 ≤ -1% (KRW 빠르게 강세) → 다음 20거래일
  KOSPI return 평균 양수
- P2: USDKRW 100일 트렌드가 KOSPI 100일 트렌드의 negative correlation
  ≥ 0.5

**Falsification**:
- F1: 위 상관관계가 0.3 이하 → Story C 의 KRW 우월성 깨짐
- F2: KRW 약세인데 KOSPI 강하게 상승하는 기간이 16년 중 30% 이상 →
  Story C 깨짐

---

## 추천 Story = **Story A**

이유:
1. **가장 mechanistic 한 설명** — "왜 그런가" 의 답이 두 다리 각각의
   메커니즘으로 명확
2. **16년 데이터를 가장 잘 설명** — 매년의 결과가 두 다리의 조합으로
   해석 가능 (Story B 는 일부 연도 - 2017, 2021 - 설명 어려움; Story C
   는 - 2017, 2020 같이 KRW 만 약하지 않은 경우 - 설명 약함)
3. **검증 가능한 5 predictions** — 명확한 falsification 가능
4. **두 독립 leg 구조** — 단일 지표의 가짜 alpha 위험 회피
5. **사용자 stated 목표와 부합** — "큰 spike 따라가기" = 두 다리
   모두 작동하는 드문 환경 잡기

Story A 를 primary 로 발전시키되, Story B 와 C 는 **반박 가설**로
유지 (Story A 가 falsification 되면 B 또는 C 로 회귀).

---

## Story A 의 더 구체적인 mechanism (Phase B 를 위해)

### Macro 다리 (외국인 자본 유입)
이 다리의 핵심 동인:
- **USD 약세 (DXY 또는 USDKRW)**: KRW 자산의 USD-기준 수익률 향상,
  외국 투자자의 FX 손실 우려 감소
- **US 금리 phase**: Fed dovish 시 EM 자산 매력 증가. Hawkish 시
  EM 매도
- **VIX / 글로벌 risk appetite**: VIX 저점 = risk-on = EM 매수
- **MSCI / FTSE rebalance**: discrete 이지만 의미있는 flow

검증 가능한 변수:
- USDKRW yoy / 5d / 20d momentum
- 미국 3m / 10y 금리 (보유)
- VIX (현재 미보유 - 필요)
- DXY (보유 USDKRW 로 부분 proxy)

### Industrial cycle 다리 (반도체 + 수출)
이 다리의 핵심 동인:
- **DRAM/NAND spot 가격**: 가장 직접적 leading indicator
- **반도체 재고 사이클**: 재고 줄어들 때 = 가격 상승 = cycle up
- **한국 월별 수출 데이터** (특히 반도체): 발표 시점 명확, leading
  indicator 됨
- **TSMC / Micron 같은 글로벌 peer 의 이익 가이던스**

검증 가능한 변수:
- DRAM/NAND spot 가격 시계열 (현재 미보유 - 필요)
- Samsung / SK Hynix 분기 실적 (현재 미보유 - 필요)
- 한국 월별 수출 데이터 (현재 미보유 - 필요)

### 두 다리의 상호작용
독립적이지만 종종 동시 강함 (글로벌 회복기). 예측 가능성:
- USDKRW 와 DRAM 가격 의 12개월 correlation 측정 필요. 만약 -0.5
  이상 negative correlation 이면 두 변수는 사실 같은 정보 — Story A
  의 "두 독립 다리" 가설 깨짐 → Story A 수정 또는 Story C 로 회귀.
- 만약 correlation 약함 (-0.3 ~ +0.3) 이면 두 변수가 독립 → Story A
  의 "두 다리" 가설 유지.

---

## 데이터 audit — predictions 검증에 필요한 것

### 보유 (사용 가능, 즉시)
| Data | Predictions 에서의 용도 |
|---|---|
| USDKRW (FRED) | P1, P3, P4, P5 의 macro 다리 |
| US 3m 금리 (FRED) | 부수적 — Fed phase |
| equity panels | KOSPI return 측정 |
| market_flow | 외국인+기관 행동 검증 (mediation analysis) |
| market_breadth | KOSPI proxy return 계산 |
| KOSPI200 선물 | 추가 derivative 신호 |
| Global futures (SP500/Nikkei/NASDAQ) | VIX 부분 proxy |

### 필요 (추가 수집 필요)
| Data | 우선순위 | 용도 |
|---|:---:|---|
| **DRAM spot 가격 시계열** (월별 또는 weekly) | **HIGH** | P2, P3, P4 의 반도체 다리 |
| **NAND spot 가격** | MED | DRAM 보조 |
| **VIX 시계열** | MED | 글로벌 risk-on/off |
| **한국 월별 수출 데이터** (특히 반도체) | MED | 반도체 다리 lagging 확인 |
| **Samsung/SK Hynix 분기 실적** | LOW | 검증용 |

DRAM 가격은 무료 데이터 (DRAMeXchange, TrendForce 등의 published series).
연구 목적 수집 가능. VIX 는 FRED 또는 CBOE 무료.

---

## Phase 진행 계획 (C002 부터)

이 thesis 가 OK 라면:

**C002 = 데이터 수집 + Predictions 정량화**
- DRAM 가격, VIX 데이터 수집 + schema 검증
- Predictions P1-P5 를 historical data 에 적용 가능한 form 으로 변환
- (예: "USDKRW yoy < 0%" 의 정확한 measurement: 일별 vs 월별, lag,
  rolling window 등)

**C003 = Story A predictions 검증 (16년)**
- P1-P5 각각의 사전 등록된 success/fail 기준 적용
- 5개 predictions 중 3개 이상 통과 → Story A 살아있음
- Falsification F1-F4 중 하나라도 발생 → Story A 큰 수정 또는 폐기

**C004 = (Story A 살아있다면) Strategy 설계**
- 두 다리의 conditional 구조
- 두 다리 모두 ON → long Korean equity (어떤 형태?)
- 두 다리 중 하나 OFF → 부분 노출 또는 cash
- 두 다리 모두 OFF → cash
- 사이즈 / 종목 선택은 별도 hypothesis

**C005 = True OOS 검증**
- 사용 안 한 데이터 또는 forward 에서 strategy 작동 확인

---

## Falsification commitment (사전 등록)

Mode C 정신:
- 이 thesis 의 falsification 기준을 사전 등록 (위 F1-F4)
- Predictions 검증 후 결과 그대로 인정. Story 끼워 맞추기 금지
- Story A 실패 시 → Story B 또는 C 로 honest 회귀
- 모든 Story 실패 시 → 정직한 project 종료

---

## Honest 우려

내가 자체적으로 짚어야 할 risks:

1. **Story A 가 너무 매끄러움** — narrative 의 함정. 16년 데이터를
   너무 잘 설명한다는 것은 어쩌면 과적합. 정량 검증 시 deltas 살펴봐야.

2. **2017, 2020 의 macro 다리 vs industrial 다리 attribution 모호** —
   둘 다 작동한 것은 맞지만 어느 다리가 main driver 인지 분리 어려움.

3. **USDKRW 와 DRAM 가격이 상관관계 높을 수 있음** — 둘 다 글로벌
   risk cycle 의 표현일 수 있어서. C002 에서 measurement 필요.

4. **B-family 의 16년 backtest 결과를 알고 thesis 쓴 점** — 일종의
   look-ahead bias. Story A 는 우리가 본 결과를 설명하기 위해 만들어진
   부분 있음. 새 데이터 (C005) 에서 forward test 가 진정한 검증.

5. **반도체 cycle 의 timing 측정 어려움** — DRAM 가격의 leading
   indicator 가치는 좋지만, "사이클 시작" 의 정의는 사후적임.

---

## 사용자에게 묻는 것

이 첫 draft 에 대해:

1. **Story A 의 큰 그림 — 동의?** 두 독립 다리 (Global macro + Industrial
   cycle) 의 골격이 한국 시장의 진짜 driver 라고 동의하는지.

2. **놓친 leg 있나?** Story A 에 빠진 중요 driver 가 있다고 보는지.
   - 중국 demand cycle 을 별도 leg 으로? (현재 industrial 다리에 implicit)
   - 한국 국내 정책 (정부 부동산, 금리)? (현재 빠짐)
   - 지정학 (북한, 미중)? (현재 빠짐)

3. **데이터 우선순위 동의?** DRAM 가격이 가장 high-priority 인지.

4. **Falsification 기준 충분히 strict?** F1-F4 가 narrative confirmation
   bias 방어로 충분한지.

이 draft 를 v2 로 발전시키기 전에 위 4가지 input 받고 싶어. 그 후
C002 (데이터 수집 + predictions 정량화) 진행.

---

## What this ticket explicitly is NOT
- ❌ 백테스트
- ❌ 새 코드
- ❌ Strategy 설계
- ❌ Predictions 의 정량 검증 (그건 C003)
- ❌ 최종 thesis (이건 v1, narrative 의 첫 정리)

## What this ticket IS
- ✓ Thesis 의 사전 등록 (검증 전에 글로 commit)
- ✓ Predictions 와 falsification 의 명시
- ✓ 데이터 needs 의 매핑
- ✓ 다음 phase 의 roadmap
