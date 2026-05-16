# B006 — T3 acceleration trigger promote ticket

## Status
planned

## What is being tested
**One single trigger candidate (T3 acceleration) on the B002
absolute carrier**, with strict 5-criterion promote / kill /
inconclusive logic.

This is a **single-point promote ticket**, NOT a descriptive
exploration. T3 was identified in B003 as the only trigger that
beat the B002 (T1 immediate) baseline on both OOS net and OOS
cost-0. B003 was descriptive (4-way) and explicitly deferred
promotion to a fresh single-point ticket — that is B006.

## Strategy composition (single variant)

| Layer | Carrier |
|---|---|
| Filter | `filter_flow_sign_both_positive` (B002 default) |
| **Trigger** | **`trigger_acceleration` (T3) — under test** |
| Ranking | `rank_by_combined_flow_5` (B002 default) |
| Exit | `exit_signal_reversal` (B002 default) |

T3 definition (frozen as in B003): on a filter-passing signal_date T,
fire entry iff `combined_flow_1(T) > combined_flow_5(T) / 5`. That
is, today's 1-day intensity exceeds the 5-day average intensity.

Universe, costs, max_positions, IS/OOS boundary, panels — all
unchanged from B002.

## Baseline for comparison
**B002 carrier (T1 immediate)**, run side-by-side in this same
ticket. Both runs use the same data, same engine, same period —
only the trigger differs.

## Why a single-point promote ticket now

B003 ran 4 trigger candidates and concluded T3 was the standout but
explicitly avoided promoting from a 4-way descriptive comparison
("multiple-testing inflation"). B005 ran 3 alpha variants and
returned inconclusive on the relative-flow hypothesis, leaving
the absolute carrier intact. The natural next step under our
pre-registered discipline is to validate (or kill) T3 as the new
trigger carrier on the absolute B002 alpha, using strict 5-criterion
promote logic.

## Hypothesis (pre-registered)

T3's `combined_flow_1 > combined_flow_5 / 5` condition isolates
days when foreign+institution buying is **accelerating** relative
to the recent 5-day average. The hypothesis is that acceleration
days carry more information than steady-state filter-passing days,
producing a higher cost-0 alpha (more raw signal) AND a lower
turnover (fewer fired entries), both of which would translate into
better net-of-cost OOS performance.

The B003 OOS evidence pointed in this direction:
- OOS net: T1 +0.641, T3 +0.780 (Δ +0.139)
- OOS cost-0: T1 +1.660, T3 +1.875 (Δ +0.215)
- Trades: T1 730, T3 724 (Δ −6, marginal turnover reduction)
- Trade overlap (T3 vs T1): Jaccard 0.617 (T3 is largely a subset
  of T1 with the worst trades filtered out)

B006 re-validates this under formal promote rules and adds the
IS-side and per-OOS-year checks that B003 did not gate on.

## Pre-registered promote criteria (ALL required)

| # | Criterion | Threshold |
|---|---|---:|
| 1 | OOS net delta (T3 − T1) | ≥ +0.10 |
| 2 | OOS cost-0 net (T3) | ≥ T1 cost-0 OOS |
| 3 | Trade count (T3) | < T1 (turnover actually reduced) |
| 4 | T3 wins T1 in OOS years | ≥ 2 of 4 (2023, 2024, 2025, 2026) |
| 5 | IS net (T3) | ≥ IS net (T1) |

Criterion 5 is the new contribution beyond B003: T3 must not be
worse in IS. Since B003 only reported OOS T3 numbers in the
descriptive comparison, B006 surfaces the IS picture and gates
on it.

## Pre-registered kill criteria (ANY triggers)

- OOS net (T3) < OOS net (T1) by ≥ 0.05 — T3 actually worse net
- OR OOS cost-0 (T3) < OOS cost-0 (T1) by ≥ 0.10 — T3 hurts the
  raw alpha (turnover reduction comes at signal-quality cost)

## Pre-registered inconclusive criteria

- T3 OOS uplift is concentrated in a single year (e.g., 2025
  delta > 0.10 but 2023, 2024, 2026 deltas all near zero)
- Cost sensitivity flips the result at 3× costs
- Mixed promote-criteria pattern not falling cleanly into promote
  or kill

If inconclusive, the next ticket explores either Option B (relative
+ T3 combination, descriptive) or Option D (older data verification),
per B005 review's recommendations. T3 is NOT silently adopted as
carrier without satisfying promote criteria.

## Reproducibility check

Because T3 was already implemented in B003 (`src/roles/triggers.py:
trigger_acceleration` is the same function), the B006 T3 metrics
must reproduce the B003 T3_acceleration metrics byte-for-byte where
formats match. Specifically:

- B006 trades for variant `t3_acceleration` filtered by trigger ==
  `acceleration` must match B003 `trades_acceleration.csv`
  row-for-row on shared columns
- B006 metrics.json `t3_acceleration` OOS net total return must
  match B003 metrics.json `T3_acceleration` `oos.total_return`
  within 1e-9 (numerical equality)
- Similarly for IS and cost-0

If reproducibility fails, the B006 implementation has unintended
divergence from B003 and Codex must stop and report.

## Reportable metrics

For both T1 baseline and T3 candidate:

1. IS net total return, hit rate, trade count, cost-0 net
2. OOS net total return, hit rate, trade count, cost-0 net
3. **Per-year net total return** for IS (2018-2022) and OOS
   (2023-2026) — 9 cells per variant
