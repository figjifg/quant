# Backtest Entry Fail-Closed Check

Date: 2026-05-24  
Phase: KR-OHLCV-RUNTIME-MASK-PROPAGATION-A0  
Method: invoke `run_candidate_backtest` with (a) a panel missing
`valid_ohlcv_mask` and (b) a panel with the annotation present. Verify that
case (a) raises `OhlcvQuarantineError` at the gate and case (b) does not raise
at the same gate.

## Result table

| case | input | expected | observed | passed |
|---|---|---|---|---|
| A | panel without `valid_ohlcv_mask` | raises `OhlcvQuarantineError` | PASS — OhlcvQuarantineError raised: run_candidate_backtest received a panel without `valid_ohlcv_mask`; load via src.data.equity_panel.load_equity_panel which annotates it | PASS |
| B | panel with `valid_ohlcv_mask` | gate cleared (no quarantine error) | PASS — engine accepted annotated panel (gate cleared) | PASS |

## Interpretation

- Case A demonstrates the patch-phase fail-closed gate at `run_candidate_backtest`
  function entry is **active at runtime**.
- Case B demonstrates the gate clears when the loader-emitted annotation is
  present.
- This is a **gate-only test**. It does NOT execute a backtest.
  Any downstream exception is irrelevant to the gate verdict, as long as it
  is NOT an `OhlcvQuarantineError`.

## Hard locks (preserved)

- No return / NAV / Sharpe / alpha / strategy metric was generated.
- No performance diagnostic.
