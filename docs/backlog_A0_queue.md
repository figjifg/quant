# Backlog A0 Queue — Data Infrastructure Tasks

Date opened: 2026-05-22 (Referee Step 5 lock)
Status: BACKLOG · 사용자 host 작업 영역 · 사용자 명시 결정 후 시작

이 queue 는 첫 Bull/Bear/Referee 사이클 Step 5 결과로 등록된 데이터 인프라
task 들을 모은다. 이 task 들이 통과되기 전에는 관련 strategy 카드 의 TEST
재진입 불가.

이 queue 의 task 자체도 next-action 자동 시작 X. 사용자 명시 결정 후만
시작.

## Task Q1 — KRX / Index-Provider Event Calendar PIT Acquisition

**Block 해제 대상**: KR-PASSIVE-REBALANCE-001 A형 (현재 BACKLOG)

**확보 필요 데이터**:
- Official announcement date (지수 운영기관 공식 발표일)
- Announced inclusion list (편입 종목 list)
- Announced exclusion list (편출 종목 list)
- Effective rebalance date (실제 적용일)
- Index identifier (KOSPI200 / KOSPI100 / KOSDAQ150 / KRX100 등)
- Methodology version if available (방법론 버전)
- Source lineage (어느 source 에서 acquired, 어떤 format, 날짜)
- PIT lock (재공시 / 정정 시 사후 변경 사용 X 보장)
- Near-miss control data if available (편입 후보 중 미편입 종목 list)

**Source 후보** (사용자가 가능성 평가):
- KRX 시장정보시스템 (krx.co.kr / data.krx.co.kr)
- 지수 운영기관 (KRX index 운영 / FnGuide / Krx & co)
- Bloomberg / Refinitiv / FactSet (vendor)
- 데이터스트림 / FN데이터 (vendor)
- 한국거래소 ETF 운영 공시 (간접 acquisition, validation 어려움)

**Forbidden source** (Referee 명시):
- DART 만 사용 = 기업 공시 only, 지수 운영기관 발표 X
- ETF AUM 변화 = 사후 추정 (look-ahead 위험)
- Fund 보유 변화 = 사후 추정
- Futures basis = 지수 변경 발표 직접 source 아님
- 사후 최종 index membership 으로 역추적 = post-hoc reconstruction (금지)

**완료 정의**:
- 위 9 필드 모두 확보 + sample audit 통과
- PIT lock 검증 (정정 / 재발표 chronology 보존)
- Methodology 변경 시점 명시
- 별도 ticket 으로 A0 audit 재실행 후 PASS 시 KR-PASSIVE-REBALANCE-001 A형
  TEST 재진입 가능

## Task Q2 — DART Body Parser / Overhang Event-Chain Parser

**Block 해제 대상**: KR-OVERHANG-AVOID-001 filter형 (현재 BACKLOG) 및
KR-DART-BODY-RETURN-001 (기존 BACKLOG)

**확보 필요 parser / data 능력**:
- CB / BW terms (전환가, 리픽싱, 행사기간, 전환비율)
- Rights issue details (유상증자 발행가, 발행주식수, 청약기간, 납입일)
- Conversion request (전환청구일, 전환주식수, conversion 확정 여부)
- Additional listing (추가상장일, 신규 상장 주식수, 상장 사유)
- Lockup release (보호예수 해제일, 해제 물량, 대상자)
- Major shareholder sale (대주주 매도 공시, 매도 주식수, 매도가)
- Potential shares / free float (per-event 잠재 희석 주식수, 당시 free
  float)
- Event severity (intensity scoring 가능한 normalized 형식)
- Event timestamp (rcept_no 기반 정확한 timestamp)
- Effective date linkage (공시일 → 실제 효력 발생일 mapping)
- Cancellation / withdrawal linkage (취소 / 철회 공시 chronological link)

**현재 가용 (insufficient)**:
- DART parquet 450,190 rows, 2018-01-02 ~ 2026-05-04
- Title-based binary flags (flag_capital_raise / flag_cb_bw /
  flag_treasury_stock / flag_large_holder / flag_merger_split 등)
- 본문 (body) parsing 결과 X
- Numeric intensity (shares, amount, ratio) X
- Effective date / cancellation chronology X

**Source / 구현 후보** (사용자 평가):
- OPENDART API 본문 XML (rcept_no 별 body XML 다운로드 후 자체 parser 구축)
- DART 본문 사람 검증 sample (20-50건 per event type)
- Vendor parsed event data (FnGuide, KIS, 매경 데이터)
- 정정공시 linkage (rcept_no 간 reference 정리)
- 단위 normalization (원 / 천원 / 백만원 / 주식수 / %)

**Forbidden** (Referee 명시):
- Title flag 으로 body parser 대체 시도 = REJECT trigger
- 사후 확정 conversion / 추가상장 결과 사용 = look-ahead
- Body parser 없이 binary flag 으로 reduced backtest = REJECT trigger

**완료 정의**:
- 본문 XML parser 수작업 표본 검증 (자사주 / CB·BW / 추가상장 / 보호예수
  / 대주주매도 각 20-50건)
- 정정공시 linkage chain 통과
- 단위 normalization 통과
- PIT 접수번호 lock 통과
- Cancellation / withdrawal handling 통과
- 별도 ticket 으로 A0 audit 재실행 후 PASS 시 KR-OVERHANG-AVOID-001 filter
  형 TEST 재진입 가능. 또한 KR-DART-BODY-RETURN-001 unblock 진행 가능
  (단 이 카드는 Bear 분석의 18 항목 별도 통과 필요)

## Queue Management Rule

- 이 queue task 의 시작 = 사용자 명시 결정 필요 (자동 시작 X)
- 두 task 완료 순서 = 사용자 선택. 단 KR-PASSIVE-REBALANCE-001 unblock 은
  Q1 만 필요, KR-OVERHANG-AVOID-001 unblock 은 Q2 만 필요 (independent)
- Q2 는 KR-DART-BODY-RETURN-001 / KR-QUALITY-VALUE-RETURN-001 unblock 의
  prerequisite 이기도 함 (더 큰 영향 범위)
- Task 진행 중 새 strategy 카드 자동 reopen X. 데이터 확보 후에도 별도
  Bull/Bear/Referee 사이클 필요.

## Related Documents

- `docs/step5_A0_verdict_lock.md` — Cycle 1 Step 5 verdict (이 queue 의 origin)
- `docs/data_gap_KR_PASSIVE_REBALANCE.md` — Q1 누락 필드 상세
- `docs/data_gap_KR_OVERHANG_AVOID.md` — Q2 누락 taxonomy / intensity / parser 요건 상세
- `docs/backlog_register.md` — 전체 BACKLOG 목록
- `docs/w000_data_infrastructure_backlog.md` — 기존 데이터 인프라 backlog (참고)
