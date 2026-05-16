# Review — B005 (Relative-flow signal redesign)

## Verdict
**inconclusive (per pre-registered rules) — relative-flow alpha
hypothesis is partially validated but does not meet promote bar**

The most important result: **relative flow does fix the V-recovery
problem (2020 IS loss reduced from −0.39 to ~−0.05, an ~86 % loss
reduction)**, validating the diagnostic mechanism. But relative
flow has weaker raw alpha (~half of absolute) AND ~30 % higher
turnover, so net OOS goes negative once costs hit.

The pre-registered "BOTH variants fail H1 by margin (≤ −0.10) AND
both OOS < +0.541" kill condition was NOT triggered (relative
variants substantially fixed 2020), so this is genuinely
inconclusive rather than killed.

## One-line conclusion
상대 강도가 V자 회복 문제는 진짜로 고치지만 (2020 IS −0.39 → −0.05),
2025 spike 의 알파 절반 가량을 잃고 turnover 가 30 % 늘어 비용에 죽는다.
즉 "상대가 절대보다 좋은 알파다" 가설은 입증 안 됐고, 두 신호가 다른
국면에서 서로 다른 가치를 갖는다는 게 입증됨.

## Headline numbers (1× cost)

| variant | IS net | OOS net | IS hit | OOS hit | IS trades | OOS trades |
|---|---:|---:|---:|---:|---:|---:|
| (a) absolute baseline | −0.840 | **+0.641** | 0.391 | 0.419 | 1214 | 730 |
| (b) relative z-score | −0.805 | **−0.077** | 0.407 | 0.391 | 1520 | 1010 |
| (c) relative median-diff | −0.829 | **−0.055** | 0.406 | 0.392 | 1531 | 1002 |

## Cost-0 OOS (raw alpha) — the most revealing single comparison

| variant | cost-0 IS | cost-0 OOS | 1× IS | 1× OOS | cost eaten % |
|---|---:|---:|---:|---:|---:|
| (a) absolute | −0.643 | **+1.660** | −0.840 | +0.641 | 61 % |
| (b) z-score | −0.467 | **+0.801** | −0.805 | −0.077 | 109 % |
| (c) median-diff | −0.530 | **+0.832** | −0.829 | −0.055 | 107 % |

**Both relative variants have real raw alpha (~+0.80 OOS cost-0).**
That's about half of absolute's +1.66. They're not noise — but the
combination of weaker alpha + higher turnover means costs eat MORE
than 100 % of the alpha at 1× cost.

## Pre-registered hypothesis checks

| Hypothesis | Threshold | (b) actual | (b) pass | (c) actual | (c) pass |
|---|---|---:|:---:|---:|:---:|
| H1 (2020 IS) | ≥ 0 | −0.054 | ❌ (close) | −0.044 | ❌ (close) |
| H2 (OOS net) | ≥ +0.641 | −0.077 | ❌❌ | −0.055 | ❌❌ |
| H3 (2025 OOS) | ≥ +0.442 | +0.272 | ❌ | +0.430 | ❌ (just barely) |
| IS net ≥ B002 | ≥ −0.840 | −0.805 | ✓ | −0.829 | ✓ |

Promote: requires all four. Fails at H1, H2, H3 for both. **Promote
denied.**

Kill: requires both (b) and (c) failing H1 by ≥ −0.10 margin AND
both OOS < +0.541. Both at 2020 IS are above −0.10 (substantial
recovery from −0.39). Kill condition #1 not triggered. **Kill not
triggered.**

→ Inconclusive.

## Year-by-year (a)−(c) and (a)−(b) deltas

| year | (a) abs | (b) z | (c) rel | (b)−(a) | (c)−(a) |
|---|---:|---:|---:|---:|---:|
| 2018 | −0.378 | −0.506 | −0.473 | −0.128 | −0.094 |
| 2019 | −0.074 | −0.094 | −0.125 | −0.020 | −0.051 |
| 2020 | **−0.387** | **−0.054** | **−0.044** | **+0.333** | **+0.343** |
| 2021 | −0.249 | −0.280 | −0.306 | −0.031 | −0.057 |
| 2022 | −0.407 | −0.375 | −0.452 | +0.032 | −0.045 |
| 2023 | −0.106 | −0.295 | −0.276 | −0.188 | −0.170 |
| 2024 | −0.206 | −0.222 | −0.320 | −0.016 | −0.114 |
| 2025 | **+0.883** | **+0.272** | **+0.430** | **−0.612** | **−0.453** |
| 2026 | +0.128 | +0.285 | +0.279 | +0.157 | +0.150 |

### The diagnostic story is clean

