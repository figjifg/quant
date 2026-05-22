# O003 rebalance report design

Status: design plus local sample runner.

## Scope

`src.ops.rebalance_report.generate_rebalance_report(quarter)` creates a quarterly paper rebalance report for P08_IEF30.

## Target Weights

- SPY 29%
- QQQ 21%
- H001 20%
- IEF 30%

## Output

Markdown under `paper_trading/operations/rebalance_reports/` with current weights, target weights, drift, BUY/SELL notional estimates, HIFO lot-selection notes, expected tax placeholders, and FX conversion notes.

The report is not an order ticket. Tax-professional confirmation is required before any live use.
