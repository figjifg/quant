# S2 OPENDART Body Parser Phase — Master Ticket

Date: 2026-05-23
Origin: Referee Round 4.1 verdict (Option A approved, conditional verification ✅)
Status: READY for Codex delegation (pending OPENDART API key environment setup)

## Lock from Referee (변경 불가)

- Scope = S2 OPENDART body parser phase only / **infrastructure repair only**
- 10 allowed event types (taxonomy below)
- 17-field output schema (below)
- Manual audit per event type 20-50 samples
- 11 hard prohibitions (no strategy testing / return / NAV / CAGR / Sharpe / alpha / Round 2 restart / flow test / DART body alpha / overhang filter / production / parser-strategy-ready)
- End condition = S2 parser A0 report only (8 items: source coverage / form coverage / parser success-failure by event type / manual audit result / PIT timestamp lock / correction-cancellation linkage / event log schema output / C2-C3 readiness)
- "Do not recommend strategy testing" — 결과 보고 시 strategy 진입 권유 금지

## Executor HOW Decisions (변경 가능, 사용자/Referee push back 가능)

### Sub-task ordering (5 waves, 일부 병렬 가능)

| Wave | Sub-task | Owner | Depends on |
|---|---|---|---|
| D1 | Bulk OPENDART body XML download (filtered by 10 event-type forms) + form name survey | Codex | API key |
| D2 | XML schema mapping per form (50 random sample per form) | Codex | D1 |
| D3a | Parser Wave 1 — 자사주 (취득/처분/소각) | Codex | D2 |
| D3b | Parser Wave 2 — CB/BW + 전환청구 | Codex | D2 |
| D3c | Parser Wave 3 — 유증/무증/감자/합병·분할/추가상장/보호예수/대주주매도/정정·철회·취소 | Codex | D2 |
| D4 | Output schema integration (17 fields, all parsers → single event log) | Codex | D3a+D3b+D3c |
| D5a | Manual audit sample extraction (30 random per event type, stratified by year) | Codex | D3 |
| D5b | Manual audit execution (사용자) — record precision/recall proxy + failure modes | 사용자 | D5a |
| D6 | C2/C3 readiness spec + S2 parser A0 report assembly | Executor (Claude) | D4 + D5b |

**Parallelization**: D3a / D3b / D3c 는 D2 완료 후 병렬 가능. D5a 는 wave 단위로 D3 wave 완료마다 가능.

### Filter scope (executor 결정)

- Period: **2018-01-01 ~ 2026-05-22** (R000 inputs 와 동일 범위)
- Universe: KOSPI + KOSDAQ (S4 listed companies 와 동일)
- Disclosure form mapping (각 event type → DART form name; D1 단계에서 verify):

| Event type | Expected DART form name (verify in D1) |
|---|---|
| 자사주 취득 | 주요사항보고서(자기주식취득결정), 주요사항보고서(자기주식취득신탁계약체결결정) |
| 자사주 처분 | 주요사항보고서(자기주식처분결정), 주요사항보고서(자기주식처분신탁계약체결결정) |
| 자사주 소각 | 주요사항보고서(자기주식소각결정) |
| CB 발행 | 주요사항보고서(전환사채권발행결정) |
| BW 발행 | 주요사항보고서(신주인수권부사채권발행결정) |
| 전환청구 | 전환청구권행사 (또는 발행등록사실확인서) |
| 유상증자 | 주요사항보고서(유상증자결정) |
| 무상증자 | 주요사항보고서(무상증자결정) |
| 감자 | 주요사항보고서(감자결정) |
| 합병 | 주요사항보고서(회사합병결정) |
| 분할 | 주요사항보고서(회사분할결정) / 회사분할합병결정 |
| 추가상장 | 추가상장(주식·구주매출·매수청구 등) |
| 보호예수 해제 | 의무보유등 |
| 대주주 매도 | 임원·주요주주특정증권등소유상황보고서 |
| 정정/철회/취소 | 정정공시 / 철회공시 / 취소공시 (별도 처리, cancellation_linkage 채움) |

D1 의 첫 작업 = 위 form name 의 실제 DART 분류 vs 추측 mapping verify (sample 100건 분류).

### Manual audit sample size (executor 결정)

- **30 samples per event type** (Referee 20-50 range mid)
- Stratified by year (2018-2026 8 buckets → 평균 3-4건/year)
- Total ≈ 30 × 10 event type ≈ 300 samples to manually review

### Output paths

```
data/acquired/round4/s2_dart_body/
├── raw_xml/                          # D1 bulk download
│   └── {YYYYMMDD}/{rcept_no}.xml
├── form_inventory.parquet            # D1 survey (rcept_no, form, ticker, date)
├── schema_mapping/                   # D2
│   └── {form_id}_fields.yaml
├── parsed/                           # D3 + D4
│   ├── treasury_events.parquet
│   ├── cb_bw_events.parquet
│   ├── other_events.parquet
│   └── all_events_unified.parquet    # 17-field schema
├── audit_samples/                    # D5a
│   └── {event_type}_samples.csv      # 30 per type, stratified
└── audit_results/                    # D5b user input
    └── {event_type}_audit_log.csv    # precision/recall proxy + failure modes

reports/experiments/S2_phase_parser_A0/   # D6 final output
├── source_coverage.md
├── form_coverage.md
├── parser_success_by_event_type.csv
├── manual_audit_summary.md
├── pit_timestamp_lock.md
├── correction_cancellation_linkage.md
├── event_log_schema.md
└── c2_c3_readiness_spec.md
```

