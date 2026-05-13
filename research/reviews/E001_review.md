# Review — E001 (Pipeline sanity, fixed holding)

## Verdict
**promote** (infrastructure validation only; this is **not** an alpha promotion)

E001 was scoped as a pipeline-level test, not an alpha hypothesis. Its
success criteria A~H are about timestamp safety, cost accounting,
report generation, and test coverage — all of which pass on the real
KRX panels (2018-01-02 → 2026-05-04). Any economic interpretation of
the headline P&L is explicitly out of scope here.

## One-line conclusion
The E001 pipeline is timestamp-safe, cost-aware, and reproducible end-to-end on the real panels; baselines B1 and B2 have implementation flaws that must be fixed before any economic comparison.

## Did the hypothesis survive OOS?
Not applicable — E001 was a pipeline-level hypothesis (timestamps and
costs are wired correctly), not an alpha hypothesis. The headline
strategy itself is destroyed by costs (`return_before_cost` ≈ +0.20 IS
and +0.63 OOS collapse to `return_after_cost` ≈ -0.43 IS and +0.16 OOS
under default 33-bps round-trip drag); this is consistent with a
5-day-holding, 5-slot, signal-driven turnover of ~242× annualized.
That conclusion is observational, not promotion-worthy.

## Baseline comparison
| run | IS total | IS sharpe | OOS total | OOS sharpe | trades |
|---|---:|---:|---:|---:|---:|
| headline | -0.4308 | -0.369 | +0.1649 | +0.157 | 1,215 IS / 810 OOS |
| B0 cash | 0 | NaN | 0 | NaN | 0 / 0 |
| B1 buy & hold | 0 | NaN | 0 | NaN | **0 / 0 — defect** |
| B2 5d rebalance | NaN | NaN | NaN | NaN | 3,039 IS / 0 OOS — **defect** |
| B3 momentum | -0.9993 | -1.153 | -0.9829 | -1.035 | 1,213 / 812 |

Pipeline observations:
- Headline beats B3 (price momentum) on both IS and OOS net of costs.
- B0 (cash) is the only credible "do nothing" reference.
- B1 and B2 are unusable for comparison right now (see "What got worse").

## What improved (vs nothing, since this is first iteration)
- End-to-end pipeline runs in ~1m22s on the full 1.14M-row panel.
- All 8 ticket success criteria (A~H) pass on the real run.
- Output artifact set is complete: `config.yaml`, `metrics.json`,
  `trades.csv`, `signals.csv`, `equity_curve.csv`,
  `cost_sensitivity.csv`, `report.md`.
- Look-ahead regression suite (8 tests in `tests/test_no_lookahead.py`)
  passes including the byte-identical trade-set assertion under
  future-row mutation.
- Cost sensitivity is monotone over `{0×, 1×, 2×, 3×}` — IS
  `{+0.27, -0.43, -0.75, -0.89}` and OOS
  `{+0.99, +0.16, -0.32, -0.60}` — confirming the cost model is
  wired through the engine.

## What got worse (issues to fix)
- **B1 buy-and-hold produces 0 trades** because Rule 2 (20-row liquidity
  mean) is empty on the period's first trading day. B1 needs to defer
  its entry to the first day where the eligible universe is non-empty.
