# O001 gross / tax NAV tracking design

Status: design plus local sample runner.

## Scope

`src.ops.gross_tax_nav.compute_gross_tax_nav(p08_ief30, as_of_date)` writes the 4 paper tracking versions:

- Gross P08_IEF30
- V1 taxable P08_IEF30
- MIX1 practical shadow
- V4 pension-only shadow

## Data Source

Gross is computed from local component NAV paths. V1, MIX1, and V4 are read from `reports/experiments/T004_account_vehicle_study/daily_nav_by_vehicle.csv`.

## Output

CSV under `paper_trading/operations/nav_history/`, including daily NAV, period returns, MDD, rolling volatility, and rolling Sharpe.

Tax-professional confirmation is required before any live use.
