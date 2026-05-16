# B009 — F3 (persistence 4-of-5) filter promote ticket

## Status
planned

## What is being tested
**One single filter candidate (F3 — `filter_persistence_4_of_5`)
on the B006 T3 carrier**, with the same 5-criterion promote / kill /
inconclusive logic used in B008.

This is a **single-point promote ticket**, NOT a descriptive
exploration. F3 was the pre-registered tiebreak winner from B007
(larger raw OOS net delta), and is the pre-registered fallback
candidate after B008 returned inconclusive (F2 marginally failed
criterion 4 by -0.0005).

## Why F3 now (after B008 inconclusive)

B008 review concluded inconclusive on F2 because IS-net delta was
-0.0005 — strictly below the criterion 4 threshold but practically
zero. Per pre-registered fallback rule:

> "If inconclusive, the natural next ticket is B009 = F3 single-point
> promote (the original tiebreak winner from B007) as fallback."

B009 applies the SAME 5-criterion logic to F3 for fairness. After
B009, both single-point results are in hand and the F2-vs-F3 choice
can be made with full information.

## Strategy composition (single variant)

| Layer | Carrier |
|---|---|
| **Filter** | **`filter_persistence_4_of_5` (F3) — under test** |
| Trigger | `trigger_acceleration` (T3) — B006 promoted |
| Ranking | `rank_by_combined_flow_5` |
| Exit | `exit_signal_reversal` |

F3 definition (frozen as in B007):
`(fnv_5(s,T) > 0) AND (inv_5(s,T) > 0) AND (count(combined_flow_1(s, day) > 0 over [T-4, T]) ≥ 4)`.

`combined_flow_1` is from `src/features/flow_ratios.py` (added in B003).

Universe, costs, max_positions, IS/OOS boundary, panels — all
unchanged from B006.

## Baseline for comparison

**B006 carrier (F1 = `filter_flow_sign_both_positive`)**, same as
B008. Run side-by-side in this same ticket. Both runs use the same
data, same engine, same period — only the filter differs.

## Hypothesis (pre-registered)

F3 = F1 + persistence requirement on top. The hypothesis is that
requiring 4-of-5-day daily buying (vs only the 5-day cumulative
sign condition) filters out short-burst entries driven by 1-2
strong days that don't have follow-through. Result should be: more
distinct trade pool than F1 (lower Jaccard), higher per-trade
quality, positive net improvement — possibly larger in magnitude
than F2 but with more concentrated/volatile per-year delta profile.

B007 evidence:
- OOS net: F1 +0.780, F3 +1.104 (Δ +0.324)
- OOS cost-0: F1 +1.875, F3 +2.418 (Δ +0.543)
- Trade count OOS: F1 724, F3 731 (Δ +7)
- F3 wins F1 in OOS years 2025, 2026 (2 of 4)
- IS net: F1 -0.793, F3 -0.787 (Δ +0.006)
- Trade-set Jaccard (F3 ↔ F1) = 0.421 (substantially different pool)

## Pre-registered promote criteria (ALL required) — IDENTICAL to B008

Using the same criteria as B008 ensures fairness across the F2 and
F3 single-point tests.

| # | Criterion | Threshold |
|---|---|---:|
| 1 | OOS net delta (F3 − F1) | ≥ +0.10 |
| 2 | OOS cost-0 net (F3) | ≥ F1 cost-0 OOS |
| 3 | OOS year-wins (F3 > F1) | ≥ 2 of 4 OOS years |
| 4 | IS net (F3) | ≥ IS net (F1) |
| 5 | OOS delta excluding 2025 alone | > 0 (single-year effect check) |

## Pre-registered kill criteria (ANY triggers)

- OOS net (F3) < OOS net (F1) by ≥ 0.05 — F3 actually worse net
- OR OOS cost-0 (F3) < OOS cost-0 (F1) by ≥ 0.10 — F3 hurts the
  raw alpha
