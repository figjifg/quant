# Review — B003 (Trigger-role exploration)

## Verdict
**descriptive (no promote)** — per ticket rules. T3 (acceleration)
is the clear standout candidate; recommend a follow-up B004 ticket
that formally promotes T3 as the new trigger carrier using single-
point criteria, after which T3 can be the trigger of subsequent
single-role experiments.

## One-line conclusion
사용자가 처음 제안한 "당일 강도 > 5일 평균" 트리거가 4 후보 중 유일하게
T1 baseline 대비 OOS net 과 cost-0 둘 다 개선시킨다. 회전율 절감이
아니라 동일 trade pool 안에서 더 좋은 subset 선택의 결과.

## 4 후보 OOS 비교

| 후보 | net | hit | trades | avg hold | cost-0 net | turnover |
|---|---:|---:|---:|---:|---:|---:|
| T1 immediate (B002) | +0.641 | 0.419 | 730 | 5.54 | +1.660 | 144.4 |
| T2 freshness | −0.350 | 0.410 | 851 | 4.73 | +0.144 | 166.6 |
| **T3 acceleration** | **+0.780** | 0.420 | 724 | 5.58 | **+1.875** | 142.8 |
| T4 persistence_3d | −0.182 | 0.436 | 826 | 4.61 | +0.416 | 165.1 |

T1 = B002 정확 재현 ✓ (sanity check)
T3 ↑ vs T1: net **+0.14**, cost-0 **+0.22**

## 결정적인 진단 — Trade Overlap Matrix

| Pair | Jaccard | 의미 |
|---|---:|---|
| T1 vs T3 | **0.617** | T3 가 T1 의 trade pool 안에서 더 나쁜 175개 걸러냄 |
| T1 vs T2 | 0.121 | 완전히 다른 trade pool 선택 |
| T1 vs T4 | 0.060 | 거의 disjoint |
| T2 vs T4 | **0.000** | 두 trade set 단 한 개도 안 겹침 |
| T3 vs T2/T4 | 0.13 / 0.06 | T3 는 T2/T4 와도 거의 안 겹침 — T1 의 정제된 부분집합 |

**T3 의 본질**: T1 이 잡은 730 trade 중 555 (76%) 를 그대로 가져가고
T1 단독 175 trade 를 걸러냄. 그 175 가 평균적으로 나쁜 trade. cost-0
+0.22 개선은 곧 "걸러낸 175 trade 가 합산하여 −0.22 정도의 raw
contribution" 의미.

→ acceleration 트리거의 가치는 **선별 (selection)**, 회전율 감소가 아님.

## T2/T4 가 왜 안 됐나

**T2 (freshness)** — 필터가 False→True 전환되는 첫날에만 진입. mental
model 에서는 trade 수가 줄어들 것 같지만 실제로는 851 trade (T1 보다 많음).
이유: 같은 종목이 청산되고 다음에 다시 양수 전환 → 또 freshness. 즉 청산 후
재진입까지 막지 않는 정의. cost-0 +0.14 — 진짜 신호 가치도 거의 zero.

**전환 순간 자체에 알파 없음.** 외국인+기관이 "이제 들어오기 시작" 한 그
첫날이 특별히 의미 있는 거 아니라는 데이터 증거.

**T4 (persistence_3d)** — 3거래일 연속 필터 양수 후 진입. 마치 추세 확인
후 진입처럼 보이지만 실제로는 trade 수 826 (T1 보다 많음) 이고 hit rate 0.436
(T1 보다 살짝 높음). 그러나 net −0.18, cost-0 +0.42.

**3일 지속을 기다리는 동안 알파의 첫 부분이 이미 끝남.** 늦은 진입의 비용.

## T3 가 왜 됐나

T3 = `combined_flow_1(T) > combined_flow_5(T) / 5` — 오늘 하루치 강도가
5일 평균보다 강함.

해석 가능성:
1. **가속 신호** = 자금 유입이 가속 중인 시점에 진입. 정상 흐름이 아닌
   확장 흐름.
