# E003 — Market-flow gate on top of E002 cap_only exit

## Status
planned

## Purpose (alpha-level)
E002 showed that the dynamic-exit concept works, but specifically the
20-day cap (alone, no stop) is the carrier of the improvement
(cap_only OOS net +0.688 vs headline cap+stop +0.581 vs E001 +0.165).
The signal itself, however, is still essentially coin-flip per trade
(cap_only OOS hit_rate 0.493). E003 is the first **Layer 4** test —
a market-level gate that conditions whether E001's per-stock signal
is allowed to fire on a given day.

This is **alpha-level**, not infra. The infra is reused unchanged.

## Hypothesis

On days when the KOSPI-wide foreign + institutional cumulative
net-buy (5 KRX trading days) is positive, the E001 per-stock signal
produces higher OOS cost-net return AND higher OOS hit_rate than
days when the gate is off, **and** that improvement is not a
re-statement of a simple KOSPI price-momentum effect.

## Failure modes being tested

- **Regime dependence of the per-stock signal** — E001's hit-rate
  ≈ 47% may average across a "signal works" regime and a "signal
  noise" regime. The gate tries to isolate the first regime.
- **Hidden price-momentum confounding** — the gate's predictive
  power, if any, could be entirely explained by KOSPI price trend.
  We must rule this out.
- **Self-referential gate** — universe stocks contribute their own
  flows to the KOSPI aggregate; the gate is partially endogenous to
  the candidates it gates. Magnitude check needed but not
  necessarily a kill criterion.

## Strategy type
Layer 4 시장 게이트. 종목 진입 신호는 E001 그대로, 청산은 E002 cap_only
그대로. 변경은 **시장 단위 사전 조건** 한 가지.

## Signal definition (unchanged from E001)

For each ticker on KRX trading day T:

```
fnv_5 = rolling_sum(외국인순매수금액추정, 5, ending at T)
      / rolling_sum(거래대금추정, 5, ending at T)
inv_5 = rolling_sum(기관순매수금액추정,   5, ending at T)
      / rolling_sum(거래대금추정, 5, ending at T)
stock_signal_T = 1 if (fnv_5 > 0) AND (inv_5 > 0) else 0
```

Tie-break for max-positions cap: `combined_flow_5 = (foreign_net_5
+ institution_net_5) / traded_value_5` descending. Same as E001.

## Market gate definition (NEW for E003)

For each KRX trading day T using **only** rows of the market-flow
panel with `date ≤ T`:

```
kospi_combined_net_5 = rolling_sum(kospi_foreign_net + kospi_institution_net,
                                   5 KRX trading days, ending at T)
market_gate_on(T)    = kospi_combined_net_5 > 0
```

The gate is observed at the close of T (after-market data) and
controls whether entries are allowed at T+1 open. Window length is
5 KRX trading days — **deliberately identical** to the per-stock
signal window so the two operate on the same time scale.

## Entry rule

- `signal_date = T`
- `execution_date = T+1`
- `entry_price = T+1 KRX 09:00 시가`
- 시가 missing or ≤ 0 → skip
- Entry condition: `(fnv_5 > 0) AND (inv_5 > 0) AND market_gate_on(T)`
- Sizing, slot mechanics, tie-break — all unchanged from E002

## Exit rule (cap_only — E002 finding)

- `holding_cap = 20 KRX trading days` (fixed)
- No volatility stop (`vol_stop_k = None`)
- Exit at `KRX종가` of `add_trading_days(execution_date, 20)`
- `missing_price_fallback`, `period_end` fallbacks unchanged from E001

## Universe (unchanged from E001 headline)

- `동적유니버스포함 == True` on most recent `날짜 ≤ T-1`
- 20-row mean `거래대금추정` ≥ 5_000_000_000 ending at `T-1`
- `거래대금추정여부 == False` on each of the 5 signal-window rows
  (Rule 3 per E001 amended policy)

## Data assumptions

**Locked data set** (no additions without a new ticket):

- IS source: `inputs/equity_panels/dynamic_top100_2018_2024_panel.csv`
- OOS source: `inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv`
- Market flow source: `inputs/market_flow/kiwoom_market_flow_2018_2026_integrated.csv`
  - Columns consumed: `date`, `kospi_foreign_net`, `kospi_institution_net`
  - **NOT consumed**: program trade columns, individual net, large
    investor columns, basis. Those are out of scope for E003 even
    though they are in the same file.
- IS period: 2018-01-02 ~ 2022-12-30
- OOS period: 2023-01-02 ~ 2026-05-04

Timing convention: market_flow CSV is per DATA_CATALOG "KRX 장마감
후" — same convention as the equity panel investor-flow rows.
Therefore `kospi_combined_net_5` observed at end of T is available
for T+1 open execution; no look-ahead.

