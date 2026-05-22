# Unresolved S2 / C2 / C3 Register — Partial Re-A0

Date: 2026-05-22
Status: ACTIVE register of remaining infrastructure dependencies
Origin: Round 4 Partial Re-A0; S2/C2/C3 not yet closure-ready

## Summary

Round 4 Partial Re-A0 결과 34 defects 중 23 CLOSED / 10 PARTIAL / 1 DEFERRED-S2.
**1 critical defect + 다수 PARTIAL** 가 S2 / C2 / C3 의존.

## S2 — OPENDART Body Parser

### Current Status
- **Feasibility verified**: ZIP > XML download OK (`document.xml` endpoint)
- DART3 schema 확인 (`<DOCUMENT> > <BODY> > <LIBRARY> > <SECTION> > <TABLE>`)
- Sample 보관: `data/acquired/round4/s2_dart_body_samples/20240125000291_document.xml.zip`
- Parser 자체 **미완** (planning only)

### Dependency Map

| Component / Defect | Depends on | Status |
|---|---|---|
| G5_000005 event_source_missing (critical) | S2 body parser | DEFERRED-S2 (1 잔존 critical) |
| G5_000004 잔존 35 events (critical, partial closed) | C3 wiring → S2 event log | 95% closed, 5% open |
| C2 corporate action factor chain | S2 + body parser | NOT STARTED |
| C3 corporate action event log loader | S2 + body parser | NOT STARTED |
| Tradability `corporate_action_day` enum (reserved) | C3 | RESERVED (count = 0) |
| limit_lock_candidate full separation (TRAD_000003) | C3 | PARTIAL (41 rows, C3 후 정확 분류) |
| Top100 trade_value re-computation | S2 enhancement | optional |
| KR-DART-BODY-RETURN-001 (Round 1 BACKLOG) | S2 | BACKLOG |
| KR-OVERHANG-AVOID-001 (Round 1 BACKLOG, filter) | S2 partial | BACKLOG |
| KR-QUALITY-VALUE-RETURN-001 (Round 1 BACKLOG) | S2 partial | BACKLOG |

### S2 Acquisition Effort

| Phase | Time | Difficulty |
|---|---|---|
| Body XML bulk download (450k disclosures, 또는 filtered subset) | 1-2일 | low (sequential API call) |
| XML schema 분석 (DART3 form mapping) | 3-5일 | medium |
| Type별 parser (자사주 / CB·BW / 증자 / 감자 / 합병 / 추가상장 / 보호예수 / 대주주매도) | 2-4주 | high |
| 정정공시 linkage + cancellation handling | 1주 | medium |
| Sample audit (per type 20-50건 manual) | 1주 | high |
| W001 v2 C2 / C3 integration | 3-5일 | medium |
| **Total** | **5-9주** | high |

### S2 Unblock Path Options

| Option | 무엇 | Trade-off |
|---|---|---|
| A) 자체 OPENDART body parser 구축 | 사용자 host + Codex 위임 가능 | 무료, 5-9주 |
| B) Vendor parsed (FnGuide / KIS / 매경) | 구입 | 유료, 1-4주 |
| C) Hybrid (vendor + 자체 sample 검증) | 일부 구입 + 자체 | 균형, 3-6주 |
| D) Defer indefinitely | S2 미진행 | C2/C3 영원 미완 |

자세히: `docs/s2_opendart_body_parser_plan.md`

## C2 — Corporate Action Factor Chain

### Current Status
- W001 v2 Component 2
- Spec: `docs/W001_v2_infrastructure_repair_plan.md` Component 2
- Implementation: NOT STARTED

### Requires
- S2 event log (Component 3 의 prerequisite)
- New function: `compute_cumulative_adjustment_factor(event_log, ticker, as_of_date) -> float`
- New column: `cumulative_adjustment_factor` (chronological per ticker)

### Effect (when implemented)
- G5_000006 (factor chain unreproducible) = 추가 audit 가능 (현재 CLOSED 단 C1 의 adjusted return 으로 implicit; explicit factor chain 별도)
- Self-verification: cumulative factor × raw_close = adjusted_close 일치

## C3 — Corporate Action Event Log

### Current Status
- W001 v2 Component 3
- Spec: `docs/W001_v2_infrastructure_repair_plan.md` Component 3
- Implementation: NOT STARTED

### Requires
- S2 body parser output
- Event log schema (사전 등록):
  - ticker, corp_code_dart, event_date, effective_date, event_type, factor, shares_before, shares_after, cancellation_linkage, source

### Effect (when implemented)
- G5_000004 잔존 35 events → linkage 분류 → 5% open close 가능
- G5_000005 DEFERRED-S2 → CLOSED
- Tradability `corporate_action_day` enum 활성화
- TRAD_000003 limit pollution → corp_action_day 분리 후 41 rows 진정한 limit 만
- KR-DART-BODY-RETURN-001 (Round 1) → audit 가능
- 잔존 35 events 중 32 year-start gap 의 일부 = corp action day 가능성

## Other Open Items (S2/C2/C3 외)

### KRX Suspension Status API 직접 reconciliation
- S3 = DART pblntf=I (88.3% direct exchange action). 단 KRX OpenAPI 또는 data.krx.co.kr 의 official suspension status table 과 sample reconciliation 미실시.
- Effect: TRAD_000001 PARTIAL → CLOSED 가능
- Effort: 1-2주 (KRX API call + sample 100 ticker × 8 year reconciliation)

### Flow Full-Year Reconciliation (S6)
- 현재 sample = 1 month × 20 ticker (440 pairs)
- Full-year stratified random sample (예: ~20,000 pairs) → 95% confidence
- Effect: FLOW_000007 PARTIAL → CLOSED 가능
- Effort: 1-2주 (pykrx call automation)

### W001 v2.1 Patch — Tradable State Naming
- `panel_absence` rename → `not_in_dynamic_universe` (Referee 명시)
- Effort: <1일 (code rename + test update)
- Effect: TRAD_000001 partial → CLOSED 가능

### Top100 Selection Rule Exact Match
- 99.78/100 → 100/100 도달 위해 vendor exact rule (tie-break, market scope) 확정
- Effort: vendor doc 확보 또는 KOSPI/KOSDAQ exact universe 적용
- Effect: TOP_000003 PARTIAL → CLOSED 가능

## Priority for User Decision

| Priority | Task | Effect | Effort |
|---|---|---|---|
| 1 (recommended) | S2 OPENDART body parser | 1 critical + multiple BACKLOG unblock | 5-9주 (또는 vendor 1-4주) |
| 2 | KRX suspension API reconciliation | TRAD partial → close | 1-2주 |
| 3 | Flow full-year reconciliation | FLOW partial → close | 1-2주 |
| 4 | W001 v2.1 naming patch | TRAD partial → close | <1일 |
| 5 | Top100 exact rule | TOP partial → close | TBD (vendor doc) |

## Round 5+ Pre-conditions

새 strategy round (Round 5+) 진입 prerequisites:
- S2 parser complete OR vendor data acquired
- C2 + C3 implemented
- Full Re-A0 (current = Partial Re-A0)
- Referee 재승인
- Audit-first 12 항목 재확인

## Related

- `docs/s2_opendart_body_parser_plan.md`
- `docs/W001_v2_infrastructure_repair_plan.md` (C2, C3)
- `docs/W001_v2_reA0_gate_spec.md`
- `data/acquired/round4/s2_dart_body_samples/`
