# Review — C003 (Monthly macro-gated Korean equity strategy v1)

## Verdict
**INCONCLUSIVE** per literal pre-registered 5-criterion (3/6 PASS).
Per pre-committed fallback, **next ticket = C004 = quarterly horizon
test of same strategy**.

But honest interpretation: only H3 (spike capture, partial) truly
PASSES. H4 and H6 pass by formula quirks (sign convention and
ratio-of-negatives respectively), not by spirit.

The strategy improves substantially over B-family (-54% vs B011 -95%
and B010 -88%) but still loses 54% over 16 years while cash makes 0%.

## One-line conclusion
월별 매크로 gate 가 B-family 의 catastrophic 손실은 40pp 절반 정도로
줄였지만, 여전히 누적 -54% 음수. 2020 V자 (+23%) 와 2025/2026 spike
(+13%/+24%) 일부 캡쳐했으나, 2018 disaster (-44%) 와 60% 기간 cash
(missed market gains) 가 손실 누적.

## Headline numbers

### V1 (macro-gated mcap top-5, monthly)
| Metric | Value |
|---|---:|
| Cumulative net (16 yr) | **-54.17%** |
| Annualized return | -5.08% |
| Annualized vol | 19.07% |
| Sharpe | -0.27 |
| Max drawdown | **-73.47%** |
| Positive years | 3 of 16 |
| Regime ON share | 40.54% |

### Comparison vs other strategies (16-year cumulative)
| Strategy | Cumul net |
|---|---:|
| C003 V1 (macro-gated monthly) | **-54.17%** ← 본 결과 |
| B010 V1 (flow carrier T3+F3) | -87.8% |
| B011 V1 (gate-only daily mcap) | -94.79% |
| Cash | 0% |
| V2 KOSPI proxy (survivor-biased) | +2009% |
| KOSPI 실제 buy-and-hold (추정) | ~+100-150% |

→ **C003 는 B-family 보다 명확히 개선**. 그러나 still negative + 어떤 합리적 KOSPI baseline 보다도 underperform.

## Hypothesis verdict (literal vs honest)

| # | Criterion | Threshold | Value | Literal | Honest |
|---|---|---|---:|:---:|:---:|
| H1 | Cumul > 0 | > 0 | -54.17% | ❌ | ❌ |
| H2 | vs KOSPI within 30pp | ≥ -30pp | -2064pp | ❌ | ❌ |
| H3 | Spike capture | ≥ 2/3 | 2/3 (2010=0%, 2025+, 2026+) | ✓ | ⚠️ (2010 zero) |
| H4 | Max DD better than V2 by 5pp | V1 DD < V2 DD - 5pp | V1 -73, V2 -34 | ✓ literal | ❌ V1 DEEPER by 39pp |
| H5 | Positive years ≥ 8 | ≥ 8 | 3/16 | ❌ | ❌ |
| H6 | net/cost-0 ≥ 0.7 | ≥ 0.7 | 1.31 | ✓ literal | ⚠️ (ratio of negatives meaningless) |

Literal: **3/6 PASS = INCONCLUSIVE**.
Honest: 1/6 truly PASSES (H3 partial), 2/6 literal-pass-but-meaningless, 3/6 clear FAIL.

## Year-by-year breakdown (V1 yearly net)