2. **품질 필터** = 약한 매수일이 아닌 강한 매수일에만 진입. 약한 진입은
   추세 안 갈 가능성 큼.
3. **사용자의 원래 직관** — 처음 신호 재정의 논의 때 "당일 강도가 5일
   평균보다 강하면" 트리거가 좋을 거라 제안한 그것이 데이터로 입증됨.

T3 의 cost-0 +1.875 = 신호의 진짜 정보 가치가 raw 알파로 약 **연 55%**
(3.4년 OOS 환산). T1 의 +1.66 (연 49%) 대비 +0.22 raw 알파 추가 추출.
비용도 약간 적어서 (turnover 142 vs 144) net 도 동시에 좋아짐.

## 가장 정직한 caveat — Multiple Testing 위험

B003 에서 4 candidate 를 동시 비교 → 하나가 우연히 좋아 보일 inflation
risk 존재. T3 의 +0.14 net 차이가 통계적으로 의미 있다는 보장 없음.

다만:
- T3 의 개선이 cost-0 에도 나타남 (raw 신호 가치 자체가 다름) → 비용
  arithmetic 만의 결과 아님
- T3 와 T1 의 trade 76% 중첩 → 같은 universe·exit 위에서 부분집합 선택의
  결과로 차이 해석 가능
- T2/T4 가 모두 손해 → "어떤 트리거나 다 잘 안 됨" 의 nullhypothesis 는
  reject. trigger 역할 안에서 특정 형태만 의미 있다는 패턴.

이 정도면 T3 promote 후보로 **다음 단계 고려할 만함**. 단 multiple testing
inflation 인지하고 진행.

## 추천 — B004 단일 점 promote ticket

B003 룰 대로 T3 를 promote 하려면 **별도 B004 ticket 으로 single-point
re-validation** 필요. 이건 새 backtest 가 아니라 **formal carrier 변경
문서화** — 같은 데이터·기간이라 숫자는 동일하지만:

- T3 (acceleration) 을 새 trigger carrier 로 사전 등록
- standard 5-criterion verdict logic 적용
- 다음 single-role 실험들 (filter / ranking / exit) 의 carrier 기준 명확
- 만약 promote 통과 안 되면 carrier 변경 없이 다른 trigger 도 시도

또는 user 가 procedural 단계 생략 원하면:
- T3 를 informal 하게 새 carrier 로 채택
- B004 = 다음 role 탐색 (filter, ranking, 또는 exit) — T3 trigger 위에서

내 추천: **B004 = T3 single-point promote ticket**. 빠르긴 procedural
하지만 다음 실험들이 명확한 carrier 위에서 진행되도록.

## 그 외 진단 가치

- B003 에서 **trigger 역할 자체가 의미 있다는 게 처음 입증** 됨. T2/T4 가
  손해 본 건 "잘못된 trigger 는 진짜 손해" 라는 의미 → trigger 신중히
  선택해야 함.
- T3 가 winner 인 건 R001 의 모듈화 + B002 의 alpha-exit 위에서 가능한
  것 — B002 cap_only carrier 였으면 T3 가 trade 수 줄여도 차이가
  20일 보유 회전율 절감 효과에 묻혔을 듯.
- Multiple testing 인지하면서 한 후보 (T3) 만 promote 절차로 — 4 중 가장
  좋은 것 무조건 채택이 아닌 cost-0 와 net 둘 다 개선된 단 하나만.

## 무엇을 하지 말 것

- T3 의 정의를 사후 튜닝 금지. `combined_flow_1 > combined_flow_5 / 5`
  사전 동결된 형태 그대로.
- T2/T4 의 정의를 손봐서 "이거 약간 바꾸면 잘 될 수도" 시도 금지.
- B004 promote 가 통과되기 전까지 T3 를 다른 ticket 의 carrier 로 사용
  금지 — 절차적 일관성 위해.

## Follow-up
- **B004 candidate** — single-point promote ticket for T3 acceleration.
- 후속 role 탐색은 B004 promote 결과 본 후 carrier 결정 후 진행.
