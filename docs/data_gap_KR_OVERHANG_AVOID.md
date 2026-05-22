# Data Gap — KR-OVERHANG-AVOID-001 filter형

Card status: BACKLOG (Referee Step 5 lock, 2026-05-22)
Block reason: A0 Item 1 (Data lineage) = PARTIAL — DART title flag only, body parser X
Unblock task: Backlog A0 Queue Task Q2 (`docs/backlog_A0_queue.md`)

## Spec Requirement vs Available

Pre-registered spec (`research/experiments/KR_OVERHANG_AVOID_001_filter_test.md`)
의 fixed scope:
- Event taxonomy: CB/BW, 전환청구, 추가상장, 유상증자, 보호예수 해제, 대주주 매도 (7 카테고리)
- Measurement: potential shares / free float, event age, event severity
- Role: long-only basket exclusion filter (intensity 기반)

→ Title-flag binary 만으로는 intensity / severity 측정 불가, taxonomy 3/7
detection 불가. spec 핵심 변수 결손.

## Available DART Data (Current Repo)

| Source | 형식 | 한계 |
|---|---|---|
| `research_input_data/inputs/events/opendart_kospi_disclosures_20180101_20260505.parquet` | 450,190 rows, 2018-01-02 ~ 2026-05-04 | title-based flag only (binary), 본문 X, numeric intensity X |

Schema: `rcept_no`, `rcept_dt`, `rcept_date`, `corp_cls`, `corp_code`,
`stock_code`, `corp_name`, `report_nm`, `flr_nm`, `rm`, `pblntf_ty_query`,
`query_bgn_de`, `query_end_de`, `dart_url`, `flag_capital_raise`,
`flag_cb_bw`, `flag_capital_reduction`, `flag_audit_issue`,
`flag_trading_halt`, `flag_litigation`, `flag_large_holder`,
`flag_treasury_stock`, `flag_merger_split`, `flag_earnings`, `flag_contract`,
`flag_event_risk`

Flag 건수 (overhang 관련):
- `flag_capital_raise` (유상증자): 5,826
- `flag_cb_bw` (CB/BW): 1,824
- `flag_treasury_stock` (자사주 — 취득 / 처분 / 소각 구별 X): 6,154
- `flag_large_holder` (대량보유 — 대주주 매도 신호 일부): 80,164

## Missing Taxonomy Coverage (7 중 3 detection 불가)

| Event taxonomy | DART flag 가용 | 비고 |
|---|---|---|
| CB / BW (전환사채 / 신주인수권부사채) | ⚠ binary only (`flag_cb_bw`) | 전환가 / 리픽싱 / 행사기간 X |
| 전환청구 | ❌ flag 없음 | report_nm 텍스트 매칭 가능성, 단 정확도 보증 X |
| 추가상장 | ❌ flag 없음 | report_nm 매칭 가능성 |
| 유상증자 | ⚠ binary only (`flag_capital_raise`) | 발행가 / 주식수 / 청약기간 X |
| 보호예수 해제 | ❌ flag 없음 | 별도 source 필요 (KRX 상장공시) |
| 대주주 매도 | ⚠ binary only (`flag_large_holder` 의 일부) | 매도 / 매수 구별 X, 매도 주식수 X |
| 자사주 | ⚠ binary only (`flag_treasury_stock`) | 취득 / 처분 / 소각 구별 X |

## Missing Intensity Fields

Bear fixed scope 의 "potential shares / free float", "event severity" 측정에
필요한 fields (현재 모두 unavailable):

| Field | 의미 |
|---|---|
| `cb_bw_terms` | 전환가, 리픽싱 조항, 행사기간, 전환비율 |
| `rights_issue_details` | 발행가, 발행주식수, 청약기간, 납입일 |
| `conversion_request_amount` | 전환청구 주식수 (per 청구 사건) |
| `additional_listing_shares` | 신규 상장 주식수 + 사유 |
| `lockup_release_amount` | 해제 물량 + 대상자 |
| `major_shareholder_sale_amount` | 대주주 매도 주식수 + 매도가 |
| `treasury_stock_action_type` | 취득 / 처분 / 소각 / 신탁 계약 구별 |
| `treasury_stock_shares` | 자사주 거래 주식수 |
| `potential_shares` | per-event 잠재 희석 주식수 |
| `free_float_at_event` | 사건 시점 free float (PIT) |
| `event_severity_normalized` | intensity scoring 가능한 normalized 값 |
| `effective_date` | 공시일 → 실제 효력 발생일 mapping |
| `cancellation_linkage` | 취소 / 철회 공시 chronological reference |

