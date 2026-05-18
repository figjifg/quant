# P006 — Live pilot go/no-go criteria + execution rule

## 상태
계획됨

## 이게 무슨 ticket 인가

지피티 권장 마지막 production validation 단계. P006 = paper trading
후 live pilot 진입 조건 + execution rule 사전 등록.

핵심: **paper trading 결과 보기 전에 criteria 동결** (사후 fitting 회피).

## 구성요소

### A. Execution rule (P002 unfavorable fill FAIL 의 mitigation)

지피티 권장:
- 시장가 (market order) 사용 금지
- 다음 거래일 시가/종가/VWAP/TWAP 사용
- Participation rate 제한 (예: 종목당 ≤ 5%)
- 분할 주문 (large order)
- Implementation shortfall 기록
- 예상 체결가가 모델 기준 보다 일정 bps 이상 불리하면 partial fill 또는 다음날 이월
- 장중 급등/급락 추격 체결 금지

### B. Live pilot go/no-go criteria

**Hard criteria** (반드시 충족):
1. 4 분기 paper trading 완료
2. 신호 모두 리밸런싱 전 사전 기록 (사후 수정 0)
3. 실제 체결가 vs 모델 기준 가 차이 평균 ≤ 20 bps
4. Data pipeline 오류 0
5. Cash fallback 발생 시 모두 logged + 정상 처리

**Performance criteria**:
6. 실제 vs 백테스트 누적 차이 ≤ 20pp
7. Implementation shortfall 분기당 평균 ≤ 30 bps
8. Slippage 평균 P003 가정 범위 (≤ 20 bps) 내

**Process criteria**:
9. ON 분기 최소 2회 발생 (성과 판단 가능 표본)
10. OFF 분기 cash 유지 + 다음 신호 대기 정상

### C. Live pilot AUM 단계

지피티 권장 단계적 운영:

| 단계 | AUM | 조건 |
|---|---|---|
| Paper | 0 | 4 분기 |
| Pilot 1 | ≤ 10억 | go/no-go 통과 후 |
| Pilot 2 | ≤ 30억 | Pilot 1 4분기 PASS 후 |
| Pilot 3 | ≤ 100억 | Pilot 2 4분기 PASS 후 |
| Full | ≤ 500억 | Pilot 3 PASS + execution desk 준비 |
| Stress 상한 | ≤ 1000억 | max participation 49%, 수동 승인 필수 |

### D. 운영 룰북 (production_rulebook.md 보완)

- 분기말 신호 산출 (T-1 거래일 장 마감 후)
- T+1 거래일 시가 매수 (P002 baseline timing)
- 5 종목 equal weight 20%
- D013 OFF 시 cash 보유
- 거래정지/관리/상폐 → cash fallback
- 단일 종목 ≥ 25% 발생 시 알람
- AUM 300억 초과 시 execution review
- AUM 500억 초과 시 주문 분할 의무
- AUM 1000억 접근 시 운영위 / 수동 승인

## 산출물

- docs/execution_rules.md (지피티 권장 execution rule)
- docs/live_pilot_criteria.md (10 go/no-go criteria)
- docs/aum_progression.md (단계적 AUM 운영)
- production_rulebook.md update (분기 운영 절차)
- final final_summary.md (전체 프로젝트 wrap-up)

## 엄격 제약

- 새 backtest 없음 (document 만)
- D013 strategy 미수정
- 모든 D, E, F, G, P 기존 결과 byte-identical
- Paper trading 시작 전 criteria 동결 (사후 fitting 회피)