Cross-check at load time: `market_flow.date.unique()` must be a
**subset of** the calendar derived from the equity panel. Any
market-flow date not in the calendar is unusable and dropped; any
calendar date with no market-flow row produces a NaN gate, which is
treated as "gate off" (conservative).

## Cost assumptions (unchanged from E001/E002)

- `commission_bps = 1.5`
- `tax_bps_sell   = 20.0`
- `slippage_bps   = 5.0`
- `cost_sensitivity_multipliers = [0.0, 1.0, 2.0, 3.0]`

## Baseline comparison

Two layers.

**Layer 1 — direct head-to-head (same signal, same universe, same cap_only exit)**
- `B_cap_only` — E002 cap_only rerun on the same period. The number to beat.
- `B_inverted_gate` — entries allowed only when `market_gate_on(T) == False` (역가설). Tests the gate's sign.
- `B_price_gate` — gate = `KOSPI 종가 5일 수익률 > 0` instead of flow-based. Tests for price-momentum confounding.
- `B_double_gate` — gate = `market_gate_on AND price_gate_on`. Tests whether flow gate adds info over a price-momentum gate.

**Layer 2 — context (E001/E002 baselines)**
- `B0_cash`, `B1_buy_and_hold`, `B2_universe_5d_rebalance`, `B3_price_momentum` — unchanged

## Parameters to test

**None. Single point.**

| Parameter | Value | Rationale |
|---|---:|---|
| Gate window | 5 KRX trading days | Identical to the per-stock signal window |
| Gate threshold | 0 (sign) | Simplest binary; no threshold tuning |
| Gate definition | `(foreign + institution) > 0` | Single aggregate; no per-investor decomposition this ticket |
| `holding_cap` | 20 KRX trading days | Carried from E002 cap_only |
| `vol_stop_k` | None | Carried from E002 cap_only |

## Parameters that must NOT be optimized

- Gate window (5 td)
- Gate threshold (> 0 strictly; no `> 0.01`-style margin)
- Gate aggregate definition (foreign + institution combined)
- Holding cap (20 td)
- vol_stop_k (None)
- IS/OOS boundary
- Signal definition
- Universe rules
- Cost defaults
- Execution prices (시가 entry, KRX종가 cap exit)

If a future ticket sweeps any of these, that is a **new experiment**,
not an E003 extension.

## Diagnostic split (within this ticket)

All on the same E001 signal + universe + cap_only exit, varying only
the gate:

- **(A) E003 headline** — `market_gate_on` AND
- **(B) cap_only baseline** — no gate (B_cap_only above)
- **(C) Inverted gate** — entries when `market_gate_on == False`
- **(D) Price gate** — entries when KOSPI 종가 5td return > 0
- **(E) Double gate** — `market_gate_on AND price_gate_on`

Plus the standard E001/E002 baselines (B0~B3) for outside context.

## Success criteria (alpha-level)

All five must hold for `promote`:

1. **Return**: OOS net total_return (A) > cap_only OOS (+0.688).
2. **Trade count**: OOS trade_count (A) ≥ 103 (≥ 50% of cap_only OOS 205).
3. **Gate sign**: OOS hit_rate (A) > OOS hit_rate (C) inverted gate.
   Both A and C must have trade_count ≥ 50 for the comparison to be
   meaningful; if C has < 50 trades, this criterion is auto-pass
   because the inverted gate effectively kills entries (still
   consistent with the gate being directionally correct).
4. **Not a price-momentum proxy**: OOS net total_return (A) ≥
   OOS net total_return (D) price gate + 0.03.
5. **Information value, not just cost saving**: cost-0 diagnostic
   OOS net return (A) > cost-0 OOS net return (B) cap_only.

If 1–4 hold but 5 fails → `revise` (gate works on cost-net basis
but the signal info contribution is unclear).

Decomposition (informational):
- (E) double_gate OOS net should help interpret whether the flow
  gate adds **on top of** a price-momentum gate.

## Kill criteria

Any one → `kill`:

- OOS net total_return (A) ≤ cap_only OOS.
- OOS trade_count (A) < 50 (gate too narrow to learn from).
- (A) − (D) OOS net difference < 0.01 (gate is a price-momentum
  rename).
- pytest regression on existing E001/E002 suite.

## Expected weaknesses

- **Self-referential gate**: ~833 unique tickers in our universe,
  some of which (large caps) materially contribute to the KOSPI
  aggregate flow. The gate is not strictly independent of the
  candidates. Magnitude TBD; flag for review even if criteria pass.
- **Lagged regime detection**: gate uses 5-day rolling, so a regime
  flip is captured with 1–5 day delay. Quick regime reversals may
  see entries during the lag.
