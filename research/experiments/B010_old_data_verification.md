# B010 — Old-data verification of current carrier (T3 + F3)

## Status
planned

## What is being tested
**The current B-family carrier (T3 trigger + F3 filter) applied to
2010-2017 data** (genuinely fresh OOS that has never been used in
any prior experiment). This is a DIAGNOSTIC verification ticket, NOT
a promote ticket — the carrier itself is unchanged.

The question: does the carrier's alpha persist in old data, or is
the 2018-2026 performance a regime artifact of the recent decade?

This is the first true OOS test in the project. Per [[feedback-
experiment-discipline]] and [[signal-regime-conditionality]] memory,
the 2018-2026 dataset has accumulated ~27 cumulative variant
comparisons; adding patches to it is increasingly suspect. Old-data
verification is the disciplined alternative.

## Why now

After B003 → B004 → B005 → B006 → B007 → B008 → B009, the carrier
has evolved:
- Trigger: immediate → **acceleration (T3)** (B006 promote)
- Filter: flow_sign_both_positive → **persistence_4_of_5 (F3)** (B009
  promote per Mode C, with honest caveat that F3 loses in 2023+2024)

Both promotes were on the 2018-2026 dataset. Every B-family review
since B003 has flagged that the underlying signal is regime-
conditional. B010 brings genuinely unseen data into play.

Per Mode C discipline (see [[feedback-experiment-discipline]]):
**this is also where the criterion improvements committed at the end
of B009 first apply.** B010 uses tightened criteria.

## Strategy composition (unchanged carrier)

| Layer | Carrier |
|---|---|
| Filter | `filter_persistence_4_of_5` (F3) — B009 promoted |
| Trigger | `trigger_acceleration` (T3) — B006 promoted |
| Ranking | `rank_by_combined_flow_5` |
| Exit | `exit_signal_reversal` |

No new alpha. No new role function. The carrier is frozen as the
current B-family default and applied to fresh data.

## Data assumptions

**New data for this experiment** (never used in B001-B009):

| File | Coverage | Use |
|---|---|---|
| `research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv` | 2010-01-04 ~ 2015-01-06 | Primary panel for 2010-2015 |
| `research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv` | 2017-01-02 ~ 2024-12-30 | Use ONLY 2017 portion (filter signal_date ≤ 2017-12-31) |
| `research_input_data/inputs/market_flow/kiwoom_market_flow_2010_2017_krx_trading_days.csv` | 2010-01-04 ~ 2017-12-28 | Market-flow context |

**Gap acknowledged**: 2016 calendar year is missing from any panel.
Per [[feedback-experiment-discipline]] "data + hypothesis +
parameters" reset rule, we do NOT extend a partial 2016 panel here.
Verification covers 2010-2015 + 2017 = ~6 years of fresh OOS, with
2016 explicitly skipped.

### Schema differences to resolve (first step in Codex work)

The old `kiwoom_dynamic_top100_2010_2016` panel has ADDITIONAL
columns vs current panels:
- `통합거래량반영여부`, `통합종가반영여부`, `통합종가제외여부`,
  `가격범위후보정여부`, `KRX종가`

The 2017-2024 panel does NOT have these. The 2025-2026 panel DOES.
Codex must:
1. Inspect both schemas precisely.
2. Document each non-matching column's meaning and whether it's
   load-bearing for the loader (`src/data/equity_panel.py`).
3. Extend the loader to normalize all three panels (old, mid, new)
   into a consistent in-memory schema, with explicit documentation
   in `docs/data_schema.md` (create if absent).
4. Apply existing rules (e.g., `거래대금추정여부 = True` row exclusion)
   on the new panels too — same rules, same effect.

If the schema diff cannot be resolved cleanly (e.g., a column has
incompatible meaning), Codex stops and writes the issue into
`research/experiments/B010_codex_questions.md`.

