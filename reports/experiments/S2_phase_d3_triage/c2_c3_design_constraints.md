# C2 / C3 Design Constraints (post-D3 triage)

Date: 2026-05-23 15:32:39

## C2 (factor chain integration) constraints

- C2 design CANNOT assume a complete corporate-action event log.
- D3a treasury events are partially available (subject to D3a PARTIAL/one-more-pass state).
- D3b dilution events (CB/BW/conversion) are NOT C3-ready.
- C2 factor chain must explicitly track which event types are sourced from parser vs not-yet-sourced.
- C2 design should NOT block on a unified event log; instead, accept per-event-type partial coverage with explicit not_available flags.

## C3 (corporate action day reclassification) constraints

- C3 cannot reclassify days for corporate actions whose events are not in the partial event log.
- Treasury cancellation (주식소각결정) and merger/split require the D3a one-more-pass to be feasible inputs to C3.
- CB/BW dilution and conversion request events are NOT available for C3 reclassification until D3b custom parsers exist (Referee approval required).
- C3 design must include a not_yet_available branch that surfaces uncovered events as audit log entries.

## Affected G5 / TRAD residuals

- G5_000005 DEFERRED-S2: still deferred; S2 phase parser cannot yet provide the corporate action day reclassification input.
- G5_000004 35 strategy-relevant events: only the treasury subset is partially reachable via D3a. Other event types (CB/BW/conversion) remain unparsed.
- TRAD_000003 limit pollution (41 rows): same constraint; C3 reclassification of corp_action_day still blocked.

## Allowed C2/C3 design activities

- Documentation updates reflecting D3a partial / D3b not-ready / D3c closed
- Schema design for event log with explicit `event_source` and `event_status` fields (parser-source / not_available / partial)
- Spec for not_yet_available event type handling in C3 day reclassification

## NOT allowed

- Wire parser outputs into a production C2/C3 path
- Create unified all-event event log
- Use C2/C3 outputs in strategy testing of any kind
- Treat parser output as strategy-ready