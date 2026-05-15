# B004 — Regime sensitivity diagnosis with market gate

## Status
planned

## Role under test
**Universe-level regime gate** — a new layer **above** the existing
`(filter, trigger, ranking, exit)` stack. Either all four roles fire
on a given signal_date, or none do, depending on the gate.

This ticket introduces ONE new component (the regime gate) but its
primary purpose is **diagnostic, not promotional**.

## Strategy composition

| Layer | Carrier |
|---|---|
| **Regime gate** (NEW) | Variable — see candidates below |
| Filter | `filter_flow_sign_both_positive` — `(fnv_5 > 0) AND (inv_5 > 0)` |
| Trigger | `trigger_immediate` (B002 default, NOT T3 — see "Carrier choice" below) |
| Ranking | `rank_by_combined_flow_5` |
| Exit | `exit_signal_reversal` — `(fnv_5 ≤ 0) OR (inv_5 ≤ 0)` |

Universe, costs, max_positions, IS/OOS boundary unchanged from the
A/B family conventions.

### Carrier choice — trigger stays at T1 (immediate), not T3 (acceleration)

B003 ended descriptively and T3 was never validated in a single-point
promote. B004 therefore continues on the B002 carrier (T1) — the most
recently promoted carrier. If B004 concludes the regime gate is real
and we want to layer T3 on top, that becomes a separate ticket
(B005-or-later) with the same diagnostic discipline applied to T3.

## Purpose — diagnostic, not promotional

B003 connection: B003 OOS positive return is essentially driven by 2025
alone. All four trigger variants lose money in IS (2018-2022) even at
zero costs except T4. This raises a fundamental two-scenario question
that we have not yet been able to resolve:

- **Scenario A**: 5-day foreign+institution flow IS a real alpha
  signal that long-only fails to harvest in down regimes. A regime
  gate would unlock that alpha by skipping bad regimes.
- **Scenario B**: 5-day flow is NOT a real alpha signal. The 2025
  positive return is bull-market beta that any trend-chasing rule
  would have captured. A regime gate would appear to "fix" things
  by skipping the very years where the signal under-performs, but
  the strategy would in fact be earning regime beta, not flow alpha.

These two scenarios produce **visually identical** results if we only
look at (signal + regime_filter). The decisive comparison is **regime
filter alone** (no flow signal at all).

B004 is therefore designed first as a diagnostic, second as a
potential promote.

## Hypothesis (pre-registered)

H1 (alpha contribution): When the regime gate is ON, the
flow-signal-driven strategy `(a) signal + gate` will outperform the
"gate-only equal-weight" strategy `(c) gate alone` in **both**:
- OOS net total return by ≥ +0.20
- IS net total return by ≥ +0.20

If H1 holds → evidence for Scenario A (signal carries real
information beyond regime selection).

If H1 fails (the gate-alone variant comes within 0.20 of the signal
variant) → Scenario B confirmed. The flow signal is essentially
regime beta. **Strategy needs to be redesigned, not patched.**

H2 (regime sensitivity): The regime gate's contribution will be
distributed across multiple IS down-years (specifically 2018 AND
2022, since those are the bear years), not concentrated in one.
Concentration in one year = overfitting suspicion.

## Pre-registered mechanism for the regime gate

**Why KOSPI 200-day SMA gate**: Long-only trend-following strategies
need a positive market backdrop to monetize trend signals. In down
regimes (KOSPI below its 200-day moving average), even temporarily
positive stocks tend to roll back as the broader market falls.
Foreign and institutional buyers also operate within market cycles
— their net buying during a down regime often unwinds before the
strategy can exit. The 200-day SMA is the simplest, most-tested
classical regime indicator (used by Faber, Antonacci, etc.) and has
no extra free parameters beyond the window choice.

**Single window choice (no tuning)**: We pre-commit to KOSPI
**200-day** SMA. NOT optimized. NOT scanned across {50, 100, 150,
200, 250}. If we scanned and chose the best, that would be
data-snooping. If 200d fails in IS, we accept the result; we do
NOT try 100d or 150d in this ticket.

**Gate rule (precise)**: On signal_date T, the gate is "ON" iff
`kospi_proxy_level(T) > kospi_proxy_sma_200(T)` (proxy level
defined in "Data source" below). Gate state at T determines
whether entries fire on T+1 morning. For variants (a) and (b),
existing positions opened before the gate flipped to "OFF" continue
to follow their normal exit rule — the gate is an **entry-side
gate only** for those variants, not a forced liquidation. This
avoids whip-saw losses from sudden gate flips. For variant (c),
the gate flipping OFF forces exit via the new `exit_on_gate_off`
exit role (see variant (c) spec below); (c) is the only variant
where the gate also drives exits.

