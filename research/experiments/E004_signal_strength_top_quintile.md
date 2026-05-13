# E004 — Signal-strength top quintile on cap_only exit

## Status
planned

## Purpose (alpha-level)
E001/E002/E003 all converged on the same Layer-1 bottleneck:
per-trade hit_rate ≈ 47 %, essentially coin-flip. Cost reductions
(E002 cap_only) and Layer-4 gates (E003) did not move that number
in the right direction. E004 is the first test that **modifies the
signal itself** — replacing the binary `(fnv_5 > 0) AND (inv_5 > 0)`
with a cross-sectional intensity filter.

This is alpha-level. The infra is reused unchanged.

## Hypothesis
Restricting entries to tickers whose `combined_flow_5` falls in the
**top quintile of the day's eligible universe**, while keeping the
safety constraints `fnv_5 > 0` and `inv_5 > 0`, yields OOS hit_rate
strictly higher than cap_only baseline (`> 0.493`) AND OOS net total
return at least as good as cap_only (`> 0.688`), with hit_rate
monotonically increasing from bottom quintile to top quintile.

In plain Korean: 외국인+기관 누적 매수 비율이 그 날 universe 내에서
강한 쪽 상위 20%에 들면, 진입 후 5일 미만~20일 사이의 수익이 평균보다
좋다. 약한 신호는 잘라낸다.

## Failure modes being tested
- **Signal intensity ≠ information**: maybe the signal is uniformly
  noisy regardless of strength. E001 binary filter is then no worse
  than a quintile filter.
- **Slot mechanics drown the quantile signal**: with max 5
  positions, top quintile per day may not produce enough additional
  selectivity to move hit_rate.
- **Cross-section ambiguity**: top quintile of *universe* vs top
  quintile of *signal-positive candidates* could give different
  answers. We pre-specify "of the universe" (see below) to lock the
  definition.

## Strategy type
Layer 1 신호 강도 quantile. 청산은 E002 cap_only. 시장 게이트 없음
(E003 결과 따라 Layer 4 게이트 보류).

## Signal definition

For each ticker on KRX trading day T, identical to E001:

```
fnv_5 = rolling_sum(외국인순매수금액추정, 5, ending at T)
      / rolling_sum(거래대금추정, 5, ending at T)
inv_5 = rolling_sum(기관순매수금액추정,   5, ending at T)
      / rolling_sum(거래대금추정, 5, ending at T)
combined_flow_5 = (외국인순매수금액추정 5td + 기관순매수금액추정 5td)
                / 거래대금추정 5td
```

These features already exist in `src/features/flow_ratios.py`. No
new feature module needed.

## Quintile definition (NEW for E004)

For each `signal_date T` and the universe eligible at `T+1` open:

1. Take the set of universe-eligible tickers on `signal_date T`
   (after Rule 1 / Rule 2 / Rule 3 of `build_execution_universe`).
2. Among those tickers, drop any with NaN `combined_flow_5` at T.
3. Sort the remaining by `combined_flow_5` ascending.
4. Assign quintile 1 (bottom 20 %) through quintile 5 (top 20 %).
   Use `pd.qcut(..., labels=[1, 2, 3, 4, 5])` semantics; on ties,
   pandas's default tie-breaking applies (rank-based — same
   `combined_flow_5` value ends up in adjacent quintiles when at a
   boundary; document if pandas behavior changes).
5. If the per-day universe has fewer than **20** eligible tickers
   (so quintile is poorly defined), **all entries on that day are
   skipped**. This is a conservative, pre-frozen rule.

Headline (E004 A) entries:
```
signal_T = (fnv_5 > 0) AND (inv_5 > 0) AND (combined_flow_5_quintile_T == 5)
```

The two-positive AND is a safety constraint kept from E001 — a
negative `inv_5` paired with a large `fnv_5` could still land in
the top quintile of `combined_flow_5` if `fnv_5` dominates, but
that's not the regime we want to enter.

## Entry rule

- `signal_date = T`
- `execution_date = T+1`
- `entry_price = T+1 시가` (KRX 09:00 verified)
- 시가 ≤ 0 or NaN → skip
- Tie-break for max-positions cap: `combined_flow_5` descending
- max_positions = 5 (unchanged)

## Exit rule (E002 cap_only — same as E003)

