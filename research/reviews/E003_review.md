# Review — E003 (Market-flow gate over cap_only exit)

## Verdict
**kill** — the flow-based market gate alone does not improve over
cap_only, and is statistically indistinguishable from a simple
KOSPI 5-day price-momentum gate. The Layer-4 macro hypothesis is
not validated in this specific test.

A side observation (double_gate beats cap_only) is interesting but
strictly **post-hoc** and must not be chased without a new pre-
registered ticket.

## One-line conclusion
KOSPI 외국인+기관 5일 누적이 KOSPI 5일 가격 모멘텀과 같은 거래일 결과를 만든다 — 즉 flow gate는 price gate의 변형.

## 5 success criteria — pass / fail

| # | Criterion | Result | Pass |
|---|---|---:|:-:|
| 1 | OOS net (A) > cap_only OOS (+0.688) | +0.5876 | ✗ |
| 2 | OOS trade_count (A) ≥ 103 | 150 | ✓ |
| 3 | OOS hit_rate (A) > inverted (C) | 0.460 > 0.455 | ✓ (margin razor-thin) |
| 4 | (A) − (D price gate) OOS ≥ +0.03 | −0.018 | ✗ |
| 5 | cost-0 (A) > cost-0 cap_only | 0.757 < 0.937 | ✗ |

Criterion 1, 4, 5 all fail. The directional gate-sign test (3)
passed numerically but with a 0.5%p margin on 150 vs 145 trades —
not statistically meaningful.

Both kill criteria triggered:
- OOS net total_return (A) ≤ cap_only OOS  ✓ (kill)
- (A) − (D) OOS net difference < 0.01 ✓ (kill)

## Diagnostic split — the empirical structure

OOS metrics for the five engine variants (same signal, same
universe, same cap_only exit, varying only the gate):

| Variant | net | hit | trade | turn | hold | max_dd | sharpe |
|---|---:|---:|---:|---:|---:|---:|---:|
| (A) headline — flow gate | +0.588 | 0.460 | 150 | 27.6 | 20.0 | −0.365 | 0.62 |
| (B) cap_only — no gate | **+0.688** | **0.493** | 205 | 41.2 | 19.6 | −0.362 | 0.59 |
| (C) inverted gate — gate-off only | +0.180 | 0.455 | 145 | 28.9 | 20.0 | −0.235 | 0.24 |
| (D) price gate — KOSPI 5d return > 0 | +0.606 | 0.490 | 200 | 39.9 | 19.8 | −0.385 | 0.52 |
| (E) double gate — flow AND price | **+0.724** | 0.467 | 150 | 27.6 | 20.0 | −0.350 | 0.74 |

Cost-0 OOS:
- cost_0_headline (A): +0.757
- cost_0_cap_only (B): +0.937
- (B) > (A) by +0.18. Cap_only carries more raw signal value than
  any gated variant.

Gate agreement on the 2,046-day calendar:
- flow gate ON: 867 days (42 %)
- price gate ON: 1,842 days (90 %)
- both agree (same direction): 1,025 days (50.1 %)
- both ON: 844 days

## Reading the numbers

1. **Flow gate ≈ price gate.** OOS net difference is −0.018 (well
   under the +0.03 threshold for criterion 4). The two filters land
   on different specific days (50 % agreement only) but average to
   essentially the same trade outcomes. The flow gate is not adding
   information beyond price momentum at this time scale.
2. **Cap_only wins.** No gate variant beats the un-gated cap_only
   on OOS net or hit_rate. Gating slightly increases sharpe by
   reducing variance, but at the cost of return.
3. **Inverted gate (C) net +0.18.** Significantly worse than
   headline. Confirms the gate has *some* directional information
   (criterion 3 passes), but the gate-off subset is far from "kill
   the strategy" bad — its hit_rate 0.455 is barely below A's 0.460.
   This is the strongest piece of evidence that the gate is a weak
   filter on noisy regime dependence, not a sharp on/off switch.
4. **Double gate (E) +0.724 vs flow alone +0.588.** 23 days are
   flow-ON-but-price-OFF; trades from those 23 days drag flow-alone
   net down by 0.136. So "외국인 자금 유입 + 시장 가격은 떨어짐" is
   the trap regime — chase-buying into foreign accumulation while
   the market is selling off costs ~0.14 net over 8 years. This is
   a real finding but it emerged from the diagnostic, **not from
   the registered hypothesis**, and must not be promoted directly.
5. **IS is bad across all gates.** Headline IS net −0.314, cap_only
   −0.334, price gate −0.079, double gate −0.267. IS cost-0 also
   negative in most variants. The strategy as a whole struggles in
   2018-2022 even with gates. OOS positive results may be regime-
   specific to 2023-2026 KR equity environment.

## Confounding analysis (criterion 4 detail)

| Comparison | OOS net | Δ vs cap_only |
|---|---:|---:|
| (B) cap_only — no gate | +0.688 | 0 |
| (D) price gate alone | +0.606 | −0.082 |
| (A) flow gate alone | +0.588 | −0.100 |
| (E) flow AND price | +0.724 | +0.036 |