### Universe and feature continuity
- Universe filter: same as 2018-2026 (dynamic_top100 + 20-day avg
  거래대금 ≥ 5 billion + 거래대금추정여부 = False)
- Features: `fnv_5`, `inv_5`, `combined_flow_1`, `combined_flow_5`
  computed from the new panels using existing
  `src/features/flow_ratios.py` — no modifications needed
- F3 filter uses `combined_flow_1` rolling 5-day count, exactly as
  in B009

### Cost assumptions
Same as 2018-2026: 1.5 / 20 / 5 bps. No old-era cost adjustment.

This is intentional: we are testing whether the SAME carrier under
the SAME cost regime works in old data. Old-era costs were higher
(commissions, taxes both higher pre-2014); using current costs is
a forgiving test. If carrier fails even under forgiving costs, that's
a strong negative signal. If it passes, we have a baseline.

A future B-or-later ticket could test under era-appropriate costs.
That's out of scope for B010.

## Pre-registered variants

All three run on the same 2010-2017 universe with the same calendar,
liquidity filter, and costs.

### V1 — `carrier_t3_f3` (the verification candidate)
T3 trigger + F3 filter + combined_flow_5 ranking + signal_reversal
exit. This is the current B-family carrier post-B009.

### V2 — `t3_f1_baseline` (B006 carrier, pre-F3)
T3 trigger + F1 filter + combined_flow_5 ranking + signal_reversal
exit. This shows whether F3's advantage over F1 (seen in B007/B009
on 2018-2026) persists in old data.

### V3 — `cash` (sanity)
0% return throughout. Absolute floor reference.

(Variant 4 — gate-only equal weight — considered and dropped to keep
the ticket scoped. B010 is verification, not benchmark sprawl.)

## Hypothesis (pre-registered)

**H1 (cost-0 alpha persistence)**: V1 carrier has cost-0 net total
return > 0 on 2010-2015 + 2017 data.

If H1 holds, the underlying flow signal carries real information in
old data. If H1 fails, the 2018-2026 OOS signal alpha was likely a
recent-regime artifact.

**H2 (net total return survival)**: V1 net total return ≥ -0.20.

Old data may show negative net (current costs are forgiving but
turnover may still eat alpha). -0.20 is the floor we accept.

**H3 (multi-year contribution)**: V1 produces a positive yearly
contribution in ≥ 3 of 6 years (2010, 2011, 2012, 2013, 2014, 2015,
2017 — 7 candidate years, with 2015 partial through 2015-01-06).

**H4 (no single-year dominance, IMPROVED CRITERION per Mode C)**:
The largest single-year (V1 − V2) delta is ≤ 80 % of total (V1 − V2)
delta. (Equivalent to: removing the best year, the V1 - V2 delta is
still positive and at least 20 % of the original.)

