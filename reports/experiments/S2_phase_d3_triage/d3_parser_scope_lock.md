# D3 Parser Scope Lock

Date: 2026-05-23 15:32:39

## Final state of each D3 wave (post-triage)

| Wave | Lock state | Reason |
|---|---|---|
| D3a | **PARTIAL** | only 2/7 base forms have deterministic labels |
| D3b | **PARTIAL / NOT C3-ready** | shares (5.9% vs v1 29.4%) and event_date (0.0%) both miss Referee pass targets; custom parsers required (see d3b_custom_parser_decision.md) |
| D3c | **CLOSED** | not opened per Referee; remains skeleton-only |

## Downstream constraints

- D3a current state may produce a partial corporate-action event log for treasury actions, but ONLY if explicitly marked as PARTIAL/INFRA. Cannot be described as strategy-ready.
- D3b state means CB/BW dilution events and conversion requests are NOT in a usable event log shape. Overhang signal construction is blocked.
- D3c forms (additional listing / lockup / major shareholder sale / correction-cancellation) remain unparsed; their event types are NOT available in any event log.
- C2 (factor chain integration) and C3 (corporate action day reclassification) are NOT C3-ready.
- KR-DART-BODY-RETURN-001 (backlog) remains unblock-able only on the D3a treasury subset, and only as PARTIAL.

## Hard locks

- No D3c full implementation
- No C2/C3 integration
- No unified all-event event log finalization
- No strategy testing / return outcome
- No parser-strategy-ready claim

## Reopen conditions (Referee-only)

- D3a one-more-pass: Referee approval after this triage
- D3b: Referee approval to implement custom parsers OR mark D3b PARTIAL permanent
- D3c: Referee approval after D3a/D3b state is resolved