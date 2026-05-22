# O000 paper NAV auto update

## Purpose

Automate daily paper NAV updates for the 9 global allocation portfolios.

## Portfolios

- P08_IEF30
- P08
- P07
- P07_IEF30
- QQQ
- SPY
- QQQ/SPY 50/50
- H001
- IEF

## Outputs

Write outputs under `paper_trading/operations/nav_history/`:

- daily NAV
- monthly return
- quarterly return
- YTD return
- MDD
- rolling volatility
- rolling Sharpe

## Trigger

The user runs this after every quarter-end plus 1 trading day. Daily or weekly refresh is allowed for paper monitoring, but it is not a live trading instruction.

## Implementation

Primary function: `src.ops.nav_update.compute_daily_nav(portfolios, as_of_date)`.

Use only local files. No external network refresh is allowed.

## Tax note

This ticket does not validate taxes. Tax-professional confirmation is required before live implementation.
