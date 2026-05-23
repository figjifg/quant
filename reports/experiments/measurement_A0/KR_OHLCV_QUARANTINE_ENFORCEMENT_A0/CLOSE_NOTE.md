# KR-OHLCV-QUARANTINE-ENFORCEMENT-A0 — Final Close Note

Date: 2026-05-23  
Verdict source: Referee final close verdict, 2026-05-23.  
Initial pass commit accepted: `06a2dfa` on origin/main.

## Verdict

**CLOSED AS DEFECT-FOUND.**

- 8 deliverables ACCEPTED.
- 143 defects ACCEPTED (51 high + 92 medium).
- Phase closed as DEFECT-FOUND (not PASS) per Referee interpretation: "The presence of
  51 INVALID_ROW_LEAK and 92 MISSING_GUARD callsites means this is not a clean pass."
- No code patches applied (this phase was audit-only).
- No revision required to the current audit.

## Accepted outputs

1. `quarantine_enforcement_referee_lock.md`
2. `invalid_ohlcv_row_contract.md`
3. `downstream_ohlcv_usage_inventory.csv`
4. `allow_with_guard_usage_audit.csv`
5. `quarantine_enforcement_summary.md`
6. `invalid_row_leak_defect_ledger.csv` *(now augmented with `current_runtime_risk` and
   `reopen_blocker` annotation columns; original defect classification and severity
   unchanged)*
7. `required_patch_register.md`
8. `downstream_blockers_after_quarantine_a0.md`

## Accepted headline findings

- 240 Python files scanned.
- 963 OHLCV / flow / tradable / universe-related callsites inventoried.
- Classification breakdown accepted:
  - 416 NOT_APPLICABLE
  - 346 GUARDED
  - 92 MISSING_GUARD
  - 58 PASS
  - 51 INVALID_ROW_LEAK
- 143 defect candidates accepted (51 high + 92 medium).
- No return / NAV / Sharpe / alpha / performance metric produced.
- No strategy test started.

## Defect ledger annotation (additive, Referee-directed)

Per the Referee's note, two annotation columns were appended to
`invalid_row_leak_defect_ledger.csv`:

- `current_runtime_risk`:
  - `inactive_closed_strategy_path` for callsites in `src/strategies/`, `src/features/`,
    `src/backtest/`, `src/ops/`, `src/roles/`, `paper_trading/` (87 defects)
  - `inactive_infrastructure_path` for callsites in `src/data/`, `src/utils/`,
    `src/run_experiment.py`, `scripts/` (56 defects)
- `reopen_blocker`: `true` for all 143 defects.

**Closed-strategy paths remain in the ledger as reopen blockers.** They are NOT removed,
suppressed, or reclassified. Original severity and classification are unchanged. The
annotation is additive only.

## Direction summary

| Topic | Referee direction |
|---|---|
| The 143 defects | Accept as recorded. Preserve the ledger. Do not delete, suppress, or reclassify. |
| `required_patch_register.md` | Hold as documentation only. Patch register is the source of truth for any future patch phase. |
| Static-scan limit | Accept the limitation. Static scan proves guard proximity / absence, not runtime mask propagation. Runtime verification is a separate future phase. |
| Closed-strategy callsites | Remain in defect ledger as reopen blockers — they can become dangerous if strategies are reopened later. |

## Possible future phases (none active)

| Phase id | Purpose | Status |
|---|---|---|
| `KR-OHLCV-QUARANTINE-PATCH-PHASE` | Implement guard patches for the 51 LEAK + 92 MISSING_GUARD findings | NOT approved (separate Referee verdict required) |
| `KR-OHLCV-RUNTIME-MASK-PROPAGATION-A0` | Verify invalid-row masks propagate through actual runtime data flows | NOT approved |
| `KR-CLOSED-STRATEGY-CODEPATH-QUARANTINE-A0` | Audit closed-strategy code paths so they cannot be accidentally reactivated with invalid OHLCV usage | NOT approved |
| `KR-KRX-CALENDAR-SOURCE-ACQUISITION-A0` | Inherited from prior measurement-layer A0 candidates | NOT approved |
| `KR-LISTED-UNIVERSE-COVERAGE-A0` | DATA BACKLOG, source not acquired | NOT approved |
| `KR-EXECUTABLE-STATUS-COVERAGE-A0` | DATA BACKLOG, source not acquired | NOT approved |

Referee recommended next candidate (if the user chooses to continue):
**`KR-OHLCV-QUARANTINE-PATCH-PHASE`** — but **must not auto-start**.

## Continuing hard locks

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

`KR-OHLCV-QUARANTINE-ENFORCEMENT-A0` is **closed as DEFECT-FOUND**. No active work
remains. Await explicit user / Referee decision for any future patch phase or runtime
verification phase.