- `holding_cap = 20 KRX trading days`
- `vol_stop_k = None`
- Exit at `KRX종가` on `add_trading_days(execution_date, 20)`
- `missing_price_fallback`, `period_end` fallbacks unchanged

## Universe (unchanged from E001 headline)

- `동적유니버스포함 == True` on most recent `날짜 ≤ T-1`
- 20-row mean `거래대금추정` ≥ 5_000_000_000 ending at `T-1`
- `거래대금추정여부 == False` on each of the 5 signal-window rows

## Data assumptions

**Locked data set**:

- IS: `inputs/equity_panels/dynamic_top100_2018_2024_panel.csv`
- OOS: `inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv`
- IS period: 2018-01-02 ~ 2022-12-30
- OOS period: 2023-01-02 ~ 2026-05-04

**No new external data.** Market-flow CSV from E003 is **not** used.
No Layer-4 gating in this experiment.

## Cost assumptions (unchanged)
- `commission_bps = 1.5`
- `tax_bps_sell = 20.0`
- `slippage_bps = 5.0`
- `cost_sensitivity_multipliers = [0.0, 1.0, 2.0, 3.0]`

## Baseline comparison

**Layer 1 — direct head-to-head**
- `B_cap_only` — E002 cap_only rerun (no quintile filter). Number to beat.
- `B_bottom_quintile` — entries only when `combined_flow_5_quintile == 1`. Sign-of-effect test.
- `B_middle_quintile` — quintile == 3. Monotonicity test.
- `B_top_decile` — top 10 % instead of top 20 %. **Diagnostic only.** Result must not be used to redefine the headline.

