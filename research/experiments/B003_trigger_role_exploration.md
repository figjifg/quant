# B003 — Trigger-role exploration on B002 carrier

## Status
planned

## Role under test
**Trigger** — single role varied across this ticket.

## Strategy composition (other roles fixed)
| Role | Carrier (fixed) |
|---|---|
| Filter | `filter_flow_sign_both_positive` — `(fnv_5 > 0) AND (inv_5 > 0)` |
| **Trigger** | **Variable — 4 pre-registered candidates** |
| Ranking | `rank_by_combined_flow_5` |
| Exit | `exit_signal_reversal` — `(fnv_5 ≤ 0) OR (inv_5 ≤ 0)` (B002 default) |

Universe, costs, max_positions, IS/OOS boundary all unchanged from the
running A/B family conventions.

## Purpose (alpha-level, descriptive)
B002 exposed that the 5-day flow signal's raw alpha is ~+1.66 (cost-0
OOS) over 3.4 years but ~60 % is eaten by transaction costs at the high
turnover of "enter on every filter-pass day, exit on signal reversal."

A trigger introduces a **second condition on top of filter** to refine
when entry actually fires. The right trigger could cut redundant
re-entries (same ticker repeatedly entering while its filter stays
true), or focus entries on the strongest moments, recovering more of
the raw alpha after costs.

B003 is **descriptive**, not a promote vehicle. Four trigger candidates
are evaluated side-by-side. The single most promising one (if any
clear winner emerges) must be re-tested in a **fresh single-point
ticket** before being adopted as a new carrier.

## Hypothesis (descriptive)
At least one of the four trigger variants reduces OOS trade_count
relative to T1 (immediate) by ≥ 30 % while either improving or
maintaining OOS cost-0 net total return. If no candidate satisfies
both, the trigger role doesn't carry actionable information at this
window.

## Pre-registered trigger candidates

### T1 — `trigger_immediate` (control, current B002 behavior)
Filter pass → entry candidate. No additional condition.

### T2 — `trigger_freshness`
Fire **only on the first signal_date** where the filter newly passes
for a ticker. That is, if `filter(T) = True` and `filter(T-1) = False`
(or T-1 absent for that ticker), fire. Subsequent days while filter
stays True do NOT re-fire for the same ticker. Once the filter goes
False and then True again, that's a new "first" and fires.

**Intent**: capture the **transition moment** when foreign+institution
flow first crosses into positive territory. Avoid re-entering the same
ticker repeatedly during a sustained positive run.

### T3 — `trigger_acceleration`
Fire when filter passes AND today's daily flow ratio (1-day, NOT 5-day)
is stronger than the 5-day average. Specifically:

```
combined_flow_1(T) > combined_flow_5(T) / 5
```

where `combined_flow_1(T) = (외국인순매수금액(T) + 기관순매수금액(T)) / 거래대금(T)`
is the single-day ratio on signal_date T.

**Intent**: capture the **acceleration moment** when today's intensity
exceeds the recent-average intensity. Avoid entering on days when the
filter is true but the inflow is just steady or decelerating.

