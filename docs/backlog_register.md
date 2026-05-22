# Backlog Register

## Purpose

This register records deferred work after Research Freeze v2. Backlog status does not authorize new alpha research.

## Family Backlog

| Family | Backlog items | Status |
|---|---|---|
| N-family | `N001-A` GLD 5%, `N003-A` TLT trade-off, `N004-A/B/C` DBC/UUP variants | Defensive library backlog |
| K-family | `K001-A/C/D/E/F` sector defensive variants | Backlog |
| K-family | `K002` sector momentum | Rejected |
| J-family | `J001-A` through `J001-F` EM static variants | Backlog |
| J-family | `J002` EM momentum | Rejected as catastrophic |
| L-family | Data fix only: pykrx unavailable before 2014 and 2014-06 error | Alpha paused |
| M-family | BTC 2-5%, ETH | Experimental shadow only |
| T-family | `T005-lite` tax sensitivity | This memo phase |
| T-family | `T006` FX hedge | Backlog |
| T-family | `T007` broker comparison | TEMPLATE READY; user host collection pending; live-precheck required |
| I-family | `I002` macro gate | Still on hold |
| Q-family | Direct Q-family | CLOSED due to survivorship bias |
| Q-family | ETF proxy: SCHD/COWZ/MTUM | MARGINAL; paper tracking X |
| Q-family | Survivorship-safe US universe | Reopen condition only |
| R-family | Title-based Korean shareholder-return disclosures | CLOSED (diagnostic finding) |
| R-family | `R007` DART body parsing | Backlog only under reopen conditions |
| S-family | S-family | CLOSED_DIAGNOSTIC_ARTIFACT |
| S-family | `S001-G` corrected smoke test | DONE; W001 후 1회 완료 |
| X-Lab ETF | `X-ETF001` + `X-ETF900` | CLOSED (no actionable edge) |
| X-Lab KR | `X-KR001` pair/residual mean reversion | CLOSED (12/12 kill gate fail) |
| X-Lab | Entire X-Lab quarantine | **FULLY CLOSED** |
| W001 v1 | Korean equity engine, long-only sleeve scope | COMPLETE (certified) |
| W001 v2 | Korean long-short residual engine | Backlog only; not active |
| V001 | P08 Korean sleeve data integrity regression | COMPLETE (PASS_BYTE_IDENTICAL) |
| L000 | Live pilot go/no-go pack | ACTIVE |
| KR-DART-BODY-RETURN-001 | DART 본문 parser / event-object / PIT lineage (alpha 아님 = parser/data 문제) | BACKLOG (Referee Step 3 lock 2026-05-22) |
| KR-EARNINGS-DRIFT-001 | PIT consensus 확보 가능성 audit | BACKLOG (Referee Step 3 lock 2026-05-22) |
| KR-CONDITIONAL-SHOCK-REVERSION-001 | flow / no-news / overhang lag audit (S-family 재포장 위험) | BACKLOG (Referee Step 3 lock 2026-05-22) |
| KR-QUALITY-VALUE-RETURN-001 | PIT factor / component audit (1번·4번 검증 전 composite 금지) | BACKLOG (Referee Step 3 lock 2026-05-22) |
| KR-PASSIVE-REBALANCE-001 A형 | A0 Item 1 FAIL — KRX index event calendar 부재 | BACKLOG (Referee Step 5 lock 2026-05-22; was TEST) |
| KR-PASSIVE-REBALANCE-001 B형 | 사전 편입 예측 모델 | BACKLOG (Referee Step 3 lock; A형 TEST 와 동일 ID 안에서 테스트 X) |
| KR-OVERHANG-AVOID-001 filter형 | A0 Item 1 PARTIAL — DART title flag only, body parser 없이 fixed scope 미충족 | BACKLOG (Referee Step 5 lock 2026-05-22; was TEST) |
| KR-FLOW-ABSORPTION-001 | Lineage-only audit (F-family overlap 위험, 성과 diagnostic 자체 금지) | BACKLOG (Referee Round 2 lock 2026-05-22) |
| W001-V1-ADJUSTED-OHLC-CORPORATE-ACTION-AUDIT-001 | W001 v1 / dynamic_top100 panel 의 adjusted OHLC 부재 + corporate action artifact (147건) + tradable_mask 4-cause distinction 불가 검증 | BACKLOG-INFRA (Referee Round 2 Step 5 Option D lock 2026-05-22; high priority) |
| KR-G5-ADJOHLC-CORPACT-AUDIT-001 | Round 3 Priority 1A. Gate 5 adjusted OHLC / corporate action repair audit only | A0 AUDIT (Referee Round 3 lock 2026-05-22) |
| KR-ID-LIFECYCLE-MASTER-AUDIT-001 | Round 3 Priority 1B. Permanent ID / delisting / merge / rename audit only | A0 AUDIT (Referee Round 3 lock 2026-05-22) |
| KR-TRADABILITY-SEMANTICS-AUDIT-001 | Round 3 Priority 2. Tradability flag semantics audit only | A0 AUDIT (Referee Round 3 lock 2026-05-22) |
| KR-TOP100-PIT-LINEAGE-AUDIT-001 | Round 3 Priority 3. Dynamic_top100 PIT universe lineage audit only | A0 AUDIT (Referee Round 3 lock 2026-05-22) |
| KR-FLOW-UNIT-TIMESTAMP-AUDIT-001 | Round 3 Priority 4 (lowest). Flow sign/unit/timestamp audit only; no flow strategy test | A0 AUDIT (Referee Round 3 lock 2026-05-22) |

