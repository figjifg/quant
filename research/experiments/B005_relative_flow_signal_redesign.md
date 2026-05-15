# B005 — Relative-flow signal redesign

## Status
planned

## What is being redesigned
**The underlying alpha definition itself**, not a single role.

Current alpha (B002): "stock has positive 5-day cumulative
foreign+institution flow ratio in absolute terms".

New alpha hypothesis (B005): "stock has positive 5-day cumulative
foreign+institution flow ratio **relative to the cross-sectional
universe median** for the same signal_date".

Because the alpha definition changes, every role that consumes it
updates consistently in the new variants:
- Filter: changes from "absolute > 0" to "relative > 0"
- Ranking: changes from "absolute strength" to "relative strength"
- Exit: changes from "absolute reversal" to "relative reversal"

Trigger does NOT consume the alpha definition; it stays at
`trigger_immediate`. Universe, costs, max_positions, IS/OOS
boundary, panels — all unchanged.

## Why this single-hypothesis interpretation does not violate the
"one role per experiment" rule

The R001 / "one role per experiment" discipline locks the alpha
definition and varies a single role. B005 inverts that: the alpha
definition itself is the variable, and the touchpoints (filter /
ranking / exit) update consistently to reflect the new definition.

The hypothesis space is **one underlying alpha definition per
ticket**. Mixing entry from one alpha and exit from another (e.g.,
"relative entry, absolute exit") is explicitly forbidden — that
would be a hybrid we cannot interpret.

## Strategy composition (per variant)

| Layer | (a) baseline (B002) | (b) relative z-score | (c) relative median-diff |
|---|---|---|---|
| Base feature | `fnv_5`, `inv_5`, `combined_flow_5` | `fnv_5_z`, `inv_5_z`, `combined_flow_5_z` | `fnv_5_rel`, `inv_5_rel`, `combined_flow_5_rel` |
| Filter | `filter_flow_sign_both_positive` | `filter_relative_flow_sign_both_positive_z` | `filter_relative_flow_sign_both_positive` |
| Trigger | `trigger_immediate` | `trigger_immediate` | `trigger_immediate` |
| Ranking | `rank_by_combined_flow_5` | `rank_by_combined_flow_5_z` | `rank_by_combined_flow_5_rel` |
| Exit | `exit_signal_reversal` | `exit_signal_reversal_z` | `exit_signal_reversal_rel` |

All other parameters (universe, costs, max_positions, IS/OOS dates)
are identical to B002.

## Hypothesis (pre-registered)

**H1 — V-recovery fix**: At least one of (b) or (c) achieves IS
2020 net total return ≥ 0 (vs B002 / variant (a) 2020 IS at −0.39).

The 2020 V-recovery is the most damning failure of the absolute-flow
signal in B004. Fixing 2020 is the single most important diagnostic
for whether the relative-flow hypothesis is correct.

**H2 — OOS preservation**: At least one of (b) or (c) achieves OOS
net total return ≥ B002 OOS net (= +0.641).

This means "don't worsen OOS in exchange for fixing 2020".

**H3 — Spike-capture preservation**: At least one of (b) or (c)
achieves 2025 OOS net total return ≥ 50 % of B002 2025 (= 0.5 ×
0.883 = +0.442).

We accept some spike attenuation since relative flow could under-
weight broad bull-market days, but losing more than half the spike
capture would defeat the user's stated goal.

H1 alone is the primary diagnostic. H2 and H3 prevent "fixed 2020
at the cost of everything else" outcomes.

## Pre-registered interpretation rules

**Promote** (one of (b) or (c) becomes the new B-family carrier) if
all four hold for that variant:
- H1 satisfied (2020 IS ≥ 0)
- H2 satisfied (OOS net ≥ +0.641)
- H3 satisfied (2025 OOS ≥ +0.442)
- IS net ≥ B002 IS net (≥ −0.840 — at least no worse overall in IS)

**Kill** the relative-flow hypothesis (move to candidate 2 or 3 from
the B005 planning discussion) if all of:
- BOTH (b) and (c) fail H1 (2020 IS still ≤ −0.10)
- AND BOTH (b) and (c) OOS net < +0.541 (i.e., 0.10 worse than B002)

**Inconclusive** — write a B006 follow-up if mixed signals:
- e.g., one variant satisfies H1 but the other satisfies H2/H3
- e.g., 2020 fix works but with an unrelated regime collapse elsewhere
- e.g., (b) and (c) give materially different outcomes (forces a
  separate single-point ticket to choose between z-score and
  median-diff)

## Pre-registered base-feature definitions

