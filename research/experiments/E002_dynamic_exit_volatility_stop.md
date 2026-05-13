# E002 — Dynamic exit: volatility stop + 20-day cap on the E001 signal

## Status
planned

## Purpose (alpha-level, NOT infra)
E001 validated the pipeline. The headline strategy showed gross alpha
(IS +20.4%, OOS +63.4% before cost) destroyed by costs (IS -43.1%,
OOS +16.5% after default 33 bps round-trip drag) at turnover
~242× annualized in IS. The dominant problem is the cost-to-alpha
ratio caused by fixed 5-day holding regardless of the trade's actual
trajectory.

E002 tests whether replacing E001's fixed exit with a volatility-based
stop + 20-day time cap (same signal, same universe, same costs)
recovers cost-net OOS return AND lowers turnover.

This is an **alpha-level** experiment. Success/kill is about strategy
quality, not pipeline correctness. The pipeline is already validated.

## Hypothesis
Replacing E001's fixed `exit_date = entry_date + 5td` with
- a 2.0×ATR(20) loss stop **AND**
- a 20 KRX-trading-day maximum hold cap,

with every other rule held constant, produces OOS cost-net return
higher than E001 headline (+0.165) at lower turnover (< 113), with
hit_rate not worse than E001 OOS (0.467) and average holding period
strictly greater than 5 days (proving the dynamic path actually
engages).

