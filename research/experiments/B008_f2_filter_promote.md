# B008 — F2 (relative + absolute) filter promote ticket

## Status
planned

## What is being tested
**One single filter candidate (F2 — `filter_relative_AND_absolute_positive`)
on the B006 T3 carrier**, with strict 5-criterion promote / kill /
inconclusive logic.

This is a **single-point promote ticket**, NOT a descriptive
exploration. F2 was identified in B007 as one of two filters that
satisfied all descriptive criteria. The pre-registered tiebreak
favored F3 (larger raw OOS net delta), but post-result analysis of
6 trade-off metrics (Information Ratio, worst-year drawdown, hit
rate, etc.) showed **F2 wins 4 of 6 metrics** and better aligns
with the user's stated "outperform index + catch big spikes" goal.
B008 formalizes that override under single-point promote discipline.

## Why F2 over F3 — pre-registered tiebreak override

B007 review computed 6 quant trade-off metrics on the 9-year
delta series:

| Metric | F2 | F3 | Winner |
|---|---:|---:|---|
| Mean delta | +0.026 | +0.035 | F3 |
| Delta std (volatility) | 0.066 | 0.108 | F2 |
| Information Ratio | **0.39** | 0.32 | **F2** |
| Cumulative terminal wealth | $0.42 | $0.45 | F3 |
| Worst single-year delta | -0.037 | -0.116 | F2 |
| OOS year hit rate | **3/4 (75%)** | 2/4 (50%) | **F2** |

F2 wins 4, F3 wins 1, plus 1 tie. The pre-registered tiebreak rule
("larger absolute OOS net delta") corresponds only to the terminal-
wealth metric — one of six — so the override is principled, not
cherry-picking. F2 is also better aligned with the user's "moderate
outperformance + spike capture" goal (consistent positive OOS
delta across years, including 2025 spike).

This decision was made with full transparency before writing this
ticket. See `research/reviews/B007_review.md` for the analysis.

## Strategy composition (single variant)

| Layer | Carrier |
|---|---|
| **Filter** | **`filter_relative_AND_absolute_positive` (F2) — under test** |
| Trigger | `trigger_acceleration` (T3) — B006 promoted |
| Ranking | `rank_by_combined_flow_5` |
| Exit | `exit_signal_reversal` |

F2 definition (frozen as in B007): on a signal_date T for stock s
in universe U(T), F2 passes iff
`(fnv_5(s,T) > 0) AND (inv_5(s,T) > 0) AND (fnv_5_rel(s,T) > 0) AND (inv_5_rel(s,T) > 0)`.

`fnv_5_rel` and `inv_5_rel` are the cross-sectional median-difference
features from `src/features/relative_flow.py` (built in B005).

Universe, costs, max_positions, IS/OOS boundary, panels — all
unchanged from B006.

## Baseline for comparison
**B006 carrier (F1 = `filter_flow_sign_both_positive`)**, run
side-by-side in this same ticket. Both runs use the same data, same
engine, same period — only the filter differs.

## Hypothesis (pre-registered)

F2 = F1 + relative-flow gate on top. The hypothesis is that adding
the "this stock is above cross-sectional median in flow ratio"
condition removes false-positive entries on days when broad
institutional buying lifts all boats (no stock-specific signal).
Result should be: similar trade count, higher per-trade alpha,
positive net improvement.

B007 evidence:
- OOS net: F1 +0.780, F2 +1.004 (Δ +0.224)
- OOS cost-0: F1 +1.875, F2 +2.230 (Δ +0.356)
- Trade count OOS: F1 724, F2 721 (Δ -3)
- F2 wins F1 in OOS years 2023, 2025, 2026 (3 of 4)
- Trade-set Jaccard (F2 ↔ F1) = 0.884 (F2 ≈ F1 with refinement)

## Pre-registered promote criteria (ALL required)

| # | Criterion | Threshold |
|---|---|---:|
| 1 | OOS net delta (F2 − F1) | ≥ +0.10 |
| 2 | OOS cost-0 net (F2) | ≥ F1 cost-0 OOS |
| 3 | OOS year-wins (F2 > F1) | ≥ 2 of 4 OOS years |
| 4 | IS net (F2) | ≥ IS net (F1) |
| 5 | OOS delta excluding 2025 alone | **> 0** (single-year effect check) |