H4 tightens the 2018-2026 criterion 5 ("OOS delta excluding 2025
alone") by adding the partial-year sensitivity that surfaced in
B009. With multiple candidate years in old data, no single year
should dominate.

**H5 (F3 vs F1 in old data, IMPROVED COMPARISON per Mode C)**: V1
net total return ≥ V2 net total return - 0.10 (F3 carrier doesn't
substantially underperform pre-F3 carrier in old data).

H5 is descriptive only — its purpose is to surface whether F3's
2018-2026 advantage transfers, not as a kill criterion. F3 promoted
on 2018-2026 evidence; if it fails to transfer, the F3 promote
caveat is strengthened, not the promote itself revoked (per Mode C,
past verdicts stand).

## Pre-registered verdict logic

This is a DIAGNOSTIC ticket. Outcomes are:

**VERIFY PASS** — all four (H1, H2, H3, H4) hold:
- Carrier alpha confirmed across decades
- Continue role exploration (B011 = ranking or exit) on the now-
  verified carrier

**VERIFY FAIL** — H1 fails (cost-0 net ≤ 0):
- Signal does not carry information in old data
- Strong evidence that 2018-2026 OOS performance was regime artifact
- Reconsider carrier definition; B011 should be either signal
  redesign (new alpha class) or a different data exploration, NOT
  more role exploration on the carrier
- Mode C means: F3 promote is NOT undone (B009 verdict stands), but
  the carrier evolution is paused pending a new alpha hypothesis

**VERIFY MIXED** — H1 holds but one of H2/H3/H4 fails:
- Alpha exists but is fragile (concentrated, cost-eaten, or single-
  year dependent)
- Carrier confirmed in a weaker sense; B011 should focus on
  understanding the failure dimension (e.g., if H4 fails, investigate
  the dominant year)
- Honest caveat added to memory: "carrier alpha exists in old data
  but is concentrated"

**No promote action regardless of verdict** — B010 changes nothing
about the carrier itself. It only changes our CONFIDENCE in the
carrier and informs B011 direction.

## Reportable metrics

For each of V1, V2, V3 (V3 trivially 0):

1. Net total return on 2010-2017 verification period (combined
   2010-2015 + 2017, with 2016 gap)
2. Cost-0 net total return (the H1 diagnostic)
3. Hit rate
4. Trade count
5. **Per-year net total return** for each of 2010, 2011, 2012, 2013,
   2014, 2015 (partial), 2017 — 7 cells per variant
6. (V1 − V2) per-year delta column (the H5 diagnostic)
7. **Largest single-year contribution as fraction of total** (the
   H4 diagnostic, computed for V1)
8. Cost sensitivity for V1 at 0×, 1×, 2×, 3×
9. **Comparison summary table**: 2018-2026 V1 vs 2010-2017 V1, the
   key carrier-survival diagnostic side-by-side

Save year breakdown as `old_data_year_breakdown.csv`.

## Implementation task (Codex)

Read this ticket end-to-end. Read AGENTS.md, R001 review, B006/B009
reviews (current carrier), and existing
`src/data/equity_panel.py` for the loader pattern.

### Scope discipline (additive only)

Touch (in this order — schema work FIRST):

1. **Schema verification (no code change yet)**: write a brief
   document `docs/data_schema_2010_2017.md` describing the schema
   diffs and proposed normalization. If unresolvable issues,
   write to `research/experiments/B010_codex_questions.md` and STOP.

2. **`src/data/equity_panel.py`** — extend loader to handle old
   panel schema. Specifically: handle the additional columns
   (`통합거래량반영여부`, `통합종가반영여부`, `통합종가제외여부`,
   `가격범위후보정여부`, `KRX종가`) gracefully on old data, and
   ensure they default to safe values on the 2017-2024 panel where
   they don't exist.

   Existing tests must remain green. Add new tests for old-panel
   loading.

3. **`src/data/market_flow.py`** — extend to load the
   `kiwoom_market_flow_2010_2017_krx_trading_days.csv` file with the
   same defensive NaN handling as the 2018-2026 file.

4. **`src/strategies/b010_old_data_verification.py`** (NEW) —
   orchestrates V1 (T3 + F3 carrier), V2 (T3 + F1 baseline), V3
   (cash) on the merged 2010-2015 + 2017 data window.

5. **`src/run_experiment.py`** — add `experiment_id == "B010"`
   dispatch.

6. **`configs/backtests/b010.yaml`** (NEW).

7. **Tests** — new tests:
   - `tests/test_old_panel_loading.py`: verifies old panel loads with
     correct row count, date coverage, and column normalization
   - `tests/test_b010_strategy.py`: V1 reproduces something
     sensible (small sanity check on synthetic mini-panel)

**Do NOT touch**:
- `src/backtest/engine.py` — should not need any change. Verify
  with `git diff src/backtest/engine.py` empty.
- Existing role functions (no new filters / triggers / rankings /
  exits).
- Existing strategy modules (a001-a004, b001-b009).
- `src/features/flow_ratios.py` and `src/features/relative_flow.py`
  must NOT be modified.
- 2018-2026 panel handling logic — old-panel loading is purely
  additive.

### Configuration file

`configs/backtests/b010.yaml`:

```yaml
experiment_id: B010
panels:
  - research_input_data/inputs/equity_panels/kiwoom_dynamic_top100_2010_2016_panel.csv
  - research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv
panel_date_filters:
  # 2017-2024 panel: ONLY use signal_dates <= 2017-12-31. Beyond is
  # already-seen 2018-2026 territory, kept out of this verification.
  research_input_data/inputs/equity_panels/dynamic_top100_2017_2024_panel.csv:
    end: 2017-12-31
market_flow_csv: research_input_data/inputs/market_flow/kiwoom_market_flow_2010_2017_krx_trading_days.csv
verification_period:
  start: 2010-01-04
  end:   2017-12-29
  exclude_calendar_years: [2016]   # gap year, no panel data
universe:
  require_dynamic_top100: true
  min_avg_traded_value_20d: 5_000_000_000
  exclude_estimated_flag_rows: true
strategy:
  lookback: 5
  max_positions: 5
filter:
  type: persistence_4_of_5      # F3 (B009 carrier)
trigger:
  type: acceleration            # T3 (B006 carrier)
ranking:
  type: combined_flow_5
exit:
  type: signal_reversal
variants:
  - carrier_t3_f3        # V1
  - t3_f1_baseline       # V2
  - cash                 # V3
costs:
  commission_bps: 1.5
  tax_bps_sell:   20.0
  slippage_bps:   5.0
cost_sensitivity_multipliers: [0.0, 1.0, 2.0, 3.0]
output_dir: reports/experiments/B010_old_data_verification
```

### Output files

Under `reports/experiments/B010_old_data_verification/`:

- `config.yaml`
- `metrics.json` — top-level keys `carrier_t3_f3`, `t3_f1_baseline`,
  `cash`, plus `cost_0_*` keys
- `trades.csv` (combined with `variant` column)
- `signals.csv` (combined with `variant` column)
- `equity_curve.csv` (wide format, one column per variant)
- `old_data_year_breakdown.csv` — per-year per-variant net total
  return, (V1 − V2) delta, largest-year fraction summary row
- `verification_diagnostic.csv` — single summary row with H1 / H2 /
  H3 / H4 / H5 pass-fail flags and the relevant numeric values
- `cost_sensitivity.csv`
- `report.md`

### Tests

Existing 156 tests must remain green. New tests bring suite to
~159+.

### Order of work

Commit (Claude commits) after each green-test boundary.

1. Schema verification → `docs/data_schema_2010_2017.md`
2. Loader extension + tests
3. Market-flow loader extension + tests
4. B010 strategy module + dispatcher + config
5. Run B010 real-panel
6. Verify engine.py untouched

### Completion criteria

- pytest fully green
- `python -m src.run_experiment --config configs/backtests/b010.yaml`
  produces every required output
- All 3 variants reported side-by-side in metrics.json
- engine.py untouched
- Final assistant message reports the verdict-relevant numbers in
  this exact format:
  - V1 (T3+F3) cost-0 net: __ (H1 check)
  - V1 net total return: __ (H2 check, threshold ≥ -0.20)
  - V1 positive years: __ of 6 (H3 check, threshold ≥ 3)
  - V1 largest-year fraction of total: __ % (H4 check, threshold ≤ 80%)
  - V1 vs V2 delta: __ (H5 descriptive)
  - 2018-2026 V1 cost-0 OOS vs 2010-2017 V1 cost-0 (the survival
    diagnostic): __

### Out of scope for B010

- Any new role function
- Any carrier change
- Era-appropriate cost adjustments
- Era-appropriate universe definition (we use current universe rule)
- 2016 partial data reconstruction
- New alpha definitions

## Result summary
DO NOT FILL until backtest is complete.

## Claude review
DO NOT FILL until result files are read.
