# Downstream Blockers After Quarantine A0

Date: 2026-05-23  
Scope: design-only — explain what remains blocked after this phase, even if every
recommended patch in `required_patch_register.md` were eventually applied.

## What this phase delivered

- 8 outputs in `reports/experiments/measurement_A0/KR_OHLCV_QUARANTINE_ENFORCEMENT_A0/`.
- Static inventory of every callsite that reads OHLCV / flow / tradable / universe
  columns across 240 .py files.
- Defect ledger of LEAK + MISSING_GUARD callsites with `QENF_NNNNN` IDs.
- ALLOW_WITH_GUARD column audit linking 66 distinct columns to their downstream
  consumers (25 of 66 have at least one outside-audit consumer).
- 10 patch-family recommendations (documentation only).

## What this phase did NOT do

- Did NOT apply any patch.
- Did NOT verify mask propagation at runtime — static scan only.
- Did NOT run strategies, backtests, or any performance diagnostic.
- Did NOT produce return / NAV / Sharpe / CAGR / MDD.
- Did NOT close any earlier defect.

## Remaining blockers (post-this-phase)

Even with patches applied (hypothetically, in a future phase), the following blockers
persist:

### Calendar source

- The authoritative KRX trading-calendar source remains unacquired (P0-2 finding).
- Execution simulation stays CLOSED until `KR-KRX-CALENDAR-SOURCE-ACQUISITION-A0`
  is opened and resolved.

### Listed universe

- No daily KRX listed-universe feed in the repo (P2 backlog).
- Survivorship-safe claims remain prohibited until
  `KR-LISTED-UNIVERSE-COVERAGE-A0` is opened (currently DATA BACKLOG).

### Executable status

- No authoritative halt / limit-lock / surveillance feed in the repo (P2 backlog).
- Tradability claims remain prohibited until
  `KR-EXECUTABLE-STATUS-COVERAGE-A0` is opened (currently DATA BACKLOG).

### Unit ambiguities (P0-1 defects)

- `kospi_foreign_net` / `kospi_institution_net` / `kospi_individual_net` /
  `large_foreign_net` / `large_institution_net` / `kospi_trade_volume` etc. carry the
  `KRW_mil_or_count` unit string.
- Any KRW conversion of these columns remains blocked until the unit is resolved with
  the vendor.

### Vendor regex-derived flags

- `flag_capital_raise` / `flag_cb_bw` / `flag_capital_reduction` / `flag_audit_issue` /
  `flag_trading_halt` / `flag_litigation` / `flag_large_holder` /
  `flag_treasury_stock` / `flag_merger_split` / `flag_earnings` / `flag_contract` /
  `flag_event_risk` are derived from `report_nm` regex matches.
- They are NOT authoritative. Strategy use is blocked until S2 body parser produces
  C3-ready event labels (S2 phase = CLOSED AS PARTIAL).

### W001 v2 derived overlays

- `tradable_state` is a v1.x derivation (TRAD_000001 critical defect, partially
  mitigated). It cannot certify executable status.
- `permanent_id` / `terminal_status` / `terminal_date` are derived from a 53.1% S3
  coverage rate on disappeared tickers; 47% of historic delistings remain unresolved.

### Strategy reopen

- All Korean standalone-alpha cards remain CLOSED (Research Freeze v2).
- This phase does not unlock any of them.
- Strategy reopen requires:
  - this audit + patch phase complete,
  - listed-universe + executable-status A0 complete,
  - calendar source acquired,
  - manual audit phase complete (S2-MANUAL-AUDIT-PHASE, currently not approved),
  - C2 + C3 implementation (currently NOT APPROVED, design-only),
  - per-card Referee reopen verdict.

## Estimated critical path (no commitments)

| Step | Status |
|---|---|
| `KR-OHLCV-QUARANTINE-ENFORCEMENT-A0` (this phase) | **complete** |
| `KR-OHLCV-QUARANTINE-PATCH-PHASE` (new) | not approved |
| `KR-KRX-CALENDAR-SOURCE-ACQUISITION-A0` | not approved |
| `KR-LISTED-UNIVERSE-COVERAGE-A0` | data backlog, source not acquired |
| `KR-EXECUTABLE-STATUS-COVERAGE-A0` | data backlog, source not acquired |
| `S2-D3A-ONE-MORE-PASS-PHASE` (~1-2 weeks) | not approved |
| `S2-D3B-CUSTOM-PARSER-PHASE` (~4-7 weeks) | not approved |
| `S2-MANUAL-AUDIT-PHASE` | not approved |
| `C2-IMPLEMENTATION-PHASE` | not approved |
| `C3-IMPLEMENTATION-PHASE` | not approved |
| `FULL-RE-A0-PHASE` | not approved |
| `STRATEGY-REOPEN-REVIEW` | not approved (per-card) |

No phase auto-progresses. Each transition requires a fresh Referee verdict.

## Affected strategy cards (no reopen implied)

The following cards remain CLOSED regardless of this audit's output:

- `KR-DART-BODY-RETURN-001`
- `KR-OVERHANG-AVOID-001`
- `KR-QUALITY-VALUE-RETURN-001`
- `KR-CONDITIONAL-SHOCK-REVERSION-001`
- Round 2 cards (5)
- All B/D/E/F/G/H (Korean standalone-alpha) closures
- All I/K/J/Q/R/S/X-Lab / N006 / W001 v2 strategy moves

P08_IEF30 production / paper / live: **UNCHANGED**.

## Hard locks

- This document does NOT open or progress any future phase.
- This document does NOT reopen any closed strategy card.
- This document does NOT recommend strategy testing.
- This document does NOT recommend production or paper tracking.