| Year | V1 | V2 KOSPI proxy | V1 가 잘됐나? |
|---|---:|---:|---|
| 2010 (post-GFC recovery) | **0%** | +33% | OFF entire year — missed |
| 2011 (Eurozone) | -13% | +0% | ON 일부, lost |
| 2012 | -6% | +19% | ON 일부, lost |
| 2013 | -5% | +6% | ON 일부, lost |
| 2014 | -13% | +6% | lost |
| 2015 (China crash) | **0%** | +17% | OFF entire — missed |
| 2017 (rally) | -2% | +32% | mostly OFF — missed |
| **2018 (bear)** | **-44%** | -8% | **disaster — ON during bad year** |
| 2019 | **0%** | +17% | OFF — missed |
| 2020 (V-recovery) | **+23%** | +53% | ✓ captured partially |
| 2021 | -17% | +13% | bad ON timing |
| 2022 (bear) | **0%** | -18% | ✓ correctly OFF |
| 2023 (rally) | -7% | +33% | bad ON timing — missed |
| 2024 (조정) | -5% | +3% | small loss |
| **2025 (spike)** | **+13%** | +105% | partial capture |
| **2026 (partial)** | **+24%** | +73% | partial capture |

### 핵심 패턴

**잘된 것**:
- 2022 bear 회피 (+0% vs V2 -18%) — gate 정상 작동
- 2020 V-recovery 부분 캡쳐 (+23%) — 핵심 성공 case
- 2025 + 2026 spike 부분 캡쳐

**못된 것**:
- 2018 disaster (-44%): regime ON 인데 V2 보다 36pp 더 손해. **5종목 집중 risk** + 잘못된 종목 선택
- 2010 entirely missed (post-GFC + 유럽위기 → VIX high → regime OFF)
- 2015, 2019 missed (bad timing of OFF)
- 2017 (KOSPI +32%) 대부분 missed
- 2025 spike +105% 중 단지 +13% 만 캡쳐

## 구조적 진단 — 왜 -54% 인가

### 1. Regime ON share 40% 의 의미
60% 기간 cash. KOSPI 가 16년에 +100-150% 가는데 60% 시간 cash 면 ~40-60% 만 참여. 그런데 그 40% 시간에 추가로 잘못된 종목 선택 / 비용으로 손실. 결과 -54%.

### 2. Top-5 mcap 집중 risk
5종목 집중. 한국 시가총액 상위는 Samsung Electronics, SK Hynix, NAVER, Hyundai, LG 같은 거대 비중. 2018 같이 이들 종목 하락 시 -44% 같은 catastrophic loss.

→ **Strategy form V1 의 본질적 weakness**: macro gate 가 옳아도 selection 단계 (top-5 mcap) 가 너무 concentrated.

### 3. 3-signal majority vote 의 conservatism
세 변수 중 2개 favorable 요구. VIX 가 종종 high 라 (post-crisis 시기, COVID 시기) 자주 OFF. 가장 좋은 진입 시점 (post-crisis recovery 초입) 을 놓침.

→ Threshold 가 너무 strict. "Recovery 시작 직전" 의 VIX 가 elevated 한 시기를 잡지 못함.

### 4. 2018 disaster 의 의미
2018: USDKRW yoy +4% (mild 약세, 음수 보다 큼), VIX 평균 ~16 (양호), DXY yoy +5% (약세). 2 of 3 favorable 인지 아닌지 marginal. 일부 시기 ON → 진입 → 손해.

이건 regime gate 의 한계. Forward-looking 정보 없이 과거 12개월 momentum 만 보고 ON/OFF 결정 → 추세 변화 시점 lag.

## What this tells us

### 정보 1: 매크로 horizon 이 옳음 (확인)
- Daily B011: -94.79%
- Monthly C003: -54.17%
- 40pp 개선. Monthly granularity 가 daily 보다 명확히 나음.

### 정보 2: 매크로 gate alone 으로는 부족 (확인)
- Daily macro fail (B011, B007/B009 모두 fail)
- Monthly macro 도 fail (C003 -54%)
- Macro gate 의 information 가치는 있으나 **strategy 의 selection / size / form 도 동시에 의미 있음**

### 정보 3: Selection 단계 (top-5 mcap) 가 큰 weakness
2018 -44% disaster 가 결정적. 5종목 집중이 macro 가 옳아도 wrong stock 선택 시 catastrophic.

### 정보 4: Cost reduction 은 큰 도움 (확인)
B-family vs C-family 의 명확한 비용 차이. Monthly rebalance = trade count 큰 폭 감소.