For every signal_date T and every stock s in the universe at T,
let `U(T)` = the set of stocks passing the universe filter on T
(dynamic_top100 + 20-day avg 거래대금 ≥ 5 billion + 거래대금추정여부 = False).
The universe membership is read from the existing equity panels;
no look-ahead.

### (b) z-score variant

For each signal_date T:
1. Collect `fnv_5(s, T)` for all `s ∈ U(T)`.
2. Compute `mean_T = mean(fnv_5(_, T))`, `std_T = std(fnv_5(_, T), ddof=1)`.
3. If `|U(T)| < 30` OR `std_T == 0` OR `std_T == NaN`: define
   `fnv_5_z(s, T) = NaN` for every s. Filter then evaluates to
   False (no entries fire on such days).
4. Else: `fnv_5_z(s, T) = (fnv_5(s, T) - mean_T) / std_T` for each
   `s ∈ U(T)`.

Same procedure for `inv_5` → `inv_5_z` and `combined_flow_5` →
`combined_flow_5_z`.

The min-30 cutoff ensures the cross-sectional moments are not
trivially noisy. In our dynamic_top100 universe this is satisfied
on essentially all dates after the warmup period.

### (c) median-diff variant

For each signal_date T:
1. Collect `fnv_5(s, T)` for all `s ∈ U(T)`.
2. Compute `median_T = median(fnv_5(_, T))`.
3. If `|U(T)| < 30`: define `fnv_5_rel(s, T) = NaN`. Filter then
   evaluates to False.
4. Else: `fnv_5_rel(s, T) = fnv_5(s, T) - median_T`.

Same procedure for `inv_5` → `inv_5_rel` and `combined_flow_5` →
`combined_flow_5_rel`.

### Why two relative variants

Z-score normalizes by within-day cross-sectional std and median-diff
does not. They answer slightly different questions:
- **z-score**: "is this stock above-average AND is the spread among
  stocks meaningful today?"
- **median-diff**: "is this stock above-average regardless of how
  spread out today is?"

On days with small std (everyone buying similarly), z-score amplifies
small absolute differences while median-diff treats them as small.
The two variants will likely diverge most in regime transitions —
exactly the periods where 2020 V-recovery failure happened. Running
both lets us see which form of "relative" is the right one.

## Pre-registered role definitions (variants (b) and (c) only)

### Filter
- (b): `(fnv_5_z(s, T) > 0) AND (inv_5_z(s, T) > 0)`
- (c): `(fnv_5_rel(s, T) > 0) AND (inv_5_rel(s, T) > 0)`

NaN inputs → False (no entry).

### Ranking
- (b): rank by `combined_flow_5_z(s, T)` descending
- (c): rank by `combined_flow_5_rel(s, T)` descending

NaN inputs → exclude from ranking.