**Data source**: We do NOT have a direct KOSPI daily close in our
processed inputs. Use a **mathematically equivalent KOSPI-proxy
level**: cumulative product of `cap_weighted_return` from
`research_input_data/inputs/macro_features/krx_market_breadth_kospi_2010_2026.csv`.
The 200-day SMA is computed on this cumulative-level series.

The gate condition `level(T) > SMA_200(T)` is multiplicatively
invariant — a positive scaling of the entire series leaves the
comparison unchanged — so a proxy level constructed from cumulative
returns yields the same gate ON/OFF decisions as actual KOSPI
levels would.

The cumulative series starts at 2010-01-04 = 1.0 baseline. By
2018-01-02 (IS start) we have ~7 years of warmup — far more than
the 200-day SMA requires.

**SMA warmup edge case**: On any signal_date T where SMA_200(T)
is undefined (fewer than 200 trading days of prior level data),
the gate is **OFF** (conservative — no entries fire). In our
B004 data window this only affects pre-2010 dates that we are
not using anyway, but the test suite must verify this behavior on
synthetic input.

## Pre-registered variants (ablation strictly required)

All four variants run on the same calendar, same universe, same
costs. Output side-by-side in the same `metrics.json`.

### (a) `signal + regime_gate` — the actual candidate strategy
- Filter / Trigger / Ranking / Exit: as listed above (B002 carrier)
- Entry only when KOSPI > 200-day SMA on signal_date

### (b) `signal only` — B002 carrier baseline
- Exactly B002. No regime gate. Carried into this ticket for
  side-by-side ablation since baselines are currently broken
  (engineering issue B0/B1/B2).

### (c) `regime gate only` — the DECISIVE comparison
- No flow filter, no flow ranking, no flow exit.
- **Selection rule** (deterministic, no flow content):
  on every signal_date T where the gate is ON, take the top 5
  names from the universe ranked by **prior-day (T) close-based
  시가총액 (market cap)**. Equal weight in `max_positions=5` slots.
  Market cap is `종가 × 상장주식수` from the equity panel; if 상장주식수
  is absent, fall back to the `시가총액` column directly. Ties
  broken by 종목코드 lexical order (deterministic). Names that are
  not in the universe on T are skipped.
- **Hold rule**: until gate flips OFF, OR the name leaves the
  universe (e.g., dropped from dynamic_top100, fails liquidity
  filter, panel row missing).
- **Exit rule**: when the gate flips OFF on signal_date T (i.e.,
  `gate(T) = OFF` while `gate(T-1) = ON`), exit ALL positions at
  T+1 시가. This is implemented as a new exit role
  `exit_on_gate_off` in `src/roles/exits.py`, consistent with the
  existing exit-role architecture.
- When gate flips ON again on signal_date T (`gate(T) = ON` while
  `gate(T-1) = OFF`): rebuild the top-5 portfolio from scratch at
  T+1 시가.
- **Why market cap, not 거래대금**: 거래대금 ranking shifts daily
  and would introduce turnover-driven noise that could look like
  alpha. Market cap is much more stable, gives a clean "buy the
  largest 5 names" benchmark, and is what passive index strategies
  effectively do. The point of (c) is to be the cleanest possible
  "no-flow-alpha" benchmark.
- This is the strategy that earns ONLY regime beta. If (a) and (c)
  look similar, our entire alpha story collapses.

### (d) `cash` — absolute floor
- 0% return throughout. Sanity reference.

## Reportable metrics

For each of (a), (b), (c), (d), report side-by-side:

1. IS net total return, hit rate, trade count, cost-0 net
2. OOS net total return, hit rate, trade count, cost-0 net
3. **Per-year net total return** for both IS (2018-2022) and OOS
   (2023-2026) — 9 cells per variant
4. Variant-vs-variant per-year delta tables:
   - (a) − (c): the alpha-attribution table (where does the flow
     signal add value beyond regime?)
   - (a) − (b): the regime-gate contribution table (where does the
     regime gate add value beyond raw signal?)
5. Number of days the gate is ON vs OFF per year (descriptive)

Save as `regime_year_breakdown.csv`.

## Pre-registered interpretation rules

**Promote** the regime-gated strategy if all four hold:
- H1 satisfied (both IS and OOS, ≥ +0.20 delta vs gate-only)
- H2 satisfied (gate contribution spread across both 2018 and 2022
  bear years, not concentrated in one)
- Cost sensitivity: at 3× costs the gate-gated strategy still beats
  cost-3× signal-only
- (a) wins (c) in at least **3 of 5 IS years**

**Kill** the regime-gated strategy AND the underlying flow signal as
currently defined if any of:
- H1 fails by margin (gate-only within 0.10 of signal+gate in OOS).
  → flow signal is regime beta. Stop adding patches; redesign signal
  from scratch.
