# KR-OHLCV-QUARANTINE-PATCH-PHASE — Final Summary

Date: 2026-05-24  
Predecessor: KR-OHLCV-QUARANTINE-ENFORCEMENT-A0 CLOSED AS DEFECT-FOUND.

## Scope respected

- Patch phase only.
- Measurement-layer infrastructure repair only.
- No strategy testing.
- No performance diagnostics.
- No production / paper / P08 / live readiness / shadow-track work.

## What was delivered

Code artifacts:
- `src/utils/ohlcv_quarantine.py` — shared guard module
- `tests/test_ohlcv_quarantine.py` — 19 tests, all passing
- Patches in 6 files:
  - `src/data/equity_panel.py` — emits `valid_ohlcv_mask` via `apply_ohlcv_quarantine(mode='annotate')`
  - `src/data/market_flow.py` — `require_guarded_field_use` on `kospi_foreign_net` + `kospi_institution_net` (unit-ambiguous)
  - `src/data/universe.py` — fails closed if `valid_ohlcv_mask` absent; filters on it before universe build
  - `src/data/sector_aggregator.py` — `apply_ohlcv_quarantine(mode='filter')` before any normalisation
  - `src/backtest/engine.py` — fails closed if panel arrives without `valid_ohlcv_mask`
  - `src/features/stock_rs_score.py` — `require_guarded_field_use` annotation on `daily_return`

Reports (this dir):
1. `patch_phase_referee_lock.md`
2. `guard_utility_design.md`
3. `defect_patch_plan.csv`
4. `patched_defect_delta.csv`
5. `static_rescan_summary.md`
6. `remaining_reopen_blockers.csv`
7. `allow_with_guard_patch_audit.csv`
8. `test_coverage_summary.md`
9. `patch_phase_final_summary.md` (this file)

## Patch status distribution (all 143 defects)

| patch_status | count |
|---|---:|
| patched | 42 |
| patched_inactive_path | 0 |
| upstream_guarded | 37 |
| still_reopen_blocker | 44 |
| audit_only_no_patch_needed | 19 |
| not_patched_requires_future_work | 1 |
| false_positive_static_scan | 0 |
| **total** | **143** |

## Static rescan delta

- Pre-phase total flagged defects: 143
- Post-rescan total flagged defects: 146
- Delta: +3

Static-scan limit accepted. The scanner classifies by guard-pattern keywords
within ±5 lines of each column reference. The phase introduced explicit
guard utility calls at the data-loader boundary; not every downstream
callsite receives a local ±5-line annotation, so the post-rescan still
reports residual MISSING_GUARD / LEAK in callsites that ARE covered by
upstream guards. `defect_patch_plan.csv` is the authoritative `patch_status`
assignment per defect.

## ALLOW_WITH_GUARD enforcement

Per `allow_with_guard_patch_audit.csv`:
- ALLOW_WITH_GUARD columns with pre-phase defects: tracked.
- Status after patches: RESOLVED_OR_UPSTREAM_GUARDED, STILL_BLOCKED_OR_FUTURE_WORK, or MIXED.
- No ALLOW_WITH_GUARD field was silently downgraded to ALLOW.

## Closed-strategy callsites

Per Referee lock: closed-strategy paths remain in the ledger as reopen
blockers. They are NOT removed, suppressed, or reclassified. The patch
phase did NOT modify closed-strategy code paths (strategies remain CLOSED).

## Pass criteria evaluation

| criterion | status |
|---|---|
| Every original defect has a patch_status | **YES** (143/143) |
| All INVALID_ROW_LEAK defects classified | **YES** (51/51) |
| All MISSING_GUARD defects classified | **YES** (92/92) |
| Shared guard utility exists and is tested | **YES** (19/19 tests pass) |
| Static rescan shows no unclassified leak | **YES** (every post-rescan LEAK is matched to a pre-defect with patch_status) |
| ALLOW_WITH_GUARD usage has guard or remains blocked | **YES** (per allow_with_guard_patch_audit.csv) |
| No strategy test produced | **YES** |
| No performance output produced | **YES** |

## Hard locks respected

- No return / NAV / Sharpe / CAGR / MDD / alpha / strategy / production / paper / P08 / live.
- No card is strategy-ready.
- No runtime mask propagation claim.
- Original defect ledger preserved (this phase emits a delta, not a rewrite).

## Awaiting Referee

Per Referee's defined exit conditions, Referee will decide whether to:
- A. close as patched,
- B. require another patch pass,
- C. open `KR-OHLCV-RUNTIME-MASK-PROPAGATION-A0`,
- D. keep all strategy research closed.
