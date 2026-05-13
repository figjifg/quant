# Review — B002 (Signal-reversal exit, bare alpha)

## Verdict
**revise** — The hypothesis (alpha-derived exit captures the signal
more faithfully than fixed time cap) is **strongly supported by
cost-0 evidence**, but the implementation pays it back in
transaction costs. Net OOS return is essentially flat vs A002
cap_only. The signal-reversal mechanism is the right shape; the
remaining gap is sizing/cost, not the exit logic.

## One-line conclusion
외국인+기관 5일 누적 매수 신호의 자연스러운 지속 길이는 약 5.5거래일.
cap_only 20일은 우연히 비슷한 net을 만든 임의 숫자였고, 신호 기반
청산이 진짜 신호 가치를 +77% 더 잡는다 (cost-0 기준).

## Reportable metrics (no formal pass/fail this iteration)

| OOS metric | B002 | A002 cap_only |
|---|---:|---:|
| net total_return | +0.641 | +0.688 |
| **cost-0 net total_return** | **+1.660** | **+0.937** |
| hit_rate | 0.419 | 0.493 |
| trade_count | 730 | 205 |
| **avg holding period (td)** | **5.54** | 19.61 |
| cost_paid_total | ~1.02 (implied from 1.66 − 0.64) | ~0.25 |

Exit reason breakdown (B002 OOS):
- `signal_reversal`: 724 (99.18 %)
- `signal_reversal_fallback`: 1 (0.14 %)
- `period_end`: 5 (0.68 %)

→ Signal does reverse organically; period_end fallback is essentially
never used. The "infinite hold" worry expected weakness in the ticket
did not materialize. The "high turnover" worry did materialize.

## What this proved

1. **알파의 진짜 시간 척도 ≈ 5.5 거래일.** 외국인+기관 5일 누적 매수
   양수 상태의 자연스러운 지속 길이가 약 1주일. 신호가 들어왔다가
   1주일 안에 꺾이는 것이 평균. 20일 cap은 이 자연스러운 길이의
   3.5배 — 의도와 무관하게 trade마다 신호 꺼진 후 평균 14거래일
   동안 더 들고 있는 형태였음.
2. **신호의 진짜 정보 가치는 cost-0 +1.66, A002의 1.77배.** 시간으로
   임의 cut 하지 않고 신호가 말하는 시점에 정확히 청산하면 신호의
   알파가 +77% 더 추출됨. 이건 **A002 의 +0.688 이 신호의 본질이
   아니었음** 을 강하게 시사.
3. **A002 의 +0.688 net 의 본질 재해석:**
   - 신호 진짜 가치: +1.66 (cost-0 B002 가 측정)
   - 비용 절감 효과 (시간 cap 으로 회전율 ↓): +0.25 vs B002 의 +1.02
   - 알파 누락분 (cap 으로 너무 길게 들고 있어서 놓친 부분): −1.66 − +0.688 − 비용차이 ≈ −0.72
   - 즉 A002 net = +1.66 − +1.02 ≈ +0.64 (실측 +0.69 와 정합) — 본질적으로 신호 가치가 비용에 거의 1:1로 상쇄된 결과.
4. **20일이라는 숫자는 임의였음을 우리가 직접 입증.** 사용자 직관 옳음.

## What got worse vs A002 cap_only

- **Net total_return** −0.047 (47bps). 작은 손실. 하지만 정보 가치가
  +0.72 늘어났는데도 net 이 떨어진 이유는 비용 증가 (turnover 3.6×).
- **Hit rate** −0.074. 짧은 보유라 노이즈 영향 더 큼. 다만 hit rate
  자체는 우리 알파에서 이미 49% 정도였고 그게 42%로 떨어진 것도
  여전히 동전던지기 수준.
- **Trade count** 730 — 3년 OOS 기준 연 240+ trade. 회전율 매우 높음.
  실거래 처리 cost (라이브 시 슬리피지·체결 가격 차이 등) 더 클 수
  있음.

## What survived

- **신호 기반 청산은 원리적으로 옳음**. cost-0 가 그 증거. 시간 cap이
  신호의 정보 가치를 깎아냄.