## Failure mode being tested
- **Cost erosion from over-turnover** (E001's biggest problem)
- **Forced exit at arbitrary 5-day horizon** cutting good trades short
- **No loss control** — E001 max_consecutive_losses 13–14 trades
  suggests cluster losses with no cap on individual trade damage

## Strategy type
청산 룰 동적화. 진입 신호는 E001과 동일.

## Signal definition (unchanged from E001)

For each ticker on KRX trading day T, using only data available
strictly before T+1 open:

```
fnv_5 = rolling_sum(외국인순매수금액추정, 5, ending at T)
      / rolling_sum(거래대금추정, 5, ending at T)
inv_5 = rolling_sum(기관순매수금액추정,   5, ending at T)
      / rolling_sum(거래대금추정, 5, ending at T)
signal_T = 1 if (fnv_5 > 0) AND (inv_5 > 0) else 0
```

Tie-break for max-positions cap: `combined_flow_5` descending.

## Entry rule (unchanged from E001)

- `signal_date = T`
- `execution_date = T+1` (next KRX trading day)
- `entry_price = T+1 시가` (verified KRX 09:00 시가 — see AGENTS.md)
- `시가` missing or ≤ 0 → skip the entry, record nothing
- Sizing: `notional = NAV_at_open / max_positions` per new entry,
  `max_positions = 5`

## Exit rule (NEW for E002)

At entry time, compute and store on the slot:

```
atr_pct_at_entry = mean over t in {entry_date − 20td, …, entry_date − 1td} of
                   (High_t − Low_t) / KRX종가_t
stop_price       = entry_price * (1 − 2.0 * atr_pct_at_entry)
cap_exit_date    = add_trading_days(entry_date, 20)
```

(`atr_pct_at_entry` uses panel rows strictly **before** `entry_date`
to avoid look-ahead.)

For each subsequent KRX trading day `d` while the slot is held:

1. **Stop check first.** If `KRX종가(ticker, d) <= stop_price`,
   set `pending_exit = (next_trading_day_after(d), "vol_stop")`.
2. **Cap check next.** Else if `d == cap_exit_date`, exit immediately
   at `KRX종가(ticker, d)` with `exit_reason = "time_cap"`.
3. **Pending stop exit on the next day.** If a stop was scheduled on
   day `d − 1`, exit on day `d` at `시가(ticker, d)` with
   `exit_reason = "vol_stop"`. The `시가` must be > 0 and not NaN; if
   it is, defer to the next day with a valid 시가 and record
   `exit_reason = "vol_stop_fallback"`.

Edge cases:
- If `KRX종가(d)` is NaN, skip the stop check that day (don't extend
  cap). The position is still held; mark-to-market uses last-known
  close for that ticker.
- If cap-day `KRX종가` is NaN, defer to the next valid `KRX종가` with
  `exit_reason = "time_cap_fallback"`.
- If the slot reaches `period_end` while still held, force-exit at
  the last day's `KRX종가`, `exit_reason = "period_end"`.

Whichever of {vol_stop, time_cap, period_end} fires first wins.

## Holding period
**Variable** — 1 to 20 KRX trading days per trade in practice. The
mean is part of the success measurement (must be > 5 to prove dynamic
engagement).

## Universe (unchanged from E001)

- `동적유니버스포함 == True` on the most recent `날짜 ≤ T-1` row.
- Mean of `거래대금추정` over the last 20 panel rows ending at `T-1`
  is `≥ 5_000_000_000` KRW.
- Headline slice: `거래대금추정여부 == False` on each of the 5
  signal-window rows. `수급금액추정여부` is **not** used as a filter
  (E001 amended policy — universally True in this panel).

## Data assumptions

- **IS source**: `inputs/equity_panels/dynamic_top100_2018_2024_panel.csv`
- **OOS source**: `inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv`
- **IS period**: 2018-01-02 ~ 2022-12-30
- **OOS period**: 2023-01-02 ~ 2026-05-04
- `시가`, `고가`, `저가`, `KRX종가` (after loader normalization) are
  the columns the engine reads. NaN or ≤ 0 in any of these on the
  relevant date is treated as "not tradable / not measurable" per the
  edge-case rules above.
- 시가 == KRX 09:00 시가 (verified per AGENTS.md).
- No new external data; same panels as E001. **No additional data
  source is permitted for this ticket** per the experiment-discipline
  rule.

## Cost assumptions (unchanged from E001)

Per leg, per name, on traded notional:
- `commission_bps     = 1.5`
- `tax_bps_sell       = 20.0` (sell leg only)
- `slippage_bps       = 5.0`

`cost_sensitivity_multipliers = [0.0, 1.0, 2.0, 3.0]` applied to the
**E002 headline** for sensitivity diagnostics.

## Baseline comparison

Two layers:

**Layer 1 — direct head-to-head (same signal/universe, different exit)**
- `B_E001_replay` — E001 headline rerun on the same period and panels:
  same signal, same universe, but exit = fixed 5-day. This is the
  number to beat.

**Layer 2 — context (same as E001 ticket)**
- `B0_cash`
- `B1_buy_and_hold` (diagnostic universe)
- `B2_universe_5d_rebalance` (diagnostic universe)
- `B3_price_momentum` (E001 engine with `recent_return_5 > 0` signal,
  fixed 5-day exit)

## Parameters to test
**None. Single point at sensible, sector-standard defaults.**

| Parameter | Value | Rationale |
|---|---:|---|
| `k` (stop multiplier) | 2.0 | Sector-standard "2× ATR" stop |
| `vol_stop_atr_window` | 20 | One month of trading days |
| `holding_cap` | 20 | 4× E001's fixed window — enough room for stop to act |

## Parameters that must NOT be optimized

- `k` = 2.0
- ATR window = 20 trading days
- holding_cap = 20 trading days
- IS/OOS boundary = 2023-01-01
- Signal definition (E001 unchanged)
- Universe rules (E001 unchanged)
- Cost defaults (E001 unchanged)
- 시가 / KRX종가 execution prices

If a future ticket sweeps `k`, that is a **separate experiment**, not
an E002 extension.

## Diagnostic split (within this ticket)

All on the same headline signal + universe, varying only the exit
rule:

- **(A) E002 headline** — vol_stop + 20-day cap ← reported as
  headline
- **(B) Cap only** — 20-day cap, vol_stop disabled. Isolates the cap
  effect alone.
- **(C) Stop only** — vol_stop active, cap effectively disabled
  (cap = 999 trading days). Isolates the stop effect alone.
- **(D) E001 replay** — vol_stop disabled, holding = 5 (rebuilt for
  this exact period). Head-to-head baseline.

(A) vs (D) is the headline comparison. (B) and (C) decompose where
the improvement (if any) comes from.

## Success criteria (alpha-level, NOT infra-level)

All five must hold for E002 to be `promote`d:

1. **Return**: OOS net `total_return` (A) > E001 OOS headline (`+0.165`).
2. **Turnover**: OOS `turnover` (A) < E001 OOS turnover (`162`) × 0.7
   = `113`. Lower turnover proves the cap+stop reduce round trips.
3. **Engagement**: OOS `average_holding_period` (A) > 5 trading days.
   Otherwise dynamic exit didn't actually fire and we just got a
   longer fixed hold.
4. **Hit rate**: OOS `hit_rate` (A) ≥ E001 OOS `hit_rate` (`0.467`).
   The cap+stop must not break what little edge we have.
5. **Information value (not just cost saving)**: cost-0× diagnostic OOS
   net return of (A) > cost-0× diagnostic OOS net return of (D).
   This ensures the improvement is not "we just paid less in costs."

If 1–4 hold but 5 fails, verdict is `revise` (engine works but signal
has no extra info to extract via dynamic exit).

Decomposition diagnostic (informational, not pass/fail):
- (C) stop_only OOS hit_rate should be > (D) E001-replay OOS hit_rate
- (B) cap_only OOS hit_rate ≈ (D) E001-replay OOS hit_rate

## Kill criteria

Any one of these → `kill`:

- OOS net `total_return` (A) ≤ E001 OOS headline.
- OOS turnover (A) ≥ E001 OOS turnover (no improvement).
- ≥ 95 % of trades exit via `time_cap` (stop never fires meaningfully).
- ≤ 5 % of trades exit via `vol_stop` (stop too tight or signal
  never hits it; effectively a degenerate cap-only run).
- OOS `average_holding_period` ≤ 5 (no dynamic engagement).
- Any `pytest` regression on the existing E001 test suite.

## Expected weaknesses

- **Stale ATR**: 20-day ATR computed at entry is fixed for the trade.
  Volatility regime changes mid-trade are not captured.
- **Close-only stop check**: intraday excursions below `stop_price`
  that recover by close do not trigger the stop. Conservative but
  may miss real drawdowns.
- **Gap-down exit**: when stop is triggered on day d's close, exit at
  day d+1's 시가. A gap-down means actual exit is worse than
  `stop_price` (realized loss > intended -2.0×ATR).
- **No take-profit**: trends that accelerate are not crystallized
  until cap. Profit factor improvement is left on the table by
  design — to limit the experiment to **one** new exit lever.
- **Cap-cuts-good-trades**: a winning position held to 20 days may
  still have alpha left. This is acceptable for E002; a future ticket
  could test cap removal vs. trailing logic.
- **Stop-then-rebuy not allowed**: if a ticker is stopped out, it is
  not re-entered immediately, even if it appears in the next day's
  candidates. The slot reuses immediately for a different ticker.

## Codex implementation task

Read this ticket end-to-end before writing code. Read `CLAUDE.md` and
`AGENTS.md`. The base commit for this step is **the latest `main`**.
Do not change the hypothesis, parameters, IS/OOS boundary, universe
rules, cost defaults, or exit-rule numerical values listed above. If
anything is ambiguous, stop and ask in the final output — do not
guess.

### Scope discipline

Code re-use, not rewrite. Most modules from E001 stay as-is:
- `src/data/equity_panel.py` — no change
- `src/backtest/calendar.py` — no change
- `src/data/universe.py` — no change
- `src/strategies/e001_flow_filter.py` — no change
- `src/strategies/baselines.py` — no change
- `src/backtest/costs.py` — no change
- `src/reporting/metrics.py`, `src/reporting/report.py` — no change

What changes:
- `src/features/flow_ratios.py` — extend with one new column:
  `atr_pct_20`. Or, equivalently, create a new file
  `src/features/volatility.py` with `build_atr_pct(panel, calendar,
  window=20) -> DataFrame[종목코드, 날짜, atr_pct_N]`. Either is
  fine; pick the one with cleaner imports.
- `src/backtest/engine.py` — extend `run_candidate_backtest` to
  accept optional `vol_stop_k`, `vol_stop_atr_window`,
  and `atr_features` (a DataFrame with columns
  `종목코드`, `날짜`, `atr_pct_20`). When `vol_stop_k is None`,
  behavior is identical to E001 (no regressions). When set, the
  exit logic follows the spec in this ticket's "Exit rule" section.
- `src/run_experiment.py` — add an alternative entrypoint
  `run_e002_experiment(config, config_path)` that wires the E002
  ConfigShape (see below) and produces the (A), (B), (C), (D)
  runs + baselines + cost sensitivity. Alternatively, generalize
  `run_experiment` to dispatch on a config key. Codex's call;
  keep E001's entrypoint working unchanged.
- `configs/backtests/e002.yaml` — new config.
- `tests/test_engine_dynamic_exit.py` — new test file covering
  vol_stop, time_cap, fallback, no-trigger, and stop-then-no-rebuy.

### ATR computation (timing-safe)

```
For each ticker, on each panel row at date T:
    Compute over the 20 panel rows of that ticker with 날짜 < T:
        atr_pct_20(T) = mean of (고가 − 저가) / KRX종가 across those rows
If fewer than 20 prior rows exist, atr_pct_20 is NaN.
```

If a 고가, 저가, or KRX종가 is NaN or ≤ 0 in the 20-row window, that
row contributes NaN to the average; the engine treats the resulting
NaN atr_pct_20 as "not tradable" and skips the entry (same behavior
as missing 시가).

Verify timing-safety: the entry at execution_date `D+1` reads
`atr_pct_20` from `date == D` (the signal date), and that value uses
only panel rows with `날짜 < D` — strictly before the signal date,
which is also strictly before the execution date. No look-ahead.

### Engine API extension

Current signature:
```python
def run_candidate_backtest(
    panel, calendar, candidates, costs, period_start, period_end,
    *, max_positions=5, holding=5, initial_cash=1.0,
) -> BacktestResult
```

Extend to (additive only — E001 callers unaffected):
```python
def run_candidate_backtest(
    panel, calendar, candidates, costs, period_start, period_end,
    *, max_positions=5, holding=5, initial_cash=1.0,
    vol_stop_k: float | None = None,
    vol_stop_atr_window: int = 20,
    atr_features: pd.DataFrame | None = None,
) -> BacktestResult
```

Behavior:
- `vol_stop_k is None` → identical to E001 (current behavior).
- `vol_stop_k is not None`:
  - Requires `atr_features` to be a DataFrame with
    `(종목코드, 날짜, atr_pct_<window>)` columns. Raise `ValueError`
    on the entry path if ATR is missing for `(ticker, signal_date)`.
  - On entry, look up `atr_pct_20` at `signal_date` for that
    ticker. If NaN, **skip the entry** (treat like 시가 NaN).
    Otherwise, compute `stop_price = entry_price × (1 − vol_stop_k ×
    atr_pct_20)` and store on the slot.
  - `holding` becomes the cap (max trading days from entry to exit).
  - Per-day per-slot routine: stop check → pending exit on next-open
    → cap exit on cap day → period-end fallback.

`exit_reason` enum extended:
- `"holding_period"` (E001 legacy; only when `vol_stop_k is None`)
- `"vol_stop"`
- `"vol_stop_fallback"` (next open NaN, deferred to next valid open)
- `"time_cap"`
- `"time_cap_fallback"`
- `"period_end"`
- `"missing_price_fallback"` (E001 legacy, preserved)

### Configuration file

`configs/backtests/e002.yaml`:

```yaml
experiment_id: E002
panels:
  - research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv
  - research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv
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
  holding: 20            # interpreted as cap when vol_stop_k is set
  max_positions: 5
exit:
  vol_stop_k: 2.0
  vol_stop_atr_window: 20
costs:
  commission_bps: 1.5
  tax_bps_sell:   20.0
  slippage_bps:   5.0
cost_sensitivity_multipliers: [0.0, 1.0, 2.0, 3.0]
output_dir: reports/experiments/E002_dynamic_exit_volatility_stop
```

No other keys. Strict validation, same style as E001 config.

### Runs to produce

Run on the full `[is.start, oos.end]` period each time; the metrics
module slices into IS / OOS / full.

1. **headline** (A) — full E002 engine (vol_stop + 20-day cap)
2. **cap_only** (B) — engine with `holding=20`, `vol_stop_k=None`
3. **stop_only** (C) — engine with `holding=999`, `vol_stop_k=2.0`
4. **E001_replay** (D) — engine with `holding=5`, `vol_stop_k=None`
5. **B0_cash, B1_buy_and_hold, B2_universe_5d_rebalance,
    B3_price_momentum** — same baselines as E001, parameters
    unchanged
6. **diagnostic_estimate_included** — same as E001's diagnostic (now
   running with E002 exit rule on the diagnostic universe). Stored
   under that key in `metrics.json`.
