# S2 Event Log Schema Feasibility — Final

Date: 2026-05-23 15:42:46

## 17-field Referee schema

Locked since D1 (Referee Round 4.1 verdict):

| Field | Type | S2 phase deliverability |
|---|---|---|
| ticker | str(6) | ✅ from R000 / KOSDAQ list API |
| corp_code_dart | str(8) | ✅ from disclosure list |
| rcept_no | str(14) | ✅ |
| rcept_date | date | ✅ |
| event_date | date | ⚠️ partial — D3a 13.9%, D3b 0% |
| effective_date | date | ⚠️ partial — D3a 2.8%, D3b 5.9% |
| event_type | str(50) | ✅ taxonomy 14 types mapped (D3a 7 + D3b 3 + D3c 4 closed) |
| amount_krw | float | ⚠️ partial — D3a 36.1%, D3b 23.5% |
| shares | float | ⚠️ partial — D3a 13.9%, D3b 5.9% |
| shares_before | float | ⚠️ partial — D3a 2.8%, D3b not in schema |
| shares_after | float | ⚠️ not extracted — D3a 0% |
| factor | float | ❌ not extracted (감자 비율 / 무증 factor) |
| cancellation_linkage | str | ⚠️ algorithm works, but linkage_to_original_rcept_no populated only in-sample |
| source | str | ✅ `dart_opendart_body_v1` |
| parser_confidence | float [0,1] | ✅ calculated; D3a max 1.0 (1 row), D3b max 0.5 |
| manual_audit_status | str | ⚠️ all `not_audited`; full audit deferred to future phase |
| pit_available_at | datetime | ✅ at rcept_date level |

## Feasibility verdict

- **Schema is structurally feasible** — every required field is reachable from OPENDART body XML in principle
- **Schema is not population-feasible at production scale** with current generic parser — field-level extraction rates are too low for an event log usable in C2/C3 integration
- **Custom parsers (D3b)** + **D3a one-more-pass** + **D3c parser** would each contribute incremental population rates
- Estimated end-state population (if all future phases approved and executed): D3a ≥ 70% per field, D3b ≥ 50% per field, D3c best-effort

## What's locked at this point

- 17-field schema definition (no changes)
- 14-event-type taxonomy (no changes)
- Correction linkage algorithm (no changes)
- Normalization rules (correction prefix / subsidiary suffix / series marker)
- PIT lock policy

## What's deferred

- Production population of the event log
- C2/C3 wiring
- Strategy-ready claim on any field