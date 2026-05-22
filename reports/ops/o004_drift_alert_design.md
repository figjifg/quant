# O004 drift / risk alert design

Status: design plus local sample runner.

## Scope

`src.ops.drift_alert.compute_drift_alerts(as_of_date)` creates a JSON alert record for P08_IEF30.

## Checks

- component drift versus target in percentage points
- portfolio rolling MDD
- US real-yield change as a 2022-like rate-shock proxy
- SPY drawdown versus 52-week high
- H001 regime status placeholder from D013 macro gate

## Output

JSON under `paper_trading/operations/drift_alerts/`.

D013 and H001 strategy code remain untouched. Tax-professional confirmation is required before any live use.
