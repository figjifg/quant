# B007 — Filter-role exploration on T3 carrier

## Status
planned

## Role under test
**Filter** — single role varied across this ticket.

## Strategy composition (other roles fixed at B006 promoted carrier)

| Layer | Carrier (fixed) |
|---|---|
| **Filter** | **Variable — 3 pre-registered candidates** |
| Trigger | `trigger_acceleration` (T3) — B006 promoted carrier |
| Ranking | `rank_by_combined_flow_5` |
| Exit | `exit_signal_reversal` |

Universe, costs, max_positions, IS/OOS boundary, panels — all
unchanged from the new B006 carrier.

## Purpose (alpha-level, descriptive)

The filter is the role we have explored least — every prior
experiment used `filter_flow_sign_both_positive` ((fnv_5 > 0) AND
(inv_5 > 0)) as the single entry-eligibility condition. B005
revealed that relative-flow has real (if contextual) value for
fixing V-recovery, but as a pure alpha replacement it lost too much
spike-capture and got destroyed by costs. B007 brings relative-flow
back into the design — but as a **filter on top of the absolute
alpha**, not as an alpha replacement (F2). The other variant probes
whether single-day spikes vs sustained 4-of-5-day buying matters
for entry quality (F3).

This is descriptive, NOT promotional. Three candidates compared
side by side. The single most differentiated winner (if any) becomes
the proposed carrier for B008 single-point promote ticket.

(An earlier draft included a "combined_flow_5 > 0 only" candidate;
removed because it would enter trades the absolute exit immediately
fires on, making the comparison conceptually muddled — that's an
alpha redesign disguised as a filter, not a true filter test.)

## Pre-registered filter candidates

### F1 — `filter_flow_sign_both_positive` (control, current carrier)
`(fnv_5 > 0) AND (inv_5 > 0)`. No change vs B006.

### F2 — `filter_relative_AND_absolute_positive` (NEW)
`(fnv_5 > 0) AND (inv_5 > 0) AND (fnv_5_rel > 0) AND (inv_5_rel > 0)`
where `fnv_5_rel` and `inv_5_rel` are the median-difference relative
features built in B005 (`src/features/relative_flow.py`).

**Intent**: Add relative-flow as an **additional gate on top of**
the absolute alpha. The alpha definition itself stays absolute (so
the exit_signal_reversal continues to use absolute fnv_5/inv_5),
but entries fire only when the stock is also above the cross-
sectional median. This is the "narrowed entry universe" framing
(distinct from B005 which replaced the alpha entirely). Tests
whether the V-recovery mechanism from B005 can be retained without
sacrificing spike-capture.

### F3 — `filter_persistence_4_of_5` (NEW)
F1 conditions AND persistence requirement:
`(fnv_5 > 0) AND (inv_5 > 0) AND (count(combined_flow_1 > 0 over [T-4, T]) ≥ 4)`.

Why F1 conditions are required: the exit_signal_reversal uses
absolute `fnv_5` / `inv_5`. If F3 allowed entry where the 5-day
cumulative is negative (just because daily persistence is high),
the exit would trigger immediately on T+1. So F3 is **F1 + extra
persistence gate**, making F3 a strict subset of F1's trade pool.

`combined_flow_1` was added in B003 (`src/features/flow_ratios.py`).

**Intent**: Test whether persistent buying days carry more signal
than short-burst entries. F1 + acceleration trigger (T3) currently
allows entry when 5-day cumulative is positive AND today's intensity
exceeds the 5-day average — but that 5-day cumulative could be
driven by 1-2 strong days. F3 additionally requires sustained
buying (4 of 5 days). Tests "sustained vs spike" entry quality.

## Hypothesis (descriptive)

At least one of F2, F3 produces:
- OOS net total return ≥ F1 OOS net + 0.10
- AND OOS cost-0 net ≥ F1 OOS cost-0 (alpha not destroyed)
- AND OOS year-wins (variant > F1) ≥ 2 of 4 (not single-year)

If at least one variant satisfies all three, that becomes the
B008 single-point promote candidate.

If no variant satisfies all three, conclude that the filter role
on the T3 carrier doesn't carry strong differentiating
information at this signal definition, and move to ranking-role
exploration (B008-or-later).

## Pre-registered interpretation rules

- B007 is **descriptive only**. No promote/kill verdict on any
  filter candidate.
- A "B008 promote candidate" recommendation requires the three
  conditions above to hold for exactly one variant. If multiple
  variants tie on the conditions, the winner is whichever has the
  larger absolute OOS net delta vs F1.
