# AGENTS.md — Quant Flow Lab Engineering Rules

This file is the engineering rulebook for **Codex** working in this repo.
For research direction, hypothesis framing, and result interpretation, see
`CLAUDE.md`. If the two files disagree on engineering specifics, this file
wins for engineering; `CLAUDE.md` wins for research framing.

## Project goal

Build a reproducible backtesting and research system for short-term Korean
equity strategies based on **foreign and institutional buying flows**.
Holding horizons are typically 1–20 KRX trading days, with initial focus on
3–10 days.

This is **not** a long-term value-investing project. Valuation and
fundamentals may be used only as secondary filters, never as the main alpha
signal.

## Absolute rules

Data integrity
- Never modify files under `research_input_data/inputs/` or `data/raw/`.
  Treat them as read-only inputs. Preprocessed artifacts go under
  `data/processed/`.
- Never download external data, hit a network endpoint, or use API
  credentials without explicit user approval in the task ticket.
- Never add a new data file without recording it in
  `research_input_data/docs/DATA_CATALOG.md` or equivalent.

Timing safety (look-ahead)
- KRX investor-flow data on day T becomes available **after KRX close on T**.
  Signal date T → execution date is **T+1 or later**, never T.
- For each feature, separate `signal_date` from `execution_date` in code and
  in `signals.csv` / `trades.csv`.
- Prefer the `KRX종가` column over `종가`. The `종가` column may carry
  NXT-integrated values whose finalization time is not the same as KRX
  close. Document any deviation in `report.md`.
- Rows with `수급금액추정여부 == True` or `거래대금추정여부 == True` carry
  estimated values that may be revised later. Default policy: **exclude
  these rows from the headline backtest** and run a diagnostic comparison
  side-by-side (estimate-included slice goes into `metrics.json` under a
  separate key, not into the headline).
- The `동적유니버스포함` flag is computed after KRX close on T. Use it to
  decide day T+1 trades, never day T trades.
- Global futures, FRED macro, OpenDART disclosures: timestamp the
  availability of each feature explicitly. When in doubt, shift forward by
  one KRX trading day. Intraday-arriving disclosures must not influence
  same-day signals.
- Add a `tests/test_no_lookahead.py` case for every new feature that could
  introduce timing leakage. A new feature without such a test does not
  pass review.

Cost accounting
- Every experiment runs with realistic transaction costs unless the ticket
  explicitly marks the run as diagnostic. Default cost model:
  - `commission_bps = 1.5` (per leg, on traded notional)
  - `tax_bps        = 20.0` (sell leg only, KRX 거래세 proxy)
  - `slippage_bps   = 5.0`  (per leg)
- Cost-free runs are stored only under `cost_sensitivity.csv` (or
  equivalent diagnostic file), never reported as the headline.

Splits and baselines
- Every experiment reports IS and OOS metrics in **separate blocks** in
  `metrics.json` and `report.md`. The IS/OOS boundary is fixed at ticket
  authoring time and never moved to flatter the result.
- Every experiment compares against the baselines named in its ticket
  (typically: cash, universe equal-weight, price momentum standalone).
  Missing a baseline is grounds for rejection.

Tests
- Run `pytest` after modifying the backtest engine, feature generation,
  strategy logic, or cost model. Do not claim a task complete with failing
  tests.
- Every new feature module needs a unit test covering: NaN handling,
  boundary windows, alignment to `signal_date`, and at least one
  look-ahead regression case.

Claims and reports
- Never claim a strategy works unless the metrics were read from generated
  report files in `reports/experiments/E###_*/`.
- Do not edit `report.md` to add interpretive claims — that is Claude's
  job. Codex writes only the metrics summary block.
- Numbers in `report.md` must match `metrics.json` byte-for-byte (no
  rounding inconsistencies).

## Engineering expectations

- Small, testable modules. Strategy logic must live separately from
  backtest execution. Feature generation must be timestamp-safe and pure
  (no global state).
- Configuration goes in `configs/`, not in code. Avoid hard-coded
  parameters in `src/`.
- Prefer explicit pandas operations over implicit ones. No silent
  forward-fill across regime breaks (e.g., no FFill across the KOSPI200
  night-futures availability gap, no FFill across delisting events).
- Do not add new third-party dependencies without:
  1. Listing them in `requirements.txt`.
  2. Explaining in the PR description why a stdlib / existing-dep
     alternative was insufficient.
