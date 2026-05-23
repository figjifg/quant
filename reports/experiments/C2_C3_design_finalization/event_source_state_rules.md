# Event-Source-State Rules per Event Type

Date: 2026-05-23
Scope: For each Referee 14-event-type taxonomy entry, the current S2-close-state classification.

## Source data

State assignments below are derived from:
- `reports/experiments/S2_phase_d3_parser_v3/` (extraction rates)
- `reports/experiments/S2_phase_d3_triage/d3a_manual_label_audit.md` (determinism)
- `reports/experiments/S2_phase_d3_triage/d3b_feasibility_triage.md` (D3b classification)
- `reports/experiments/S2_phase_final_A0/` (final close state)

## Treasury group (D3a wave)

| Event type | Base form | Current state | Field-level usability | Reason |
|---|---|---|---|---|
| `treasury_acquire` | 주요사항보고서(자기주식취득결정) | **manual_required** | amount/shares/event_date partial; not deterministic | 3 fields partial on 4-sample subset; ACODE 11332 |
| `treasury_dispose` | 주요사항보고서(자기주식처분결정) | **manual_required** | amount/shares/event_date partial | 3 partial / 1 non-det; ACODE 11333 |
| `treasury_cancel` | 주식소각결정 | **available_partial** (treasury subset only) | amount + event_date deterministic; shares + effective_date non-det | 2/4 deterministic; usable for partial C3 input on amount/event_date |
| `treasury_trust_create` | 주요사항보고서(자기주식취득신탁계약체결결정) | **manual_required** | all fields non-deterministic | 0/4 deterministic; ACODE 11334 |
| `treasury_trust_terminate` | 주요사항보고서(자기주식취득신탁계약해지결정) | **manual_required** | 2 partial / 2 non-det | ACODE 11335 |
| `treasury_acquire_result` | 자기주식취득결과보고서 | **available_partial** (best of D3a) | all 4 deterministic | 4/4 deterministic; ACODE 00681; one-more-pass could elevate to available_verified |
| `treasury_dispose_result` | 자기주식처분결과보고서 | **manual_required** | all 4 partial | 0/4 deterministic; ACODE 00683 |

## CB / BW / Conversion group (D3b wave)

| Event type | Base form | Current state | Reason |
|---|---|---|---|
| `cb_issue` | 주요사항보고서(전환사채권발행결정) | **not_available** (event_date) + **manual_required** (other fields) | event_date 0% extraction; body table does not contain it; requires SECTION/COVER text scanner (S2-D3B-CUSTOM-PARSER-PHASE) |
| `bw_issue` | 주요사항보고서(신주인수권부사채권발행결정) | **not_available** (event_date) + **manual_required** (other fields) | same as cb_issue |
| `conversion_request` | 전환청구권행사 | **not_available** (most fields, html_inline) + **manual_required** (a few rows) | 5/6 ambiguous in html_inline; needs dedicated parser family |

## D3c group (closed)

| Event type | Current state | Reason |
|---|---|---|
| `rights_issue` | **unsupported_form** | D3c never opened; ACODE 11306 + 11307 + 11308 catalogued in inventory but parser not implemented |
| `bonus_issue` | **unsupported_form** | D3c never opened; ACODE 11308 inventory exists |
| `capital_reduction` | **unsupported_form** | D3c never opened; ACODE 11309 inventory exists |
| `merger_split` | **unsupported_form** | D3c never opened; ACODE 11344 + 11345 inventory exists |
| `additional_listing` | **unsupported_form** | R000 KOSPI has only 3 disclosures (`기타시장안내`); KOSDAQ separate source needed |
| `lockup_release` | **unsupported_form** | html_inline `기타안내사항(안내공시)` form; free-text heavy |
| `major_shareholder_sale` | **unsupported_form** | ACODE 00634 임원ㆍ주요주주특정증권등소유상황보고서; large volume but html_inline |
| `correction_withdrawal_cancel` | **unsupported_form** | 철회신고서 + heterogeneous 취소공시; whitelist required |

## Aggregated state distribution (S2-close snapshot)

| State | Event-type count |
|---|---|
| available_verified | 0 (none verified — manual audit not run) |
| available_partial | 2 (treasury_cancel partial fields, treasury_acquire_result) |
| manual_required | 5 (treasury_acquire/dispose/trust_create/trust_terminate/dispose_result) |
| not_available | 3 (cb_issue, bw_issue, conversion_request for event_date) |
| unsupported_form | 8 (all D3c types) |
| deferred_s2 | (G5_000005 ledger entry, NOT a body-parser event_type slot) |
| attachment_only | 0 in D3a/D3b sample; 4 D1 carryover assigned to missing_xml |
| parser_failed | 0 across 3 D3 rounds |
| correction_unlinked | 24 of 27 correction rows in D1+D2 sample union (in-sample limitation) |
| low_confidence | many D3a/D3b rows below 0.6 confidence gate |

## Rules for new event types

If a new disclosure form is introduced into the OPENDART universe AFTER this design lock:
- Default state = `unsupported_form` until added to a parser wave
- Adding a form to a parser wave requires the Referee phase verdict that opens that wave
- C2/C3 MUST NOT auto-promote unsupported_form rows to usable states

## Hard locks

- No event type is described as strategy-ready in this document
- No event type is wired into C2/C3 implementation
- All state assignments are advisory metadata for future Referee verdicts
