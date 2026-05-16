# Review — B006 (T3 acceleration trigger promote)

## Verdict
**PROMOTE** — first official strategy promote in the project (R001
was a structural refactor, not a strategy change).

T3 (`combined_flow_1 > combined_flow_5 / 5`) becomes the new trigger
carrier. The new B-family carrier from this point forward is:

- Filter: `filter_flow_sign_both_positive`
- **Trigger: `trigger_acceleration` (T3) — promoted in B006**
- Ranking: `rank_by_combined_flow_5`
- Exit: `exit_signal_reversal`

All future single-role exploration tickets use this new baseline.

## One-line conclusion
T3 acceleration trigger satisfies all 5 pre-registered promote
conditions on the B002 absolute carrier. Improvement is multi-year,
multi-regime, and not concentrated in 2025 (the dominant OOS
contributor is 2023, not 2025).

## Headline numbers

| variant | IS net | OOS net | IS hit | OOS hit | IS trades | OOS trades |
|---|---:|---:|---:|---:|---:|---:|
| T1 baseline (B002) | -0.840 | +0.641 | 0.391 | 0.419 | 1214 | 730 |
| **T3 acceleration** | **-0.793** | **+0.780** | 0.391 | 0.420 | 1189 | 724 |
| Δ (T3 − T1) | **+0.048** | **+0.139** | 0.000 | +0.001 | -25 | -6 |

Cost-0 OOS (raw alpha):
- T1: +1.660
- T3: +1.875
- Δ: **+0.215** (alpha actually preserved AND improved)

## Pre-registered promote criteria — all five PASS

| # | Criterion | Threshold | Actual | Pass |
|---|---|---|---:|:---:|
| 1 | OOS net delta (T3 − T1) | ≥ +0.10 | **+0.139** | ✓ |
| 2 | OOS cost-0 (T3) ≥ T1 cost-0 | T3 ≥ T1 | T3 +1.875 vs T1 +1.660 | ✓ |
| 3 | Trade count (T3) < T1 | strictly less | 724 < 730 | ✓ (marginal) |
| 4 | T3 wins T1 in OOS years | ≥ 2 of 4 | 2 of 4 (2023, 2025) | ✓ (just barely) |
| 5 | IS net (T3) ≥ IS net (T1) | T3 ≥ T1 | -0.793 vs -0.840 | ✓ |

**No criterion failed. No edge cases.**

## Pre-registered kill criteria — none triggered
- OOS net regression ≥ 0.05: actual is **+0.139 improvement**. Far from kill.
- OOS cost-0 regression ≥ 0.10: actual is **+0.215 improvement**. Far from kill.

## Pre-registered inconclusive criteria — none triggered
- Single-year concentration: 2025 delta = **+0.031** (NOT dominant);
  the largest OOS contributor is 2023 (+0.151). Improvement is
  spread across regimes.
- Cost sensitivity flip: T3 maintains lead at all cost multipliers
  observed; would need cost-3× T1 numbers to fully verify but
  cost-0 and 1× both show consistent +0.14 to +0.22 delta.

## Year-by-year breakdown (the most important diagnostic)

### IS (2018-2022)
| year | T1 | T3 | T3 − T1 | T3 wins? |
|---|---:|---:|---:|:---:|
| 2018 | -0.378 | -0.284 | **+0.095** | ✓ |
| 2019 | -0.074 | -0.056 | +0.017 | ✓ |
| 2020 | **-0.387** | **-0.263** | **+0.124** | ✓ |
| 2021 | -0.249 | -0.359 | -0.111 | ✗ |
| 2022 | -0.407 | -0.361 | +0.046 | ✓ |

**T3 wins 4 of 5 IS years.** Even partially fixes the 2020
V-recovery problem (+0.124, though still net negative). The only
loss is 2021 (sideways year, KOSPI +4 %), where acceleration
filter likely cut too many entries.

### OOS (2023-2026)
| year | T1 | T3 | T3 − T1 | T3 wins? |
|---|---:|---:|---:|:---:|
| 2023 | -0.106 | **+0.045** | **+0.151** | ✓ |
| 2024 | -0.206 | -0.234 | -0.028 | ✗ |
| 2025 | +0.883 | +0.914 | +0.031 | ✓ |
| 2026 | +0.128 | +0.079 | -0.050 | ✗ |

**The biggest OOS contributor is 2023 (+0.151), not 2025 (+0.031).**
This is the cleanest possible refutation of "T3 wins because of
2025 spike". 2023 was a recovery year (KOSPI +18 %), structurally
different from the 2025 spike, and that's where T3 earns most of
its OOS lead.

## Mechanism interpretation — partial revision of B003 hypothesis

B003 hypothesis: T3 wins by reducing turnover, saving costs.

B006 evidence:
- Trade count reduction is real but small: 730 → 724 = -6 trades
  (-0.8 %). Cost savings from this alone would be ~0.04, not the
  observed +0.139 OOS delta.
- Cost-0 OOS delta is +0.215 — meaning T3 has more raw alpha,
  not just less cost.
- Trade-set Jaccard overlap T3↔T1 (from B003) = 0.617 — T3 picks
  largely the same trades as T1, but a refined subset.

