# KR-OHLCV-QUARANTINE-ENFORCEMENT-A0 — Referee Lock

Date: 2026-05-23  
Verdict source: Referee verdict opening this phase, 2026-05-23.  
Predecessor: Measurement-layer A0 initial pass CLOSED AS PARTIAL / DEFECT-FOUND (commit
`6607a83`).

## Scope (Referee-fixed)

- Measurement-layer A0 only.
- Verify that invalid OHLCV rows are excluded or explicitly guarded in all downstream
  code paths.
- No strategy testing.
- No performance diagnostics.
- No production / paper / P08 / live readiness / shadow-track work.

## Reason for opening

Measurement-layer A0 initial pass found broad invalid OHLCV rows:

- OHLC ordering violations (58,649 across 4 panels + S1 adjusted),
- nonpositive price rows (53,556),
- the OHL=0 / `close>0` vendor non-trading-row signature (shared signature across all
  sources).

Referee lock requires these rows to be quarantined. They MUST NOT be treated as price
observations, halt evidence, suspension evidence, or alpha signals. Before any future
diagnostic can safely use OHLCV fields, downstream guard enforcement must be audited.

## Allowed tasks (6)

1. Build invalid-row contract.
2. Scan downstream code paths (`src/`, `research/`, `backtest/`, `scripts/`, reports
   build scripts).
3. Verify quarantine enforcement (audit-only; no perf diagnostic).
4. Field guard audit (ALLOW_WITH_GUARD fields from the field metadata contract).
5. Defect classification (PASS / GUARDED / MISSING_GUARD / INVALID_ROW_LEAK / AMBIGUOUS
   / NOT_APPLICABLE).
6. Patch recommendation only — documentation; no implementation unless Referee approves
   a separate patch phase.

## Required outputs (8)

1. `quarantine_enforcement_referee_lock.md` (this file)
2. `invalid_ohlcv_row_contract.md`
3. `downstream_ohlcv_usage_inventory.csv`
4. `allow_with_guard_usage_audit.csv`
5. `quarantine_enforcement_summary.md`
6. `invalid_row_leak_defect_ledger.csv`
7. `required_patch_register.md`
8. `downstream_blockers_after_quarantine_a0.md`

## Pass criteria

- All downstream OHLCV consumers inventoried.
- Invalid-row signatures explicitly defined.
- Every invalid-row use is guarded, blocked, or recorded as a defect.
- Every ALLOW_WITH_GUARD field use has a documented guard or a defect.
- No invalid OHLCV row silently treated as a valid price observation.
- No invalid OHLCV row interpreted as halt / suspension evidence without official
  executable-status source.
- No performance metric generated.

## Kill / fail gates

- Any downstream path uses invalid OHLCV rows without guard.
- Any code treats OHL=0 / `close>0` rows as valid price observations.
- Any code infers halt, suspension, or executable status from invalid OHLCV alone.
- Any ALLOW_WITH_GUARD field is used without documented guard.
- Any return / alpha / NAV / Sharpe / CAGR / MDD / strategy metric is produced.
- Any strategy testing is started.

## Hard prohibitions (continuing)

- No return backtest.
- No NAV / CAGR / Sharpe / hit rate / alpha / excess return / MDD.
- No post-event drift / migration return / turnover return / resume return / reversal
  return / flow-return.
- No raw jump alpha.
- No price-only mean reversion.
- No generic value / quality / momentum / RS ranking.
- No DART body alpha test.
- No overhang filter alpha test.
- No flow strategy testing.
- No executable assumption from panel presence.
- No survivorship-safe claim without official listed universe.
- No use of ALLOW_WITH_GUARD fields without documented guard.
- No use of invalid OHLCV rows without quarantine.
- No production / paper / P08 / live readiness / shadow connection.
- No card may be described as strategy-ready.

## End condition

- Return OHLCV quarantine enforcement A0 report only.
- Do not recommend strategy testing.
- Do not recommend production or paper tracking.
