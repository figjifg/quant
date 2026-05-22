# O004 drift / risk alert

## Purpose

Monitor P08_IEF30 drift and risk conditions.

## Outputs

Write outputs under `paper_trading/operations/drift_alerts/`:

- SPY / QQQ / H001 / IEF drift versus target in percentage points
- portfolio current rolling MDD
- 2022-like rate shock proxy from real-yield changes
- US equity drawdown versus 52-week high
- H001 regime ON/OFF status placeholder from the D013 macro gate
- alert thresholds, for example drift > 10pp or MDD < -15%

## Refresh cadence

Daily or weekly.

## Implementation

Primary function: `src.ops.drift_alert.compute_drift_alerts(as_of_date)`.

Use only local data. D013 and H001 strategy code must remain untouched.

## Tax note

Alerts do not authorize live trades. Tax-professional confirmation is required before live implementation.