- The signal+gate strategy performs worse than gate-only in OOS.
  → flow signal is anti-alpha in regime-gated context.

**Inconclusive** if:
- H1 satisfied in OOS but not IS, or vice versa
- Cost sensitivity flips the result
- Then a follow-up B005 ticket is required to disambiguate

**Important**: If we Kill at this stage, that does NOT mean the
project is dead. It means the working alpha definition is wrong, and
the next experiment must redesign the signal — e.g., relative flow
strength (signal vs market average), longer/shorter windows, or
entirely different alpha hypotheses.

## Data assumptions

**No new external data.** Same two equity panels as the A/B family.

KOSPI-proxy level is constructed from
`research_input_data/inputs/macro_features/krx_market_breadth_kospi_2010_2026.csv`,
specifically the `cap_weighted_return` column (already present in
the file). Codex extends `src/data/` to load this file and computes
the cumulative-level series + 200-day SMA. No new data downloads,
no API calls.

Market cap for variant (c)'s ranking comes from the existing equity
panel columns (`종가 × 상장주식수`, or `시가총액` directly if available).

## Universe / costs / dates (unchanged from B002)

- Universe: dynamic Top100, 거래대금 ≥ 5 billion KRW (20-day avg),
  exclude rows with `거래대금추정여부 = True`
- Costs: 1.5 / 20 / 5 bps (commission / tax-sell / slippage)
- IS: 2018-01-02 ~ 2022-12-30
- OOS: 2023-01-02 ~ 2026-05-04
- max_positions: 5
- Entry: T+1 시가 (KRX 09:00)
- Exit: rule-based (signal_reversal for (a)(b); gate-off for (c))

## Multiple-testing acknowledgment

Cumulative variant comparisons across this project so far: ~11.
B004 adds 4 more (a, b, c, d) — but only (a) is the new candidate
under test; (b)(c)(d) are required ablations not new optimization
targets. The promote criteria above are intentionally stricter than
B002's were, to compensate.

We commit to: **B004 is the final tweaking experiment on the
2018-2026 dataset using the current flow-signal definition.** After
B004, regardless of verdict, the next experiment either (i) uses new
data (older history or new universe) for a true OOS check, or
(ii) redesigns the signal from scratch under a new hypothesis. We do
not add a 6th layer onto the same data without resetting.

## Codex implementation task

Read this ticket end-to-end. Read AGENTS.md and the R001 review for
role structure context. Base commit = latest `main`.

### Scope discipline (additive only)

Touch:
- `src/data/kospi_proxy.py` (NEW) — load `krx_market_breadth_kospi_2010_2026.csv`,
  compute cumulative product of `cap_weighted_return` to derive the
  KOSPI-proxy level series, then `kospi_proxy_sma_200`. Both indexed
  by date. Strict no-look-ahead: SMA at T uses levels through T
  inclusive only.
- `src/features/regime.py` (NEW) — compute
  `regime_gate_on(T) = level(T) > sma_200(T)`. Returns boolean
  series indexed by date. Where `sma_200(T)` is undefined (fewer
  than 200 prior levels), gate = OFF.
- `src/roles/exits.py` — add `exit_on_gate_off` exit role function.
  Signature consistent with the other exit roles (returns
  parameters consumed by the engine). When the engine sees
  `gate(T) = OFF` while a position is open from a date when
  `gate = ON`, exit at T+1 시가.
- `src/strategies/b004_regime_gate.py` (NEW) — orchestrates the 4
  variants. Each variant is a clean independent backtest run:
  - (a) uses B002 carrier + regime_gate suppresses entries when OFF
  - (b) uses B002 carrier exactly (no gate at all)
  - (c) uses gate-driven entries (top-5 by 시가총액 when gate ON) +
    `exit_on_gate_off` + universe-exit rule
  - (d) cash (no signals, no positions, zero return)
- `src/backtest/engine.py` — minimal extensions:
  1. Accept an optional `regime_gate_dates` set; on signal_dates
     NOT in this set, entries are suppressed (used by variant (a)).
  2. Support the new `exit_on_gate_off` exit role (used by (c)).
  3. Backward compatible: default behavior unchanged when neither
     hook is supplied. All 6 prior experiments must reproduce
     byte-identical results — verify with a quick rerun of E001
     (A001) as a regression sanity check before committing the
     engine change.
- `src/run_experiment.py` — add `experiment_id == "B004"` dispatch.
- `configs/backtests/b004.yaml` (NEW).
- `tests/test_kospi_proxy.py` (NEW) — feature timing tests for
  level cumulation and `sma_200` (no look-ahead), warmup-period
  gate-OFF behavior on synthetic input.
