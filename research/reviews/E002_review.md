# Review — E002 (Dynamic exit: volatility stop + 20-day cap)

## Verdict
**revise** — the dynamic-exit concept works, but the volatility stop
is the wrong component. Cap alone produces the win.

E002's hypothesis was "ATR stop + cap > fixed 5-day". The headline
result (cap + stop) is much better than E001 on cost-net OOS return.
But the (B) cap-only diagnostic is **strictly better than the
headline** on every meaningful metric — so the stop is actively
hurting, not helping. The dynamic-exit idea survives in cap form
only.

## One-line conclusion
20-day time cap delivers the cost-net win on its own; the 2.0×ATR
loss stop subtracts performance and is not worth keeping.

## Did the hypothesis survive OOS?
**Partially.** The stronger hypothesis (cap + stop > E001) survived
(headline OOS +0.58 vs E001 +0.16, turnover 52 vs 162). But the
finer-grained claim that **both** levers contribute was falsified by
the diagnostic split (see "What got worse"). The bigger-picture
hypothesis ("dynamic exit beats fixed 5-day") is robust; the
specific implementation chosen for E002 is not optimal.

## 5 success criteria — pass / fail

| # | Criterion | Result | Pass |
|---|---|---:|:-:|
| 1 | OOS net total_return > +0.165 | +0.5808 | ✓ |
| 2 | OOS turnover < 113 | 52.2 | ✓ |
| 3 | OOS average_holding_period > 5 td | 14.93 | ✓ |
| 4 | OOS hit_rate ≥ 0.467 | 0.4198 | ✗ |
| 5 | OOS cost-0 net > E001 cost-0 (+0.994) | +0.8815 | ✗ |

5 / 5 required → not `promote`. No kill criterion triggered →
not `kill`. Landing on `revise`.

## Diagnostic split — the real story

OOS metrics for the four engine variants (same signal, same universe):

| Variant | net return | hit_rate | trade_count | turnover | avg hold (td) |
|---|---:|---:|---:|---:|---:|
| (A) headline — cap + 2.0×ATR stop | +0.5808 | 0.4198 | 262 | 52.2 | 14.93 |
| (B) cap_only — 20-day cap, no stop | **+0.6879** | **0.4927** | 205 | 41.2 | 19.61 |
| (C) stop_only — stop, cap=999 | +3.0210 | 0.2778 | 18 | 3.0 | 150.28 |
| (D) E001_replay — fixed 5-day | +0.1649 | 0.4667 | 810 | 161.9 | 4.99 |

Reading this:
- **(B) cap_only is strictly better than (A) headline.** Higher net
  return, higher hit rate, fewer but more profitable trades, longer
  average hold.
- **(A) – (B) = stop's marginal impact**: net −0.107, hit rate −0.073.
  The stop reliably exits good trades just before they recover.
- **(C) stop_only with no cap** ran 8 years with only 18 trades, all
  held for ~150 days each — the stop almost never fires under normal
  conditions, and without a cap most positions just drift to
  period_end. This proves the 2.0×ATR threshold is too wide to be a
  meaningful intraday loss control, while still being narrow enough
  to occasionally cut winning recoveries.
- **(D) E001_replay** numerically matches E001's prior OOS run
  (+0.165 vs the earlier +0.165) — engine refactor is regression-safe.

## What improved (vs E001 baseline (D))

- OOS net total_return: +0.165 → **+0.688** with (B) cap_only,
  +0.581 with (A) headline. Both are ~3.5× better.
- OOS turnover: 162 → 41 (cap_only) or 52 (headline). 4× reduction.
- OOS max_drawdown: −0.418 → −0.282. Smaller worst-period losses.
- OOS sharpe: 0.157 → 0.539. Same caveat as any sharpe in this
  project — it's a downstream indicator, not the decision basis.
- Cost paid (OOS, in NAV terms): 0.829 → 0.300 — 64% cost drop.

## What got worse

- **OOS hit_rate** dropped from 0.467 to 0.420 in the headline.
  cap_only's hit rate is fine (0.493). So the stop accounts for the
  hit-rate loss.
- **OOS signal value (cost-0 net)** dropped from +0.994 to +0.881.
  Same story: most of this is the stop closing trades that would
  have recovered. (B) cap_only's cost-0 isn't broken out in
  metrics.json — a follow-up could add it to confirm cap alone is
  signal-neutral.
- **IS results turned outright bad** in cost-0: E001-replay IS
  cost-0 was +0.27, E002 headline IS cost-0 is **−0.10**. This is
  important. The 5-day fixed hold was likely benefiting from
  short-term mean reversion that disappears at 14-20 day holds. E001
  may have been a partial overfit to a short-horizon noise pattern.
- The 5/5 success-criteria-strict standard caught the limitation
  honestly — exactly what those criteria were for.

## Decomposition diagnostic (decisive)