**Layer 2 — context (carried from E001/E002/E003)**
- B0_cash, B1_buy_and_hold, B2_universe_5d_rebalance, B3_price_momentum
- (Same broken-baseline caveat from E003 review applies — B0/B1 may
  report 0 trades, B2 may report NaN; this is a known engineering
  defect, not E004's responsibility.)

## Parameters to test

**None. Single point.**

| Parameter | Value | Rationale |
|---|---:|---|
| Quintile cut | top 20 % (quintile 5 of 5) | Sector-standard "top fifth" rule of thumb |
| Cross-section scope | universe-eligible tickers on `T` | Avoids mixing tickers we don't trade |
| Min daily universe size | 20 | Stable quintiles require at least 4 tickers per bin |
| `holding_cap` | 20 KRX trading days | Carried from E002 cap_only |
| `vol_stop_k` | None | Carried from E002 cap_only |
| Tie-handling | pandas `qcut` default | Documented; not optimized |

## Parameters that must NOT be optimized

- Top quintile cut (no shifting to decile / 25 / 15 %)
- Cross-section scope (no shifting to "across all panel" or "across sector")
- Min daily universe size (20)
- `holding_cap` (20)
- `vol_stop_k` (None)
- IS/OOS boundary
- Signal definition
- Universe rules
- Cost defaults

If a future ticket sweeps any of these, that is a **new experiment**
and must be pre-registered.

## Diagnostic split (within this ticket)

All on the same signal × universe × cap_only exit, varying only the
quintile filter:

- **(A) E004 headline** — top quintile (5)
- **(B) cap_only baseline** — no quintile filter (E002 cap_only)
- **(C) bottom quintile** (1) — sign test
- **(D) middle quintile** (3) — monotonicity test
- **(E) top decile** — diagnostic only, NOT a promotable variant

## Success criteria (alpha-level)

All five must hold for `promote`:

1. **Return**: OOS net total_return (A) > cap_only OOS (+0.688)
2. **Hit rate**: OOS hit_rate (A) > cap_only OOS (+0.493)
3. **Trade count**: OOS trade_count (A) ≥ 50
4. **Monotonicity** (sign of effect): OOS hit_rate (A top) > OOS
   hit_rate (D middle) > OOS hit_rate (C bottom). Both A and C must
   have trade_count ≥ 30 for the comparison to be meaningful.
5. **Information value**: cost-0 OOS net (A) > cost-0 OOS net (B)
   cap_only (+0.937). Confirms quintile filter raises raw signal
   value, not just cost arithmetic.

If 1–4 hold but 5 fails → `revise` (quintile filter helps net
return but doesn't improve raw signal).

Top-decile diagnostic (E) is **informational only** — do not adopt
it as the new headline even if it scores higher than (A). Promoting
(E) post-hoc is data snooping.

## Kill criteria

Any one → `kill`:

- OOS net total_return (A) ≤ cap_only OOS (+0.688)
- OOS trade_count (A) < 30 (too narrow to learn from)
- OOS hit_rate (A) ≤ OOS hit_rate (C bottom) — wrong sign
- pytest regression on E001/E002/E003 suite

## Expected weaknesses

- **Single binary quantile cut** (top vs not-top) loses graduated
  signal-intensity information. A continuous weighting could be
  better — but it's also more degrees of freedom and a separate
  experiment.
- **Daily cross-section sensitivity to universe definition**:
  changes in `동적유니버스포함` from day to day could redistribute
  which tickers are in the quintile. Stable on average but noisy
  per-day. Effect on hit_rate measurement should be small at OOS
  scale (~50+ trades).
- **`combined_flow_5` is correlated with both `fnv_5 > 0` and
  `inv_5 > 0`** — top quintile is almost always sign-positive. The
  AND safety filter is therefore mostly redundant in practice but
  not in principle. Worth noting in the review.
- **Top quintile may concentrate in specific market-cap or sector
  buckets** — large caps may dominate quintile membership. If hit
  rate improvement happens entirely on large caps, the strategy's
  generalization to other universe definitions is limited.

## Codex implementation task

Read this ticket end-to-end before writing code. Read `CLAUDE.md`,
`AGENTS.md`, and the E003 review for cap_only context. Base commit
is the latest `main` (fd336f4 at write time).

### Scope discipline (additive only)

Most modules unchanged. Touch:

- `src/strategies/e004_strength_quintile.py` (NEW) — single function
  `build_e004_top_quintile_candidates(flow_features, universe,
  quintile_value=5, min_daily_universe_size=20)` returning the same
  candidate frame shape as E001/E003 strategies (columns:
  `execution_date`, `signal_date`, `종목코드`, `fnv_5`, `inv_5`,
  `combined_flow_5`). Parameterized by `quintile_value` so that
  bottom/middle/diagnostic variants reuse the same function.
- `src/run_experiment.py` — add `experiment_id == "E004"` dispatch
  and `run_e004_experiment(config, config_path)`. Five runs (A, B,
  C, D, E) + B0~B3 + cost sensitivity + cost-0 diagnostic for (A)
  and (B).
- `configs/backtests/e004.yaml` (NEW).
- `tests/test_e004_strategy.py` (NEW) — synthetic universe fixture,
  verify quintile membership at the boundary, min-universe-size
  cutoff, NaN handling, monotonicity of quintile labels.

**Do NOT touch**: engine, baselines, features, universe, calendar,
costs, metrics, report, market-flow loader, market-gate features
(E003 work stays unchanged).

### Strategy filter spec

```python
def build_e004_top_quintile_candidates(
    flow_features: pd.DataFrame,
    universe: pd.DataFrame,
    quintile_value: int = 5,
    min_daily_universe_size: int = 20,
) -> pd.DataFrame:
    """For each signal_date in `universe`, restrict to tickers whose
    combined_flow_5 falls in the target quintile of that day's
    universe (after `fnv_5 > 0` AND `inv_5 > 0` safety filter).

    Quintile is computed via pandas qcut over the eligible universe
    of that signal_date (not across all panel rows). On signal_dates
    where the daily eligible universe has fewer than
    min_daily_universe_size tickers, all entries are dropped (return
    no rows for that signal_date).
    Output schema matches build_e001_flow_filter_candidates."""
```

Edge cases the function handles explicitly:
- NaN `combined_flow_5` → excluded from quintile computation
- Insufficient universe (< min_daily_universe_size) → no candidates
  that day
- `quintile_value` must be in `{1, 2, 3, 4, 5}`; otherwise raise.

### Configuration file

`configs/backtests/e004.yaml`:

```yaml
experiment_id: E004
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
  holding: 20
  max_positions: 5
exit:
  vol_stop_k: null    # cap_only
  vol_stop_atr_window: 20
quintile:
  value: 5
  min_daily_universe_size: 20
costs:
  commission_bps: 1.5
  tax_bps_sell:   20.0
  slippage_bps:   5.0
cost_sensitivity_multipliers: [0.0, 1.0, 2.0, 3.0]
output_dir: reports/experiments/E004_signal_strength_top_quintile
```

Strict validation. The `quintile.value` and
`quintile.min_daily_universe_size` are surface-of-record; do not
sweep them.

### Runs to produce

On the full `[is.start, oos.end]` period:

1. **headline** (A) — top quintile (5)
2. **cap_only** (B) — no quintile filter (E001 candidates)
3. **bottom_quintile** (C) — quintile_value = 1
4. **middle_quintile** (D) — quintile_value = 3
5. **top_decile** (E) — implemented as a variant of the same
   function with `quintile_value = "top_decile"` accepted as a
   special case (and pandas `qcut(..., 10)` taking top label = 10),
   OR add a parallel function. Diagnostic only.
6. **B0_cash, B1, B2, B3** — unchanged
7. **diagnostic_estimate_included** — top quintile + diagnostic universe
8. **cost_sensitivity** — (A) at `[0, 1, 2, 3]`
9. **cost_0_headline**, **cost_0_cap_only**

`metrics.json` top-level keys: `headline`, `cap_only`,
`bottom_quintile`, `middle_quintile`, `top_decile`, `B0`, `B1`,
`B2`, `B3`, `diagnostic_estimate_included`, `cost_0_headline`,
`cost_0_cap_only`.

### Output files

Under `reports/experiments/E004_signal_strength_top_quintile/`:
- `config.yaml`, `metrics.json`, `trades.csv` (A),
  `signals.csv` (A candidates after quintile filter),
  `equity_curve.csv` (A), `cost_sensitivity.csv`, `report.md`
- `quintile_membership_sample.csv` — for inspection: 20 random
  signal_dates with the per-day eligible universe size, the chosen
  quintile boundaries, and the tickers chosen in (A). This is a
  diagnostic aid only (not consumed by metrics).

`종목코드` preserved as 6-digit string (zero-padded), regression
test already in place from E003.

### Tests (new `tests/test_e004_strategy.py`)

1. `test_top_quintile_returns_top_20_percent_when_universe_large` —
   synthetic universe of 25 tickers on a single signal_date with
   distinct `combined_flow_5` values. Verify exactly 5 are selected
   (the 5 highest).
2. `test_safety_filter_drops_negative_components` — universe of 25
   tickers; top 5 by `combined_flow_5` include one whose `inv_5 <
   0`. Verify that ticker is excluded; the next-highest
   `combined_flow_5` (with both components positive) replaces it.
3. `test_insufficient_universe_returns_no_candidates_that_day` —
   synthetic signal_date with only 15 eligible tickers. Verify
   output has zero rows for that day.
4. `test_nan_combined_flow_excluded_from_quintile` — synthetic
   universe of 25 tickers, one with NaN `combined_flow_5`. Verify
   that ticker is treated as not-in-quintile, not in any quintile,
   and not chosen.
5. `test_quintile_membership_is_per_signal_date_independent` —
   two signal_dates with different universes; quintile membership
   on day 1 must not depend on day 2's data (forward-leakage
   regression).
6. `test_bottom_quintile_returns_bottom_20_percent` — same fixture
   as test 1, but `quintile_value = 1`. Verify the 5 lowest.

### Order of work

Commit (Claude commits) after each green-test boundary.

1. `src/strategies/e004_strength_quintile.py` +
   `tests/test_e004_strategy.py`. Pytest must remain fully green
   (currently 79; new tests bring it to ~85).
2. CLI extension and config.
3. Real-panel run end-to-end.

### Completion criteria

- pytest fully green (no E001/E002/E003 regression)
- `python -m src.run_experiment --config configs/backtests/e004.yaml`
  produces all required outputs without manual intervention
- All 5 success criteria computable from `metrics.json` alone
- Final message lists any spec-ambiguity calls made

### Out of scope for E004

- Quintile cut sweep
- Continuous-weight signal (sigmoid, linear, etc.)
- Sector-conditional or market-cap-conditional quintiles
- Adding Layer 4 market gate (E003 retired)
- Adding `vol_stop_k` (E002 retired the stop)
- Adding new data sources

## Result summary
DO NOT FILL until backtest is complete.

## Claude review
DO NOT FILL until result files are read.
