# R000 OPENDART 이벤트 데이터 감사

Verdict: PASS

## 데이터 구조

- 전체 row count: 450190
- column count: 26
- 공시 제목 column: report_nm
- 종목 코드 column: stock_code
- 종목명 column: corp_name
- 공시일 column: rcept_dt
- 공시 시간 column: rcept_dt

## 이벤트 분류

- 대상 이벤트 row count: 22988
- 정정공시 후보 count: 3391
- 취소공시 후보 count: 0
- 공시 시간 누락 count: 0

## Quality 평가

- 공시 제목 기반 이벤트 분류는 가능하다.
- 공시일 기반 PIT 정렬은 가능하다.
- 공시 시간 기반 장중/장후 구분은 가능하다.
- 정정/취소 공시는 제목 키워드로 1차 flag 처리 가능하다.

## R001-R006 진행 정당성

R000은 이벤트 분류와 공시일 기반 PIT audit gate를 통과한다. R001-R006은 각 ticket의 별도 timing test와 execution-date shift를 전제로 진행 가능하다.