## Output Schema (Referee Lock, 17 fields)

| Field | Type | Note |
|---|---|---|
| ticker | str(6) | KRX listed code |
| corp_code_dart | str(8) | DART corp code |
| rcept_no | str(14) | DART receipt number = PIT 시점 |
| rcept_date | date | rcept_no → date |
| event_date | date | 본문 명시 결의일 / 행사일 |
| effective_date | date | 효력 발생일 (rcept_date ≠ event_date 와 별개) |
| event_type | str(50) | 10 taxonomy 중 1 |
| amount_krw | float | 금액 (없는 type 은 null) |
| shares | float | 주식 수 |
| shares_before | float | 발행 주식 수 (before) |
| shares_after | float | 발행 주식 수 (after) |
| factor | float | 무증/감자/액면분할 factor (없는 type 은 null) |
| cancellation_linkage | str | 정정/철회/취소 시 원 rcept_no 연결 |
| source | str | "dart_opendart_body_v1" |
| parser_confidence | float [0,1] | parser 자체 자신감 score |
| manual_audit_status | str | "passed" / "failed" / "not_audited" |
| pit_available_at | datetime | rcept_no submit datetime (= PIT lock) |

## Hard Prohibitions (Referee Lock)

- No return backtest
- No NAV / CAGR / Sharpe / hit rate / alpha / excess return / MDD
- No post-event drift / migration / turnover / resume / reversal / flow-return
- No raw return as signal/outcome
- No Round 2 strategy restart
- No residual-event exclusion followed by testing
- No flow strategy testing
- No DART body alpha test
- No overhang alpha/filter test
- No production / paper / P08 / live readiness / shadow connection
- No parser result described as strategy-ready

## Kill Gates (Referee Lock)

| Gate | Action |
|---|---|
| Body XML bulk download 안정성 부족 | stop |
| Event type parser precision 수작업 audit 실패 | stop |
| 정정공시 linkage 불가 | partial only |
| Cancellation/withdrawal 처리 불가 | partial only |
| event_date / effective_date 구분 불가 | C3 integration 금지 |
| Shares/amount 단위 normalization 실패 | overhang/return component 금지 |
| PIT rcept_date lock 불가 | strategy linkage 금지 |
| C2 factor chain 재현 불가 | G5 full pass 금지 |
| Parser output 직접 strategy 테스트 시도 | protocol violation |

## Prerequisites (사용자 action 필요)

1. **OPENDART API key**: `OPENDART_API_KEY` 환경 변수 셋업 (`.env` 또는 셸 환경).
2. Codex 환경에서 위 key 사용 가능 확인.
3. 최초 D1 시작 전 small-scale dry run (50 rcept_no) 으로 endpoint + key 검증.

## Timeline Estimate

| Wave | Duration | Notes |
|---|---|---|
| D1 | 2-3 days | sequential API call, 450k disclosures 또는 filtered subset |
| D2 | 3-5 days | sample + schema doc |
| D3a (자사주) | 1-2 weeks | KR-DART-BODY-RETURN-001 의 main unblock 후보 |
| D3b (CB/BW + 전환청구) | 1-2 weeks | overhang 의 main 후보 |
| D3c (기타) | 1-2 weeks | edge case 많음 |
| D4 | 3-5 days | 통합 + dedup + validation |
| D5a (sample extraction) | 1-2 days | Codex |
| D5b (manual audit) | 1-2 weeks | 사용자 ~ 1 시간/event type × 10 |
| D6 (A0 report) | 1 week | executor 직접 |

**Total: 6-10 weeks** (기존 5-9 주 estimate 와 일치, manual audit 사용자 시간 포함).

## Compliance with Round 4.1 Lock

- ✅ Verification confirmed (HEAD == origin/main = 9052ef1, 10 files + tradability.py rename push 완료)
- ✅ Infrastructure repair only — no strategy testing
- ✅ No production / paper / P08 / live connection
- ✅ S2 parser A0 report only as end condition
- ✅ Sub-task HOW decisions = executor authority (per 2026-05-23 사용자 위임)

## Related

- `docs/round4_1_v2_1_referee_lock.md`
- `docs/s2_opendart_body_parser_plan.md` (Round 4 feasibility verified)
- `reports/experiments/round4_1_v2_1/S2_phase_decision_brief.md` (Round 4.1 brief)
- `docs/W001_v2_infrastructure_repair_plan.md` Component 3
- `research/experiments/R000_opendart_event_data_audit.md` (R000 pattern)
- `data/acquired/round4/s2_dart_body_samples/20240125000291_document.xml.zip` (sample seed)
