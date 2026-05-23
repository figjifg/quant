# S2 Form Coverage — Final

Date: 2026-05-23 15:42:46

## Referee 10-event-type taxonomy coverage

| Event type | D1+D2 samples | Parser wave | Final state |
|---|---|---|---|
| treasury_acquire | 5 | D3a | PARTIAL — 0/4 fields deterministic on 4-sample subset |
| treasury_dispose | 5 | D3a | PARTIAL — 0/4 fields deterministic |
| treasury_cancel | 5 | D3a | PARTIAL — 2/4 fields deterministic (amount, event_date) |
| treasury_trust_create | 5 | D3a | NON-DETERMINISTIC — 0/4 fields, custom parser needed if reopened |
| treasury_trust_terminate | 5 | D3a | PARTIAL — 2/4 fields partial |
| treasury_acquire_result | 5 | D3a | DETERMINISTIC — 4/4 fields (best of D3a) |
| treasury_dispose_result | 6 | D3a | PARTIAL — 0/4 deterministic but all 4 partial |
| cb_issue | 6 | D3b | NOT C3-ready — event_date 0% in body tables; needs COVER text scanner |
| bw_issue | 5 | D3b | NOT C3-ready — same as cb_issue |
| conversion_request | 6 | D3b | NOT C3-ready — html_inline ambiguous; dedicated parser family required |
| rights_issue | 0 | D3c | CLOSED — never opened in D3 |
| bonus_issue | 0 | D3c | CLOSED |
| capital_reduction | 0 | D3c | CLOSED |
| merger_split | 0 | D3c | CLOSED |
| additional_listing | 0 | D3c | CLOSED — R000 KOSPI has only 3 disclosures (`기타시장안내`) |
| lockup_release | 0 | D3c | CLOSED — `기타안내사항(안내공시)` HTML, free-text heavy |
| major_shareholder_sale | 0 | D3c | CLOSED — 임원ㆍ주요주주특정증권등소유상황보고서, large volume but html_inline |
| correction_withdrawal_cancel | 0 | D3c | CLOSED — `철회신고서` + heterogeneous 취소공시; whitelist required |

## Base form inventory (38 distinct base forms encountered)

See `reports/experiments/S2_phase_d2_schema_mapping/d2_form_inventory_expanded.md` for the full form-level inventory and `d2_actual_form_taxonomy_mapping.md` for the taxonomy mapping with normalization rules.

## Hard locks

- No strategy claim associated with any form
- No event log produced; coverage state is reporting only