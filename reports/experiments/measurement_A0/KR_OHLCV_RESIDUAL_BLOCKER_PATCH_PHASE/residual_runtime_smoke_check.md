# Residual Patch Runtime Smoke Check

Date: 2026-05-24  
Phase: KR-OHLCV-RESIDUAL-BLOCKER-PATCH-PHASE  
Method: each patched closed-strategy entry function is invoked with a panel
lacking `valid_ohlcv_mask`. The expected outcome is `OhlcvQuarantineError`
raised by the newly added `assert_panel_has_valid_mask` call.

**This is NOT a backtest.** No strategy is executed. The smoke check only
verifies the fail-closed assertion fires.

## Headline: **6/6 smoke checks passed**

## Per-entry results

| entry | raised? | exception type | passed |
|---|---|---|---|
| `baselines.run_baseline` | True | `OhlcvQuarantineError` | PASS |
| `b004.run_b004_variants` | True | `OhlcvQuarantineError` | PASS |
| `c003.run_c003_variants` | True | `OhlcvQuarantineError` | PASS |
| `d004.run_d004_variants` | True | `OhlcvQuarantineError` | PASS |
| `p002.run_p002_execution_backtest` | True | `OhlcvQuarantineError` | PASS |
| `p003.run_capacity_backtest` | True | `OhlcvQuarantineError` | PASS |

## Interpretation

Each of the 6 patched closed-strategy files now raises `OhlcvQuarantineError`
at function entry when a panel arrives without the loader-emitted
`valid_ohlcv_mask` column. This is defense-in-depth on top of the runtime-
verified backtest engine entry gate; together they provide two independent
fail-closed layers if a closed strategy were ever reactivated.

## Hard locks (preserved)

- No backtest executed.
- No return / NAV / Sharpe / alpha / strategy metric produced.
- No production / paper / P08 / live / shadow touched.
- All 6 closed-strategy files remain CLOSED under Research Freeze v2.