### T4 — `trigger_persistence_3d`
Fire when filter has passed for **3 consecutive signal_dates** on the
same ticker. That is, `filter(T) = filter(T-1) = filter(T-2) = True`,
and `filter(T-3) = False` (or the chain hasn't yet hit 3) the day
before. Subsequent days while the run is sustained do NOT re-fire.

**Intent**: capture the **sustained trend** confirmation. Avoid
1-2 day flash signals that may not be meaningful. By definition,
fewer entries than T1 and T2.

## Entry / exit / universe / costs (unchanged from B002)
- Entry: T+1 시가 (KRX 09:00 verified)
- Exit: signal_reversal — `(fnv_5(d-1) ≤ 0) OR (inv_5(d-1) ≤ 0)` → next-day 시가
- Universe: A 가족 default (dynamic Top100, 거래대금 50억, 거래대금추정여부 False)
- max_positions: 5
- Costs: 1.5 / 20 / 5 bps
- IS: 2018-01-02 ~ 2022-12-30, OOS: 2023-01-02 ~ 2026-05-04

## Data assumptions
**No new external data.** Same two panels as A 가족.

**New feature derived**: `combined_flow_1` (1-day combined flow ratio)
needs to be added to `src/features/flow_ratios.py`. It's a simple
non-rolling version of `combined_flow_5`. Used by T3 only.

## Reportable metrics per candidate

For each of T1/T2/T3/T4 (head-to-head, same universe and exit):

1. **OOS net total_return**
2. **OOS hit_rate**
3. **OOS trade_count**
4. **OOS average holding period (trading days)**
5. **OOS cost-0 net total_return** (the raw alpha number)
6. **OOS cost_paid_total**
7. **OOS turnover**
8. **OOS exit_reason breakdown** (signal_reversal / fallback / period_end)
9. **Per-trigger IS metrics 1-7** for completeness
10. **Trade-set overlap matrix**: for each pair (Ti, Tj), the fraction
    of (entry_date, 종목코드) pairs that appear in both vs only one.
    This tells us how DIFFERENT the trade sets are — important for
    judging whether any improvement is meaningful or just noise.

## Pre-registered interpretation rules
- B003 is **description only**. No verdict of promote/kill on any
  trigger candidate. The reviewer (Claude/user) describes the observed
  pattern.
- If one trigger clearly dominates on multiple OOS metrics (e.g., higher
  cost-0 net AND lower trade_count AND comparable hit_rate), that
  candidate becomes the proposed carrier for **B004**, a single-point
  promote ticket. B004 will rerun that single trigger with everything
  else identical, and apply standard 5-criterion promote/kill logic.
- If no candidate clearly dominates, conclude "trigger role does not
  carry actionable information at this window" and move on (e.g., to
  filter or ranking exploration).
- **Do not promote any trigger directly from this ticket.** That would
  be multiple-testing inflation.

## Kill criteria (minimal — only for clearly broken outcomes)
- pytest regression on existing 104-test suite
- Any trigger candidate produces OOS trade_count = 0 (signal definition
  broken)
- The new `combined_flow_1` feature has a look-ahead bug (caught by
  feature-timing tests)

## Codex implementation task

Read this ticket end-to-end. Read AGENTS.md and the R001 review for
role structure context. Base commit = latest `main`.

### Scope discipline (additive only)

Touch:
- `src/features/flow_ratios.py` — add `combined_flow_1` column.
  Computed per (종목코드, 날짜) as
  `(외국인순매수금액추정(T) + 기관순매수금액추정(T)) / 거래대금추정(T)`.
  If 거래대금추정 is ≤ 0 or NaN, the column is NaN. Timing: strictly
  uses panel rows with `날짜 == T` only — no look-ahead.
- `src/roles/triggers.py` — add three new functions:
  - `trigger_freshness(filtered_features, full_features) -> DataFrame`
  - `trigger_acceleration(filtered_features, full_features) -> DataFrame`
  - `trigger_persistence_3d(filtered_features, full_features) -> DataFrame`

  All three take a filtered_features DataFrame (output of
  `filter_flow_sign_both_positive`) and the full flow_features (for
  context like the previous-day filter state or combined_flow_1).
  All three return a subset of filtered_features rows where the
  trigger fires.

- `src/strategies/b003_trigger_exploration.py` (NEW) — a single setup
  function that returns the four candidate candidate-frames + engine
  kwargs, ready to run all four through `run_candidate_backtest`.

- `src/run_experiment.py` — add `experiment_id == "B003"` dispatch.
  Runs four trigger variants on the same period, plus B0-B3 baselines
  (carried), plus cost sensitivity on the **best-looking variant**
  selected by OOS net total return (DESCRIPTIVE selection only; no
  promotion). Always include cost-0 metric blocks for all four variants
  to enable raw-alpha comparison.

- `configs/backtests/b003.yaml` (NEW).