## Q-family Final Freeze

Direct Q-family is closed for production because the US fundamental tests used
a survivor universe. ETF proxy diagnostics using SCHD/COWZ/MTUM showed only
marginal improvement and are not added to paper tracking.

Q-family may reopen only after survivorship-safe historical constituent data is
available and a new ticket explicitly authorizes renewed work.

## R-family Closure

R-family title-based strategy is CLOSED as a diagnostic finding. R000 OPENDART
audit passed, but R001-R004 failed the standalone promotion gate. R005 cost
validation and R006 portfolio combination are skipped because gross standalone
results did not pass. R005-QA-lite is retained only as a closure sanity check
(production X).

Closed / skipped tickets:

- `R000`: OPENDART event data audit gate.
- `R001`: Buyback announcement return study.
- `R002`: Buyback cancellation/retirement-related title bucket study.
- `R003`: Dividend increase study.
- `R004`: Shareholder-return composite.
- `R005`: Skip; R005-QA-lite sanity check only.
- `R006`: Skip; standalone gate 미통과.

## R007 Backlog Reopen Conditions

`R007` DART body parsing is backlog only. Reopen requires:

1. True retirement-only events 분리 가능
2. Buyback amount / market cap PIT parse 가능
3. Dividend amount / yield / increase rate parse 가능
4. Price-return vs total-return (dividend caveat) 처리
5. Size / liquidity / sector / market-cap matched control 가능
6. Pre-registered intensity-based hypotheses (broad keyword fishing X)
7. 사전 등록 (예: buyback ≥ 1-2% market cap, retirement ≥ 0.5-1%, dividend increase + high yield)

## S-family

S-family is CLOSED_DIAGNOSTIC_ARTIFACT. S000 strong result = measurement
artifact. The identified issues are entry/exit alignment, filtered-row
execution, unadjusted corporate action, per-trade leverage, and invalid random
control. S001-D placebo failed.

No production, no paper, no P08 satellite. S001-G is allowed only once after
W001 as corrected smoke test infrastructure QA, alpha X.

## Active Family Status