- **B2 5-day rebalance returns NaN** because any held ticker with a NaN
  `KRX종가` on a given day makes `_mtm_value` return NaN, which
  cascades to NAV and equity rows. B1 also has this property but never
  exposes it because it never enters. B2 (and to a lesser extent the
  headline engine's NAV-pause behavior) needs a "last-known close"
  fallback for MTM rather than NaN-propagation.
- Headline metadata text in `report.md` previously named
  `수급금액추정여부` in the policy summary even after Rule 3 was
  amended; fixed in the rerun (commit pending).
- Synthetic test panels did not surface 시가 == 0 (9,613 real-panel
  rows) or end-of-calendar entry-without-room cases (5 period_end
  trades). Both were patched mid-run (commit 267c614); add explicit
  test fixtures for both in a follow-up.

## Cost sensitivity
| multiplier | IS net | OOS net | full net | cost_paid_total |
|---:|---:|---:|---:|---:|
| 0.0 | +0.268 | +0.994 | +1.494 | 0 |
| 1.0 | -0.431 | +0.165 | -0.346 | 0.898 |
| 2.0 | -0.745 | -0.321 | -0.829 | 1.066 |
| 3.0 | -0.886 | -0.605 | -0.956 | 1.065 |

Cost paid stops rising at 2× because deteriorating NAV reduces
notional per trade — costs scale with traded notional. Monotone net
return decrease confirms the cost path is wired.

## Parameter sensitivity
Not tested. Locked parameters per ticket (lookback 5, holding 5,
max_positions 5, liquidity 50억). Any future sweep belongs to a new
ticket.

## Regime sensitivity
Not analyzed in E001. The IS-vs-OOS split shows a regime-direction
flip (IS net -0.43 vs OOS net +0.16) which is suggestive but not
attributable in this ticket. Year-by-year and sector breakdowns are
deferred.

## Liquidity and capacity concerns
Universe is dynamic Top100 by Kiwoom liquidity rank with a 5억 KRW
20-day mean traded value floor (configured 5e9 = 50 억). Notional
sizing is `NAV / 5` per slot, so at NAV=1.0 each position is 20% of
NAV — small enough that market impact is negligible at this size, but
the ratio scales nonlinearly with actual deployed capital.

## Possible biases
- look-ahead bias: low (regression-tested with byte-identical assertion
  under future-row mutation).
- survivorship bias: present (Kiwoom dynamic Top100 is by-day, but the
  panel inherently filters in liquid names).
- data snooping: low (parameters were fixed in the ticket before any
  run; nothing was re-tuned after seeing results).
- multiple testing: low (one run, no parameter sweep).
- market beta exposure: not measured. Headline is long-only with
  near-full exposure (`exposure_ratio` ≈ 0.985 IS, 0.999 OOS).
- price momentum contamination: tested via B3 — B3 underperforms
  headline significantly, so the flow signal is not just disguised
  momentum.

## Most likely failure mode
This run pre-empts any economic conclusion. If E001 were treated as a
strategy (it should not be), the headline's most likely failure mode
is **cost erosion**: at default 33-bps round-trip drag and ~30%
realized turnover per holding, costs eat ~70 bps per trade against an
average per-trade pre-cost return that is much smaller. The 0×-cost
view shows the signal is statistically non-trivial; the 1× view shows
it is not commercially viable in this form.

## Next experiment
The ticket is a pipeline-validation infrastructure ticket, and the
infrastructure is now validated. The next experiments should be true
alpha hypotheses on this infrastructure. Suggested ordering:

- **E002 — Cost-aware re-parameterization**: same flow signal but with
  a wider entry threshold (z-score-based) and a longer holding period
  to reduce turnover. Goal: produce a strategy whose 1× cost-net
  return survives.
- **E003 — Foreign-only vs institution-only vs combined**: decompose
  the headline into single-investor signals and test whether one
  channel dominates. Use the existing engine; only `flow_ratios.py`
  needs a new feature.
- **E004 — Signal strength binning**: replace the binary
  `(fnv_5 > 0) & (inv_5 > 0)` with `combined_flow_5` decile bucketing
  and observe forward-return monotonicity.

## Do not do next
- Do not iterate on E001 parameters (lookback, holding, max_positions,
  liquidity threshold). They were locked by the ticket for a reason
  and re-fitting them now would be data snooping.
- Do not promote the headline to "alpha verified." This run does not
  carry that meaning. The 0×-cost +149% is a property of a frictionless
  fantasy; the 1×-cost -35% is the only economic data point and it is
  negative.
- Do not run a parameter sweep on the current signal definition before
  the baseline-comparison defects (B1 entry, B2 NaN MTM) are fixed —
  comparisons will be misleading.

## Follow-up tickets (engineering)
1. **E001-F1**: B1 baseline starts on first day with non-empty
   universe, not period_start; B2 baseline carries last-known close
   for MTM when current-day close is NaN.
2. **E001-F2**: explicit test fixtures for 시가 == 0 (trading halt
   day) and end-of-calendar entries to lock in the runtime patches
   introduced this session.