- `tests/test_regime_gate.py` (NEW) — gate boolean correctness on
  hand-crafted level series (crossings up and down).
- `tests/test_engine_regime_gate.py` (NEW) — synthetic backtest
  where the gate is OFF for a known window; verify no entries
  fire in that window for variant (a), and verify variant (c)
  forces exit on gate-OFF flip.
- `tests/test_exit_on_gate_off.py` (NEW) — unit test for the new
  exit role independently of the engine.

**Do NOT touch**: existing role functions (filter / trigger / ranking /
existing exit roles), existing strategy modules (a001-a004, b001-b003),
baselines, existing tests. Adding `exit_on_gate_off` to the exits
module is allowed; modifying `exit_signal_reversal`, `exit_time_cap`,
or `exit_volatility_stop_plus_cap` is NOT.

### Variant (c) implementation note

(c) is fully specified above in "Pre-registered variants → (c)". To
recap for implementation:
- Selection: top 5 names by `시가총액` (prior signal_date close) from
  the dynamic_top100 universe after liquidity filter. Equal weight.
  Tie-break by 종목코드.
- Hold until gate OFF or name leaves universe.
- Exit on gate OFF at T+1 시가 via `exit_on_gate_off` role.
- Rebuild on gate flip ON.

Contains zero flow-signal alpha. The only edge it could have is
regime beta.

### Configuration file

`configs/backtests/b004.yaml`:

```yaml
experiment_id: B004
panels:
  - research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv
  - research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv
market_flow_csv: research_input_data/inputs/market_flow/kiwoom_market_flow_2018_2026_integrated.csv
market_breadth_csv: research_input_data/inputs/macro_features/krx_market_breadth_kospi_2010_2026.csv
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
  max_positions: 5
regime:
  gate_type: kospi_sma
  window: 200
exit:
  type: signal_reversal
trigger:
  type: immediate
variants:
  - signal_plus_gate
  - signal_only
  - gate_only_equal_weight
  - cash
costs:
  commission_bps: 1.5
  tax_bps_sell:   20.0
  slippage_bps:   5.0
cost_sensitivity_multipliers: [0.0, 1.0, 2.0, 3.0]
output_dir: reports/experiments/B004_regime_sensitivity_diagnosis
```

### Output files

Under `reports/experiments/B004_regime_sensitivity_diagnosis/`:

- `config.yaml`
- `metrics.json` — top-level keys `signal_plus_gate`, `signal_only`,
  `gate_only_equal_weight`, `cash`, plus cost-0 variants for the
  first three
- `trades.csv` — combined with `variant` column
- `signals.csv` — combined with `variant` column
- `equity_curve.csv` — wide format: `date, signal_plus_gate_value,
  signal_only_value, gate_only_value, cash_value`
- `regime_year_breakdown.csv` — per-year per-variant net total
  return; deltas (a)−(b), (a)−(c) included as separate columns
- `regime_state_log.csv` — for each signal_date, the KOSPI-proxy
  level, the 200-day SMA, and gate ON/OFF flag
- `cost_sensitivity.csv`
- `report.md`

### Tests

Existing tests must remain green. New tests bring suite to ~115+.

### Order of work
Commit (Claude commits) after each green-test boundary.

1. Load KOSPI-proxy level (from cap_weighted_return cumulation) +
   add 200-day SMA + `regime_gate_on` boolean + timing tests
2. Add `exit_on_gate_off` exit role in `src/roles/exits.py` + unit
   test
3. Extend engine: optional `regime_gate_dates` entry-side hook +
   support for `exit_on_gate_off` exit role + tests + regression
   check on E001/A001 byte-identical reproduction
4. Implement variant (c) gate-only equal-weight setup (market-cap
   ranked top-5) + integration test
5. Implement strategy module orchestrating all 4 variants +
   dispatcher + config
6. Run B004 real-panel

### Completion criteria
- pytest fully green
- `python -m src.run_experiment --config configs/backtests/b004.yaml`
  produces every required output
- All 4 variants reported side-by-side in metrics.json
- regime_year_breakdown.csv contains per-year deltas
- Final assistant message reports the verdict-relevant numbers:
  - (a) vs (c) IS net delta, OOS net delta
  - (a) vs (c) win count across 5 IS years
  - 2018 and 2022 specific deltas (the bear-year diagnostic)

### Out of scope for B004
- Trigger variation (T3 stays out until separate ticket)
- Alternative regime windows (50d, 100d, 150d, 250d)
- Alternative gate definitions (RSI-based, drawdown-based)
- New data sources
- Forced liquidation on gate-off for (a)(b)
- Engine changes beyond the minimal gate hook

## Result summary
DO NOT FILL until backtest is complete.

## Claude review
DO NOT FILL until result files are read.
