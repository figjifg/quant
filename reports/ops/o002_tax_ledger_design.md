# O002 tax ledger design

Status: design plus local sample runner.

## Scope

`src.ops.tax_ledger.compute_tax_ledger(as_of_date)` summarizes:

- realized gain/loss by year
- current unrealized gain/loss
- used and remaining KRW 2.5M annual exemption
- estimated capital gains tax
- dividend withholding
- vehicle-specific tax for V1 / V2 / ISA / pension / IRP

## Data Source

The ledger is derived from existing T000 and T004 local outputs. It is not a broker tax statement and does not fetch broker data.

## Output

CSV under `paper_trading/operations/tax_ledger/`.

Tax-professional confirmation is required before any live use.
