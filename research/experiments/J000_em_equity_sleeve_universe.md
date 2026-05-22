# J000 — EM Equity Sleeve Universe

Status: BACKLOG

## Context

T-family and O-family are complete. New alpha-family analysis is deferred until
paper tracking is stable. This ticket only preregisters a future universe and
validation frame.

Data collection is allowed through `scripts/host_data_collection.py` after host
network access is available.

## Purpose

Evaluate whether a small EM equity sleeve has diversification value for
`P08_IEF30` without becoming a new primary alpha family.

## Candidate Universe

- `VWO`: broad emerging markets.
- `EWY`: Korea ADR sleeve.
- `EWJ`: Japan comparator.
- `EWZ`: Brazil.
- `MCHI`: China.

Initial sleeve candidates are 5% additions or substitutions around the
`P08_IEF30` anchor. Exact weights must be fixed in a future execution ticket
before any backtest.

## Validation Frame

- Compare `P08_IEF30` versus `P08_IEF30 + EM sleeve`.
- Metrics: Sharpe, CAGR, MDD, realized volatility.
- Stress focus: 2022 rate shock and EM-specific drawdowns.
- Baselines: cash, `P08_IEF30`, and SPY/QQQ/IEF static proxies.

## Data

Expected files after host collection:

- `research_input_data/inputs/global_etf/yf_em_VWO.csv`
- `research_input_data/inputs/global_etf/yf_em_EWY.csv`
- `research_input_data/inputs/global_etf/yf_em_EWJ.csv`
- `research_input_data/inputs/global_etf/yf_em_EWZ.csv`
- `research_input_data/inputs/global_etf/yf_em_MCHI.csv`

## Strict Constraints

- Status remains BACKLOG until data collection and paper tracking stabilize.
- No alpha claim, strategy promotion, or parameter selection in this ticket.
- Do not modify D013, H001, or `src/backtest/engine.py`.