- **2020 (V자 회복)**: 상대 변형들이 +0.33~+0.34 로 큰 개선. 가설이
  맞았다는 직접 증거.
- **2025 (강한 상승장 spike)**: 상대 변형들이 −0.45~−0.61 로 큰 손실.
  같은 메커니즘 (시장 평균 빼기) 이 spike 년에는 알파를 깎아냄.
- **다른 모든 해**: 거의 다 작은 차이 또는 약간 마이너스. 즉 상대
  변형은 두 극단 (V자 vs spike) 에서만 결정적으로 다르고, 평년에는
  차이가 작음.

→ 절대와 상대는 본질적으로 **다른 환경에서 가치를 가지는 신호**.
상대가 무조건 좋은 게 아니고, 절대가 무조건 좋은 것도 아님.

## Trade-set overlap matrix

| | (a) absolute | (b) z-score | (c) median-diff |
|---|---:|---:|---:|
| (a) absolute | 1.000 | 0.296 | 0.356 |
| (b) z-score | 0.296 | 1.000 | 0.550 |
| (c) median-diff | 0.356 | 0.550 | 1.000 |

(b) 와 (c) 는 서로 비슷 (0.55). (a) 와는 둘 다 약 30 % 만 겹침.
즉 상대 변형들은 절대와 진짜 다른 종목 풀을 선택. 신호 정의 변화의
효과가 단순 thresholding 효과가 아니라 본질적인 ranking 차이를 만듦.

## What this rules in / out

### Confirmed
1. **상대 강도 알파는 진짜 존재함**. cost-0 +0.80 OOS 는 noise 아님.
2. **V자 회복 문제는 신호 정의의 문제였음**. 절대 신호가 V자에서
   fail 한 것은 시장 전체 매수에 휩쓸렸기 때문이라는 가설이 데이터로
   입증됨.
3. **절대 신호의 OOS 알파의 상당 부분 (정확히는 알 수 없으나 큰
   비중) 이 실제로는 시장 베타 / 광범위 매수 효과**. 상대로 만들면
   그 부분이 사라지고 신호는 절반으로 줄어듦.

### Refuted
1. "상대가 절대보다 더 좋은 알파다" — 강하게 반박. 상대는 절반의
   raw 알파만 가짐.
2. "상대 신호가 V자 fix + 스파이크 캡쳐 둘 다 잘함" — 반박. 둘은
   trade-off 관계.
3. "신호 정의만 바꾸면 비용 문제도 같이 해결" — 반박. 상대 신호는
   오히려 turnover 30 % 증가.

### Open / unresolved
1. **상대 + 낮은 turnover trigger 조합이 가능한가?** B003 의 T3
   acceleration 은 turnover 를 약간 감소시켰음. 상대 신호 위에 T3 를
   끼우면 비용 파괴를 일부 회복할 수도. 단, 가설 stacking 위험.
2. **하이브리드 (절대 + 상대) 가 의미 있는가?** 두 신호가 다른 환경에서
   가치를 가지므로 적응형 조합이 가능할지도. 단, 메커니즘 명확하지
   않으면 patches stacking.
3. **5일이 옳은 lookback 인가?** 1d (acceleration only) 또는 10d
   (longer trend) 에서 상대-vs-절대 trade-off 가 어떻게 변할지 미지수.

## Cost-0 IS — also worth noting

| variant | cost-0 IS net |
|---|---:|
| (a) absolute | −0.643 |
| (b) z-score | −0.467 |
| (c) median-diff | −0.530 |

