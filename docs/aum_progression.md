# D013 AUM Progression (지피티 권장)

단계적 live deployment. **각 단계 4 분기 PASS 후 다음 단계**.

| 단계 | AUM | 조건 |
|---|---|---|
| Paper trading | 0 | 4 분기 추적 |
| Pilot 1 | ≤ 10억 원 | Paper go/no-go 통과 |
| Pilot 2 | ≤ 30억 원 | Pilot 1 4 분기 PASS |
| Pilot 3 | ≤ 100억 원 | Pilot 2 4 분기 PASS |
| Full | ≤ 500억 원 | Pilot 3 4 분기 PASS + execution desk 준비 |
| Stress 상한 | ≤ 1000억 원 | 운영위 / 수동 승인 (max participation 49%) |

## 각 단계 평가 기준

- Paper trading: docs/live_pilot_criteria.md 10 criteria
- Pilot 1-3: 동일 기준 + actual slippage / IS 누적 추적
- Full: institutional execution desk 룰
- Stress: 단일 종목 max participation < 30% 유지

## 단계 전환 조건 (사전 등록)

| 항목 | 임계 |
|---|---|
| 4 분기 누적 수익 (vs paper baseline) | ≥ -20pp |
| Implementation shortfall 평균 | ≤ 30 bps |
| Slippage 평균 | ≤ 20 bps |
| Process incidents | 0 critical |
| Data pipeline uptime | ≥ 99% |

## 단계 후퇴 (regression)

다음 발생 시 이전 단계 또는 paper 로 후퇴:
- 누적 수익 차이 > 30pp
- Implementation shortfall 분기 > 50 bps
- Data pipeline 중대 오류
- D013 신호 산출 실패
