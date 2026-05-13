# Review — E004 (Signal-strength top quintile)

## Verdict
**kill** — restricting to top-quintile signal strength reduces both
net return and raw signal value vs cap_only. The 5-day flow
signal's information content is **not** concentrated at the strength
tail.

## One-line conclusion
약한 신호 trade도 평균적으로 양의 기여를 한다 — 강도 분위로 잘라내면
hit_rate도 net return도 cost-0 정보 가치도 모두 떨어진다.

## 5 success criteria — pass / fail

| # | Criterion | Result | Pass |
|---|---|---:|:-:|
| 1 | OOS net (A) > cap_only OOS (+0.688) | +0.495 | ✗ |
| 2 | OOS hit_rate (A) > cap_only (0.493) | 0.478 | ✗ |
| 3 | OOS trade_count (A) ≥ 50 | 205 | ✓ |
| 4 | Monotonicity (top > mid > bot, both ≥ 30 trades) | bot trade_count = 0 | ✗ (technical) |
| 5 | cost-0 (A) > cost-0 cap_only (+0.937) | +0.716 | ✗ |

Kill criterion 1 (`net (A) ≤ cap_only`) triggered → `kill`.

## Diagnostic split

OOS metrics for the five quintile variants (same signal × universe ×
cap_only exit; only the quintile filter changes):

| Variant | net | hit | trade | turn | hold | sharpe |
|---|---:|---:|---:|---:|---:|---:|
| (A) headline — top quintile (5) | +0.495 | 0.478 | 205 | 41.3 | 19.4 | 0.45 |
| (B) cap_only — no quintile | **+0.688** | **0.493** | 205 | 41.2 | 19.6 | 0.59 |
| (C) bottom quintile (1) | ~0 | n/a | **0** | — | — | — |
| (D) middle quintile (3) | (computed) | 0.429 | (some) | — | — | — |
| (E) top decile (top 10 %) | (computed) | — | — | — | — | — |

Cost-0 OOS:
- cost_0_headline (A): +0.716
- cost_0_cap_only (B): +0.937
- (B) > (A) by +0.22. Quintile filter strips raw signal value.

Headline (A) and cap_only (B) coincidentally land on the same OOS
trade count of 205, which is striking — the quintile filter removes
roughly the same number of *opportunities* that cap_only's slot
mechanics would have naturally rejected anyway. So (A) and (B)
represent similar-sized trade sets that disagree on *which*
specific tickers to take. (B) wins on every metric.

## Reading the numbers

1. **Hit rate ordering directionally correct, magnitude tiny.** Top
   quintile 0.478 > middle 0.429. So strength quintile *does* carry
   some weak signal directionally. But top quintile (0.478) is still
   **below** the un-filtered baseline (0.493), meaning the top
   quintile is worse than the average of all positive-flow signals.
2. **Bottom quintile (C) returned 0 trades.** Combined with the
   safety filter `(fnv_5 > 0) AND (inv_5 > 0)`, bottom quintile
   essentially has no overlap with the positive-signal area —
   tickers with the *smallest* `combined_flow_5` tend to have at
   least one of fnv_5 or inv_5 negative, so they fail the safety
   AND. This is a mechanical artifact, not a deep finding.
3. **Cost-0 (A) − (B) = −0.22.** This is the headline failure
   number. If quintile filter were saving costs without losing
   signal, cost-0 would be similar across (A) and (B). Instead it
   drops by 22 % of starting NAV. **The quintile filter removes
   alpha along with the trades it removes.**
4. **The two-component AND safety filter** is mostly redundant
   under the top quintile: top quintile by `combined_flow_5`
   already implies both components are not too negative. But not
   strictly — a few cases where one component is positive and the
   other negative still make it into top quintile if the positive
   one is large. The safety AND drops those, and Codex confirmed it
   used post-quintile filtering per the spec.

## Why the hypothesis failed (best honest explanation)

The 5-day flow signal in E001-E003 had hit_rate ≈ 47 %. That number
is the **average** of all positive-flow days. When we slice that
average by intensity:
- Top quintile hit rate is 0.478 — slightly below the average
- Middle quintile hit rate is 0.429 — clearly below the average

So the within-positive-flow distribution of hit rates is **roughly
flat or slightly inverted at the high end**. The strong-flow days
are not the days that work better; if anything they're a bit
worse, possibly because strong flow appears at trend tops where
chase-buying is late.

This is consistent with three readings:
1. **Information is in the sign, not the magnitude** of 5-day
   cumulative flow. Magnitude noise washes out.
2. **Crowding penalty**: strong recent flow attracts more crowd
   trade; price has already moved before our entry at T+1 open.
3. **Time-scale mismatch**: 5-day cumulative flow magnitude reflects
   completed buying; the next 5-20 days of return are no longer
   driven by that completed flow.

