# O002 tax ledger

## Purpose

Track tax-utilization status for the global allocation paper portfolio.

## Outputs

Write outputs under `paper_trading/operations/tax_ledger/`:

- realized gain/loss by year, separated by sleeve where available
- unrealized gain/loss at the current as-of date
- used KRW 2.5M annual exemption for the current year
- remaining KRW 2.5M annual exemption
- estimated capital gains tax for the current year
- cumulative dividend withholding
- vehicle-specific tax split for V1 / V2 / ISA / pension / IRP

## Refresh cadence

Update every quarter.

## Implementation

Primary function: `src.ops.tax_ledger.compute_tax_ledger(as_of_date)`.

Use existing T-family local outputs. No external data or broker API is allowed without a separate user-approved ticket.

## Tax note

This is not a tax filing ledger. Tax-professional confirmation is required before live implementation.
