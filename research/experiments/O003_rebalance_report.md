# O003 rebalance report

## Purpose

Generate an automatic quarterly rebalance report for P08_IEF30.

## Target

P08_IEF30 target weights:

- SPY 29%
- QQQ 21%
- H001 20%
- IEF 30%

## Outputs

Write outputs under `paper_trading/operations/rebalance_reports/`:

- current weights after quarter drift
- target weights
- trade list with BUY / SELL, trade amount, and quantity placeholder
- expected realized gains using HIFO lot-selection recommendation
- expected tax with capital gains tax and remaining KRW 2.5M exemption
- expected FX conversion from KRW to USD
- HIFO lot selection suggestion by component

## Refresh cadence

Generate every quarter-end.

## Implementation

Primary function: `src.ops.rebalance_report.generate_rebalance_report(quarter)`.

The report is paper only and must not be treated as an order ticket.

## Tax note

HIFO, FX tax basis, broker reporting, ISA/pension treatment, and exemption usage require tax-professional confirmation before live implementation.
