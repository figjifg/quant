# Q000 — US Fundamental Data Audit

Status: READY (user host work required; SEC EDGAR API network access)

## Decision

Q-family is a US individual-stock fundamental sleeve. It is completely
separate from `P08_IEF30`.

Q000 is the gate ticket. If point-in-time data, filing-date alignment, or
survivorship-free universe construction is not feasible, the Q-family stops.

## Hypothesis

SEC EDGAR `companyfacts`, 10-K, and 10-Q data may be sufficient to build
point-in-time US individual-stock fundamental factors with filing-date
availability and a survivorship-free universe.

## Audit Scope

Pre-register the following checks before any backtest:

1. SEC filing-date based financial data can be used only after 10-K / 10-Q
   availability.
2. XBRL tag mapping is stable enough across years and companies in the
   `companyfacts` API.
3. Delisted companies and historical universe membership can be represented.
4. Current S&P 500 constituents are not used as a historical universe.
5. Dividend, buyback, and shares outstanding timestamps are accurate enough
   for shareholder-yield calculation.
6. Split, merger, and ticker-change handling is feasible and documented.

## Required Factor Feasibility Checks

- Quality: ROIC, FCF margin, leverage.
- Value: FCF yield, earnings yield.
- Shareholder Yield: buyback yield, dividend yield, dilution.

## Pass Criteria

- At least five years, for example 2019-2024, of survivorship-free universe
  construction is feasible.
- Filing-date based PIT data is feasible.
- Core factors are calculable: ROIC, FCF yield, dividend, and buyback.

## Fail Alternative

If Q000 fails, do not continue individual-stock Q-family research. Use ETF
proxy diagnostics only:

- `QUAL`
- `VLUE`
- `MTUM`
- `USMV`
- `SCHD`
- `COWZ`

## Explicit Failure Modes To Avoid

- Current S&P 500 constituents must not be used for historical backtests.
  That is survivorship bias.
- Financial statement values must not be used before their SEC filing date.
  That is look-ahead bias.
- Many factor combinations must not be searched for the best Sharpe. That is
  overfitting.

## Implementation Notes

- Use `scripts/q000_sec_edgar_audit.py` on the user host only.
- Codex sandbox must not call external network endpoints.
- Sample output target:
  `research_input_data/inputs/us_fundamentals/sec_edgar_sample.json`.
- If a data file is produced, update `research_input_data/docs/DATA_CATALOG.md`
  before using it downstream.

