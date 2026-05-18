# P002 — D013 execution simulation

## 상태
계획됨

## 이게 무슨 ticket 인가

P001 후 D013 = 유일 검증된 valid carrier. 지피티 권장 P002 = execution
simulation. D013 의 백테스트 가 실제 체결 가능성 반영하는지 검증.

## 시나리오 (사전 등록)

| 시나리오 | 체결 시점 |
|---|---|
| baseline (D013 그대로) | 분기말 다음 거래일 시가 |
| **A: next-day close** | 분기말 다음 거래일 종가 |
| **B: 1-day delay** | 분기말 + 2 거래일 시가 |
| **C: 2-day delay** | 분기말 + 3 거래일 시가 |
| **D: unfavorable fill** | 매수 = 그 거래일 고가, 매도 = 저가 |
| **E: partial fill** | 매수의 일부만 (예: 80%) 체결, 나머지 cash |
| **F: cash fallback** | 거래정지/관리 종목 발생시 cash 대체 |

## 사전 등록 pass 기준

| 시나리오 | 기준 |
|---|---|
| A (next-day close) | 누적 D013 의 80% (≥ +203%) |
| B (1-day delay) | 누적 ≥ +150% |
| C (2-day delay) | 누적 ≥ +120% |
| D (unfavorable fill) | 누적 ≥ +100% |
| E (partial fill 80%) | 누적 ≥ D013 의 70% |
| F (cash fallback) | 발생 빈도 + 영향 보고 |

전체 종합:
- 평균 누적 ≥ +150%
- Sharpe ≥ 0.40
- MDD 악화 ≤ 5pp

## 산출물

- reports/experiments/P002_d013_execution_simulation/
- A_next_day_close/, B_1day_delay/, C_2day_delay/, D_unfavorable_fill/, E_partial_fill/, F_cash_fallback/
- execution_summary.csv (모든 시나리오 비교)
- report.md (pass/fail 판정)

## 엄격 제약

- engine.py 수정 가능성 — execution timing 변경 필요시 사용자 승인
- 기존 strategy 미수정 (D013, E014 등)
- D001-D015, E003-E015, F002-F012, G000-G002, P001, P001.5 byte-identical
- D013 carrier 정의 변경 X
- sandbox pandas 없으면 직접 실행 OK