4. (T3 − T1) per-year delta column
5. **OOS year-wins count** — number of OOS years where (T3 − T1) > 0,
   for criterion 4
6. Cost sensitivity for T3 at 0×, 1×, 2×, 3× — for inconclusive check

Save year breakdown as `t3_promote_year_breakdown.csv`.

## Universe / costs / dates (unchanged from B002)

- Universe: dynamic Top100, 거래대금 ≥ 5 billion KRW (20-day avg),
  exclude rows with `거래대금추정여부 = True`
- Costs: 1.5 / 20 / 5 bps (commission / tax-sell / slippage)
- IS: 2018-01-02 ~ 2022-12-30
- OOS: 2023-01-02 ~ 2026-05-04
- max_positions: 5
- Entry: T+1 시가 (KRX 09:00)
- Exit: signal reversal

## Multiple-testing acknowledgment

Cumulative variant comparisons across this project: ~19 prior + 1
new (T3 vs T1). The single-point design intentionally minimizes
new comparison count. The 5-criterion promote bar is calibrated to
B003's observed numbers (OOS Δ +0.139) — a +0.10 threshold means
T3 must hold most of its B003 OOS lead under formal verification,
not magnify it.

We commit to: **B006 either Promotes T3 as the new trigger carrier
or returns inconclusive**. No silent adoption. No bar-lowering after
seeing results.

## Codex implementation task

Read this ticket end-to-end. Read AGENTS.md, R001 review, B003
review (T3 origin), B005 review (recent strategic context). Base
commit = latest `main`.

### Scope discipline (additive only)

Touch:
- `src/strategies/b006_t3_promote.py` (NEW) — orchestrates two
  runs: T1 baseline (B002 carrier exact reproduction) and T3
  candidate. Imports `trigger_immediate` and `trigger_acceleration`
  from `src/roles/triggers.py` (already exist; do NOT modify).
- `src/run_experiment.py` — add `experiment_id == "B006"` dispatch.
- `configs/backtests/b006.yaml` (NEW).
- `tests/test_b006_strategy.py` (NEW) — sanity test that B006
  T3 numbers match B003 T3 numbers within tolerance.

**Do NOT touch**:
- `src/backtest/engine.py` — should not need any change. Verify
  with `git diff src/backtest/engine.py` returning empty before
  commit.
- Existing role functions (no new triggers / filters / rankings /
  exits added in this ticket).
- Existing strategy modules (a001-a004, b001-b005).
- Existing tests must remain green (currently 140).

### Configuration file

`configs/backtests/b006.yaml`:

```yaml
experiment_id: B006
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
filter:
  type: flow_sign_both_positive
ranking:
  type: combined_flow_5
exit:
  type: signal_reversal
variants:
  - t1_baseline
  - t3_acceleration
costs:
  commission_bps: 1.5
  tax_bps_sell:   20.0
  slippage_bps:   5.0
cost_sensitivity_multipliers: [0.0, 1.0, 2.0, 3.0]
output_dir: reports/experiments/B006_t3_acceleration_promote
```

### Output files

Under `reports/experiments/B006_t3_acceleration_promote/`:

- `config.yaml`
- `metrics.json` — top-level keys `t1_baseline`, `t3_acceleration`,
  plus `cost_0_*` keys
- `trades.csv` — combined with `variant` column
- `signals.csv` — combined with `variant` column
- `equity_curve.csv` — wide format: `date, t1_baseline_value,
  t3_acceleration_value`
- `t3_promote_year_breakdown.csv` — per-year per-variant net total
  return, (T3 − T1) delta column, win-flag column
- `cost_sensitivity.csv` — for T3 only (since promote candidate)
- `report.md`

### Order of work

Commit (Claude commits) after each green-test boundary.

1. Add B006 strategy module + dispatcher + config
2. Add B006 strategy test (verifies T3 numbers reproduce B003 T3
   within tolerance)
3. Run B006 real-panel
4. Verify reproducibility against B003 T3 outputs (md5sum / row-
   match where formats align)
5. Verify engine.py untouched

### Completion criteria

- pytest fully green (currently 140; should grow to ~142+)
- `python -m src.run_experiment --config configs/backtests/b006.yaml`
  produces every required output
- B006 T3 metrics match B003 T3 metrics within tolerance (numerical
  equality on shared metric keys)
- T1 baseline in B006 matches B002 within tolerance (since B002 is
  T1 + same other roles)
- engine.py untouched (`git diff src/backtest/engine.py` empty)
- Final assistant message reports the verdict-relevant numbers in
  this exact format:
  - OOS net: T1=__, T3=__, delta=__
  - OOS cost-0: T1=__, T3=__, delta=__
  - IS net: T1=__, T3=__, delta=__
  - Trade count OOS: T1=__, T3=__
  - OOS year-wins (T3 > T1) count: __ of 4
  - 2025 OOS delta (T3-T1): __ — for single-year inconclusive check

### Out of scope for B006

- Any new alpha definition
- Any new role function (T3 already exists)
- Engine changes
- Combinations with relative-flow signal (B005)
- Combinations with regime gate (B004)
- Other trigger candidates (T2, T4 already explored in B003)
- New data sources

## Result summary
DO NOT FILL until backtest is complete.

## Claude review
DO NOT FILL until result files are read.