**모든 변형이 IS 에서 비용 0 에도 마이너스**. 이건 신호가 universal
alpha 가 아니라는 점을 다시 확인. B004 review 의 결론 ("이 신호 정의는
2025 spike 같은 특정 환경에서만 양수") 이 B005 에서도 유지됨.

다만 (b)(c) 가 (a) 보다 IS 에서 덜 마이너스 (cost-0 IS 에서 +0.18 ~
+0.11 개선). 상대 신호가 IS 환경에서는 절대 신호보다 약간 나음. 즉
상대 신호의 가치는 IS regime 에서 더 큼.

## Multiple-testing budget update

지금까지 비교한 alpha 변형 수: ~17 (B005 이전) + 2 (B005 의 (b)(c),
(a) 는 baseline 재검정) = **약 19개**. 다음 실험에서는 promote
기준이 더 엄격해야 함.

## Strategic interpretation — the bigger picture

B003 + B004 + B005 를 종합하면 일관된 메시지가 떠오름:

> **5일 누적 외국인+기관 flow 신호 (절대 또는 상대) 는 universal
> alpha 가 아니다. 다른 시장 국면에서 다른 부분이 가치를 가지는
> regime-conditional signal 이다.**

- 절대 = 시장 전체 매수가 강한 spike 년 (2025) 에 강함
- 상대 = 시장이 일관되지 않은 환경 (2020 V자, 2018 약세) 에 강함
- 둘 다 공통적으로 정상적인 추세 환경 (2019, 2021) 에서는 약함

이건 사용자의 "지수 + α + 큰 스파이크 따라가기" 목표와 충돌. 사용자
목표는 spike 캡쳐 우선이지만, 우리가 spike 캡쳐를 위해 절대 신호를
쓰면 V자 회복에서 깨지고, V자 회복 안전을 위해 상대 신호를 쓰면
spike 를 못 따라감.

## Possible next directions

### 옵션 A: B006 = 절대 + T3 acceleration trigger (single-point promote)
- B003 에서 T3 가 promote 보류된 상태. 이걸 B005 결과 본 뒤에 정식
  검증.
- 가설: T3 가 turnover 줄여 절대 신호의 비용을 추가로 절감.
- 단순. 새 가설 stacking 없음. B003 의 발견을 promote 단계로 진행.

### 옵션 B: B006 = 상대 + T3 trigger 결합
- B005 의 상대가 비용에 죽었음. T3 가 turnover 30% 감소시키면 cost-0
  +0.80 OOS 의 알파를 더 많이 살릴 수 있음.
- 단, 두 변경 (상대 + T3) 동시 적용은 multiple-testing 위험. promote
  안 되고 descriptive 로만 가야 함.

### 옵션 C: B006 = 단순 가속 신호 (절대 1d 강도) 단독
- 5일 누적 자체를 버리고, 1일 강도 (combined_flow_1) 위에서 진입/청산.
- B003 의 T3 정의 ("오늘 강도 > 5일 평균") 가 사실상 1일 vs 5일 비교.
  이걸 신호 자체로 격상.
- 새 alpha 정의 → 새 ticket.

### 옵션 D: 새 데이터 검증 (B006 또는 B007)
- 2008-2017 데이터 추가해서 같은 패턴 (regime-conditional, spike-dependent)
  이 옛 환경에서도 보이는지 확인.
- B005 의 결과가 strong enough 해서 옛 데이터로 가도 결론이 바뀔 가능성
  낮음. 다만 검증으로 값어치는 있음.

### 옵션 E: 정직한 후퇴 — gate-only 채택
- B004 variant (c) 가 OOS +0.24, IS −0.69 로 사용자의 "지수 +α"
  목표에 가장 단순하게 부합.
- 정교한 알파 추구를 멈추고 단순 regime-following 채택.
- "quant 전략" 이라기보다 "systematic regime-following" 이지만
  사용자 목표와 부합한다면 정직한 답.

### 내 추천: 옵션 A
이유:
1. **단순함** — 가설 stacking 없음. B003 의 발견 (T3 가 약간 더 좋음)
   을 정식 promote 절차로 검증.
2. **B005 결과와 무관한 독립 가설** — T3 의 가치는 turnover 절감.
   상대 vs 절대 결과와 무관하게 T3 가 비용에 도움이 되는지 직접
   확인 가능.
3. **다음 layer 의 baseline 명확화** — T3 가 promote 되면 B007 에서
   "T3 위에 또 다른 무엇 (필터, 청산, etc)" 을 검증 가능. T3 가
   promote 안 되면 트리거 역할은 immediate 로 확정.
4. **사용자의 spike-following 목표 보존** — 절대 신호 유지로 2025
   같은 해에서의 spike 캡쳐 능력 유지.

옵션 B/C/D 는 옵션 A 의 결과를 본 뒤 결정해도 늦지 않음.

## Do not do next
- 상대 신호 위에 추가 patches 끼우기. B005 가 inconclusive 라
  hypothesis 자체에 추가 patches 는 사전 등록 약속 위반.
- 상대 변형 안에서 z-score vs median-diff 만 비교하는 single-point
  ticket. 둘 다 fail 했음. (b)(c) 단독 검증 의미 없음.
- 상대 + 절대 hybrid 를 사후에 fitting. 메커니즘 사전 등록 없으면
  data-snooping.
- "z-score 변형 좀 더 손보면 OK 일 것" 같은 직관에 따라 정의 수정.
  사전 등록된 정의 그대로.

## Follow-up
- **B006 candidate** — T3 acceleration trigger 정식 promote ticket
  on B002 absolute carrier. 단일 변경 (trigger), 5-criterion
  promote logic.
- B006 결과 본 뒤 옵션 B (상대 + T3) 또는 옵션 D (옛 데이터) 검토.
