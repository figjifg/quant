# C3 Corporate-Action Day Reclassification Prerequisites

Date: 2026-05-23
Scope: design-only — what C3 needs from parser output before reclassification is allowed.

## C3 purpose recap

C3 = corporate-action day reclassification. Reclassifies trading days that fall under a known corporate event from the default `regular_trading_day` enum into one of the corporate-action enum values, so downstream returns and signals can treat them differently (or exclude them).

## Current reserved enum state

| Enum value | Definition | Current population |
|---|---|---|
| `regular_trading_day` | Default; no known corporate event | All trading days not in any of the below |
| `corporate_action_day` | At least one corporate event affects the row | **0 rows** (reserved enum, never populated — see G5_000005 DEFERRED-S2) |
| `not_tradable` | KRX status indicates suspension/halt | populated by tradability v2.1 |
| `not_in_dynamic_universe` | Outside top-100 dynamic universe | populated by W001 v2.1 |
| `corp_action_day_reserved_pending_parser` | Reserved slot waiting on parser-output verification | All rows that would have been `corporate_action_day` if S2 parser were C3-ready |

## What can be classified now

Under S2-close-as-PARTIAL state:

| Subset | Classification possible? | Reason |
|---|---|---|
| Treasury cancel events (주식소각결정 amount + event_date) | **Partial — design only, no wiring** | D3a triage: 2/4 fields deterministic on 5-sample subset |
| Treasury acquire result | **Partial — design only** | All 4 fields deterministic but only 5 samples |
| Treasury acquire/dispose decisions | NOT yet | Most fields partial; manual_required |
| Treasury trust create | NOT yet | All non-deterministic |
| CB/BW issuance | NOT yet | event_date 0%; requires SECTION/COVER scanner |
| Conversion request | NOT yet | html_inline ambiguous |
| Rights issue / bonus issue / capital reduction / merger / split | NOT yet | D3c never opened (unsupported_form) |
| Additional listing / lockup release / major shareholder sale / correction-cancellation | NOT yet | D3c never opened |

**Net**: C3 cannot reclassify ANY trading day under current S2-close state, because design-only locks prevent wiring. The reserved-pending-parser enum remains the default for would-be corporate-action days.

## What remains `not_yet_available`

By construction, the following remain `not_yet_available` in C3:
- All 8 D3c event types
- All D3b event types (CB/BW/conversion event_date)
- D3a manual_required event types (5 of 7 base forms)

## Residual 35 G5 events — treatment

From Round 4.1 G5 residual ledger:
- 35 events with reserved enum (corp_action_day) pending parser output
- Of these, 1 was strategy-relevant (선도전기 2026-04-29)
- 34 were universe-outside (no strategy impact even if reclassified)

Under C3 design lock:
- The 35 events MUST remain in `corp_action_day_reserved_pending_parser` enum
- C3 design MUST include explicit `audit_log_entry` for each, citing parser_state and reopen condition
- The 1 strategy-relevant case is NOT actionable from this S2 phase; revisit during `S2-D3A-ONE-MORE-PASS-PHASE` if approved AND if parser_state for that base form reaches `available_partial` or higher

## How `corporate_action_day` enum remains reserved

Locked design rules:
1. C3 does NOT populate `corporate_action_day` from any parser output until:
   - The contributing event_type is in state `available_verified` OR `available_partial`, AND
   - Manual audit per event type has run (≥ 30 samples), AND
   - Full Re-A0 has accepted the parser as C3-ready, AND
   - Referee separately approves C3 wiring
2. Until all 4 above conditions are met, `corporate_action_day` enum value remains UNUSED in the production dataset
3. Any tooling reading the C3 enum MUST handle the case where `corporate_action_day` count = 0 (no implicit assumption it will be populated)

## Required fields for C3 reclassification

For any (corp_code, calendar_date) pair, C3 needs:
- `event_date` (≤ calendar_date)
- `effective_date` (defines window end)
- `event_type` (taxonomy bucket)
- `parser_confidence` ≥ acceptance gate (per parser_output_acceptance_gates.md)
- `manual_audit_status` = passed
- `event_source` ∈ {available_verified, available_partial}
- `pit_available_at` ≤ trading_date (PIT discipline)

If any are missing or not in the required state, the row CANNOT be used for reclassification in C3.

## C3 audit log contract

For each event-related row C3 evaluates, the audit log MUST record:
- input rcept_no, corp_code, calendar_date
- decision: `reclassified_to_corporate_action_day` | `kept_reserved` | `rejected_state` | `rejected_audit` | `rejected_pit`
- contributing event_type
- parser_state at evaluation time
- referee_phase_id (the phase that last verified the parser_state for this event type)

## Hard locks

- No C3 wiring in this design phase
- No `corporate_action_day` enum population
- No reclassification done on any row
- The 35 residual events remain reserved-pending
- No strategy-side use