- OR criterion 5 fails badly: OOS delta excluding 2025 < -0.05
  (F3 LOSES in non-2025 OOS years)

## Pre-registered inconclusive criteria

- 4 of 5 promote criteria pass but one fails marginally (same as
  B008's borderline definition)
- Cost sensitivity flips the result at 3× costs
- Mixed pattern not falling cleanly into promote or kill

## Honest acknowledgments before result

Things to keep in mind when interpreting B009's verdict:

1. **F3's OOS uplift has 2026 concentration**. From B007: the
   non-2025 OOS delta of +0.148 is driven almost entirely by 2026
   partial year (+0.221), with 2023 and 2024 negative. If we
   excluded 2026 too, F3's non-spike OOS contribution would be
   negative (−0.073).
2. **The pre-registered criteria do NOT have a "exclude partial 2026"
   guard**. B008 set criterion 5 as "exclude 2025 only" for both
   tickets. Adding a 2026-exclusion criterion now would be data-
   snooping (we know it would specifically hurt F3).
3. **F3 is therefore evaluated on the same bar as F2 was**. If F3
   passes, the verdict stands per discipline; the 2026-concentration
   concern goes into the review but doesn't override the formal
   verdict.
4. **F3 passes all 5 expected** (per B007 numbers): OOS Δ +0.324,
   cost-0 Δ +0.543, year-wins 2/4, IS Δ +0.006, ex-2025 OOS Δ
   +0.148.

## Reproducibility check

Because F3 was already run in B007:

- B009 trades for variant `f3_promote` must match B007 trades for
  variant `f3_persistence_4_of_5` row-for-row on shared columns
- B009 metrics.json `f3_promote` IS / OOS / cost-0 metrics must
  match B007 `f3_persistence_4_of_5` corresponding keys within 1e-9
- B009 `f1_baseline` must match B006 T3 within 1e-9 (also matches
  B007 F1 and B008 F1)

If reproducibility fails, B009 has unintended divergence and Codex
must stop and report.

## Reportable metrics

For both F1 baseline and F3 candidate:

1. IS net total return, hit rate, trade count, cost-0 net
2. OOS net total return, hit rate, trade count, cost-0 net
3. Per-year net total return for IS (2018-2022) and OOS (2023-2026)
4. (F3 − F1) per-year delta column
5. OOS year-wins count
6. **OOS delta excluding 2025** — sum of (F3 − F1) for OOS years
   2023, 2024, 2026 only (criterion 5)
7. **OOS delta excluding 2025 AND 2026** — sum of (F3 − F1) for OOS
   years 2023, 2024 only. **Reported as descriptive context only,
   NOT used as a promote/kill criterion** (would be data-snooping
   to add it after seeing B007 numbers).
8. Cost sensitivity for F3 at 0×, 1×, 2×, 3×

Save year breakdown as `f3_promote_year_breakdown.csv`.

## Universe / costs / dates (unchanged from B006)

- Universe: dynamic Top100, 거래대금 ≥ 5 billion KRW (20-day avg),
  exclude rows with `거래대금추정여부 = True`
- Costs: 1.5 / 20 / 5 bps
- IS: 2018-01-02 ~ 2022-12-30
- OOS: 2023-01-02 ~ 2026-05-04
- max_positions: 5
- Entry: T+1 시가 (KRX 09:00)
- Exit: signal reversal on absolute fnv_5 / inv_5

## Multiple-testing budget

Cumulative: ~25 prior + 1 (B009 single-point) = 26.

We commit to: **B009 either Promotes F3 as the new filter carrier
or returns inconclusive**. No silent adoption. No bar-lowering.

If both B008 and B009 promote → user has a real F2 vs F3 choice
with both formal verdicts in hand; revisit B007 review's 6-metric
analysis with full information.

If B009 promotes but B008 was inconclusive → F3 becomes new carrier
unless user explicitly overrides.

If B009 also inconclusive → both filter candidates exhausted,
B010 = different role exploration (ranking or exit).

## Codex implementation task

Read this ticket end-to-end. Read AGENTS.md, R001 review, B006
review, B007 review, and B008 review. Base commit = latest `main`.

### Scope discipline (additive only)

Touch:
- `src/strategies/b009_f3_promote.py` (NEW) — orchestrates two
  runs: F1 baseline (B006 T3 carrier reproduction) and F3 candidate.
  Imports `filter_flow_sign_both_positive` and
  `filter_persistence_4_of_5` from `src/roles/filters.py` (already
  exist; do NOT modify).
- `src/run_experiment.py` — add `experiment_id == "B009"` dispatch.
- `configs/backtests/b009.yaml` (NEW).
- `tests/test_b009_strategy.py` (NEW) — sanity test that B009 F3
  numbers match B007 F3 within 1e-9, and B009 F1 numbers match
  B006 T3 / B008 F1 within 1e-9.

**Do NOT touch**:
- `src/backtest/engine.py` — should not need any change. Verify
  with `git diff src/backtest/engine.py` empty before commit.
- Existing role functions (no new filters / triggers / rankings /
  exits added in this ticket).
- Existing strategy modules (a001-a004, b001-b008).
- Existing tests must remain green (currently 154).
- `src/features/flow_ratios.py` and `src/features/relative_flow.py`
  must NOT be modified (read-only).

### Configuration file

`configs/backtests/b009.yaml`:

```yaml
experiment_id: B009
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
  - f3_promote
costs:
  commission_bps: 1.5
  tax_bps_sell:   20.0
  slippage_bps:   5.0
cost_sensitivity_multipliers: [0.0, 1.0, 2.0, 3.0]
output_dir: reports/experiments/B009_f3_filter_promote
```

### Output files

Under `reports/experiments/B009_f3_filter_promote/`:

- `config.yaml`
- `metrics.json` — top-level keys `f1_baseline`, `f3_promote`, plus
  `cost_0_*` keys for both
- `trades.csv` — combined with `variant` column
- `signals.csv` — combined with `variant` column
- `equity_curve.csv` — wide format: `date, f1_baseline_value,
  f3_promote_value`
- `f3_promote_year_breakdown.csv` — per-year per-variant net total
  return, (F3 − F1) delta, win-flag column
- `cost_sensitivity.csv` — for F3 only (since promote candidate)
- `report.md`

### Order of work

Commit (Claude commits) after each green-test boundary.

1. Add B009 strategy module + dispatcher + config
2. Add B009 strategy reproducibility test
3. Run B009 real-panel
4. Verify reproducibility against B007 F3 and B006 T3 outputs
5. Verify engine.py untouched

### Completion criteria

- pytest fully green (currently 154; should grow to ~155+)
- `python -m src.run_experiment --config configs/backtests/b009.yaml`
  produces every required output
- Both variants reported side-by-side in metrics.json
- B009 f3_promote metrics match B007 f3_persistence_4_of_5 within
  1e-9 numerical equality
- B009 f1_baseline matches B006 T3 within 1e-9
- src/backtest/engine.py untouched
- Final assistant message reports the verdict-relevant numbers in
  this exact format:
  - OOS net: F1=__, F3=__, delta=__
  - OOS cost-0: F1=__, F3=__, delta=__
  - IS net: F1=__, F3=__, delta=__
  - Trade count OOS: F1=__, F3=__
  - OOS year-wins (F3 > F1) count: __ of 4
  - **OOS delta excluding 2025**: __ (criterion 5)
  - 2025 OOS delta (F3-F1): __
  - **OOS delta excluding 2025 AND 2026** (descriptive only): __

### Out of scope for B009

- Any new role function (F3 already exists)
- Any new filter candidate
- Engine changes
- Combinations with F2 (previously tested in B008)
- New data sources

## Result summary
DO NOT FILL until backtest is complete.

## Claude review
DO NOT FILL until result files are read.
