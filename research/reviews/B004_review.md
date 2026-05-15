# Review — B004 (Regime sensitivity diagnosis)

## Verdict
**inconclusive (functionally killing the "current signal + 200d
regime gate" composite)**

Strictly: no pre-registered Promote / Kill / Inconclusive condition
fires cleanly. The OOS (a)−(c) delta of +0.166 just misses both
the Promote bar (≥ +0.20) and the Kill bar (within 0.10). However,
the strategic implication is unambiguous: this composite does not
meet our pre-registered promote standard, and the signal as
currently defined does NOT add alpha on top of regime selection in
the IS period.

Per the pre-registered commitment in the B004 ticket, the next
experiment must NOT be another patch on this signal. It must be
either (i) new data or (ii) signal redesign.

## One-line conclusion
Regime gate cuts costs and limits IS losses, but adds no real alpha
in IS and recovers only ~70 % of the threshold improvement in OOS.
The "2025 spike does most of the work" pattern from B003 survives,
and gate-only equal-weight competes head-to-head with our flow
signal — which is exactly the Scenario B evidence the ticket was
designed to test for.

## Headline numbers (1× cost)

| variant | IS net | OOS net | IS hit | OOS hit | IS trades | OOS trades |
|---|---:|---:|---:|---:|---:|---:|
| (a) signal + gate | −0.721 | **+0.407** | 0.372 | 0.410 | 779 | 692 |
| (b) signal only (B002) | −0.840 | +0.641 | 0.391 | 0.419 | 1214 | 730 |
| (c) gate only equal-weight | −0.692 | +0.241 | 0.411 | 0.458 | 785 | 780 |
| (d) cash | 0 | 0 | — | — | 0 | 0 |

## Pre-registered promote criteria — check

| Criterion | Threshold | Actual | Pass |
|---|---|---:|:---:|
| H1 IS (a)−(c) | ≥ +0.20 | **−0.029** | ❌ |
| H1 OOS (a)−(c) | ≥ +0.20 | **+0.166** | ❌ (close miss) |
| H2 spread 2018 AND 2022 | both positive | 2018 +0.160, 2022 +0.016 | ⚠ asymmetric |
| (a) wins (c) in IS years | ≥ 3 of 5 | 3 of 5 (barely) | ✓ |
| Cost: 3× (a) beats (c) | yes | (a) −0.901 vs (c) −0.892 → (a) loses by 0.01 | ❌ |

**4 of 5 pre-registered promote conditions fail.** Promote denied.

## Pre-registered kill criteria — check

| Criterion | Threshold | Actual | Trigger |
|---|---|---:|:---:|
| OOS gate-only within 0.10 of signal+gate | yes → kill | actual gap +0.166 | NOT triggered |
| (a) OOS < (c) OOS | yes → kill | +0.407 > +0.241 | NOT triggered |

Strict kill criteria not triggered. Saved by OOS just barely
clearing the kill threshold.

## Year-by-year diagnostic (this is the heart of the result)

| year | (a) | (b) | (c) | (a)−(c) | gate ON / OFF days |
|---|---:|---:|---:|---:|---|
| 2018 (bear −17%) | −0.298 | −0.378 | −0.458 | **+0.160** | 124 / 120 |
| 2019 (+8%) | −0.110 | −0.074 | −0.084 | −0.026 | 170 / 76 |
| 2020 (V +30%) | −0.260 | −0.387 | **+0.219** | **−0.479** | 202 / 46 |
| 2021 (+4%) | −0.275 | −0.249 | −0.359 | +0.084 | 212 / 36 |
| 2022 (bear −25%) | −0.190 | −0.407 | −0.206 | +0.016 | 18 / 228 |
| 2023 (OOS +18%) | −0.194 | −0.106 | −0.293 | +0.099 | 227 / 18 |
| 2024 (OOS −10%) | −0.202 | −0.206 | −0.089 | −0.113 | 213 / 31 |
| 2025 (OOS big up) | **+0.868** | +0.883 | +0.280 | **+0.589** | 236 / 6 |
| 2026 (partial) | +0.128 | +0.128 | +0.463 | −0.334 | 82 / 0 |

### The decisive observation

The flow signal's value over a gate-only large-cap basket is
**−0.13 across all years EXCEPT 2025** (sum of 2018-2024 + 2026
(a)−(c) deltas, excluding 2025).

In 2025 alone, the signal contributed **+0.589**. The entire
"signal is alpha" story rests on one year.

### 2020 is particularly damning

2020 was a V-recovery (+30 % KOSPI) and the gate was ON 81 % of
the year. The simplest possible regime-beta strategy — buy top 5
large-caps when gate is ON, cash when OFF — made **+21.9 %**.
Our supposedly-smart flow signal + gate made **−26 %**. The
signal actively destroyed value in a year it should have ridden
the recovery.

This is hard to square with "the signal carries real alpha". It
strongly suggests **Scenario B** (the signal is selectively picking
up certain regime patterns, not a stable alpha).

### 2022 is also damning

The gate was OFF for 228 of 246 days (93 %). Both (a) and (c)
barely traded in 2022, and the contribution of the signal beyond
just being out of the market was +0.016 — essentially nothing.
The bear-year H2 hypothesis ("the gate should distribute
contribution across 2018 AND 2022 bear years") fails this asymmetry
test: 2018 contribution is 10× the 2022 contribution.

## Cost sensitivity diagnostic

| variant | cost 0 | cost 1× | cost 2× | cost 3× |
|---|---:|---:|---:|---:|
| **OOS** (a) signal+gate | +1.218 | +0.407 | −0.110 | −0.438 |
| **OOS** (c) gate only | +1.077 | +0.241 | −0.260 | −0.560 |
| OOS gap (a) − (c) | +0.141 | +0.166 | +0.150 | +0.122 |
| **IS** (a) signal+gate | −0.532 | −0.721 | −0.834 | −0.901 |
| **IS** (c) gate only | −0.482 | −0.692 | −0.817 | −0.892 |
| IS gap (a) − (c) | −0.050 | −0.029 | −0.017 | −0.009 |

Stable ~+0.14 OOS gap, stable ~−0.03 IS gap. Cost doesn't flip the
direction, so the result is robust on that axis.

The OOS gap shrinks to +0.12 at 3× costs (still positive, still
below 0.20 promote bar). At any realistic Korean retail cost regime,
the signal's alpha over regime beta is real but small.

## Decision in plain Korean

신호 + 게이트 조합은 promote 기준에 못 미친다. IS 에서는 신호 자체가
게이트만 쓰는 것보다 약간 못하고 (−0.03), OOS 에서는 +0.17 정도 더 좋지만
+0.20 사전 등록 기준에 닿지 않는다. 2025년 한 해의 +0.59 가 OOS 전체
이득의 거의 전부를 만들고 다른 해들은 제로 또는 음수에 가깝다.

특히 2020년 V자 회복기에 게이트만 쓰는 단순 대형주 동일가중이 +21.9 %
인데 우리 신호는 −26 %. 같은 게이트 ON 환경에서 신호가 더 안 좋은 종목을
골랐다. 이건 "신호가 진짜 알파가 있다" 와 일치하기 어려운 결과.

**결론**: 현재 정의된 5일 누적 외국인+기관 신호는 단독 alpha 라기보다는
**특정 장세에서만 작동하는 regime-conditional 신호**. 이 신호 위에 더
많은 layer 를 쌓는 것 (예: 더 많은 필터, 다른 트리거, 다른 청산) 은
사전 등록된 "B004 가 마지막 tweaking 실험" 약속에 위배.

## What this rules out

- **"단순한 regime gate 가 우리 신호를 살릴 것"** — 반박됨. 200d
  SMA gate 는 2018, 2022 의 대형 손실을 일부 막아주지만 2020,
  2024 의 신호 자체의 약점을 못 고친다.
- **"5일 누적 flow 가 universal alpha 다"** — 강하게 반박됨. 같은
  flow signal 이 2020 V자 (gate ON) 에서 −26 % 만들고 2025 spike
  (gate ON) 에서 +87 % 만든다. 같은 신호, 같은 게이트 상태, 정반대
  성과 → 신호가 reliably 신호가 아니다.
- **"좋은 트리거 + 좋은 게이트 = promote 가능"** — 동시에 반박됨.
  B003 의 T3 promote 시도도 보류했고, B004 의 gate promote 도
  실패했다. 같은 OOS 데이터로 더 많은 변형 비교는 multiple-testing
  inflation 만 더할 뿐.

## Multiple-testing budget update

지금까지 우리가 비교한 alpha 변형: 약 **15개** (B003 4 + B004 4 +
B001/B002/A001-A004/E001-E004 약 7). 이 데이터셋에서 더 비교를
계속하는 것은 점점 신뢰도가 떨어진다. 사전 등록 약속대로 **다음
실험은 새 데이터 또는 신호 재설계** 둘 중 하나만.

## What survives

- **거래비용은 결정적으로 중요하다.** Cost 0 에서 모든 변형이 OOS
  에서 강하게 플러스 (+1.0 ~ +1.7). Cost 1× 에서 절반 이하로 깎임.
  단기 추세 추종 전략의 본질적 비용 한계.
- **2018 bear year 에서 gate 가 신호를 도왔다.** (a)−(c) = +0.160.
  Gate 가 가치를 더하는 경우가 존재함은 확인.
- **R001 의 role-based 아키텍처는 새 컴포넌트 (regime gate, exit_on_gate_off)
  추가에 잘 작동했고, A001 byte-identical 회귀 확인됨.**
  엔진 확장이 backward compatible 하게 유지됨.

## Next experiment — two pre-committed options

### 옵션 I: 신호 재설계 (signal redesign)
현재 신호 정의 (5일 누적 외국인+기관 > 0, 신호 반전 청산) 를 버리고
다른 가설로 새 신호 정의. 후보:
- 상대 강도: 외국인+기관 net buy 를 KOSPI 평균 net buy 와 비교한
  z-score
- 가격 confirmation 결합: 신호 + 20일 신고가 돌파 또는 5일 SMA 위
- 다른 lookback: 1일 (acceleration only), 또는 10일 (longer)
- 청산 재설계: 시간 cap + 변동성 trail + 신호 반전 OR 결합

### 옵션 II: 새 데이터로 진짜 OOS 검증
2008-2017 데이터를 추가해서 현재 신호 정의가 옛 환경에서도 같은
패턴 (regime-conditional, 2025 같은 해에서만 강함) 을 보이는지 확인.
가설: 옛 데이터에도 같은 패턴 보이면 신호 정의가 본질적으로
regime-conditional 임을 더 강하게 입증. 새 데이터에서 패턴이 다르면
2018-2026 의 발견이 한 시대의 artifact.

### 내 추천: 옵션 I 먼저, 그 뒤 옵션 II
이유:
1. B004 의 2020 데이터 (gate ON, V자 회복, 신호 손해) 가 이미
   현재 신호 정의의 약점을 충분히 입증한다. 옛 데이터를 더 봐도
   결론이 크게 바뀔 가능성 낮음.
2. 신호 재설계는 새 hypothesis 를 만드는 일이라 더 가치 있는 활동.
3. 옵션 II 는 옵션 I 의 결과를 검증할 때 쓸 수 있는 OOS holdout
   역할로 더 유용.

## Do not do next
- 같은 신호 위에 추가 layer (vol filter, sector filter, market cap
  filter 등) 끼우기. 사전 등록 약속 위반.
- Regime gate 의 window 를 50/100/150 으로 스캔. 사전 등록 약속 위반.
- T3 acceleration trigger 를 carrier 로 채택. B003 에서 보류한 상태
  유지. 신호 자체가 promote 안 됐는데 트리거만 promote 는 의미 없음.
- 2025 spike 만 분리한 별도 분석을 promote 근거로 사용. 사후 분리는
  cherry-picking.

## Follow-up
- **B005 candidate** — 신호 재설계 ticket. 새 hypothesis 사전 등록.
  현재 carrier 의 약점 (2020 V자 fail, 2025 spike 의존) 을 가설
  설계 동기로 명시.
- B005 결과 본 뒤 옵션 II (옛 데이터 추가) 검토.