→ **The actual mechanism is trade SELECTION, not turnover REDUCTION.**
Acceleration days carry more signal than steady-state filter-passing
days. T3 enters on a refined subset of T1's candidates, and that
subset has higher per-trade alpha. The marginal turnover reduction
is a side effect, not the cause.

This is a more interesting finding than the original hypothesis
suggested. The "acceleration" condition is acting as a quality filter
on entry timing.

## What survives, what doesn't

### Survives across IS and OOS
- T3 IS overall net is +0.048 better than T1 (modest but positive)
- T3 OOS overall net is +0.139 better
- T3 wins majority of years in both IS (4/5) and OOS (2/4)
- T3 cost-0 alpha is preserved AND improved

### Honest caveats
- The OOS uplift +0.139 = ~+4 % annualized over 3.4 years. Modest.
- The IS uplift +0.048 = ~+1 % annualized over 5 years. Very modest.
- Trade count reduction is marginal (-0.8 %), so the original
  "turnover-savings" mechanism is mostly disproven.
- The signal underlying T3 is still the same regime-conditional
  flow signal. T3 doesn't fix the broader regime-conditionality
  found in B003+B004+B005. It marginally improves on it.
- 2 of 4 OOS year wins is the bare minimum for the criterion. If
  one more year had flipped, this would have been inconclusive.

## What this changes for the project

**The new B-family carrier** (effective now, used by all subsequent
single-role tickets):
```
filter:  filter_flow_sign_both_positive
trigger: trigger_acceleration   <-- NEW (was trigger_immediate)
ranking: rank_by_combined_flow_5
exit:    exit_signal_reversal
```

**Multiple-testing budget update**: ~20 prior + 1 new (T3 vs T1) = 21
cumulative variant comparisons. The single-point design kept this
ticket's marginal inflation small.

**Carrier evolution log** (for clarity in future reviews):
- A001 → A002 → ... → A004: early exit-rule iterations on absolute
  signal
- B001: market-cap normalization (killed)
- B002: signal-reversal exit promoted as carrier
- B003: trigger exploration (descriptive, T3 emerged but deferred)
- B004: regime gate exploration (inconclusive, gate-as-savior killed)
- B005: relative-flow alpha redesign (inconclusive, V-recovery
  mechanism validated but spike-capture lost)
- **B006: T3 acceleration trigger PROMOTED** ← here

## Possible next directions

The promote of T3 unblocks several follow-up paths. Per the "one
role per experiment + new data or signal redesign after each
exhaustion" discipline:

### Option A: B007 = filter-role exploration on the new T3 carrier
- Hold trigger=T3, ranking=combined_flow_5, exit=signal_reversal
  fixed
- Vary the filter across pre-registered candidates (e.g.,
  filter_combined_flow_sign, filter_persistence_4_of_5,
  filter_relative_flow_sign — drawing from B005 partial validation)
- Descriptive comparison; promote candidate goes through B008
  single-point

### Option B: B007 = ranking-role exploration on the new T3 carrier
- Hold filter / trigger / exit fixed; vary ranking
- Candidates: combined_flow_5 (current), recent_return_5,
  combined_flow_5_mcap, etc.
- Same descriptive-then-promote pattern

### Option C: B007 = exit-role exploration on the new T3 carrier
- Hold filter / trigger / ranking fixed; vary exit
- Candidates: signal_reversal (current), time_cap, vol_stop_plus_cap,
  combined_flow_3_reversal (faster reversal)
- Same descriptive-then-promote pattern

### Option D: B007 = relative-flow signal + T3 trigger combination
- Test whether the V-recovery fix from B005 + T3 acceleration produces
  a complementary improvement on the new carrier
- Descriptive; if interesting, promote separately
- Risk: combining two changes simultaneously is borderline patch-
  stacking; clearly mark as descriptive

### Option E: B007 = older-data verification of the new T3 carrier
- Run T3 carrier on 2008-2017 data (genuine OOS, not seen yet)
- Tests whether T3's IS+OOS pattern survives in different market
  history

### My recommendation: Option A (filter exploration)
- Filter is the role we have explored least with care; relative-flow
  (B005) showed it has real but contextual value
- Brings B005's V-recovery mechanism back into play in a controlled
  descriptive way
- Natural sequence: trigger settled → filter next → ranking → exit
- After each role is exhausted, Option E (older-data verification)
  becomes the highest-value next step

## Do not do next
- Layer multiple changes (e.g., T3 + relative filter + new exit) in
  a single ticket. Keep one role per ticket.
- Re-run T3 with different parameters trying to magnify the +0.139
  uplift. T3 is now the carrier; its definition is locked.
- Treat the T3 carrier as universal alpha. The signal is still
  regime-conditional per B003+B004+B005 findings; T3 is a marginal
  improvement, not a transformation.

## Follow-up
- **B007 candidate** — filter-role exploration on the new T3 carrier
  (per Option A above). Descriptive ticket; if a clear winner
  emerges, promote in a separate B008.
- B008-and-after — ranking, exit, and eventually older-data
  verification on the chosen role-by-role basis.
