# J000 EM Equity Baseline Diagnostic

Status: READY

## Purpose

Build the J-family baseline library for EM and EM-adjacent equity ETFs before
testing portfolio sleeves.

J-family is not expected to raise returns. The diagnostic question is whether
small EM equity exposure can reduce US concentration while preserving Sharpe
and drawdown behavior.

## Universe

| Ticker | Role |
|---|---|
| VWO | Broad EM |
| EWY | Korea ADR |
| EWJ | Japan, developed-market reference |
| EWZ | Brazil |
| MCHI | China |

## Required Diagnostics

- KRW buy-and-hold NAV using local USDKRW interpolation.
- CAGR, Sharpe, max drawdown, and SPY daily-return correlation.
- Correlation matrix across the five ETFs.
- Stress windows:
  - dot-com 2000-2002, with availability noted by ETF.
  - GFC 2008-2009.
  - COVID 2020-02 through 2020-03.
  - 2022 rate shock.

## Guardrails

- Local data only; no external network.
- No ranking, timing, or parameter grid.
- Diagnostic only. J-family results enter the backlog candidate library and do
  not directly promote `P08_IEF30`.