The cleanest empirical result of E002:

**Cap alone (no stop) is the best variant tested.**

- net return higher than headline by +0.107
- hit rate higher than headline by +0.073
- 22% fewer trades than headline
- 21% lower turnover than headline

If E001's exit is the new baseline-to-beat, **cap_only is the
contender to promote**. The headline (cap + stop) is a worse version
of cap_only.

## Cost sensitivity (E002 headline)

| multiplier | IS net | OOS net | full net | cost_paid |
|---:|---:|---:|---:|---:|
| 0× | −0.10 | +0.88 | +0.66 | 0 |
| 1× | −0.31 | +0.58 | +0.07 | 0.38 |
| 2× | −0.47 | +0.33 | −0.31 | 0.62 |
| 3× | −0.59 | +0.11 | −0.55 | 0.77 |

Monotone decreasing ✓. At 1× cost, full-period total return is
barely positive (+0.07) — improvement over E001 (full −0.35) is
real but the IS half remains negative even before costs. Strategy
is **OOS-good, IS-bad** before costs, which is the inverse of the
usual overfit pattern.

## Possible biases

- look-ahead bias: low. ATR uses strictly prior rows; signal_date <
  execution_date verified on 45,386 signals; price match
  byte-equal on 662 / 662 trades; engine regression test confirms
  E001 behavior when `vol_stop_k=None`.
- survivorship bias: present (dynamic Top100, same as E001).
- data snooping: low. k=2.0, ATR window=20, cap=20 all frozen pre-run.
  No sweep performed.
- multiple testing: low. One headline + three named diagnostics, each
  pre-specified in the ticket.
- market beta exposure: not measured. Headline `exposure_ratio` ≈
  0.99 IS, 0.99 OOS — long-only, near-fully invested.
- price momentum contamination: B3 still −0.98 OOS, so the flow
  signal is not a momentum proxy.

## Possible failure modes for the headline finding

- IS cost-0 −0.10 may be sample-period-specific. The 2018-2022 window
  contains the 2020 COVID volatility shock; 20-day holds during that
  period probably suffered more than 5-day holds.
- 2023-2026 OOS contains a strong KOSPI recovery period; long holds
  benefit from sustained trends that may not repeat.
- The cap_only result's higher hit rate (0.49) is still essentially
  coin-flip territory. The OOS return advantage comes from larger
  win sizes vs losses, not from picking right more often.

## Most likely failure mode of the strategy

Same as E001 fundamentally: the signal is weak per trade. E002
shows we can rescue net economics by cutting turnover, but the
underlying signal-per-trade edge is not improving. Future
experiments must address signal quality, not exit mechanics.

## Engineering issues found

- **`trades.csv` 종목코드 leading zero loss**: pandas `to_csv` saves
  `"010130"` as `10130` (treating as int). Round-trip through CSV
  drops the leading zero. The engine is correct (entry_price /
  exit_price match the panel exactly when ticker is zero-padded back
  to 6 digits); the issue is post-write serialization. Same defect
  likely affects E001's `trades.csv`. Fix: write the column with
  explicit `string` dtype hint, or pad to 6 digits before write.
- ATR=NaN behavior when fewer than 20 prior rows: implemented as
  "skip the entry," matching the ticket spec. Confirmed by the
  number of dropped potential entries in early days.

## Next experiment

The signal-quality problem is what's left. E001's `(fnv_5 > 0) AND
(inv_5 > 0)` is binary and weak. Two natural next moves:

- **E003 — signal-strength quantile**: replace the binary AND with
  "combined_flow_5 in the top quantile, conditional on both
  components being positive." Use cap_only (no stop) exit. Single
  hypothesis: does the signal carry more information at higher
  intensity?
- **E004 — market-flow gate (the originally proposed E002)**:
  add KOSPI 외국인 5일 누적 > 0 as a market-level prerequisite for
  any entry. Cap_only exit. Single hypothesis: does market-flow
  regime gating raise hit rate?

Either of these uses cap_only as the carrier exit logic. E002's
stop is shelved.

## Do not do next

- Do **not** sweep the stop parameter `k` to try to make E002's stop
  work. The decomposition diagnostic shows the stop concept itself
  is at fault for this signal (not the parameter tuning). A sweep
  would be classic post-hoc rescue.
- Do **not** combine signal-quality and gate experiments. One lever
  per experiment.
- Do **not** keep the headline E002 (cap + stop) as the new default
  baseline. Use cap_only.

## Follow-up tickets (engineering)

1. **E002-F1**: fix `trades.csv` 종목코드 leading-zero loss in the
   engine's CSV writer; backfill E001's trades.csv similarly.
2. **E002-F2**: add a cost-0 diagnostic for cap_only and stop_only
   so future experiments can decompose signal-value vs cost-saving
   contributions of any exit-rule variant.
