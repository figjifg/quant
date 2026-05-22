# W001 v2 — Infrastructure Repair Plan

Date: 2026-05-22
Status: **DEFINITION-ONLY**. Active code work 시작 = 사용자 명시 결정 후
Origin: Referee Round 3 final lock (`docs/round3_final_referee_lock.md`)
Phase: Round 4 = W001 v2 Infrastructure Repair + Re-A0 (NOT Bull alpha)

## Purpose

Round 3 의 34 defects (6 critical / 9 high) 를 해결하기 위한 W001 v2
infrastructure repair 의 **requirements 정의**.

이 문서는 **plan 의 spec 만**. 실제 code 작성 / 데이터 acquisition 은 사용자
명시 결정 후. Round 4 deliverable = infrastructure repair artifacts only,
followed by Re-A0.

## Scope (Referee 명시 7 components)

Round 4 는 다음 7 component 의 requirements 를 정의:

1. Real adjusted OHLC / adjusted return
2. Corporate action factor chain
3. Corporate action event log
4. Permanent identifier fallback
5. tradable_state categorical field
6. KRX suspension/resumption reconciliation
7. Flow vendor documentation

## Component 1 — Real Adjusted OHLC / Adjusted Return

### Resolves defects
- G5_000001 (`adjusted_column_missing`, critical)
- G5_000002 (`adjusted_column_is_raw_alias`, critical)
- G5_000003 (`metadata_only_no_actual_adjustment`, high)
- TOP_000006 (Top100 Gate 5 dependency, high)

### Requirements

**Source (S1)**:
- Adjusted OHLCV columns (open / high / low / close + optional volume)
- 모두 PIT (사후 정정 X)
- Source lineage 명시 (vendor / KRX 공식 / 자체 calc 등)

**Code (W001 v2)**:
- 새 panel column: `adjusted_open` / `adjusted_high` / `adjusted_low` / `adjusted_close`
- 기존 raw column (`시가` / `종가` 등) 과 분리 (alias 아님)
- `adjusted_*_source` column: `'vendor'` / `'krx_official'` / `'self_calculated'` / `'unadjusted_raw_alias'` (마지막은 deprecated)

**Validation**:
- 모든 row 에서 `adjusted_close > 0`
- |adjusted_daily_return| > 50% events count < 10 (current = 147 → repair target)
- Sample audit: 10-20 known corporate action (예: 미래산업 2020-07-02 split) 의 adjusted return 이 ~0 인지 확인

## Component 2 — Corporate Action Factor Chain

### Resolves defects
- G5_000006 (`corporate_action_factor_unreproducible`, high)
- G5_000004 (`extreme_return_unexplained`, critical, 147 events)

### Requirements

**Source (S2 dependency)**:
- Event log per ticker × date with adjustment factor

**Code (W001 v2)**:
- 새 function: `compute_cumulative_adjustment_factor(event_log, ticker, as_of_date) -> float`
- 새 column: `cumulative_adjustment_factor` (chronological per ticker)
- Validation: cumulative factor 가 raw_close × factor = adjusted_close 와 일치

**Validation**:
- Sample 5-10 ticker × 3-5 corporate action 의 factor chain reconstruct + reconciliation
- Edge case: 같은 날 다수 events (split + 증자 동시) handling

## Component 3 — Corporate Action Event Log

### Resolves defects
- G5_000005 (`event_source_missing`, critical)
- G5_000004 (`extreme_return_unexplained`, critical)

### Requirements

**Source (S2)**:
- Event log table

**Schema** (사전 등록):
| Field | Type |
|---|---|
| `ticker` | string (KRX 6-digit) |
| `corp_code_dart` | string (DART corp_code, fallback) |
| `event_date` | date (공시일) |
| `effective_date` | date (효력 발생일) |
| `event_type` | enum: split / reverse_split / capital_reduction / rights_issue / bonus_issue / merger / spin_off / suspension / resumption / delisting / relisting / rename |
| `factor` | float (split ratio 등) |
| `shares_before` | int |
| `shares_after` | int |
| `cancellation_linkage` | string (cancellation 공시 rcept_no, if applicable) |
| `source` | string (`'opendart'` / `'krx'` / `'vendor_xyz'`) |

**Validation**:
- Cross-reference: 모든 147 extreme return events 가 event log 에 매칭되거나
  unexplained list 로 분류
- Cancellation handling: 취소된 event 의 효력 X 처리

## Component 4 — Permanent Identifier Fallback

### Resolves defects
- ID_000005 (`permanent_id_source_missing`, high)