Current active work: **L000 live pilot pack only**.
W001 v1, V001, X-Lab work all complete or closed.
Non-active work = paper tracking + production hardening (T007 broker, drift
alert, quarterly dry-run, drawdown memo, owner's manual).

## Bull/Bear/Referee First Cycle Cards (2026-05-22)

이 섹션은 첫 multi-LLM decision cycle 결과로 등록된 BACKLOG 카드의 unblock
조건을 정의한다. **성과 테스트 금지** (BACKLOG 단계 = 데이터 / A0 audit
artifact 전까지 성과 측정 X). 각 카드의 즉시 REJECT trigger 도 명시.

### Step 5 Downgrades

원래 Step 3 에서 TEST 였던 두 카드가 Step 5 A0 audit 결과 BACKLOG 강등됨:

- **KR-PASSIVE-REBALANCE-001 A형**: A0 FAIL (지수 운영기관 발표 데이터 부재).
  Unblock = `docs/backlog_A0_queue.md` Task Q1 (KRX/index-provider event
  calendar PIT acquisition).
- **KR-OVERHANG-AVOID-001 filter형**: A0 PARTIAL (DART title flag only,
  body parser X). Unblock = `docs/backlog_A0_queue.md` Task Q2 (DART body
  parser / overhang event-chain parser).

자세한 데이터 gap = `docs/data_gap_KR_PASSIVE_REBALANCE.md` /
`docs/data_gap_KR_OVERHANG_AVOID.md`.

Round 1 end state (Step 5 final): TEST 0 / BACKLOG 6 / REJECT 0.

### Round 2 Cards (2026-05-22 Referee lock)

Round 2 Bull 의 5 신규 카드 + Referee lock. **TEST = A0 diagnostic only,
성과 backtest 승인 아님.**

- **KR-LIQ-FRAGILITY-AVOID-001** (TEST, Priority 1) — A0 diagnostic only,
  long-only basket exclusion filter only. Spec:
  `research/experiments/spec_KR_LIQ_FRAGILITY_AVOID_A0.md`
- **KR-TRADABILITY-RESUME-RISK-001** (TEST, Priority 2) — infrastructure
  A0 first, strategy diagnostic second. 5-step sequential. Spec:
  `research/experiments/spec_KR_TRADABILITY_RESUME_RISK_A0.md`
- **KR-LIQ-MIGRATION-001** (TEST, Priority 3) — strict hidden momentum
  controls required. Trailing-return matched control 후 잔존 시만 의미.
  Spec: `research/experiments/spec_KR_LIQ_MIGRATION_A0.md`
- **KR-TURNOVER-ATTENTION-001** (TEST, Priority 4) — PIT market cap +
  corporate action checks. KR-LIQ-MIGRATION 과 overlap 감시 (≥ 80% 시
  하나만 유지). Spec: `research/experiments/spec_KR_TURNOVER_ATTENTION_A0.md`
- **KR-FLOW-ABSORPTION-001** (BACKLOG, Priority 5) — lineage-only audit
  only, no performance diagnostic. Spec:
  `research/experiments/lineage_only_KR_FLOW_ABSORPTION_A0.md`

Round 2 supporting docs:
- `docs/round2_referee_verdict_lock.md`
- `docs/round2_global_A0_gates.md` (10 non-negotiable gates)
- `docs/round2_event_ledger_schema.md`

Cycle 1 total (Round 1 + Round 2): TEST 4 / BACKLOG 7 / REJECT 0.

### Round 2 Step 5 Option D Lock (2026-05-22)

Round 2 Priority 1 (KR-LIQ-FRAGILITY-AVOID-001) A0 audit 결과 Gate 5
(Adjusted OHLC sanity) FAIL. Referee Option D 선택.

**KR-LIQ-FRAGILITY-AVOID-001 → A0 KILL / BACKLOG-INFRA** (전략 가설 영구
REJECT 아님; W001 v1 measurement layer 결함). 같은 panel 사용하는 Priority
2-4 카드 모두 영향:

- KR-TRADABILITY-RESUME-RISK-001: strategy diagnostic 중단, infrastructure audit only
- KR-LIQ-MIGRATION-001: BACKLOG 대기 (Gate 5 fix 까지)
- KR-TURNOVER-ATTENTION-001: BACKLOG 대기 (Gate 5 fix 까지)

새 backlog task: **W001-V1-ADJUSTED-OHLC-CORPORATE-ACTION-AUDIT-001**
(BACKLOG-INFRA, high priority).

#### W001-V1-AUDIT minimum artifacts (Referee 명시)

| # | Artifact | 상태 |
|---|---|---|
| 1 | `docs/round2_gate5_fail_lock.md` | ✅ 작성 완료 |
| 2 | `docs/data_gap_adjusted_ohlc.md` | ✅ 작성 완료 |
| 3 | `reports/experiments/W001_V1_AUDIT/corporate_action_artifact_ledger.csv` | ✅ 작성 완료 (147 events) |
| 4 | `docs/tradability_semantics_audit.md` | ✅ 작성 완료 |
| 5 | `docs/adjustment_engine_requirements.md` | ✅ 작성 완료 |

#### Unblock 조건

`docs/round2_gate5_fail_lock.md` Unblock Conditions 섹션:
1. Adjusted OHLCV source 확보 (사용자 host)
2. Corporate action event log source 확보
3. Adjustment verification (147 events root cause 분류)
4. `adjust_for_corporate_actions()` repair (or new function)
5. Permanent ID mapping (KRX ticker → corp_code)
6. dynamic_top100 PIT lineage confirm
7. Tradability 4-cause distinction 구현
8. Executable rule 보수적 처리

위 8 조건 통과 후 Gate 1-6 재실행 → Round 2 strategy diagnostic 재개 가능
(Referee 재승인 필요).

Cycle 1 total (Round 2 Step 5 end): TEST 0 / BACKLOG-INFRA 1 (W001 audit) / BACKLOG 7 / REJECT 0.
Active strategy TEST = 0. Infrastructure audit allowed = 1 (KR-TRADABILITY-RESUME-RISK-001).

### Round 3 — Gate-5-aware Infrastructure A0 Audit Queue (2026-05-22)

Round 3 = 새 alpha 탐색 아님. Gate-5-aware infrastructure A0 audit queue.
5 카드 모두 A0 AUDIT only (performance test 일체 금지).

| Priority | Strategy ID | Scope |
|---|---|---|
| 1A | KR-G5-ADJOHLC-CORPACT-AUDIT-001 | adjusted OHLC / corporate action repair audit |
| 1B | KR-ID-LIFECYCLE-MASTER-AUDIT-001 | permanent ID / delisting / merge / rename audit |
| 2 | KR-TRADABILITY-SEMANTICS-AUDIT-001 | tradability flag semantics audit |
| 3 | KR-TOP100-PIT-LINEAGE-AUDIT-001 | dynamic_top100 PIT universe lineage audit |
| 4 / lowest | KR-FLOW-UNIT-TIMESTAMP-AUDIT-001 | flow data lineage audit; no strategy test |

Round 3 Sequencing: 1A + 1B 병렬 → 2 → 3 → 4.

Round 3 supporting docs:
- `docs/round3_referee_verdict_lock.md`
- `docs/round3_no_performance_rule.md` (forbidden metric / pattern)
- `docs/round3_defect_ledger_schema.md`
- `docs/round3_missing_source_register.md` (S1-S6)

Round 3 specs:
- `research/experiments/spec_KR_G5_ADJOHLC_CORPACT_AUDIT_A0.md`
- `research/experiments/spec_KR_ID_LIFECYCLE_MASTER_AUDIT_A0.md`
- `research/experiments/spec_KR_TRADABILITY_SEMANTICS_AUDIT_A0.md`
- `research/experiments/spec_KR_TOP100_PIT_LINEAGE_AUDIT_A0.md`
- `research/experiments/spec_KR_FLOW_UNIT_TIMESTAMP_AUDIT_A0.md`

Cycle 1 total (Round 3 end): TEST 0 / A0 AUDIT 5 / BACKLOG 12 / REJECT 0.

### Round 3 Final + Round 4 Framework (2026-05-22)

**Round 3 CLOSED** (Referee final lock). Round 3 audit 5/5 complete = 34
defects registered (6 critical / 9 high / 6 medium / 3 low / 10 informational).

**Round 4 = W001 v2 Infrastructure Repair + Re-A0** (NOT Bull alpha).

#### Round 3 Final Card Locks
- KR-G5-ADJOHLC-CORPACT-AUDIT-001: FAIL / BACKLOG-INFRA
- KR-ID-LIFECYCLE-MASTER-AUDIT-001: PARTIAL / continue repair
- KR-TRADABILITY-SEMANTICS-AUDIT-001: FAIL / BACKLOG-INFRA
- KR-TOP100-PIT-LINEAGE-AUDIT-001: CONDITIONAL PARTIAL PASS
- KR-FLOW-UNIT-TIMESTAMP-AUDIT-001: PARTIAL FAIL / BACKLOG-LINEAGE

#### Round 4 Definition Artifacts (작성 완료)
- `docs/round3_final_referee_lock.md`
- `docs/round3_missing_source_register.md` (priority + S5 resolved)
- `docs/W001_v2_infrastructure_repair_plan.md` (7 components)
- `docs/W001_v2_reA0_gate_spec.md` (Re-A0 trigger + pass criteria)

#### 34 Defects Preserved
All 34 defects in card-level ledgers + aggregate:
- `reports/experiments/KR_*_AUDIT_001/defect_ledger.csv` (per-card)
- `reports/experiments/round3_aggregate/all_defects.csv` (unified)
- `reports/experiments/round3_aggregate/round3_defect_summary.md` (matrix + cross-card insights)

#### Source Status After Round 3 Final
- 🔴 S1 Adjusted OHLC: mandatory (Round 4)
- 🔴 S2 Corporate Action Event Log: mandatory
- 🔴 S3 KRX Suspension Status: mandatory
- 🟡 S4 Permanent ID fallback: needed for full lifecycle pass
- 🟢 **S5 Top100 Rule: RESOLVED** (reverse-engineered = 거래대금추정 top 100)
- 🔴 S6 Flow Vendor Doc: mandatory for any flow continuation

Top100 Gate 5 dependency (trading value = raw close × volume) = open
(C1 adjusted OHLC fix 시 같이 해결).

Cycle 1 total (Round 4 definition end): TEST 0 / A0 AUDIT 5 complete +
Re-A0 pending / BACKLOG 12 / REJECT 0.

### KR-DART-BODY-RETURN-001 (BACKLOG)

- **BACKLOG 이유**: alpha 문제가 아니라 parser / data-lineage 문제. 본문에서
  자사주 취득 규모, 소각 여부, 배당 증가, 정정 여부 추출 불가 상태에서
  성과 테스트 의미 X.
- **TEST 승격 조건** (모두 통과 필수):
  1. 본문 XML parser 수작업 표본 검증 (자사주 / 소각 / 배당 각 20-50건)
  2. 정정공시 linkage (정정 전 / 후 매핑)
  3. 단위 normalization (원 / 천원 / 백만원 / 주식수 / 비율)
  4. PIT 접수번호 lock (접수일 기준 사용 가능 본문만)
  5. 이벤트 taxonomy 정의 (취득 / 신탁 / 소각예정 / 소각완료 / 배당)
  6. title-only R-style baseline 재현
  7. adjusted OHLCV / corporate action sanity check
- **즉시 REJECT trigger**:
  - DART 본문 대신 제목 키워드 확장 성과 테스트
  - 사후 확정 전환 물량 / 소각 주식 수 결과를 발표일 신호로 사용

### KR-EARNINGS-DRIFT-001 (BACKLOG)

- **BACKLOG 이유**: PIT consensus 없으면 surprise mechanism 자체 붕괴. "시장
  기대 대비 surprise" 가 아니라 "전년동기 대비 좋아진 기업" 으로 퇴화 →
  generic quality / momentum / sector beta 가 됨.
- **TEST 승격 조건**:
  1. PIT consensus 데이터 source 확보
  2. Consensus snapshot timestamp 와 실적공시 timestamp alignment 확보
  3. 잠정 / 확정 / 정정 분리 가능
  4. 금융주 별도 처리 정의
  5. Pre-announcement 20일 수익률 통제 가능
  6. Sector-neutral event count 확인
- **즉시 REJECT trigger**:
  - non-PIT consensus 또는 사후 수정 consensus 사용
  - actual-change 를 surprise 로 포장
  - PIT consensus 없이 rolling baseline 으로 후퇴

### KR-CONDITIONAL-SHOCK-REVERSION-001 (BACKLOG)

- **BACKLOG 이유**: S-family 재포장 위험 과대. 가격 조건만 남으면 즉시
  closed S-family 와 구별 불가. "악재 없음" 가정은 가장 위험 (정보 기반
  매도가 공시보다 먼저 나타날 수 있음).
- **TEST 승격 조건**:
  1. 투자자별 flow 공개 lag audit (t일 flow 를 t+1 에 쓸 수 있는지 검증)
  2. DART/KIND no-news precision audit (악재 누락 가능성)
  3. Overhang filter 연결 (KR-OVERHANG-AVOID-001 TEST 결과 활용 가능)
  4. W001 corrected calendar / tradability engine 사용
  5. S-family corrected loser baseline (S001-G 결과) 재현
  6. Price-only loser baseline 대비 명확한 추가 mechanism 정의
- **즉시 REJECT trigger**:
  - price-only loser / S-family 평균회귀 재포장
  - flow / no-news / overhang filter 가 실질적 효과 없는 상태에서 성과 테스트

### KR-QUALITY-VALUE-RETURN-001 (BACKLOG)

- **BACKLOG 이유**: 검증 안 된 DART-return / overhang component 의존.
  Component 가 먼저 살아남아야 composite 가 의미 있음. 지금 composite 테스트
  = weight mining.
- **TEST 승격 조건**:
  1. KR-DART-BODY-RETURN-001 component 가 독립 A0/TEST 에서 incremental
     value 입증 (현재 BACKLOG → 통과 필요)
  2. KR-OVERHANG-AVOID-001 component 가 incremental value 입증 (현재 TEST
     → 결과 필요)
  3. 재무제표 filing-date lag PIT 처리
  4. PIT factor reconstruction (PBR/PER/ROE/FCF)
  5. 금융주 별도 처리
  6. Value-only / quality-only baseline 재현
  7. Component correlation 명시
  8. Score weight freeze (사전 등록, tuning 금지)
- **즉시 REJECT trigger**:
  - generic value / quality ranking 으로 축소 (Component 검증 우회)
  - 1번 / 4번 검증 전 composite 성과 테스트 시작
  - 사후 확정 재무 / 배당 / 소각 / 전환 데이터 사용

### KR-PASSIVE-REBALANCE-001 B형 (BACKLOG)

- **BACKLOG 이유**: A형 TEST 와 동일 ID 에서 테스트 X. 사전 편입 예측 모델
  = look-ahead 위험 큼 (당시 기준 free-float / 시총 / 거래대금 / 방법론을
  재구성해야 함).
- **TEST 승격 조건**:
  1. 지수 방법론 PIT 재구성 (당시 룰 그대로)
  2. Free-float / 시총 / 거래대금 PIT 재구성
  3. Near-miss inclusion universe PIT 정의
  4. A형 TEST 결과가 mechanism 검증 통과 (= edge 가 진짜인지 먼저 확인)
  5. 별도 ID 부여 후 진행
- **즉시 REJECT trigger**:
  - 실제 편입 결과를 알고 사전 예측 모델 학습
  - 사후 ETF 매수 결과를 발표일 신호로 사용

## X-Lab Closure (2026-05-21)

X-Lab is FULLY CLOSED. Both X-ETF track (X-ETF001 + X-ETF900) and X-KR track
(X-KR001) failed pre-registered audit-first kill gates. X-Lab does not
auto-restart. See `x_lab/final_status.md` and `docs/z000_failure_register.md`.

## W001 Scope Decision (2026-05-21)

W001 v1 is certified for Korean long-only sleeve research only. W001 v2
(long-short residual engine, including borrow/short/margin/leverage/financing)
is backlog-only and not active. See `docs/w001_v2_backlog.md`.

## Reopen Conditions (strengthened 2026-05-21)

Backlog work can resume only if **all** of the following are true:

1. Explicit user decision (no automatic restart, no "비슷한 아이디어 한 번만 더").
2. One of:
   - A new verifiable PIT data source (survivorship-safe universe, true PIT
     fundamentals, clean intraday/order-book data, reliable filing body +
     timestamp + numerical event intensity), OR
   - A genuinely new audit-first verifiable hypothesis that is **not** a
     closed-family threshold/parameter repackaging.
3. Korean long-only research uses W001 v1.
4. Korean long-short research requires W001 v2 to be built and certified first.
5. Q-family direct requires survivorship-safe historical US constituent data.
6. R007 requires the body-parsing reopen conditions listed above.

Until then, deployment preparation and paper tracking take priority.