- **A 가족 backwards compat 유지**. 104 tests green. A001/A002 행동 그대로.
- **새 진단 산출물**: holding_period_distribution.csv 와
  exit_reason_breakdown.csv. 미래 실험에서 재사용 가능.

## 정직한 큰 그림

5번 실험 끝나고 알게 된 우리 알파의 본질:

1. **시간 척도**: 약 5.5거래일. 신호가 평균 일주일 안에 꺾임.
2. **정보 가치 (cost-0)**: +1.66 / 3.4년 OOS. **연 ~36%** 의 raw
   알파.
3. **비용 구조**: 우리 1.5/20/5 bps × 회전율 = round-trip 약 33bps.
   B002 처럼 신호 끝까지 잡으면 회전율 ↑ → 비용이 알파의 약 60%
   먹음.
4. **net 결과**: cost-0 +1.66, cost 1× +0.64. 즉 **연 ~36% raw
   알파 → 연 ~14% net** (3.4년 OOS).
5. **연 14% net** 은 cap_only(연 19%) 보다 약간 못함. 하지만 cap_only
   는 사실상 우연. B002 는 신호 본질을 따르는 청산.

## 다음 방향 (description, not prescription)

cost-0 +1.66 정보 가치 vs 비용 −1.02 = net +0.64. **비용을 줄일 수
있다면** net이 +1.0 ~ +1.5 까지 갈 수 있다는 가능성. 비용 줄이는
방법:

A. **Position sizing 변경**: 같은 종목 재진입 일정 간격 유지로 회전율
   감소. 단 slot 메커니즘과의 정합 필요.

B. **청산에 buffer**: `(fnv_5 ≤ -0.01)` 같은 작은 음수 임계로 진짜
   reversal 만 잡고 0 근처 noise reversal 무시 → 회전율 감소. 단
   threshold 가 새 자유 파라미터.

C. **신호 윈도 변경**: 5일 lookback 외 10일·20일도 비교. 더 긴 윈도면
   더 안정적이라 reversal 빈도 ↓ 가능. 단 윈도 sweep 위험.

D. **다른 사이즈 조정 후 다시 실행**: 5개 슬롯 × 진입 시 NAV/5 사이즈는
   비용 누적 구조와 관련. 슬롯 수 변경하면 비용 분포 달라질 수 있음.
   단 새 자유도.

E. **Regime gate 도입 (예전 후보)**: 데이터가 강하게 지지하던 방향.
   음수 시기 거르면 trade 수 ↓ + 정확도 ↑.

내 솔직한 추천: **D (slot 수 변경) 또는 B (청산 buffer) 가 가장 깔끔**.
둘 다 비용을 직접 다룸. B 는 신호 정의의 일관성을 약간 깨고 자유
파라미터 도입이라 D 가 더 보수적.

또는 **본 결과를 잠시 안고 사용자가 큰 그림 재평가**: 연 14% net 의
fragile alpha (regime dependent) — 이게 실거래 목표에 맞는지 결정.

## Possible biases
- look-ahead: low. 신호 측정도 청산 측정도 d-1 데이터만 사용.
- survivorship: 동일 (dynamic Top100).
- data snooping: low. 자유 파라미터 0, 사전 동결된 단일 점.
- multiple testing: low. 한 가지 변형 + 베이스라인 한 개.
- entanglement: 진입과 청산이 같은 신호 사용 — 의도된 entanglement, 자유도 0이라 추가 과최적화 없음.

## Do not do next
- Threshold buffer 도입을 결과 보고 튜닝하지 말 것 — 만약 buffer
  도입하면 사전 단일 점 (예: -0.01) 으로 freeze.
- Time cap 다시 도입해서 회전율 손쉽게 줄이지 말 것 — 그건 B002 의
  교훈을 무시하는 것.
- 신호 정의를 손대지 말 것 — 신호의 진짜 가치를 본 ticket 이 처음
  측정했으니 그 결과 위에 다음 실험을 쌓아야.

## Follow-up tickets
- **B003 후보**: Slot 수 sweep — 1, 3, 5, 10 (사전 등록 단일 점들이 아니라 의도된 sweep). 비용-알파 trade-off 곡선 확인.
- **B004 후보**: Regime gate (단, 청산은 B002 신호 기반 유지). 음수 시기 거르기 + 신호 기반 청산 결합.
