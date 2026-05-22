# O001 gross / tax NAV tracking

## Purpose

Track P08_IEF30 pre-tax and after-tax NAV versions side by side.

## Versions

| version | definition |
| --- | --- |
| Gross P08_IEF30 | research reference |
| V1 taxable P08_IEF30 | overseas ETF direct, HIFO + KRW 2.5M exemption + 22% capital gains tax |
| MIX1 practical shadow | V1 50% + ISA 30% + pension 20%, simplicity first |
| V4 pension-only shadow | pension savings 100%, withdrawal tax reflected, lock-up assumed |

## Outputs

Write outputs under `paper_trading/operations/nav_history/`:

- 4 NAV versions tracked daily
- monthly, quarterly, YTD return
- MDD, rolling volatility, rolling Sharpe
- quarterly comparison table

## Implementation

Primary function: `src.ops.gross_tax_nav.compute_gross_tax_nav(p08_ief30, as_of_date)`.

Use existing T004 outputs for tax-shadow paths and local component marks for Gross.

## Tax note

All tax treatment is paper/diagnostic. Tax-professional confirmation is required before live implementation.