- "Inconclusive" / "no recommendation" is an acceptable B007
  outcome and triggers B008 = a different role exploration, not
  a forced promote on the best-of-bad candidates.

## Pre-registered kill criteria (only for clearly broken outcomes)
- pytest regression on existing 142-test suite
- Any variant produces zero trades in IS or OOS
- F1 fails to reproduce B006 T3 metrics byte-identically (would
  signal an unintended divergence in the B007 strategy module)

## Reportable metrics per candidate

For each of F1/F2/F3 (head-to-head, same period):

1. IS net total return, hit rate, trade count, cost-0 net
2. OOS net total return, hit rate, trade count, cost-0 net
3. **Per-year net total return** for IS (2018-2022) and OOS
   (2023-2026) — 9 cells per variant
4. (F* − F1) per-year delta tables
5. **2020 IS row highlighted** (F2 V-recovery fix check)
6. **2025 OOS row highlighted** (spike-capture preservation check)
7. **Trade-set Jaccard overlap matrix (4×4)** — how DIFFERENT each
   variant's trade pool is from F1 and from each other
8. Cost sensitivity for the best OOS variant (descriptive only)

Save year breakdown as `filter_exploration_year_breakdown.csv`.
Save overlap matrix as `filter_overlap_matrix.csv`.

## Reproducibility check

F1 in B007 must reproduce B006 T3 metrics numerically (within 1e-9
tolerance) on shared metric keys. Specifically:
- B007 metrics.json `f1_baseline` IS / OOS / cost-0 metrics match
  B006 metrics.json `t3_acceleration` corresponding keys
- B007 trades for variant `f1_baseline` match B006 trades for
  variant `t3_acceleration` row-for-row on shared columns

If reproducibility fails, B007 strategy module has unintended
divergence and Codex must stop and report.

## Universe / costs / dates (unchanged from B006 carrier)

- Universe: dynamic Top100, 거래대금 ≥ 5 billion KRW (20-day avg),
  exclude rows with `거래대금추정여부 = True`
- Costs: 1.5 / 20 / 5 bps (commission / tax-sell / slippage)
- IS: 2018-01-02 ~ 2022-12-30
- OOS: 2023-01-02 ~ 2026-05-04
- max_positions: 5
- Entry: T+1 시가 (KRX 09:00)
- Exit: signal reversal on absolute fnv_5 / inv_5

## Multiple-testing acknowledgment

Cumulative variant comparisons across this project: ~21 prior + 3
new (F2, F3 vs F1 baseline). F1 is a B006 reproduction so adds
no new comparison. Any winner-recommendation from B007 must go
through a fresh B008 single-point promote ticket — same pattern as
B003 → B006.

We commit to: **B007 either Identifies a clear B008 candidate
(satisfying all three descriptive conditions) or returns no-
recommendation**. Best-of-bad cherry-picking is NOT allowed.

## Codex implementation task

Read this ticket end-to-end. Read AGENTS.md, R001 review, B003
review (filter pattern), B005 review (relative-flow features),
B006 review (T3 promote — current carrier definition). Base
commit = latest `main`.

### Scope discipline (additive only)

Touch:
- `src/roles/filters.py` — ADD three new functions:
  - `filter_relative_AND_absolute_positive(features, relative_features)`:
    requires (fnv_5 > 0) AND (inv_5 > 0) AND (fnv_5_rel > 0) AND
    (inv_5_rel > 0). Reads from `src/features/relative_flow.py`
    output (median-diff variant, NOT z-score).
  - `filter_persistence_4_of_5(features, daily_flow_features)`:
    requires `(fnv_5 > 0) AND (inv_5 > 0) AND (count(combined_flow_1 > 0
    over rolling [T-4, T]) ≥ 4)` per ticker. F3 is F1 + extra
    persistence gate, so it's a strict subset of F1's pool.
    Strict no-look-ahead: only days ≤ T enter the persistence count.

  Existing `filter_flow_sign_both_positive` (F1) NOT modified.

- `src/strategies/b007_filter_exploration.py` (NEW) — orchestrates
  3 variants (F1, F2, F3) on the same period, sharing the T3
  trigger + combined_flow_5 ranking + signal_reversal exit. Each
  variant is a clean independent backtest run.

- `src/run_experiment.py` — add `experiment_id == "B007"` dispatch.

- `configs/backtests/b007.yaml` (NEW).

