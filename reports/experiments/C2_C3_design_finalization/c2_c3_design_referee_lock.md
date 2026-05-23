# C2/C3 Design Finalization — Referee Lock

Date: 2026-05-23
Origin: Referee verdict (2026-05-23) — selected next active work after S2 close.

## Verdict (paste from Referee, locked)

> Selected next work: **C2-C3-DESIGN-FINALIZATION**
>
> Scope:
> - Design-only.
> - No parser wiring.
> - No C2/C3 implementation.
> - No unified all-event event log finalization.
> - No strategy testing.
> - No performance diagnostics.
> - No production / paper / P08 / live readiness / shadow-track work.

## Rationale (Referee)

- S2 OPENDART Body Parser Phase is CLOSED AS PARTIAL.
- D3a is PARTIAL.
- D3b is PARTIAL / NOT C3-ready.
- D3c is CLOSED.
- Current parser output is not reliable enough for C3-ready corporate-action event logs.
- Before any further parser phase, C2/C3 must have a clear design contract for unavailable, partial, manual-required, and parser-confidence-limited event sources.

## 7 Allowed Tasks

1. Define C2/C3 input-state taxonomy (10 states)
2. Define event_source_state rules per event type
3. Define C2 corporate-action factor-chain prerequisites
4. Define C3 corporate-action day reclassification prerequisites
5. Define parser-output acceptance gates
6. Define blocked downstream strategy implications (per card)
7. Define future phase dependency graph

## 9 Required Outputs (this directory)

1. `c2_c3_design_referee_lock.md` (this file)
2. `c2_c3_input_state_taxonomy.md`
3. `event_source_state_rules.md`
4. `c2_factor_chain_prerequisites.md`
5. `c3_corporate_action_day_prerequisites.md`
6. `parser_output_acceptance_gates.md`
7. `downstream_strategy_blockers.md`
8. `future_phase_dependency_graph.md`
9. `c2_c3_design_final_summary.md`

## Hard Prohibitions

- No parser wiring
- No C2/C3 implementation
- No unified all-event event log finalization
- No D3c full implementation
- No return backtest
- No NAV / CAGR / Sharpe / hit rate / alpha / excess return / MDD
- No post-event drift / migration / turnover / resume / reversal / flow-return
- No raw return as signal/outcome
- No Round 2 strategy restart
- No flow strategy testing
- No DART body alpha test
- No overhang alpha/filter test
- No production / paper / P08 / live readiness / shadow connection
- No parser result described as strategy-ready

## End Condition

- Return design-only C2/C3 finalization bundle
- Do not recommend strategy testing
- Do not recommend production or paper tracking

## Compliance posture

All 9 outputs in this bundle are design artifacts only. They define contracts, taxonomies, gates, and dependency relationships. No code change to parser modules. No data wiring. No strategy claim.
