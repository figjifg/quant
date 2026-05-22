# M000 — Crypto Sleeve Universe

Status: BACKLOG

## Context

T-family and O-family are complete. New alpha-family analysis is deferred until
paper tracking is stable. Crypto is the lowest-priority backlog family because
of extreme volatility, operational complexity, and regime instability.

Data collection is allowed through `scripts/host_data_collection.py` after host
network access is available.

## Purpose

Evaluate cautiously whether BTC or ETH has portfolio diversification value when
added as a small sleeve to `P08_IEF30`.

## Candidate Universe

- `BTC-USD`
- `ETH-USD`

Initial BTC sleeve candidates are 2-5% additions or substitutions around the
`P08_IEF30` anchor. Exact weights must be fixed in a future execution ticket
before any backtest.

## Validation Frame

- Compare `P08_IEF30` versus `P08_IEF30 + BTC sleeve`.
- Metrics: Sharpe, CAGR, MDD, realized volatility, drawdown duration, and
  worst calendar-year loss.
- Stress focus: crypto-specific crash windows and 2022 rate shock.

## Data

Expected files after host collection:

- `research_input_data/inputs/global_etf/yf_crypto_BTC-USD.csv`
- `research_input_data/inputs/global_etf/yf_crypto_ETH-USD.csv`

## Strict Constraints

- Status remains BACKLOG and lowest priority.
- No alpha claim, strategy promotion, or parameter selection in this ticket.
- Do not modify D013, H001, or `src/backtest/engine.py`.