7. **cost_sensitivity** — E002 headline at multipliers
   `[0.0, 1.0, 2.0, 3.0]`. Save `cost_sensitivity.csv`.

`metrics.json` top-level keys:
`headline`, `cap_only`, `stop_only`, `E001_replay`, `B0`, `B1`, `B2`,
`B3`, `diagnostic_estimate_included`. Each is the
`metrics_is_oos` block (`{is, oos, full}`).

### Output files (under `reports/experiments/E002_dynamic_exit_volatility_stop/`)

- `config.yaml` (copy of input)
- `metrics.json`
- `trades.csv` (headline (A) trades)
- `signals.csv` (headline candidates frame)
- `equity_curve.csv` (headline equity curve)
- `cost_sensitivity.csv`
- `report.md` (deterministic, no interpretive prose)

### Tests (new file `tests/test_engine_dynamic_exit.py`)

Use small synthetic panels with hand-crafted prices to make the
expected exits computable by hand.

1. `test_vol_stop_triggers_on_close_and_exits_next_open` — engineer
   a ticker whose close on day d3 falls just below
   `entry × (1 − 2.0 × ATR)`. Verify the trade exits on d4 시가 with
   `exit_reason == "vol_stop"`.
2. `test_time_cap_exits_at_close_when_no_stop` — engineer a ticker
   whose price drifts but never hits stop within 20 days. Verify
   exit at day 20 close with `exit_reason == "time_cap"`.
