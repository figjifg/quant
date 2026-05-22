# K000 — US Sector Rotation Universe

Status: BACKLOG

## Context

T-family and O-family are complete. New alpha-family analysis is deferred until
paper tracking is stable. This ticket only preregisters a future universe and
simple validation frame.

Data collection is allowed through `scripts/host_data_collection.py` after host
network access is available.

## Purpose

Evaluate whether US sector ETF rotation is superior to a plain SPY sleeve after
costs, turnover, and stress behavior are accounted for.

## Candidate Universe

- `XLE`: Energy
- `XLF`: Financials
- `XLK`: Technology
- `XLV`: Health Care
- `XLI`: Industrials
- `XLY`: Consumer Discretionary
- `XLP`: Consumer Staples
- `XLU`: Utilities
- `XLB`: Materials
- `XLRE`: Real Estate
- `XLC`: Communication Services

## Validation Frame

Simple hypotheses only:

- Equal-weight sector basket versus SPY.
- Sector momentum rotation versus SPY.

Metrics: Sharpe, CAGR, MDD, turnover, and 2022 stress behavior. Exact lookback,
rebalance frequency, and cost assumptions must be fixed in a future execution
ticket before any backtest.

## Data

Expected files after host collection:

- `research_input_data/inputs/global_etf/yf_sector_XLE.csv`
- `research_input_data/inputs/global_etf/yf_sector_XLF.csv`
- `research_input_data/inputs/global_etf/yf_sector_XLK.csv`
- `research_input_data/inputs/global_etf/yf_sector_XLV.csv`
- `research_input_data/inputs/global_etf/yf_sector_XLI.csv`
- `research_input_data/inputs/global_etf/yf_sector_XLY.csv`
- `research_input_data/inputs/global_etf/yf_sector_XLP.csv`
- `research_input_data/inputs/global_etf/yf_sector_XLU.csv`
- `research_input_data/inputs/global_etf/yf_sector_XLB.csv`
- `research_input_data/inputs/global_etf/yf_sector_XLRE.csv`
- `research_input_data/inputs/global_etf/yf_sector_XLC.csv`

## Strict Constraints

- Status remains BACKLOG until data collection and paper tracking stabilize.
- No alpha claim, strategy promotion, or parameter selection in this ticket.
- Do not modify D013, H001, or `src/backtest/engine.py`.