## Mode C 정직성 — 사전 등록한 fallback 진행

C003 ticket 에서 commit:
> "INCONCLUSIVE → C004 = quarterly horizon 재검증 (pre-committed fallback)"

3/6 = INCONCLUSIVE 이니 strict Mode C: C004 = quarterly 진행.

**하지만 honest 추가 고민**:
- 진짜 문제가 horizon (monthly vs quarterly) 인가?
- 아니면 selection (top-5 mcap 집중) 인가?
- 아니면 threshold (2 of 3 vs 1 of 3) 인가?

C004 quarterly 만으로는 selection 또는 threshold 문제 해결 못함. 사전 commitment 따르되 동시에 **C005 candidates 미리 검토**:

- **C005a: Selection 변경** — top-5 mcap → broader basket (top-20, 또는 KOSPI ETF proxy) → 집중 risk 완화
- **C005b: Threshold 변경** — 2 of 3 → 1 of 3 (덜 conservative, ON share 증가) — 단 cherry-picking risk
- **C005c: Macro v2 deepening** — 매크로 변수 더 추가 (VIX 외에 ISM PMI 등) — discipline 정통

## 4가지 다음 단계

### Option α: Strict Mode C → C004 = quarterly horizon
- 사전 commit 그대로 진행
- 결과 비슷하게 negative 일 가능성 큼 (horizon 만 바꾼다고 selection / threshold 안 고침)
- 그래도 pre-commit 약속 honor

### Option β: 사전 등록한 가능성 외 다른 진단 먼저
- C004 = monthly 유지하되 selection 변경 (broader basket 검토)
- 또는 C004 = monthly 유지하되 threshold 완화 (1 of 3 ON)
- ⚠️ pre-registered fallback 변경 = mode B 위반 risk

### Option γ: Macro v2 deepening
- 3개 변수 → 더 추가 (US ISM PMI, oil 등)
- C001 v2 의 macro deepening roadmap 따라 v2 정의
- C004 = monthly + 매크로 v2

### Option δ: 전체 strategy form 재고
- Macro gate + concentration selection 의 조합이 본질적 weakness
- 다른 strategy form (예: macro gate + 가중 KOSPI ETF proxy holding)
- 더 fundamental redesign

## 내 추천 — **Option α (C004 quarterly) 진행** + **Option γ 사전 commit**

이유:
1. **Mode C 약속 honor**: C003 ticket 에서 quarterly fallback 사전 commit 했음. Strict 적용.
2. **단순함 우선**: Selection / threshold 변경은 multi-variable 변경. 한 번에 하나만 변경 discipline.
3. **Quarterly 결과 본 후 진단 더 명확**: Quarterly 가 monthly 보다 substantially 좋으면 → horizon 이 문제. 비슷하면 → horizon 아닌 다른 문제 (selection/threshold) 임을 확인.
4. **Macro v2 는 자연 다음 step**: C004 (quarterly) 결과 본 뒤 C005 = macro v2 (변수 추가) 진행 — 사전 commit 가능.

순서:
- **C004 = quarterly monthly horizon 의 same strategy** (현 macro v1 으로)
- C004 결과 본 뒤:
  - 만약 quarterly 도 INCONCLUSIVE/FAIL → C005 = macro v2 deepening (variables 추가)
  - 만약 quarterly 명확히 좋음 → C005 = sector layer or selection refinement

## Do not do next
- Selection 형태와 horizon 을 동시 변경 (multi-variable change)
- Threshold (2 of 3) 를 결과 보고 변경 (cherry-pick)
- 2018 disaster 만 따로 보고 strategy fix (사후 합리화)

## Follow-up
- **C004 = quarterly horizon 동일 strategy** (pre-committed fallback)
- After C004 결과: C005 candidate decision (macro v2, selection, or sector layer)