- **Price-flow correlation**: KOSPI cumulative net buy and KOSPI
  price changes are positively correlated; the (A)-vs-(D)
  comparison is the safeguard but not the elimination.
- **NaN gate days at start of period**: first 4 trading days of
  panel have insufficient prior rows for 5-day rolling. Those days
  are gate-off (conservative).
- **Single binary gate**: no graduated information from gate
  strength. A future experiment could test quantile-based gate.

## Codex implementation task

Read this ticket end-to-end before writing code. Read `CLAUDE.md`,
`AGENTS.md`, and the E002 ticket and review for cap_only context.
Base commit = latest `main` (840aff6 at write time).

### Scope discipline (additive only)

Most modules unchanged. Touch:
- `src/data/market_flow.py` (NEW) — loader for the market_flow CSV.
- `src/features/market_gate.py` (NEW) — `build_market_gate_features(market_flow_df, calendar, equity_panel) -> DataFrame` with columns `signal_date`, `execution_date`, `kospi_combined_net_5`, `market_gate_on`, `kospi_5d_return`, `price_gate_on`.
- `src/strategies/e003_market_gate.py` (NEW) — `build_e003_market_gated_candidates(flow_features, universe, market_gate_features, gate_column) -> DataFrame`. `gate_column` selects which column to gate on (`market_gate_on`, `price_gate_on`, etc.) — keeping it parameterized lets the same function build B_inverted_gate, B_price_gate, B_double_gate without duplication.
- `src/run_experiment.py` — add `experiment_id == "E003"` dispatch and `run_e003_experiment(config, config_path)` that wires all five variants (A, B, C, D, E) + B0~B3 + cost sensitivity + cost-0 diagnostic for (A) and (B).
- `configs/backtests/e003.yaml` (NEW).
- `tests/test_market_flow_loader.py` (NEW) — schema validation, BOM/encoding, timestamp parsing.
- `tests/test_market_gate_features.py` (NEW) — 5-day rolling, sign correctness, NaN/insufficient-window behavior, calendar alignment, and forward-leakage regression on a synthetic market_flow.
- `tests/test_e003_strategy.py` (NEW) — gate filtering correctness on a synthetic combined fixture (per-stock signals + market gate). Confirm that gate-off days have zero candidates and gate-on days are unaffected.

**Do NOT touch**:
- `src/backtest/engine.py` (no engine change needed — gate is enforced via candidate filtering)
- `src/data/equity_panel.py`, `src/data/universe.py`, `src/backtest/calendar.py`, `src/backtest/costs.py`, `src/features/flow_ratios.py`, `src/strategies/e001_flow_filter.py`, `src/strategies/baselines.py`, `src/reporting/*`, E001 / E002 tests, E001 / E002 configs

### Market-flow loader spec

```python
def load_market_flow(path: Path | str, calendar: KRXTradingCalendar) -> pd.DataFrame:
    """Returns DataFrame indexed by date (sorted ascending) with
    columns: kospi_foreign_net, kospi_institution_net.
    Drops rows where date is not in `calendar.dates`.
    Raises if either column has NaN values inside the calendar range."""
```

Strict on missing fields. The market_flow file already has the columns
we need; other columns in the file are ignored.

### Market-gate feature builder spec

```python
def build_market_gate_features(
    market_flow_df: pd.DataFrame,
    calendar: KRXTradingCalendar,
    kospi_close_series: pd.Series | None = None,
) -> pd.DataFrame:
    """Returns one row per calendar trading day with:
        - signal_date (date the gate is observed)
        - execution_date (signal_date + 1 trading day, NaT on last day)
        - kospi_combined_net_5: 5-day rolling sum of (foreign + institution) ending at signal_date
        - market_gate_on: kospi_combined_net_5 > 0
        - kospi_5d_return: KOSPI close on signal_date / KOSPI close on signal_date - 5td - 1
        - price_gate_on: kospi_5d_return > 0
    If fewer than 5 prior values exist (start of panel), the
    rolling value is NaN and gate_on is False (conservative)."""
```

KOSPI close series for `price_gate_on` is **not** in the market_flow
file. Options:
- (preferred) derive from the equity panel by computing the
  value-weighted average daily return of dynamic Top100 — this
  approximates KOSPI but is internal to our locked data set
- alternative: read it from `inputs/macro_features/krx_market_breadth_kospi_2010_2026.csv`
  if a KOSPI close column is present there
- whichever you choose, document in the function docstring and add a
  test that asserts the price_gate_on column is well-defined for all
  trading days

If you choose the value-weighted-Top100 approximation, name the
column explicitly `kospi_proxy_5d_return` in `report.md` metadata so
nobody mistakes it for the official KOSPI index.

### Strategy filter spec

