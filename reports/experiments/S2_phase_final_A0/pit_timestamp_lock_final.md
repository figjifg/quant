# S2 PIT Timestamp Lock — Final

Date: 2026-05-23 15:42:46

## PIT anchor fields (Referee-required)

| Field | Source | Lock state |
|---|---|---|
| `rcept_no` | OPENDART receipt number | **LOCKED 100%** (verified on all 108 D1+D2 rows in D3 parsed audit trail) |
| `rcept_date` | OPENDART receipt date (R000 column `rcept_date`) | **LOCKED 100%** |
| `pit_available_at` | rcept_no datetime floor (= disclosure submit timestamp) | Locked at rcept_date level; intraday timestamp `rcept_dt` (YYYYMMDD) available in R000 |

## PIT discipline maintained throughout S2 phase

- Look-ahead avoidance: all parser outputs include `pit_available_at` (= rcept_date)
- `event_date` (when extracted) is treated separately from `pit_available_at`; signals can only use event_date for grouping, not for execution timing prior to pit_available_at
- Correction linkage uses prior rcept_no (chronologically before correction) — never future linkage
- No event_date was ever substituted for rcept_date as PIT (Referee explicit directive)

## What PIT lock does NOT guarantee

- Field-level extraction precision (separate concern; remains low — see manual_audit_findings_final.md)
- Event semantic correctness (separate concern; remains in scope for any future C3 phase)

## Hard locks

- PIT lock verified at receipt-date level only; intraday PIT (for same-day signal availability) requires C2/C3 follow-up
- No strategy was built on PIT lock alone