### Requirements

**Current state**:
- DART corp_code 가 94% coverage (783/833) = strong base
- 6% (50 tickers) 가 DART 에 없음 (외국 ETF / 지주회사 / 합병 사라진 entity 등)

**Source (S4)**:
- KRX listed companies master file 또는 ISIN
- 6% fallback 만 보강

**Code (W001 v2)**:
- 새 mapping table: `permanent_id_master.csv`
  - `ticker_at_event_time`
  - `corp_code_dart` (if available)
  - `isin_fallback` (if DART missing)
  - `permanent_id` (composite: corp_code if exists else isin)
- 새 function: `resolve_permanent_id(ticker, as_of_date) -> str`

**Validation**:
- 833 unique panel tickers 100% mapped (94% DART + 6% fallback = 100%)
- Code reuse 발견 시 (현재 0) 시점별 mapping 가능

## Component 5 — `tradable_state` Categorical Field

### Resolves defects
- TRAD_000001 (`tradability_flag_is_panel_presence_proxy`, critical)
- TRAD_000002 (`true_suspension_indistinguishable`, critical)
- TRAD_000003 (`limit_lock_polluted_by_corporate_action`, high)
- TRAD_000004 (`zero_volume_vs_missing_row_conflation`, medium)
- TRAD_000005 (`delisting_transition_indistinguishable`, high)

### Requirements

**Source dependency**: S3 (suspension status) + S2 (corporate action) + S4 (lifecycle)

**Schema** (사전 등록):
- 새 column: `tradable_state` (categorical, mutually exclusive)
- Values:
  - `executable` (정상 거래 가능)
  - `true_suspension` (KRX 공식 매매정지)
  - `limit_lock_up` (상한가 종가 고정)
  - `limit_lock_down` (하한가 종가 고정)
  - `panel_absence` (universe 밖)
  - `data_missing` (vendor 누락)
  - `delisting_transition` (상폐 진행 중)
  - `relisting_transition` (재상장 직후)
  - `corporate_action_day` (split / 증자 day, limit lock 과 분리)

**Code (W001 v2)**:
- 새 function: `tradable_state(panel, suspension_log, event_log) -> pd.Series`
- 기존 `tradable_mask()` deprecated 또는 wrap (`tradable_state == 'executable'`)

**Validation**:
- 9 state 모두 nonzero count
- Cross-card: 147 extreme return events 의 `tradable_state = 'corporate_action_day'` 분류 (false limit_lock 제거)
- True suspension count = KRX 공식 suspension count 일치

## Component 6 — KRX Suspension / Resumption Reconciliation

### Resolves defects
- TRAD_000002 (`true_suspension_indistinguishable`, critical)
- TRAD_000005 (`delisting_transition_indistinguishable`, high)
- ID_000002 (`delisting_terminal_event_missing`, high)
- ID_000003 (`code_reuse_unrecognized`, medium)

### Requirements

**Source (S3)**:
- KRX 공식 suspension / delisting / managed status archive

**Schema** (사전 등록):
- `suspension_start_date`, `suspension_end_date`, `suspension_reason`
- `delisting_date`, `delisting_reason`
- `managed_designation_date`, `managed_designation_reason`
- `listing_status`: active / suspended / managed / 투자주의 / delisted

**Code (W001 v2)**:
- 새 module: `src/utils/listing_status.py`
- Functions: `is_suspended(ticker, date)`, `is_delisted(ticker, date)`, `get_status(ticker, date)`
- Component 5 의 `tradable_state` 가 이 module 사용

**Validation**:
- 258 disappeared tickers 의 terminal event reason 명시
- 307 reappeared tickers 의 cause (suspension+resume vs code reuse) 분류
- Sample audit: 알려진 suspension (예: 거래정지 -> 재개) 의 timing 일치

## Component 7 — Flow Vendor Documentation

### Resolves defects
- FLOW_000004 (`publication_lag_unknown`, high)
- FLOW_000007 (`100% estimated finding`, high, CRITICAL new)
- FLOW_000001 (`documentation_gap`, low)

### Requirements

**Source (S6)**:
- Vendor (Kiwoom) 의 official documentation
  - Sign convention 공식 명시
  - Unit 명시 (KRW exact)
  - Publication timing (장마감 후 정확한 시점)
  - Estimation method (왜 100% True?)
  - Missing handling
- 또는 KRX 투자자별 거래실적 (krx.co.kr) reconciliation