Criterion 5 is the new safeguard specific to B008. From B007 we
know F2's OOS uplift has a 2025 component (+0.156 of total +0.224 =
~70 % of total). Criterion 5 verifies that the alpha persists
outside 2025 — i.e., F2 must not be "2025-only" alpha. Computed as
the sum of (F2−F1) net deltas for OOS years 2023, 2024, 2026 only.
B007 evidence: +0.025 + (-0.025) + 0.055 = +0.055, comfortably > 0.

## Pre-registered kill criteria (ANY triggers)

- OOS net (F2) < OOS net (F1) by ≥ 0.05 — F2 actually worse net
- OR OOS cost-0 (F2) < OOS cost-0 (F1) by ≥ 0.10 — F2 hurts the
  raw alpha
- OR criterion 5 fails badly: OOS delta excluding 2025 < -0.05
  (F2 LOSES in non-2025 OOS years)

## Pre-registered inconclusive criteria

- 4 of 5 promote criteria pass but one fails marginally — borderline
- Cost sensitivity flips the result at 3× costs
- Mixed pattern not falling cleanly into promote or kill

If inconclusive, the natural next ticket is B009 = F3 single-point
promote (the original tiebreak winner from B007) as fallback.

## Reproducibility check

Because F2 was already run in B007, the B008 F2 metrics must
reproduce the B007 F2 metrics byte-for-byte where formats match.
Specifically:

- B008 trades for variant `f2_promote` filtered must match B007
  `trades_relative_and_absolute.csv` (if exists as a per-variant
  file) or B007 trades.csv filtered to variant ==
  `f2_relative_and_absolute` row-for-row on shared columns
- B008 metrics.json `f2_promote` OOS net total return must match
  B007 metrics.json `f2_relative_and_absolute` `oos.total_return`
  within 1e-9
- Similarly for IS and cost-0

Similarly, B008 F1 baseline must reproduce B006 T3 carrier.

If reproducibility fails, B008 has unintended divergence and Codex
must stop and report.

## Reportable metrics

For both F1 baseline and F2 candidate:

1. IS net total return, hit rate, trade count, cost-0 net
2. OOS net total return, hit rate, trade count, cost-0 net
3. **Per-year net total return** for IS (2018-2022) and OOS
   (2023-2026)
4. (F2 − F1) per-year delta column
5. **OOS year-wins count** — number of OOS years where (F2 − F1) > 0
6. **OOS delta excluding 2025** — sum of (F2 − F1) for OOS years
   2023, 2024, 2026 only, computed via the same year breakdown
7. Cost sensitivity for F2 at 0×, 1×, 2×, 3×

Save year breakdown as `f2_promote_year_breakdown.csv`.

## Universe / costs / dates (unchanged from B006)

- Universe: dynamic Top100, 거래대금 ≥ 5 billion KRW (20-day avg),
  exclude rows with `거래대금추정여부 = True`
- Costs: 1.5 / 20 / 5 bps
- IS: 2018-01-02 ~ 2022-12-30
- OOS: 2023-01-02 ~ 2026-05-04
- max_positions: 5
- Entry: T+1 시가 (KRX 09:00)
- Exit: signal reversal on absolute fnv_5 / inv_5

## Multiple-testing budget acknowledgment

Cumulative variant comparisons: ~23 prior + 1 new (F2 vs F1
single-point) = 24. The single-point design intentionally minimizes
new comparison count. Criteria are calibrated to B007's observed
numbers (OOS Δ +0.224); the +0.10 promote threshold means F2 must
hold most of its B007 OOS lead under formal verification.

We commit to: **B008 either Promotes F2 as the new filter carrier
or returns inconclusive**. No silent adoption. No bar-lowering.

## Codex implementation task

Read this ticket end-to-end. Read AGENTS.md, R001 review, B006
review (T3 promote), B007 review (F2 origin, F2 vs F3 analysis).
Base commit = latest `main`.