- `tests/test_trigger_roles.py` (NEW) — unit tests for the three new
  triggers on hand-crafted synthetic panels. At minimum:
  - `trigger_freshness` fires only on transition days (False→True)
  - `trigger_acceleration` fires only when 1-day > 5-day average
  - `trigger_persistence_3d` requires 3 consecutive True days
  - Each trigger's prior-row safety (no look-ahead) regression
- `tests/test_flow_ratios.py` (existing or new) — add a case for
  `combined_flow_1` formula correctness and NaN handling.

**Do NOT touch**: engine, baselines, universe, calendar, costs, metrics,
report, market_flow, market_gate, the existing role functions
(filters/rankings/exits), and all existing strategy modules. Backwards
compatibility unaffected.

### Configuration file

`configs/backtests/b003.yaml`:

```yaml
experiment_id: B003
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
exit:
  type: signal_reversal
trigger:
  candidates: [immediate, freshness, acceleration, persistence_3d]
costs:
  commission_bps: 1.5
  tax_bps_sell:   20.0
  slippage_bps:   5.0
cost_sensitivity_multipliers: [0.0, 1.0, 2.0, 3.0]
output_dir: reports/experiments/B003_trigger_role_exploration
```

No `holding` key (signal_reversal exit). `trigger.candidates` is a
fixed list of the 4 pre-registered candidates. Strict validation:
the list must equal `[immediate, freshness, acceleration, persistence_3d]`
exactly — no reordering, no additions, no deletions in this ticket.

### Runs to produce

- **T1 (immediate)**: B002 carrier exactly. Should reproduce B002 OOS
  numbers within numerical tolerance — sanity check.
- **T2 (freshness)**, **T3 (acceleration)**, **T4 (persistence_3d)**.
- **B0_cash, B1, B2, B3**: context (carried).
- **cost_sensitivity**: applied to whichever T-variant has the highest
  OOS net total return (for descriptive cost behavior only; not for
  promotion).
- **cost_0** blocks for all four T-variants.

### Output files

Under `reports/experiments/B003_trigger_role_exploration/`:

- `config.yaml`
- `metrics.json` — top-level keys `T1_immediate`, `T2_freshness`,
  `T3_acceleration`, `T4_persistence_3d`, `B0`, `B1`, `B2`, `B3`,
  `cost_0_T1`, `cost_0_T2`, `cost_0_T3`, `cost_0_T4`
- `trades.csv` — combined: one big file with a column
  `trigger_variant ∈ {T1, T2, T3, T4}` so the rows can be split per
  variant for analysis
- `signals.csv` — same shape, with `trigger_variant` column
- `equity_curve.csv` — one wide file: columns `date, T1_net_value,
  T2_net_value, T3_net_value, T4_net_value, T1_cash, ...` etc.
- `cost_sensitivity.csv`
- `report.md`
- **`trigger_overlap_matrix.csv`** (new): 4×4 matrix of trade-set
  overlap fractions (intersection / union of (entry_date, 종목코드)
  pairs)

### Tests

Existing 104 tests must remain green. New `test_trigger_roles.py`
brings ~5 more → ~109. New `test_flow_ratios.py` case brings ~1 more.

### Order of work
Commit (Claude commits) after each green-test boundary.

1. Add `combined_flow_1` feature + test.
2. Add three new triggers + tests.
3. Add B003 strategy module + CLI dispatch + config.
4. Run B003 real-panel.

### Completion criteria
- pytest fully green
- `python -m src.run_experiment --config configs/backtests/b003.yaml`
  produces every required output
- T1 metrics within 1 % numerical tolerance of B002 headline (sanity
  check that the carrier reproduction is faithful)
- Final assistant message reports OOS metrics 1-9 (from the
  Reportable metrics section above) for all four variants side-by-side

### Out of scope for B003
- Filter, ranking, or exit role variations
- Other trigger candidates (only the 4 pre-registered)
- New data sources
- Promote/kill verdict on any specific trigger
- Engine changes

## Result summary
DO NOT FILL until backtest is complete.

## Claude review
DO NOT FILL until result files are read.