- Do not introduce abstractions for future hypothetical experiments. Three
  similar lines are better than a premature abstraction. Strategy classes
  appear only when there are at least two concrete strategies to share an
  interface.
- Match Python style of `numpy`/`pandas` idioms already in the repo. If no
  precedent exists, prefer vectorized pandas over Python loops, and prefer
  `pd.DataFrame.assign` chains over in-place mutation.

## Repo layout (target — create as needed)

```
quant/
  CLAUDE.md
  AGENTS.md
  requirements.txt
  research_input_data/   (read-only inputs; do not modify)
  configs/
    data/                YAML for raw → processed pipelines
    strategies/          YAML for strategy parameters
    backtests/           YAML for backtest runs (universe, dates, costs)
  src/
    data/                loaders, schema validation
    features/            timestamp-safe feature builders
    indicators/          stateless transforms
    strategies/          signal → position logic
    backtest/            execution engine, cost model, calendar
    portfolio/           sizing, position bookkeeping
    reporting/           metrics, report.md generation
    utils/
  research/
    ideas/
    experiments/         E###_*.md experiment tickets (Claude authors)
    reviews/             E###_review.md (Claude authors)
  reports/
    experiments/E###_*/  config.yaml, metrics.json, trades.csv,
                         signals.csv, equity_curve.csv, report.md, ...
    dashboards/
  tests/
    test_data_schema.py
    test_feature_timing.py
    test_no_lookahead.py
    test_backtest_engine.py
  data/
    raw/                 (do not modify; mirror of research_input_data when
                          a local cache is needed)
    processed/           parquet/CSV outputs from configs/data pipelines
```

Build only the parts a ticket requires. Do not scaffold empty directories
for hypothetical future work.

## Data conventions

Source of truth: `research_input_data/docs/DATA_CATALOG.md`.

Currently usable equity panels for backtests:
- `inputs/equity_panels/dynamic_top100_2018_2024_panel.csv`
- `inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv`

Older panels (`2010_2016`, `2017_2024`) have schema differences and a
pre-NXT trading environment; do not mix them into a single backtest
without an explicit ticket instruction.

Calendar: derive the KRX trading-day calendar from the panel itself (the
set of distinct dates that appear with non-null `KRX종가`). Do not invent
a calendar or fetch one from an external source.

Universe membership: when the ticket says "use `동적유니버스포함`,"
restrict to rows where it is True **and** the membership was determined
using panel data up to and including T-1, not T.

## Required experiment outputs

For each experiment `E###`, write to `reports/experiments/E###_<slug>/`:

Required
- `config.yaml`        — full backtest configuration, byte-exact rerun
- `metrics.json`       — IS block + OOS block + diagnostic blocks
- `trades.csv`         — entry_date, exit_date, signal_date, entry_price,
                          exit_price, cost_paid, holding_days, exit_reason
- `signals.csv`        — date, ticker, signal_value, signal_date,
                          execution_date, included_in_trade
- `equity_curve.csv`   — date, gross_value, net_value (after cost),
                          cash, n_positions
- `report.md`          — metrics summary (IS/OOS), baseline table,
                          metadata (panels used, 추정 row policy,
                          통합 column policy, calendar source)

Conditional (only when the ticket asks for them)
- `parameter_sensitivity.csv`
- `cost_sensitivity.csv`
- `regime_breakdown.csv`

Never write an experiment output to a location outside its
`reports/experiments/E###_*/` directory.

## Definition of done

A task is done when **all** of these hold:
- The implementation matches the ticket spec; deviations are documented
  in the PR description, not silently in code.
- `pytest` passes; any skipped or xfail tests have a comment explaining
  why.
- The required experiment output files exist on disk at the expected paths
  and are reproducible from `config.yaml` alone.
- `report.md`'s metrics summary is generated from `metrics.json`, not
  hand-edited.
- The diff is reviewable: no unrelated reformatting, no dead code, no
  commented-out blocks.
- Timestamps in `signals.csv` and `trades.csv` pass
  `tests/test_no_lookahead.py`.

## What Codex must not decide alone

Codex implements; the following decisions belong to the experiment ticket
(authored by Claude / the user):
- Hypothesis text and strategy direction.
- Parameter values; what to sweep and what to freeze.
- IS/OOS split dates.
- Whether an experiment is killed, revised, or promoted.
- Whether a result is "good." Codex reports the numbers; interpretation
  happens in `research/reviews/`.

If a ticket is ambiguous on any of these, **stop and ask** rather than
guess. Adding parameters not listed in the ticket is a ticket violation.