- `tests/test_filter_relative_AND_absolute.py` (NEW)
- `tests/test_filter_persistence_4_of_5.py` (NEW)
- `tests/test_b007_strategy.py` (NEW) — orchestration test that F1
  reproduces B006 T3 metrics within tolerance, all variants produce
  non-trivial trade counts.

**Do NOT touch**:
- `src/backtest/engine.py` — should not need any change. Verify
  with `git diff src/backtest/engine.py` returning empty before
  commit.
- Existing role functions other than additions to filters.py.
- Existing strategy modules (a001-a004, b001-b006).
- Existing tests must remain green (currently 142).
- `src/features/flow_ratios.py` and `src/features/relative_flow.py`
  must NOT be modified (read-only; reuse existing features).

### Configuration file

`configs/backtests/b007.yaml`:

```yaml
experiment_id: B007
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
  type: acceleration
ranking:
  type: combined_flow_5
exit:
  type: signal_reversal
filter:
  candidates:
    - flow_sign_both_positive          # F1 (control)
    - relative_AND_absolute_positive   # F2
    - persistence_4_of_5               # F3
relative:
  cross_sectional_min_count: 30
costs:
  commission_bps: 1.5
  tax_bps_sell:   20.0
  slippage_bps:   5.0
cost_sensitivity_multipliers: [0.0, 1.0, 2.0, 3.0]
output_dir: reports/experiments/B007_filter_role_exploration
```

Strict validation: the candidates list must equal exactly
`[flow_sign_both_positive, relative_AND_absolute_positive,
persistence_4_of_5]` — no
reordering, no additions, no deletions.

### Output files

Under `reports/experiments/B007_filter_role_exploration/`:

- `config.yaml`
- `metrics.json` — top-level keys `f1_baseline`,
  `f2_relative_and_absolute`, `f3_persistence_4_of_5`, plus
  `cost_0_*` keys for each
- `trades.csv` — combined with `variant` column ∈ {F1, F2, F3}
- `signals.csv` — combined with `variant` column
- `equity_curve.csv` — wide format: `date, F1_value, F2_value,
  F3_value`
- `filter_exploration_year_breakdown.csv` — per-year per-variant
  net total return; (F* − F1) deltas as columns; 2020 IS and 2025
  OOS rows must be sortable / identifiable
- `filter_overlap_matrix.csv` — 4×4 Jaccard overlap matrix of trade
  sets ((entry_date, 종목코드) pairs)
- `cost_sensitivity.csv` — for the best-OOS variant only
- `report.md`

### Tests

Existing 142 tests must remain green. New tests bring suite to
~148+.

### Order of work

Commit (Claude commits) after each green-test boundary.

1. Add 3 new filter functions + per-filter unit tests
2. Add B007 strategy module + dispatcher + config
3. Add B007 strategy reproducibility test (F1 == B006 T3)
4. Run B007 real-panel
5. Verify engine.py untouched and reproducibility passes

### Completion criteria

- pytest fully green (currently 142; should grow to ~148+)
- `python -m src.run_experiment --config configs/backtests/b007.yaml`
  produces every required output
- All 4 variants reported side-by-side in metrics.json
- F1 metrics match B006 T3 within 1e-9 numerical equality on
  shared metric keys
- F1 trades match B006 T3 trades row-for-row on shared columns
- engine.py untouched (`git diff src/backtest/engine.py` empty)
- Final assistant message reports the verdict-relevant numbers in
  this exact format:
  - For each of F1/F2/F3:
    - IS net, OOS net, OOS cost-0
    - Trade count IS, OOS
    - 2020 IS net (V-recovery diagnostic)
    - 2025 OOS net (spike-capture diagnostic)
  - For each of F2/F3 (deltas vs F1):
    - OOS net delta
    - OOS cost-0 delta
    - OOS year-wins count (out of 4)
  - Trade-set Jaccard overlap matrix (4×4)

### Out of scope for B007

- Trigger / ranking / exit variation (those are separate single-role
  tickets later)
- Other filter candidates beyond the 3 pre-registered (no scanning,
  no exploration of variants like persistence_3_of_5 etc.)
- New data sources
- Engine changes
- Promote/kill verdict on any specific filter
- Z-score variant of relative flow (median-diff is the carrier; B005
  showed both variants behave similarly)
- Combinations with regime gate (B004 verdict killed gate-as-savior)

## Result summary
DO NOT FILL until backtest is complete.

## Claude review
DO NOT FILL until result files are read.
