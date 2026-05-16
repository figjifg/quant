# B011 — Gate-only carrier on full 2010-2026 timeline

## Status
planned

## What is being tested
**B004 variant (c) — gate-only equal-weight market-cap top 5 with
KOSPI 200d SMA gate — applied to the full 2010-2026 timeline (with
2016 gap)** to test whether this simple regime-following strategy
satisfies the user's stated goal ("outperform index moderately +
catch big spikes") better than the failed flow-based carrier.

This is a DIAGNOSTIC / direction-setting ticket, NOT a promote
ticket. The flow-based carrier (T3+F3) failed verification in B010.
B011 asks: does the simple gate-only baseline (already-known OOS
+24% in 2018-2026) hold up over 16 years?

## Why this experiment now

B010 proved the T3+F3 carrier is regime-conditional, not universal
alpha. Per the B010 review's "Option D" path:

> "Option D: 단순 regime-following 채택. B004 (c) 단순 대형주
> 동일가중 + 200d gate = OOS +24% over 3.4년. 사용자 목표 ('지수 + α
> + spike following') 에 가장 단순하게 부합. 정교한 alpha 추구 중단,
> regime-beta 만 깨끗하게 캡쳐."

B011 verifies Option D quantitatively on the longest data we have
(2010-2017 from B010-prepared loaders + 2018-2026 from existing
B004 data + market_breadth_kospi for the gate signal).

## Strategy composition

| Layer | Carrier |
|---|---|
| Regime gate | KOSPI proxy level > 200-day SMA (from B004) |
| Selection (when gate ON) | top 5 by **prior-day 시가총액** (market cap), equal weight |
| Hold | until gate flips OFF or name leaves universe |
| Exit | gate-off (`exit_on_gate_off` from B004 roles) |

No flow signal anywhere. No filter, trigger, ranking, exit roles
from the flow carrier. This is pure regime beta with large-cap
selection. Reused unchanged from B004 (c) implementation.

## Variants

### V1 — `gate_only_mcap` (the candidate strategy)
B004 (c) carrier reproduction on full 2010-2026 timeline.

### V2 — `kospi_buy_and_hold` (the comparator)
**Always-invested** alternative: hold the KOSPI-proxy level
(cumulative `cap_weighted_return`) from 2010-01-04 through
2026-05-04 with no gate. Represents "passive index" performance over
the same period.

Why this comparator: gate-only's main hypothesis is that it
sidesteps drawdowns during bear regimes while still capturing
upside. To test this, we compare against the alternative of just
sitting in the market.

### V3 — `cash`
Sanity reference, always zero return.

## Hypothesis (pre-registered descriptive)

This is exploration, not a promote ticket. We pre-register what we
expect / accept / reject in plain language so the verdict is not
result-fitted.

**H1 (cumulative survival)**: V1 cumulative net total return > 0
over 2010-2026 (with 2016 gap).

The flow carrier failed this catastrophically (V1 of B010 cumulative
= -87.8 % over the same span). H1 verifies that gate-only actually
makes money over 16 years.

**H2 (vs always-invested KOSPI)**: V1 cumulative net total return
≥ V2 cumulative net total return - 0.10 (gate-only is within 10
points of KOSPI buy-and-hold).

A pure regime-following strategy doesn't need to beat KOSPI to be
useful — if it gets close to KOSPI returns with substantially less
drawdown, that's still valuable. H2 is a "doesn't badly trail
KOSPI" check, not a "must outperform" check.

**H3 (spike capture)**: V1 produces positive net total return in
each of the three known spike years (2010, 2025, 2026 partial).

The user's explicit goal includes "catching big spikes". The
strategy must, at minimum, be positive in the years that visibly
were spikes. If it misses them, it's not serving the goal.

**H4 (drawdown protection)**: V1 max drawdown < V2 max drawdown by
at least 5 percentage points.

The other half of the user's goal is "don't crash too badly". The
gate's whole purpose is to avoid the worst of bear periods. H4
verifies this works at the cumulative level.

**H5 (multi-year robustness)**: V1 produces a positive yearly net
total return in ≥ 8 of 16 candidate years (majority — 2010, 2011,
…, 2015, 2017, 2018, …, 2026).

The flow carrier was positive in only 3 of 16. Gate-only doesn't
need to be positive every year, but ≥ 50 % positive years is the
minimum bar for "this is a real strategy, not occasional luck".

## Verdict logic (pre-registered)

**ADOPT as primary deployable strategy** if all five hold:
- H1, H2, H3, H4, H5 all pass
- Then gate-only becomes the formal project answer for the user's
  stated goal

**ADOPT WITH CAVEATS** if 3-4 of 5 pass:
- Strategy has clear value but one dimension fails
- Document which dimension failed and decide whether to live with
  it or look for improvements

**NOT VIABLE** if H1 fails (cumulative loses money over 16 years):
- Even simple regime-following doesn't work on Korean equities for
  this universe and these costs
- Project conclusion: this hypothesis class is exhausted; pivot
  required or accept that no strategy in our hypothesis space works

**MIXED** if H1 passes but multiple H2/H3/H4/H5 fail:
- Strategy makes money but doesn't deliver the stated goal
- Discuss with user whether the trade-off is acceptable

## Reportable metrics

For each of V1, V2, V3:

1. **Cumulative net total return** over 2010-01-04 to 2026-05-04
   (with 2016 gap)
2. **Per-year net total return** — 16 cells per variant
3. **Max drawdown** (running peak-to-trough)
4. **Year-wise positive count**
5. **Annualized return** and **annualized volatility**
6. **Sharpe ratio** (annualized return / annualized vol)
7. Trade count
8. Hit rate
9. Cost paid total

Save:
- `gate_only_year_breakdown.csv` — per-year per-variant net total return
- `gate_only_drawdown.csv` — daily drawdown series for V1 and V2
- `gate_only_summary.csv` — single-row verdict diagnostic (H1-H5 flags)

## Universe / costs / dates

- Universe (V1 only): dynamic_top100 + 20-day avg 거래대금 ≥ 5 billion +
  거래대금추정여부 = False (same rule applied across 2010-2026)
- V2 (KOSPI proxy buy-and-hold): no universe filter (just hold the
  index)
- Costs (V1 only): 1.5 / 20 / 5 bps (same as B004 (c))
- V2 has NO costs (passive holding has no turnover)
- Period: 2010-01-04 to 2026-05-04 with calendar year 2016 excluded
- max_positions: 5 (V1 only)
- Entry: T+1 시가 (V1 only)

## Data assumptions

**No new data introduction.** All data files are already in use:
- 2010-2017 panels (from B010 work)
- 2017-2024 panel (existing, used for 2017 only per B010 config)
- 2018-2024 panel (existing)
- 2025-2026 panel (existing)
- market_breadth_kospi 2010-2026 (existing, from B004)
- market_flow files (not needed — gate-only doesn't use flow data)

## Implementation task (Codex)

Read this ticket end-to-end. Read AGENTS.md, B004 review (variant
(c) origin), B010 review (regime-conditionality verdict), and
existing src/strategies/b004_regime_gate.py for the (c) variant
implementation pattern.

### Scope discipline (additive only)

Touch:
- `src/strategies/b011_gate_only_full_timeline.py` (NEW) —
  orchestrates V1 (gate_only_mcap on full 2010-2026), V2 (KOSPI
  buy-and-hold), V3 (cash). Reuses B004 (c) selection logic and
  `exit_on_gate_off` exit role. For V2, compute the cumulative
  KOSPI proxy level from market_breadth.cap_weighted_return and
  return its cumulative as the equity curve directly (no engine
  involvement).
- `src/run_experiment.py` — add `experiment_id == "B011"` dispatch.
- `configs/backtests/b011.yaml` (NEW).
- `tests/test_b011_strategy.py` (NEW) — sanity test on synthetic
  panel that V1 produces non-trivial trades when gate is ON and zero
  trades when gate is OFF; V2 monotonically tracks the proxy level.

**Do NOT touch**:
- `src/backtest/engine.py` — should not need any change. Verify
  with `git diff src/backtest/engine.py` empty.
- Existing role functions (use existing `exit_on_gate_off` and
  KOSPI proxy / regime features).
- Existing strategy modules (a001-a004, b001-b010).
- Existing tests must remain green (currently 160).

### Configuration file

`configs/backtests/b011.yaml`:

```yaml
experiment_id: B011
panels:
  - research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv
  - research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv
  - research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv
  - research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv
panel_date_filters:
  # 2017-2024 panel: ONLY 2017 portion (to avoid overlap with the
  # 2018-2024 panel which is used for 2018-2024 coverage)
  research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv:
    end: 2017-12-31
market_breadth_csv: research_input_data/inputs/macro_features/krx_market_breadth_kospi_2010_2026.csv
period:
  start: 2010-01-04
  end:   2026-05-04
  exclude_calendar_years: [2016]
universe:
  require_dynamic_top100: true
  min_avg_traded_value_20d: 5_000_000_000
  exclude_estimated_flag_rows: true
regime:
  gate_type: kospi_sma
  window: 200
selection:
  type: market_cap_top_n
  n: 5
costs:
  commission_bps: 1.5
  tax_bps_sell:   20.0
  slippage_bps:   5.0
variants:
  - gate_only_mcap        # V1
  - kospi_buy_and_hold    # V2
  - cash                  # V3
output_dir: reports/experiments/B011_gate_only_full_timeline
```

### Output files

Under `reports/experiments/B011_gate_only_full_timeline/`:

- `config.yaml`
- `metrics.json` — top-level keys `gate_only_mcap`,
  `kospi_buy_and_hold`, `cash`, including all reportable metrics
- `trades.csv` (V1 trades; V2 and V3 have no trades)
- `equity_curve.csv` — wide format: `date, V1_value, V2_value,
  V3_value`
- `gate_only_year_breakdown.csv`
- `gate_only_drawdown.csv` — daily drawdown for V1 and V2
- `gate_only_summary.csv` — single-row summary with H1-H5 flags and
  values
- `report.md`

### Tests

Existing 160 tests remain green. New tests bring suite to ~162+.

### Order of work

Commit (Claude commits) after each green-test boundary.

1. Add B011 strategy module + dispatcher + config
2. Add B011 sanity test on synthetic panel
3. Run B011 real-panel
4. Verify engine.py untouched

### Completion criteria

- pytest fully green
- `python -m src.run_experiment --config configs/backtests/b011.yaml`
  produces every required output
- All 3 variants reported side-by-side in metrics.json
- src/backtest/engine.py untouched
- Final assistant message reports the verdict-relevant numbers in
  this exact format:
  - V1 cumulative net (16yr): __%
  - V2 (KOSPI buy-and-hold) cumulative net: __%
  - V1 - V2 cumulative delta: __%
  - V1 max drawdown: __% ; V2 max drawdown: __%
  - V1 positive years: __ of 16
  - V1 in (2010 / 2025 / 2026 / each individually): __ / __ / __
  - V1 annualized return: __% ; V1 annualized vol: __%
  - V1 Sharpe: __

### Out of scope for B011
- Any flow-based variant
- Any new role function
- Any new alpha hypothesis
- Engine changes
- Era-appropriate cost adjustments
- 2016 gap reconstruction

## Result summary
DO NOT FILL until backtest is complete.

## Claude review
DO NOT FILL until result files are read.
