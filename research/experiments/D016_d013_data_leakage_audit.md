# D016 — D013 데이터 누수 (look-ahead) 감사

## 상태
계획됨

## 이게 무슨 ticket 인가

지피티 권장. D013 을 Layer 1 챔피언으로 동결 전, 모든 입력 변수가
정말 미래 정보를 보지 않는지 정식 감사.

기존 tests 에 일부 look-ahead 체크가 있지만, 변수별로 정리한 감사
보고서는 없음.

## 감사 대상

D013 의 10 개 변수 + 합성 점수 계산 + 매매 시점:

| 변수 | 원본 데이터 | 갱신 주기 | 발표 lag |
|---|---|---|---|
| VIX (60d/240d) | fred_vix.csv | 일간 | 당일 |
| BAA10Y spread | fred_baa10y_spread.csv | 일간 | 당일 |
| USDKRW yoy | fred_dexkous_usdkrw.csv | 일간 | 당일 |
| DXY yoy | fred_dxy.csv | 일간 | 당일 |
| US 10y real yield | fred_us_10y_real.csv | 일간 | 당일 |
| US 2-10y curve | fred_dgs2/10.csv | 일간 | 당일 |
| Brent yoy | fred_brent.csv | 일간 | 당일 |
| 10y breakeven | fred_us_breakeven_10y.csv | 일간 | 당일 |
| OECD CLI Korea | fred_kr_cli.csv | 월간 | 약 2개월 lag |
| KR exports yoy | fred_kr_exports.csv | 월간 | 약 1개월 lag |

## 감사 항목

### A. 각 변수별 확인
1. 데이터 파일의 observation_date vs 발표 가능 시점
2. 월간 데이터 (CLI, KR exports) 의 lag 가 코드에서 반영되는지
3. 수정치 (revision) 사용 여부 — original release 와 차이
4. 신호일 (signal_date) 에 그 변수 값이 정말 알 수 있었던 값인지

### B. z-score 계산 확인
1. T 시점의 z-score 가 [T-60mo, T] 만 사용하는지
2. T 자체를 포함하는 게 맞는지 (당일까지의 데이터)
3. 표준편차 / 평균 계산에 미래 데이터 들어가는지

### C. 합성 점수 → 매수 결정 확인
1. signal_date 에 신호 계산 → execution_date 에 체결 분리 확인
2. signal_date < execution_date 가 항상 참인지
3. 분기 리밸런싱 시점 (분기 마지막 거래일) 의 timing 정확한지

### D. 매수 후 데이터 사용
1. 보유 기간 동안의 종가 갱신이 future-leaking 아닌지
2. 매도 시점의 가격이 그 시점에 알 수 있던 가격인지

## 사전 등록 판정

| 결과 | 판정 |
|---|---|
| 모든 항목 통과 + 모든 변수에 대해 timing 명시 | **무결성 확인** → D013 동결 정당 |
| 일부 변수에 lag 미반영 또는 timing 불명 | 수정 후 D013 재실행 필요 |
| 명백한 look-ahead 발견 | **D013 결과 무효화** → 수정 후 재검증 |

## 구현 작업

새 backtest 거의 필요 없음. 분석 위주:

추가만:
- `src/audit/look_ahead_audit.py` (신규) — 변수별 timing 감사 함수
- `tests/test_d013_look_ahead_audit.py` (신규) — 각 변수의 timing
  invariant 강화된 테스트
- `reports/experiments/D016_d013_data_leakage_audit/audit_report.md` —
  변수별 결과 정리
- `reports/experiments/D016_d013_data_leakage_audit/timing_table.csv` —
  변수별 timing 정보 (lag, 사용 시점, 검증 결과)

**수정 금지**:
- engine.py
- 기존 strategy 모듈 (a001-a004, b001-b011, c003-c020, d001-d015)
- D013 결과의 바이트 단위 재현성 (D013 자체는 변경 X)
- research_input_data/

만약 누수 발견:
- 즉시 정지, `D016_codex_questions.md` 작성
- D013 결과 재실행 여부는 사용자 결정

## 완료 기준
- pytest 통과
- audit_report.md 에 변수별 결과 명시
- timing_table.csv 생성
- D013 결과 unchanged (감사만, 수정 없음)
- 최종 보고:
  - 10 변수 각각의 timing 평가
  - 발견된 issue 있으면 명시
  - 전체 무결성 판정

## 범위 외
- ❌ D013 carrier 변경
- ❌ 변수 추가/제거
- ❌ 새 backtest 변형