**Code (W001 v2)**:
- 새 doc: `docs/flow_data_methodology.md` (vendor doc + reconciliation)
- 새 function: `flow_t1_safe(panel, current_date) -> pd.DataFrame` (t+1 사용 가능한 flow only return)

**Validation**:
- 100 random sample 의 panel flow vs KRX 공식 reconciliation > 95%
- Publication lag 명시 (T close → T+X 사용 가능 시점)

## Cross-Component Dependency Matrix

| Component | Depends on |
|---|---|
| C1 Adjusted OHLC | S1 |
| C2 Factor Chain | S2 |
| C3 Event Log | S2 |
| C4 Permanent ID | S4 (+ DART base) |
| C5 tradable_state | C3, C4, S3 |
| C6 Suspension Reconciliation | S3 |
| C7 Flow Documentation | S6 |

→ S1, S2, S3, S6 = source mandatory (Referee Round 4 lock).
→ S4 = optional for full lifecycle pass.
→ S5 = closed (reverse-engineered).

## Sourcing Path (사용자 host 영역)

| Source | Cost estimate | Time estimate | Approach 후보 |
|---|---|---|---|
| S1 Adjusted OHLC | 무료-유료 | 1-4 weeks | KRX 공식 / Bloomberg / FnGuide / pykrx |
| S2 Event Log | 무료 (DART API) -유료 | 2-8 weeks | OPENDART body parser 자체 / vendor parsed |
| S3 Suspension Status | 무료 | 1-2 weeks | KRX 공시 archive / DART suspension 공시 |
| S4 ID Fallback | 무료 | 1 week | KRX listed companies file |
| S6 Flow Doc | 무료 (vendor contact) | 1 day - 1 week | Kiwoom 문의 또는 KRX 투자자별 거래실적 |

자세히 = `docs/round3_missing_source_register.md`.

## Code Fix Path (사용자 결정 후)

### W001 v1.x (immediate, source 없이 가능)
- C5 `tradable_state` skeleton (suspension / event source 없이도 4-cause 일부 분류)
- `adjust_for_corporate_actions()` 의 naming / doc 수정 (alias-only 명시)
- Generation script documentation (Top100 = 거래대금 top 100 reverse-engineered)

### W001 v2 (source acquire 후)
- C1 adjusted OHLC integration
- C2 factor chain
- C3 event log loader
- C4 permanent ID master
- C5 full tradable_state
- C6 listing status module
- C7 flow t+1 safe wrapper

## Re-A0 Trigger Conditions

W001 v2 의 어느 정도가 완료되면 Re-A0 진행 가능?

자세한 gate criteria = `docs/W001_v2_reA0_gate_spec.md`.

Minimum for Re-A0:
- C1 + C2 + C3 (Gate 5 complete)
- C5 (Gate 3 complete)
- C6 (Gate 1, 2 complete)
- C7 (Flow gate complete)

C4 (S4 fallback) 미완 시 Re-A0 가능 단 partial pass only.

## Round 4 Deliverable

Round 4 의 deliverable = **infrastructure repair artifacts only**:

1. ✅ `docs/round3_final_referee_lock.md` (Round 3 closure)
2. ✅ Updated `docs/round3_missing_source_register.md`
3. ✅ This file (`docs/W001_v2_infrastructure_repair_plan.md`)
4. ✅ `docs/W001_v2_reA0_gate_spec.md`
5. ✅ 7 component requirements (이 문서에 통합)
6. ✅ 34 defects preserve (defect ledgers 그대로 유지)
7. ✅ S5 = resolved 마크; Top100 Gate 5 dependency open

이 문서 작성 후 = **Round 4 deliverable 완료** (사용자 host 작업 + code 작성
시작 = 별도 사용자 결정).

## Forbidden (Round 4 lock, Referee 명시)

- Performance tests
- NAV / CAGR / Sharpe / hit rate / alpha / excess return / MDD / post-event drift / migration / turnover / resume / reversal / flow-return
- Raw return as signal or outcome
- Round 2 strategy diagnostic 재시작
- 147 extreme-return events 제외 후 testing 계속
- Flow data strategy testing (100% estimated + S6 missing 상태)
- Production / paper tracking / P08 / live readiness / shadow 연결

## Related

- `docs/round3_final_referee_lock.md`
- `docs/round3_missing_source_register.md`
- `docs/W001_v2_reA0_gate_spec.md`
- `docs/round3_defect_ledger_schema.md`
- `reports/experiments/round3_aggregate/round3_defect_summary.md`
- Per-card defect ledgers: `reports/experiments/KR_*_AUDIT_001/defect_ledger.csv`