All three readings point in the same direction: the strength
dimension at this window is not informative for short-term forward
return. A different window or a different signal-decomposition is
needed.

## Possible biases

- Look-ahead: low. Quintile uses only T-aligned candidates per
  signal_date; cross-section is over universe-eligible-at-T-1
  tickers, not future data. Tests pass.
- Survivorship: same as E001 (dynamic Top100).
- Data snooping: low for the registered hypothesis. (E) top-decile
  is held back as informational only — even though it was implemented,
  promoting it post-hoc is forbidden by the ticket.
- Multiple testing: criteria 1–5 plus four diagnostics; each
  directly testable. No Bonferroni applied, but the magnitude of
  failure on criteria 1, 2, and 5 is large enough that significance
  is not the concern — direction is.

## What survived

- **`종목코드` zero-padding fix** from E002-F1 still holds across
  E003 and E004 outputs.
- **Pipeline regression-clean**: 88 tests pass. Engine, baselines,
  features, universe, calendar, costs, metrics, report, market-flow,
  market-gate all green. No regression introduced by adding the
  E004 strategy module.
- **The infrastructure for cross-section quintile filtering** is now
  in `src/strategies/e004_strength_quintile.py`. Future experiments
  that want to test other quintile cuts or different cross-section
  scopes can reuse this code.

## Cumulative state of the strategy after E001 ~ E004

Four experiments. One concrete win:

| Experiment | Verdict | Carry-over |
|---|---|---|
| E001 fixed 5-day | promote (infra) | Pipeline validated |
| E002 vol-stop + cap | revise | **cap_only adopted** as default exit |
| E003 market-flow gate | kill | Layer 4 infra reusable, but flow gate ≈ price gate |
| E004 top quintile | kill | Strength dimension at 5-day window is not informative |

**Current best variant**: cap_only with the E001 binary signal:
OOS net +0.688, hit_rate 0.493, sharpe 0.59, turnover 41, avg hold
19.6 trading days. That is the strategy as it stands.

## What this tells us about the next experiment

We've now tested three "obvious" ways to improve the strategy and
none worked. That's information.

- Cost was the first-order problem (E002 fixed it via cap)
- Layer-4 market regime at 5-day window does not help (E003)
- Signal-strength quintile at 5-day window does not help (E004)

The remaining dimensions we have not touched:
1. **Signal time scale** — what if 5-day cumulative is the wrong
   window? Same signal at 1-day or 10-day might behave differently.
   But this is parameter sweeping in disguise unless we have a
   clear prior.
2. **Signal persistence** — what if it's the *consecutive* days of
   buying that carries information, not the strength of a single
   window? `foreign_persistence_5` (count of days with positive
   foreign net buy in last 5) is a different mathematical aspect of
   the same data. Already a candidate feature in CLAUDE.md §4.3.
3. **Investor-type decomposition** — what if "외국인 + 기관 합산" is
   the wrong aggregation? KIS exposes the institution split
   (증권/투신/은행/보험/연기금/사모/etc). Maybe one specific
   institution channel is the carrier.
4. **Different signal entirely** — abandon the 5-day cumulative
   flow framing. Try a flow-vs-price divergence signal, or an
   intraday-pattern signal, etc. Most ambitious; biggest reach.

## Next experiment

I lean toward **signal persistence (E005)** for these reasons:

- It's a *qualitatively different* aspect of the same data (count
  of positive-flow days vs sum of flow ratios). Tests a different
  hypothesis cleanly.
- No new data sources required — just count days, not magnitudes.
- The mechanical relationship to E001 binary is "binary checks if
  cumulative > 0 over 5 days; persistence checks how many of those
  5 days had positive component flow." Different math, same data.
- Cleanly addresses one specific reading from E004's failure
  analysis: maybe what matters is "how persistent was the buying"
  rather than "how big was the cumulative."

The other strong candidate is **investor-type decomposition (E006)**.
This is more ambitious and requires pulling new data from KIS — but
sticks within the data inventory we already inventoried. Worth
considering as the experiment after E005.

## Do not do next

- Do **not** sweep the quintile cut (decile, vigintile, top-N) to
  rescue E004. That is post-hoc rescue and the failure pattern
  (cost-0 dropping in tandem with trade count) tells us the issue
  is not the cut threshold — it's that strength itself doesn't
  carry information.
- Do **not** combine E004's quintile filter with another lever
  (market gate, vol stop) hoping the combination works. That's
  multiplicative complexity for a starting position that already
  failed.
- Do **not** promote (E) top decile diagnostic.

## Follow-up tickets (engineering)

No new engineering issues found this iteration. The pipeline
remained green throughout. B0/B1/B2 baselines still defective from
E001, still tracked.
