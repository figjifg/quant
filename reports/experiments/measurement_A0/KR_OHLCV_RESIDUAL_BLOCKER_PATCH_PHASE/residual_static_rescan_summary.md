# Residual Static Rescan Summary

Date: 2026-05-24  
Phase: KR-OHLCV-RESIDUAL-BLOCKER-PATCH-PHASE  
Method: re-run `p_ohlcv_quarantine_enforcement.py` after closed-strategy
hardening patches; compare residual-blocker classification.

## Global classification (from rescan)

| classification | count |
|---|---:|
| `GUARDED` | 352 |
| `INVALID_ROW_LEAK` | 51 |
| `MISSING_GUARD` | 95 |
| `NOT_APPLICABLE` | 518 |
| `PASS` | 72 |

## Interpretation

The closed-strategy hardening adds a `assert_panel_has_valid_mask` call to
the entry function of 6 closed strategy files. The static scanner's GUARD
pattern regex recognises the function name (containing `valid` and `mask`
literals nearby) within the ±5-line window of OHLCV references in those
patched files. As a result, some prior MISSING_GUARD / INVALID_ROW_LEAK
callsites in those 6 files re-classify into GUARDED on rescan.

Authoritative status remains the `residual_patch_plan.csv` rather than the
static rescan classification. The rescan is informational only.

## Enforcement-phase artifacts preserved

The original `KR_OHLCV_QUARANTINE_ENFORCEMENT_A0/` defect ledger is preserved
by the rescan wrapper (post-rescan snapshots are saved to
`KR_OHLCV_RESIDUAL_BLOCKER_PATCH_PHASE/rescan/`).