Reading: every "single gate" variant subtracts from cap_only. The
flow gate subtracts slightly more than the price gate (so it is
**weaker** as a filter, not stronger). The conjunction (E) is the
only variant that exceeds cap_only, but it does so by a thin margin
that could be sampling variance.

## Cost sensitivity (E003 headline)

Monotone decreasing verified. At default 1×, OOS net is +0.588.
Pattern qualitatively matches E002 cap_only. No new insight.

## What survived from the experiment

- **Pipeline (timestamp safety, deterministic CLI, reports)**: all
  green. The Layer-4 plumbing (market-flow loader, gate feature
  builder, gated strategy module, gate-timeseries output) now exists
  as reusable infrastructure. Future Layer-4 experiments do not have
  to re-build this.
- **`종목코드` leading-zero fix (E002-F1)** shipped and verified.
  trades.csv now preserves 6-digit ticker codes.
- **Loader spec amendment** for tail-NaN handling (2025-12 onward
  market_flow missing data) was applied mid-run and documented. The
  amendment does not introduce look-ahead — missing dates become
  conservative gate-off, same as start-of-period.

## Possible biases

- look-ahead bias: low. Gate features use only prior-row data;
  no-lookahead regression test on a synthetic panel still passes.
- survivorship bias: same as E001/E002.
- data snooping: low for the **registered** hypothesis. The post-
  hoc double_gate observation is itself a snooping risk that must
  not be promoted.
- multiple testing: criteria 1–5 + four diagnostics (B, C, D, E).
  No Bonferroni was applied because each criterion has a directly
  testable yes/no formulation; the three failures are unambiguous.
- self-referential gate: KOSPI aggregates include our universe
  stocks. Magnitude check deferred — but given the gate **failed**,
  self-reference is no longer a concern (we cannot be claiming
  spurious alpha from a self-referencing gate when the gate didn't
  produce alpha).

## Most likely reason for the failure

Two-line explanation:
1. KOSPI cumulative net buy by foreigners + institutions is tightly
   correlated with KOSPI 5-day price change. The two measure the
   same regime variable at this time scale.
2. KOSPI 5-day price change is itself a weak filter — most days are
   above zero (1,842 / 2,046 = 90 %), so it doesn't filter much.
   The flow gate is more selective (42 % ON days), but the
   additional days it excludes happen to be average rather than
   especially bad — so the more aggressive filtering removes good
   trades along with bad ones.

In one sentence: **the gate at 5-day window aggregates too much
information at the same time scale as the signal, leaving no
separate Layer-4 contribution.**

## Engineering issues found / fixed this iteration

- **Fixed**: trades.csv 종목코드 leading-zero loss (E002-F1).
- **Fixed-by-amendment**: load_market_flow strict-NaN rule (allowed
  recent-data tail to fail loud; now drops with logging).
- **Still open**: B0_cash and B1_buy_and_hold both report 0 trades
  / 0 return. B2_universe_5d_rebalance reports NaN. These baselines
  are not informative as currently implemented. Same defect was
  flagged in E001 review. Worth fixing before any future strategy
  comparison.

## Next experiment

Two viable directions, in order of priority:

- **E004 — Signal-strength quantile** (the deferred candidate from
  the earlier discussion). Replace the binary `(fnv_5 > 0) AND
  (inv_5 > 0)` with "top quintile of `combined_flow_5` daily
  cross-section, plus both components positive." Cap_only exit.
  Tests whether the signal has more information at higher intensity.
  Independent of Layer 4 entirely — cleanly tests Layer 1's
  intrinsic edge.
- **E005 (or whatever number) — Trap-day regime gate**, a clean
  re-test of the post-hoc double_gate observation. Pre-register:
  "exclude entries on days where foreign net flow into KOSPI is
  positive while KOSPI 5d price change is negative" (the trap
  regime found in E003 diagnostic). Cap_only exit. Stronger
  hypothesis because we have specific reason to expect a positive
  result, but exactly because of that, we need to be more careful
  about not double-counting evidence (E003's diagnostic data
  contributes to motivation but cannot be re-used as confirmation
  — IS/OOS boundary fresh re-evaluation is mandatory).

I lean toward **E004** because:
- Cleaner. Tests one well-defined intervention without re-using
  E003's diagnostic data.
- Addresses the actual bottleneck (hit_rate at 49 % is the ceiling).
- Doesn't propagate the data-snooping risk of E005.

## Do not do next

- Do **not** sweep the gate window (3d, 10d, 20d) hoping to find a
  time scale where the gate decouples from price. That is post-hoc
  rescue.
- Do **not** combine the gate with a stop or a different exit rule
  to "make it work." The gate's failure is independent of exit.
- Do **not** add new data sources (e.g., USD/KRW, US futures) at
  this point to revive Layer 4. If we do that, it's a new
  experiment with a new hypothesis, not E003 redux.
- Do **not** promote double_gate directly.

## Follow-up tickets (engineering)

1. **E003-F1**: B0_cash / B1_buy_and_hold / B2 baselines still
   broken. They've been broken since E001 and were not addressed
   here. Either fix (last-known close MTM fallback in baselines, B1
   entry-on-first-eligible-day) or drop them from the report
   permanently with a clear note. Drop is acceptable if they aren't
   carrying interpretive weight.
