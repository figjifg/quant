# S2 C2 / C3 Readiness — Final

Date: 2026-05-23 15:42:46

## C2 (factor chain integration) — DESIGN ONLY

Status: **NOT integrated**. Design constraints documented in `reports/experiments/S2_phase_d3_triage/c2_c3_design_constraints.md`.

C2 design requirements (locked):
- Accept per-event-type partial coverage with explicit `event_source` and `event_status` fields
- Include `not_available` branch for event types whose parser is not yet C3-ready
- Do NOT block on a unified event log; per-event-type partial coverage is allowed if marked explicitly

## C3 (corporate-action day reclassification) — DESIGN ONLY

Status: **NOT integrated**. Design constraints documented.

C3 design requirements (locked):
- Reclassification of `corp_action_day` requires deterministic event_date + effective_date per disclosure
- Current D3a 13.9% event_date rate is insufficient; one-more-pass on the 2 deterministic forms might lift this for the treasury subset
- D3b CB/BW/conversion: event_date 0%, blocked entirely
- Spec: not_yet_available branch surfaces uncovered events as audit log entries, not as reclassified days

## Blocked downstream items

| Item | Status | Reason |
|---|---|---|
| G5_000005 | DEFERRED-S2 → **REMAINS DEFERRED** | S2 parser cannot deliver C3 reclassification input |
| G5_000004 (35 strategy-relevant events) | Partially reachable for treasury subset only | Other event types unparsed |
| TRAD_000003 limit pollution (41 rows) | **STILL BLOCKED** | Same root cause |
| KR-DART-BODY-RETURN-001 backlog | Partial unblock on treasury subset only | Other event types not C3-ready |
| KR-OVERHANG-AVOID-001 backlog | **STILL BLOCKED** | CB/BW/conversion event_date 0% in body tables |

## Allowed C2/C3 work going forward (design only)

- Finalize design constraints documents
- Define `event_source` / `event_status` / `manual_required` enum values
- Spec how C2/C3 would consume future parser outputs (interface contract)
- Document what custom parser work would be required (D3B-CUSTOM-PARSER-PHASE pre-spec)

## NOT allowed

- Wire parser outputs into a production C2/C3 path
- Create unified all-event event log
- Reclassify corp_action_day using parser outputs
- Use C2/C3 outputs in any strategy testing
- Treat parser output as strategy-ready

## Hard locks

- C2/C3 = DESIGN-ONLY
- Reopen requires Referee-approved D3B-CUSTOM-PARSER-PHASE + subsequent integration approval