3. `test_vol_stop_fallback_when_next_open_nan` — stop triggers on
   d3 close, 시가 on d4 is NaN, valid 시가 on d5. Exit at d5 시가
   with `exit_reason == "vol_stop_fallback"`.
4. `test_engine_unchanged_when_vol_stop_k_is_none` — call the
   refactored engine with `vol_stop_k=None`, `holding=5`. Compare
   trades and equity_curve to E001's existing engine output on a
   synthetic panel. Must match (byte-equal trades is acceptable;
   tolerance is allowed only on floating point if numerically
   identical computations differ in implementation order).
5. `test_atr_pct_20_uses_strictly_prior_rows` — mutate panel rows
   with `날짜 >= T`. Recompute ATR for date T. Result must be
   identical.
6. `test_stop_then_no_rebuy_same_day` — synthetic case where the
   same ticker re-emerges as a candidate on the very next day after
   stopping out. Verify the engine does not re-enter that ticker
   on the day immediately following the stop exit (held_tickers
   set includes the just-exited ticker until end of that day).
   Note: the existing engine already drops already-held tickers
   during entry. The new check is that after a same-day exit, the
   slot is empty by the time entries run for the same day — but
   re-entry on the **next** day is allowed.

### Order of work

Commit (Claude commits on Codex's behalf, per established pattern)
after each green-test boundary.

1. Add `atr_pct_20` feature builder (new file or extension of
   `src/features/flow_ratios.py`).
2. Engine refactor: optional vol_stop path.
3. New tests `tests/test_engine_dynamic_exit.py`.
4. New config `configs/backtests/e002.yaml`.
5. CLI extension for E002.
6. Run E002 backtest end-to-end on the real panels.

### Completion criteria

- `pytest` is fully green (E001 suite preserved, new suite passes).
- `python -m src.run_experiment --config configs/backtests/e002.yaml`
  produces every required output file with no manual steps.
- All 5 ticket success criteria are computable from `metrics.json`
  alone.
- The PR description (or final assistant message) lists every place
  the implementation chose one reading of an under-specified spec.

### Out of scope for E002

- `k` sweep
- ATR window sweep
- `cap` sweep
- Take-profit / trailing logic
- Re-entry after stop (allowed on the next day, never on the same day)
- Adding any new data source
- Modifying the entry signal

## Result summary
DO NOT FILL until backtest is complete and files exist on disk.

## Claude review
DO NOT FILL until result files are read.
