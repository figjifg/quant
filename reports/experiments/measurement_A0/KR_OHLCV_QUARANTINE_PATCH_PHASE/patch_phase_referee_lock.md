# KR-OHLCV-QUARANTINE-PATCH-PHASE — Referee Lock

Date: 2026-05-24  
Verdict source: Referee verdict opening this phase, 2026-05-24.  
Predecessor: KR-OHLCV-QUARANTINE-ENFORCEMENT-A0 CLOSED AS DEFECT-FOUND (commit `f0d40be`).

## Scope (Referee-fixed)

- Patch phase only.
- Measurement-layer infrastructure repair only.
- Implement guards for the 143 findings from `KR-OHLCV-QUARANTINE-ENFORCEMENT-A0`.
- No strategy testing.
- No performance diagnostics.
- No production / paper / P08 / live readiness / shadow-track work.

## Primary source-of-truth (read-only)

- `reports/experiments/measurement_A0/KR_OHLCV_QUARANTINE_ENFORCEMENT_A0/invalid_row_leak_defect_ledger.csv`
- `reports/experiments/measurement_A0/KR_OHLCV_QUARANTINE_ENFORCEMENT_A0/required_patch_register.md`
- `reports/experiments/measurement_A0/KR_OHLCV_QUARANTINE_ENFORCEMENT_A0/invalid_ohlcv_row_contract.md`
- `reports/experiments/measurement_A0/KR_OHLCV_QUARANTINE_ENFORCEMENT_A0/downstream_ohlcv_usage_inventory.csv`

These inputs are **not modified** by this phase.

## Allowed work groups (8)

1. Build shared guard utilities (`src/utils/ohlcv_quarantine.py`) with fail-closed
   semantics on missing required columns.
2. Patch INVALID_ROW_LEAK findings (51 high).
3. Patch MISSING_GUARD findings (92 medium).
4. ALLOW_WITH_GUARD enforcement cross-check.
5. Closed-strategy paths remain as reopen blockers (never deleted; mark with the
   appropriate `patch_status`).
6. Re-run static scan + before/after comparison.
7. Unit tests for the guard module.
8. Documentation (patch delta ledger; original ledger preserved).

## Patch status taxonomy (every defect must receive one)

- `patched` — call site received an explicit local guard.
- `patched_inactive_path` — call site is in closed-strategy code; guard added but path
  is currently inactive.
- `upstream_guarded` — call site is covered by an upstream guard (e.g., the data
  loader's `valid_ohlcv_mask`).
- `still_reopen_blocker` — call site not patched; remains a blocker for any future
  strategy reopen.
- `audit_only_no_patch_needed` — call site is in audit/reports code that only reports
  on the column, never consumes it for value. **Requires evidence.**
- `not_patched_requires_future_work` — patch deferred to a separate phase.
- `false_positive_static_scan` — verified false positive of the static scan.
  **Requires evidence.**

Rules (Referee-locked):
- Do NOT delete original defects.
- `false_positive_static_scan` requires evidence.
- `audit_only_no_patch_needed` requires evidence.
- `still_reopen_blocker` remains a blocker for any future strategy reopen.
- Original defect ledger from the enforcement phase is preserved unchanged.

## Required outputs (9)

1. `patch_phase_referee_lock.md` (this file)
2. `guard_utility_design.md`
3. `defect_patch_plan.csv`
4. `patched_defect_delta.csv`
5. `static_rescan_summary.md`
6. `remaining_reopen_blockers.csv`
7. `allow_with_guard_patch_audit.csv`
8. `test_coverage_summary.md`
9. `patch_phase_final_summary.md`

## Required code artifacts

- `src/utils/ohlcv_quarantine.py` (shared guard module)
- tests for the new guard module
- minimal call-site patches needed to reduce or block the 143 defects
- no broad refactor unless required for guard insertion

## Pass criteria

- Every original defect has a `patch_status`.
- All 51 high-severity INVALID_ROW_LEAK defects: patched / upstream_guarded /
  still_reopen_blocker.
- All 92 medium-severity MISSING_GUARD defects: patched / upstream_guarded /
  still_reopen_blocker.
- Shared invalid OHLCV guard utility exists and is tested.
- Static rescan shows no unclassified leak.
- ALLOW_WITH_GUARD usage has documented guard or remains blocked.
- No strategy test or performance output produced.

## Fail gates

- Any invalid OHLCV row can still enter an active or potentially reopenable code path
  without guard.
- Any ALLOW_WITH_GUARD field used without guard or documentation.
- Any defect deleted, suppressed, or downgraded without evidence.
- Any closed-strategy path removed from blocker tracking.
- Any return / NAV / CAGR / Sharpe / hit rate / alpha / excess return / MDD produced.
- Any strategy test started.
- Any production / paper / P08 / live readiness / shadow-track work touched.

## Hard prohibitions

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
- No production / paper / P08 / live readiness / shadow connection.
- No card may be described as strategy-ready.

## Important boundary

This is a **patch phase**, NOT runtime verification.

- Do NOT claim runtime mask propagation is fully verified.
- If runtime propagation needs validation, record it as a future phase
  `KR-OHLCV-RUNTIME-MASK-PROPAGATION-A0` (not started here).

## End condition

- Return patch-phase report only.
- Do not recommend strategy testing.
- Do not recommend production or paper tracking.
- Referee will decide after reviewing the patch-phase output whether:
  - A. close as patched,
  - B. require another patch pass,
  - C. open runtime mask propagation A0,
  - D. keep all strategy research closed.