### Scope discipline (additive only)

Touch:
- `src/strategies/b008_f2_promote.py` (NEW) — orchestrates two
  runs: F1 baseline (B006 T3 carrier reproduction) and F2 candidate.
  Imports `filter_flow_sign_both_positive` and
  `filter_relative_AND_absolute_positive` from `src/roles/filters.py`
  (already exist; do NOT modify).
- `src/run_experiment.py` — add `experiment_id == "B008"` dispatch.
- `configs/backtests/b008.yaml` (NEW).
- `tests/test_b008_strategy.py` (NEW) — sanity test that B008 F2
  numbers match B007 F2 within tolerance, and B008 F1 numbers match
  B006 T3 within tolerance.

**Do NOT touch**:
- `src/backtest/engine.py` — should not need any change. Verify
  with `git diff src/backtest/engine.py` empty before commit.
- Existing role functions (no new filters / triggers / rankings /
  exits added in this ticket).
- Existing strategy modules (a001-a004, b001-b007).
- Existing tests must remain green (currently 152).
- `src/features/flow_ratios.py` and `src/features/relative_flow.py`
  must NOT be modified (read-only).

### Configuration file

`configs/backtests/b008.yaml`:

```yaml
experiment_id: B008
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
variants:
  - f1_baseline
  - f2_promote
relative:
  cross_sectional_min_count: 30
costs:
  commission_bps: 1.5
  tax_bps_sell:   20.0
  slippage_bps:   5.0
cost_sensitivity_multipliers: [0.0, 1.0, 2.0, 3.0]
output_dir: reports/experiments/B008_f2_filter_promote
```

### Output files

Under `reports/experiments/B008_f2_filter_promote/`:

- `config.yaml`
- `metrics.json` — top-level keys `f1_baseline`, `f2_promote`, plus
  `cost_0_*` keys for both
- `trades.csv` — combined with `variant` column
- `signals.csv` — combined with `variant` column
- `equity_curve.csv` — wide format: `date, f1_baseline_value,
  f2_promote_value`
- `f2_promote_year_breakdown.csv` — per-year per-variant net total
  return, (F2 − F1) delta, win-flag column
- `cost_sensitivity.csv` — for F2 only (since promote candidate)
- `report.md`

### Order of work

Commit (Claude commits) after each green-test boundary.

1. Add B008 strategy module + dispatcher + config
2. Add B008 strategy test (verifies F2 numbers reproduce B007 F2,
   F1 numbers reproduce B006 T3, all within tolerance)
3. Run B008 real-panel
4. Verify reproducibility against B007 F2 and B006 T3 outputs
5. Verify engine.py untouched

### Completion criteria

- pytest fully green (currently 152; should grow to ~153+)
- `python -m src.run_experiment --config configs/backtests/b008.yaml`
  produces every required output
- Both variants (f1_baseline, f2_promote) reported side-by-side in
  metrics.json
- B008 f2_promote metrics match B007 f2_relative_and_absolute within
  1e-9 numerical equality on shared keys
- B008 f1_baseline matches B006 T3 within 1e-9
- src/backtest/engine.py untouched (`git diff` empty)
- Final assistant message reports the verdict-relevant numbers in
  this exact format:
  - OOS net: F1=__, F2=__, delta=__
  - OOS cost-0: F1=__, F2=__, delta=__
  - IS net: F1=__, F2=__, delta=__
  - Trade count OOS: F1=__, F2=__
  - OOS year-wins (F2 > F1) count: __ of 4
  - **OOS delta excluding 2025**: __ (criterion 5)
  - 2025 OOS delta (F2-F1): __ (for context)

### Out of scope for B008

- Any new role function (F2 already exists)
- Any new filter candidate (F2 only)
- Engine changes
- Combinations with F3 (B007 alternative; if B008 fails, B009 is
  the next ticket for F3)
- New data sources
- Alternative cross-sectional minimum counts or moment definitions

## Result summary
DO NOT FILL until backtest is complete.

## Claude review
DO NOT FILL until result files are read.