## Why Existing Flags Cannot Substitute

| 시도 | 왜 금지 |
|---|---|
| `flag_capital_raise` 만 binary exclusion | "DART 본문 대신 제목 키워드 확장" 글로벌 REJECT trigger |
| `flag_treasury_stock` 으로 자사주 취득 / 처분 / 소각 동일 처리 | 의미 정반대 (취득 = bullish, 처분 = bearish). 데이터 손실 |
| `flag_large_holder` 의 매도 / 매수 동일 처리 | 의미 정반대. 노이즈 |
| report_nm 텍스트 매칭으로 전환청구 / 추가상장 / 보호예수 detection | title 키워드 확장 = REJECT trigger |
| 사후 확정 전환 / 추가상장 결과 사용 | look-ahead = global REJECT |

## Parser / Source Requirements (Task Q2 완료 정의)

DART body parser 또는 동등 event-chain data 구축:

1. **본문 XML acquisition**: OPENDART API 의 rcept_no 별 body XML download
   pipeline
2. **타입별 parser**:
   - 자사주 취득 / 처분 / 소각 결정 parser (취득가 / 처분가 / 소각 주식수 / 신탁 vs 직접)
   - CB / BW 발행 parser (발행조건, 전환가, 리픽싱, 행사기간)
   - 전환청구 parser (청구 주식수, 전환가, 확정일)
   - 유상증자 parser (발행가, 주식수, 청약기간, 납입일)
   - 추가상장 parser (상장 주식수, 사유)
   - 보호예수 parser (해제일, 물량, 대상자)
   - 대주주 매도 parser (매도자, 매도 주식수, 매도가)
3. **단위 normalization**: 원 / 천원 / 백만원 / 주식수 / % 통일
4. **정정공시 linkage**: rcept_no 간 reference (정정 전 / 후 chronological)
5. **취소 / 철회 linkage**: cancellation 공시 → 원본 공시 reference
6. **PIT timestamp lock**: rcept_no 기반 정확한 timestamp + effective_date
   분리
7. **수작업 표본 검증**: 자사주 / CB·BW / 추가상장 / 보호예수 / 대주주매도
   각 20-50건 사람 검증, precision / recall 측정

## Source Candidates (사용자 평가)

| Source | Cost | 시간 | 난이도 |
|---|---|---|---|
| OPENDART API 본문 XML 직접 parser 구축 | 무료 (API 무료) | 2-8 주 | 높음 (XML schema 복잡, 정정 chronology, edge case 多) |
| Vendor parsed event data (FnGuide / KIS / 매경) | 유료 | 1-4 주 | 중 (vendor field coverage 평가 필요) |
| Hybrid (vendor + 자체 sample 검증) | 유료 + 자체 시간 | 3-6 주 | 중 |
| 학술 / 공개 dataset | 무료 | 1 일 (있을 시) | 낮음, 단 coverage 매우 제한 |

추정만. 사용자 자체 평가 필요.

## Forbidden Actions (Referee 명시)

- No binary flag reduced TEST under the current ID
- No return backtest using title flags only
- No standalone alpha framing
- No long-short framing
- No production linkage

Optional non-performance audit (별도 weak diagnostic ID 사용 시만):
- Title flag coverage / precision audit plan 가능
- 단 returns / alpha / excess performance / NAV / Sharpe / CAGR / MDD /
  portfolio results 포함 X
- KR-OVERHANG-AVOID-001 ID 사용 X (별도 weak diagnostic ID)

## Impact Beyond This Card

Task Q2 완료 = 두 카드 추가 unblock 가능:

- KR-DART-BODY-RETURN-001 (BACKLOG): 본문 parser 가 핵심 prerequisite
- KR-QUALITY-VALUE-RETURN-001 (BACKLOG): component 의 하나가 본문 기반
  주주환원 intensity 측정. Q2 통과 시 component 검증 가능 (단 1번 + 4번
  component 둘 다 살아남아야 composite TEST 가능)

따라서 Q2 = data infrastructure 우선순위에서 매우 높음 (3 카드 unblock
영향).

## Post-Unblock Path

Task Q2 완료 → A0 audit 재실행 → 12 항목 PASS 시:
- `KR_OVERHANG_AVOID_001_filter_test.md` spec 그대로 사용 (lock 됨)
- Bull/Bear/Referee 재심의
- Codex 위임 backtest 진입 가능

자동 진입 X. 사용자 명시 결정 + Referee 재 lock 필요.
