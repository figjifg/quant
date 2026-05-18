# P005 — D013 production risk constraints

## 상태
계획됨

## 이게 무슨 ticket 인가

G-family slow overlay 가 fail 했지만 production-level constraints 는
필요 (지피티 권장). P005 = D013 위에 실전 제약 적용.

## Constraints (사전 등록)

### 1. 단일 종목 최대 비중
- D013 = 시총 top 5, equal weight 20%
- Constraint: max 25% per stock (현재 20% 이라 영향 없음)
- 만약 4종목 만 매수 가능 시: 25% 까지 허용

### 2. 상위 2개 종목 합산
- D013 의 top 2 종목 = 종종 삼성전자 + SK하이닉스
- Constraint: top 2 합산 ≤ 50%
- 현재 20% × 2 = 40% 이미 충족

### 3. 유동성 제한
- 일평균 거래대금 ≥ 5e9 KRW (50억 원)
- 미달 종목 매수 제외
- D013 universe (dynamic top 100) 이미 충족 가능성 높음

### 4. 거래정지 / 관리 / 상폐 위험 제외
- panel 의 거래정지 / 관리종목 flag 가 있으면 제외
- Cash fallback

### 5. 회전율 제한
- 분기마다 종목 변경 비율 ≤ 100% (5종목 모두 교체 OK)
- 현재 자연스럽게 충족

### 6. AUM cap
- P003 결과: 보수적 100억, 확장 500억
- Production constraint: AUM ≥ 1000억 시 알람 (capacity 임계)

## Backtest 검증

constraints 적용 후 D013 결과:
- 누적 / Sharpe / MDD
- D013 baseline 과 차이
- 어떤 constraint 가 실제로 binding 했는지

기대: 대부분 constraint 가 D013 (시총 top 5 보수적) 에 binding 안 함.
즉 constraint 적용 후에도 D013 결과 거의 동일.

## Pass 기준
- 모든 constraint 가 운영상 합리적
- D013 baseline 대비 누적 ≤ 20pp 감소
- 실전 위험 (거래정지 등) 처리 가능

## 산출물

- src/strategies/p005_d013_with_constraints.py (NEW)
- configs/backtests/p005.yaml
- reports/experiments/P005_production_constraints/
- constraint_binding_log.csv (각 분기 어느 constraint 가 binding)
- comparison_with_d013.csv
- production_rulebook.md (constraint list + 운영 가이드)
- report.md

## 엄격 제약

- engine 미수정 (constraint 는 strategy 단에서)
- D013 carrier 정의 변경 X
- D001-D015, E003-E015, F002-F012, G000-G002, P001-P003 byte-identical
