# L000 — KOSDAQ Universe Expansion

Status: BACKLOG

## Context

T-family and O-family are complete. New alpha-family analysis is deferred until
paper tracking is stable. This ticket only preregisters a future universe and
validation frame.

Data collection is allowed through `scripts/host_data_collection.py` after host
network access is available.

## Purpose

Evaluate whether the H001 Korean sleeve has incremental value when expanded
from KOSPI top 100 style coverage into a KOSDAQ150 universe.

## Candidate Universe

- KOSDAQ150 constituents from quarterly pykrx snapshots.
- Daily KOSDAQ price and volume from pykrx for 2010-2026.

## Validation Frame

- Test whether D013-style macro gates behave similarly on KOSDAQ exposure.
- Compare KOSPI-only H001 style results against KOSPI plus KOSDAQ variants.
- Metrics: Sharpe, CAGR, MDD, turnover, liquidity exposure, and stress behavior.

Exact signal definitions, universe membership timing, liquidity filters, and
IS/OOS split must be fixed in a future execution ticket before any backtest.

## Data

Expected file after host collection:

- `research_input_data/inputs/equity_panels/pykrx_kosdaq150_panel.csv`

## Timing Notes

- KOSDAQ150 snapshot membership must be treated as available only after the
  relevant snapshot date.
- Any future strategy must write separate `signal_date` and `execution_date`.
- Same-day use of close-derived KOSDAQ data is forbidden.

## Strict Constraints

- Status remains BACKLOG until data collection and paper tracking stabilize.
- No alpha claim, strategy promotion, or parameter selection in this ticket.
- Do not modify D013, H001, or `src/backtest/engine.py`.