```python
def build_e003_market_gated_candidates(
    flow_features: pd.DataFrame,
    universe: pd.DataFrame,
    market_gate_features: pd.DataFrame,
    gate_column: str,
) -> pd.DataFrame:
    """Build E001 headline candidates, then drop any row whose
    execution_date corresponds to gate_column == False (or NaN).
    Preserves all candidate columns. Validates that gate_column
    exists in market_gate_features."""
```

The function is parameterized by `gate_column` so the four gate
variants (A, C inverted, D price, E double) use the same code path
with different gate columns.

For (E) double gate, add a derived column `double_gate_on =
market_gate_on AND price_gate_on` in the gate features frame.

For (C) inverted, add `market_gate_off = ~market_gate_on & gate_features_well_defined`
— note the well-defined guard so the inverted gate doesn't treat
NaN as "off" (it would otherwise sweep in early-period rows where
the gate is undefined).

### Configuration file

`configs/backtests/e003.yaml`:

```yaml
experiment_id: E003
panels:
  - research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv
  - research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv
market_flow:
  path: research_input_data/inputs/market_flow/kiwoom_market_flow_2018_2026_integrated.csv
periods:
  is:
    start: 2018-01-02
    end:   2022-12-30
  oos:
    start: 2023-01-02
    end:   2026-05-04
universe:
  require_dynamic_top100: true
  min_avg_traded_value_20d: 5_000_000_000
  exclude_estimated_flag_rows: true
strategy:
  lookback: 5
  holding: 20
  max_positions: 5
exit:
  vol_stop_k: null    # cap_only — no vol stop
  vol_stop_atr_window: 20
gate:
  window: 5
  threshold: 0
costs:
  commission_bps: 1.5
  tax_bps_sell:   20.0
  slippage_bps:   5.0
cost_sensitivity_multipliers: [0.0, 1.0, 2.0, 3.0]
output_dir: reports/experiments/E003_market_flow_gate
```

Strict validation (no unknown keys). The `gate.window` and
`gate.threshold` are surface-of-record; do not actually sweep them.

### Runs to produce

On the full `[is.start, oos.end]` period:

1. **headline** (A) — E001 signal × universe × `market_gate_on` × cap_only
2. **cap_only** (B) — E002 cap_only rerun for direct comparison
3. **inverted_gate** (C) — same as (A) with `market_gate_off`
4. **price_gate** (D) — same as (A) with `price_gate_on`
5. **double_gate** (E) — same as (A) with `double_gate_on`
6. **B0_cash, B1, B2, B3** — preserved as in E001/E002
7. **diagnostic_estimate_included** — E001 signal × diagnostic universe (no estimate-row filter) × `market_gate_on` × cap_only
8. **cost_sensitivity** — (A) headline at multipliers `[0, 1, 2, 3]`
9. **cost_0_headline**, **cost_0_cap_only** — for criterion 5

### Output files (under `reports/experiments/E003_market_flow_gate/`)

- `config.yaml`, `metrics.json`, `trades.csv` (headline (A)),
  `signals.csv` (headline candidates after gate),
  `equity_curve.csv` (headline), `cost_sensitivity.csv`, `report.md`
- Additionally: `market_gate_timeseries.csv` with columns
  `signal_date, execution_date, kospi_combined_net_5,
  market_gate_on, kospi_5d_return, price_gate_on, double_gate_on`
  so the reviewer can inspect when the gate fired.

Fix the known `종목코드` leading-zero loss this iteration: write
`종목코드` to `trades.csv` and `signals.csv` with explicit string
dtype that preserves the 6-character form. Add a regression test
that round-trips a synthetic ticker (`'000020'`) through the
CSV writer and asserts it stays as `'000020'`, not `20`.

### Order of work

Commit (Claude commits) after each green-test boundary.

1. `src/data/market_flow.py` + `tests/test_market_flow_loader.py`.
2. `src/features/market_gate.py` + `tests/test_market_gate_features.py`.
3. `src/strategies/e003_market_gate.py` + `tests/test_e003_strategy.py`.
4. CSV writer fix + regression test for the 종목코드 zero-padding bug.
5. CLI extension for E003.
6. Run E003 backtest end-to-end on the real panels.

### Completion criteria

- `pytest` fully green.
- `python -m src.run_experiment --config configs/backtests/e003.yaml`
  produces every required output file.
- All 5 success criteria computable from `metrics.json` alone.
- Final message lists any spot the implementation chose one reading
  of an under-specified spec.

### Out of scope for E003

- Gate parameter sweep (window, threshold, definition variants)
- Per-investor decomposition (foreign-only or institution-only gates)
- Quantile-based gate (only binary in this ticket)
- New data sources
- Modifying signal, universe, or exit

## Result summary
DO NOT FILL until backtest is complete.

## Claude review
DO NOT FILL until result files are read.