### Exit
On signal_date T (i.e., after market close on T, applied to next
day's open T+1 시가):
- (b): exit if `(fnv_5_z(s, T) ≤ 0) OR (inv_5_z(s, T) ≤ 0)`
- (c): exit if `(fnv_5_rel(s, T) ≤ 0) OR (inv_5_rel(s, T) ≤ 0)`

NaN exit signal → treat as ≤ 0 (exit). This is conservative; no
free rides if the cross-sectional moments degenerate.

## Reportable metrics per variant

For each of (a), (b), (c), output:

1. IS net total return, hit rate, trade count, cost-0 net
2. OOS net total return, hit rate, trade count, cost-0 net
3. Per-year net total return for IS (2018-2022) and OOS (2023-2026)
   — 9 cells per variant
4. (b) − (a) per-year delta and (c) − (a) per-year delta
5. **2020 IS row highlighted** (the H1 diagnostic)
6. **2025 OOS row highlighted** (the H3 diagnostic)
7. Trade-set overlap matrix (3×3): Jaccard overlap of
   (entry_date, 종목코드) pairs across (a), (b), (c). Tells us
   how DIFFERENT the relative-flow trade pool is from the absolute
   trade pool.
8. **Cross-sectional std diagnostic**: per signal_date, compute
   `std_T` of `fnv_5` and `inv_5`. Save as `cross_sectional_std.csv`
   so we can see if z-score and median-diff diverge on small-std
   days as expected.

Save year breakdown as `signal_redesign_year_breakdown.csv`.

## Sanity / consistency checks

- Variant (a) must reproduce B002 numerically. Because B005's
  combined `trades.csv` adds a `variant` column, byte-identical
  comparison is not possible. Instead, Codex verifies that the
  rows of B005 `trades.csv` filtered to `variant ==
  "absolute_baseline"` match B002's `trades.csv` row-for-row on the
  shared columns (entry_date, signal_date, exit_date, 종목코드,
  entry_price, exit_price, exit_reason). And: B005's metrics.json
  `absolute_baseline` block matches B002's headline OOS net total
  return within 1e-9 (numerical equality, not approximate).
- Variants (b) and (c) must NOT use absolute-flow features in
  filter, ranking, or exit. Codex's strategy module asserts this
  by inspecting the function references.
- The cross-sectional median/std/z-score must be computed using
  ONLY data from signal_dates ≤ T. A unit test verifies no future
  rows leak into the moment computation.

## Universe / costs / dates (unchanged from B002)

- Universe: dynamic Top100, 거래대금 ≥ 5 billion KRW (20-day avg),
  exclude rows with `거래대금추정여부 = True`
- Costs: 1.5 / 20 / 5 bps (commission / tax-sell / slippage)
- IS: 2018-01-02 ~ 2022-12-30
- OOS: 2023-01-02 ~ 2026-05-04
- max_positions: 5
- Entry: T+1 시가 (KRX 09:00)
- Exit: rule-based (signal reversal, where the signal definition is
  the variant's alpha)

## Multiple-testing acknowledgment

Cumulative variant comparisons across this project: ~17 prior + 3
new (B005's a, b, c) = 20. (a) is a re-test of B002 baseline so it
adds no new comparison; the new comparisons are 2 (b vs baseline,
c vs baseline). The per-criterion thresholds in H1/H2/H3 are
intentionally stricter than B003's were, to compensate for
accumulated multiple-testing pressure.

We commit to: **B005 either Promotes a new alpha definition or
Kills the relative-flow hypothesis.** It does not introduce a new
patch on the absolute-flow signal. If B005 kills, the next ticket
is either candidate 2 (가속 + 가격 confirmation) or candidate 3
(다른 lookback window) from the B005 planning discussion, on a
fresh ticket with its own pre-registration.

## Codex implementation task

Read this ticket end-to-end. Read AGENTS.md, R001 review, and B004
review for role-architecture and signal-redesign context. Base
commit = latest `main`.

### Scope discipline (additive only)

Touch:
- `src/features/relative_flow.py` (NEW) — compute `fnv_5_z`,
  `inv_5_z`, `combined_flow_5_z` (z-score variant) and `fnv_5_rel`,
  `inv_5_rel`, `combined_flow_5_rel` (median-diff variant) per the
  pre-registered definitions. Universe membership for cross-sectional
  moments comes from existing universe-filter logic (read, do NOT
  modify). NaN handling per spec. Strict no-look-ahead (test).
- `src/roles/filters.py` — ADD two new functions:
  `filter_relative_flow_sign_both_positive_z` and
  `filter_relative_flow_sign_both_positive` (median-diff). Same
  signature pattern as the existing `filter_flow_sign_both_positive`.
- `src/roles/rankings.py` — ADD two new functions:
  `rank_by_combined_flow_5_z` and `rank_by_combined_flow_5_rel`.
  Same signature pattern as existing `rank_by_combined_flow_5`.
- `src/roles/exits.py` — ADD two new functions:
  `exit_signal_reversal_z(z_features)` and
  `exit_signal_reversal_rel(rel_features)`. Same signature pattern
  as existing `exit_signal_reversal`.

  **Engine-immutability trick**: the engine has columns `fnv_5` and
  `inv_5` hardcoded inside `_SignalExitLookup` (see
  `src/backtest/engine.py:818-833`). To avoid engine changes, the
  new exit roles must internally **rename their relative columns to
  `fnv_5` / `inv_5` before packaging into `signal_exit_features`**.
  The engine then sees identically-named columns containing
  variant-specific values (z-scores or median-differences), and the
  generic `≤ 0` reversal check works without modification. Example:

  ```python
  def exit_signal_reversal_z(z_features):
      df = z_features[["날짜", "종목코드", "fnv_5_z", "inv_5_z"]] \
              .rename(columns={"fnv_5_z": "fnv_5", "inv_5_z": "inv_5"})
      return {"holding": 5, "vol_stop_k": None,
              "vol_stop_atr_window": 20, "atr_features": None,
              "signal_exit_features": df.copy()}
  ```

  The same pattern applies to `exit_signal_reversal_rel`.
- `src/strategies/b005_relative_flow.py` (NEW) — orchestrates the
  3 variants. Each variant is a clean independent backtest run on
  the engine. Includes the consistency assertion that variants
  (b) and (c) do not reference any absolute-flow role function.
- `src/run_experiment.py` — add `experiment_id == "B005"` dispatch.
- `configs/backtests/b005.yaml` (NEW).
- `tests/test_relative_flow.py` (NEW) — feature timing tests
  (no look-ahead on cross-sectional moments), correctness on
  hand-crafted synthetic panel (small universe, known median/std,
  expected output rows), edge cases (|U(T)| < 30, std == 0).
- `tests/test_filter_relative_flow.py` (NEW)
- `tests/test_rank_relative_flow.py` (NEW)
- `tests/test_exit_relative_signal_reversal.py` (NEW)
- `tests/test_b005_strategy.py` (NEW) — orchestration test that
  variant (a) numerically matches B002 within tolerance, variants
  (b) and (c) produce non-trivial trade counts on a small synthetic
  panel.

**Do NOT touch**:
- `src/backtest/engine.py` — engine should not need ANY change.
  Verify this assertion before commit.
- Existing role functions (`filter_flow_sign_both_positive`,
  `trigger_immediate`, `trigger_freshness`, `trigger_acceleration`,
  `trigger_persistence_3d`, `rank_by_*` existing, `exit_*` existing).
- Existing strategy modules (a001-a004, b001-b004).
- Universe / calendar / panel loader logic.
- Existing tests must remain green (currently 125).

### Configuration file

`configs/backtests/b005.yaml`:

```yaml
experiment_id: B005
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
  max_positions: 5
trigger:
  type: immediate
exit:
  type: signal_reversal
variants:
  - absolute_baseline
  - relative_zscore
  - relative_median_diff
relative:
  cross_sectional_min_count: 30
costs:
  commission_bps: 1.5
  tax_bps_sell:   20.0
  slippage_bps:   5.0
cost_sensitivity_multipliers: [0.0, 1.0, 2.0, 3.0]
output_dir: reports/experiments/B005_relative_flow_signal_redesign
```

### Output files

Under `reports/experiments/B005_relative_flow_signal_redesign/`:

- `config.yaml`
- `metrics.json` — top-level keys `absolute_baseline`,
  `relative_zscore`, `relative_median_diff`, plus `cost_0_*` keys
- `trades.csv` — combined with `variant` column
- `signals.csv` — combined with `variant` column
- `equity_curve.csv` — wide format: `date, absolute_baseline_value,
  relative_zscore_value, relative_median_diff_value`
- `signal_redesign_year_breakdown.csv` — per-year per-variant net
  total return; (b)−(a) and (c)−(a) deltas as columns; **2020 and
  2025 rows must be sortable / identifiable for the H1, H3 checks**
- `cross_sectional_std.csv` — per signal_date, the cross-sectional
  std of `fnv_5` and `inv_5` over the universe
- `trigger_overlap_matrix.csv` — 3×3 Jaccard overlap of trade sets
- `cost_sensitivity.csv` — sensitivity for the best-OOS variant
  (descriptive only, not for promote)
- `report.md`

### Tests

Existing 125 tests must remain green. New tests bring suite to
~135+.

### Order of work
Commit (Claude commits) after each green-test boundary.

1. Add `relative_flow.py` features + tests (no look-ahead, edge
   cases, correctness on hand-crafted synthetic data)
2. Add new filter / ranking / exit role functions + unit tests
3. Add B005 strategy module + dispatcher + config
4. Run B005 real-panel
5. Verify (a) reproduces B002 within tolerance; verify engine.py
   was NOT touched (`git diff src/backtest/engine.py` returns empty)

### Completion criteria
- pytest fully green
- `python -m src.run_experiment --config configs/backtests/b005.yaml`
  produces every required output
- All 3 variants reported side-by-side in metrics.json
- (a) numerically matches B002 within 1 % on OOS net (sanity that
  the carrier reproduction is faithful)
- engine.py untouched (`git diff src/backtest/engine.py` empty)
- Final assistant message reports the verdict-relevant numbers:
  - 2020 IS net for (a), (b), (c) — H1 check
  - OOS net for (a), (b), (c) — H2 check
  - 2025 OOS net for (a), (b), (c) — H3 check
  - IS overall net for (a), (b), (c)
  - Trade-set Jaccard overlap (b)↔(a) and (c)↔(a)

### Out of scope for B005
- Trigger variation (T3 stays out — separate ticket if needed)
- Regime gate (B004 verdict was kill the gate-as-savior thesis)
- Alternative lookback windows (5d only)
- New data sources
- Engine changes
- Combinations with B003 / B004 candidates (single-hypothesis ticket)

## Result summary
DO NOT FILL until backtest is complete.

## Claude review
DO NOT FILL until result files are read.
