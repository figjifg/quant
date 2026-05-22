# T-family complete to O-family handoff

Status: T-family complete as research. O-family operations tooling starts.

## Mission

Build a tax-aware global allocation quant system using the validated Korean macro sleeve plus global ETF exposures.

## Research Decision

New alpha family X. O-family is operations tooling, not a new alpha search.

## Default Portfolio

P08_IEF30:

- SPY 29%
- QQQ 21%
- H001 20%
- IEF 30%

## T-family Defaults

- HIFO plus KRW 2.5M annual exemption is the default taxable-lot assumption.
- Quarterly rebalance remains the operational default.
- No-trade band is X for default operations.
- TLH is a low-priority diagnostic in the current trending bull sample.
- Account/vehicle selection is the main implementation lever.

## Paper Tracking Versions

- Gross P08_IEF30
- V1 taxable P08_IEF30
- MIX1 practical shadow
- V4 pension-only shadow

## O-family Tickets

| ticket | purpose | implementation |
| --- | --- | --- |
| O000 | 9-portfolio NAV auto update | `src.ops.nav_update` |
| O001 | 4-version gross/tax NAV tracking | `src.ops.gross_tax_nav` |
| O002 | tax-utilization ledger | `src.ops.tax_ledger` |
| O003 | quarterly rebalance report | `src.ops.rebalance_report` |
| O004 | drift/risk alerts | `src.ops.drift_alert` |
| O005 | quarterly evaluation template | `src.ops.quarterly_evaluation` |

## Live Constraint

All O-family outputs are paper operations artifacts. Tax-professional confirmation is mandatory before live implementation.
