# Review — B011 (Gate-only carrier on full 2010-2026 timeline)

## Verdict
**NOT VIABLE** per pre-registered logic (H1 cumulative > 0 fails
decisively: V1 cumulative = −94.79 % over 16 years).

The "Option D" path proposed at the end of B010 — adopting simple
regime-following (B004 (c) gate-only top-5 mcap) as the project's
deployable answer — is **not viable**. Same magnitude of failure
as the flow-based carrier (B010 V1 = −87.8 % over the same span).

Both candidate strategies fail catastrophically over 16 years on
this universe with these costs.

## One-line conclusion
Gate-only 도 carrier 도 16년 누적 -90% 대 catastrophic 손실. 활성
overlay 전략 모두 같은 universe 의 cap-weighted hold (+2009% per the
breadth basket; 진짜 KOSPI 도 +100% 이상) 대비 -2000pp 이상 underperform.
우리 hypothesis class 자체가 알파가 없거나 음수.

## Headline numbers (V1 = gate-only top-5 mcap with 200d SMA gate)

| Metric | Value | Pre-registered threshold | Pass |
|---|---:|---|:---:|
| **H1 cumulative net (16yr)** | **−94.79 %** | > 0 | ❌ |
| H2 vs V2 delta | **−2104.31 %** | ≥ V2 − 10 pp | ❌ |
| H3 spike capture: 2010 / 2025 / 2026 | +11.06 % / +27.97 % / +46.25 % | all positive | ✓ (all small +) |
| **H4 V1 max DD vs V2 max DD** | **−98.04 %** vs **−34.49 %** | V1 lower by ≥ 5 pp | ❌ (V1 WORSE by 64 pp) |
| H5 positive years | **5 of 16** | ≥ 8 | ❌ |
| Annualized return | −17.90 % | — | — |
| Sharpe | **−0.73** | — | — |

**4 of 5 hypotheses fail.** H1 fails catastrophically. Verdict =
NOT VIABLE per pre-registered logic.

## V2 (KOSPI proxy buy-and-hold) — important caveat

V2 was specified as "cumulative product of `cap_weighted_return` from
market_breadth_kospi_2010_2026.csv." The literal implementation
produces +2009.52 % over 16 years (annualized +22 %).

**This is NOT broad KOSPI.** Investigation shows:
- KOSPI's historical annualized return is ~6-8 %
- The breadth file's `cap_weighted_return` is the cap-weighted return
  of the **dynamic top-100 universe** (which changes daily), not the
  full KOSPI
- Dynamic top-100 has survivorship bias built in (stocks that leave
  the top-100 vanish from the calculation, while incoming stocks join
  retroactively in their reporting)
- Realistic KOSPI total-return cumulative 2010-2026 would be roughly
  +100 % to +150 %

So V2 is an inflated benchmark. But V1's failure (−94.79 % cumulative)
is decisive against ANY reasonable benchmark including just holding
KOSPI ETF (~+100 %), so the V2 issue doesn't change the verdict.

The data finding itself is important: **the dynamic top-100 universe
appears to return +2000 % cumulatively (survivorship bias) yet our
active overlay returns −95 %**. The overlay actively destroys value
relative to even a survivorship-biased buy-and-hold.

## Year-by-year (V1, all 16 years)

| year | V1 net | positive? |
|---|---:|:---:|
| 2010 | +11.06 % | ✓ |
| 2011 (Eurozone) | −16.43 % | ✗ |
| 2012 | +14.69 % | ✓ |
| 2013 (taper) | −12.55 % | ✗ |
| 2014 | +5.47 % | ✓ |
| 2015 (China) | −8.84 % | ✗ |
| 2017 (rally) | −10.34 % | ✗ |
| 2018 (bear) | −38.31 % | ✗ |
| 2019 | −0.36 % | ✗ |
| 2020 (V) | −22.10 % | ✗ |
| 2021 | −24.34 % | ✗ |
| 2022 (bear) | −29.81 % | ✗ |
| 2023 (recovery) | −29.28 % | ✗ |
| 2024 (correction) | −8.88 % | ✗ |
| 2025 (rally) | +27.97 % | ✓ |
| 2026 (4mo) | +46.25 % | ✓ |

(Source: `reports/experiments/B011_gate_only_full_timeline/gate_only_year_breakdown.csv`)

5 of 16 positive (slightly better than flow carrier's 3 of 16, but
still far from H5's threshold of 8).

The pattern is clear: gate-following adds whip-saw losses during
choppy periods (most years 2011-2024). Only "clean trend" years (2010
recovery, 2012/2014 rally, 2025/2026 post-bear) deliver positive
contribution.

## Why gate-following fails over 16 years

Several mechanisms compound:

1. **Whip-saw losses**: KOSPI 200d SMA crosses many times per year.
   Each cross triggers a full exit and re-entry on 5 positions =
   high transaction cost burden. Multiple false crosses (gate flips
   ON then OFF within weeks) generate pure friction.

2. **Concentration risk**: top-5 by market cap = ~5 large names.
   Even when gate is correctly ON, a single bad pick (e.g., one of
   the top 5 underperforms broad market) drags the basket. Equal
   weighting magnifies this.

3. **Cash drag during gate OFF**: when gate is OFF, V1 is in cash.
   Cash misses upside on early gate-OFF (when market is just dipping
   before recovery, V1 sits out the recovery).

4. **Cost regime mismatch**: 1.5 / 20 / 5 bps assumed costs may be
   too low for 5-position turnover at high frequency. Actual costs
   would be higher.

5. **No edge in selection**: top-5 by market cap during gate-ON is
   a heuristic, not an alpha. It happens to work in some windows
   (2018-2026 hit a lucky stretch with 2025 spike) but doesn't
   produce edge across regimes.

## What this means strategically

### Both candidate strategies fail

- **Flow-based carrier** (T3+F3, B010): -87.8 % over 16 years
- **Gate-only top-5 mcap** (B011): -94.79 % over 16 years
- **Universe itself** (cap-weighted, survivorship-biased): +2009 %
  cumulative (realistic KOSPI ~+100 %)

The pattern: every active overlay we've tried destroys value vs just
holding the underlying universe. Our 27 cumulative variant
comparisons across B001-B009 plus the two true OOS tests (B010,
B011) have produced no positive-net strategy over 16 years.

### Implications

1. **Active short-term trading on Korean top-100 universe with our
   cost regime appears to be a losing game.** Costs + turnover +
   universe selection effects compound to negative net even when the
   universe itself is positive.

2. **The 2018-2026 OOS positive results were fortunate windows**,
   not signal. Both T3+F3 (+2.42 cost-0 OOS) and gate-only (+24 %
   OOS 2018-2026) happened to hit good periods. Neither replicates
   over 16 years.

3. **The user's stated goal ("outperform index + catch spikes")
   appears unreachable via any strategy we have tested**. The
   simplest version of "outperform" is to NOT actively trade — just
   hold the index. The user's goal might be intrinsically
   incompatible with active management within our hypothesis space.

### What we've definitively learned

- **Pre-registration discipline + new-data verification works.**
  B010 and B011 caught what 9 prior variant comparisons could not.
  Without these, the project would have shipped a deeply broken
  carrier.
- **The 5-day cumulative foreign+institution flow signal is not a
  stable Korean-equity alpha.** Proven across decades.
- **Simple regime-following via 200d SMA gate is not a stable
  alternative.** Proven across decades.
- **Mode C discipline preserved the integrity of past verdicts.**
  T3 (B006) and F3 (B009) remain as historical promotes despite
  the carrier failing verification.

## Multiple-testing budget

Cumulative: 28 prior + 1 (B011 has 3 variants but only V1 is the
candidate; V2 and V3 are sanity comparators). Total 29 cumulative
comparisons. The 2018-2026 dataset is exhausted as a testing
ground; the 2010-2026 dataset (with 2016 gap) is now also
substantially used.

## Possible B012 directions — strategic, not just tactical

### Option 1: Project conclusion / pivot
Accept that our hypothesis class (active overlay on Korean top-100
with current costs and 5-day flow / regime-gate signals) doesn't
produce viable strategies. Project deliverable becomes:
- A documented research finding ("these specific strategies don't
  work, here's the evidence")
- Recommendation to deploy a passive KOSPI ETF for the user's stated
  goal
- Honest closure

### Option 2: Major hypothesis pivot — different alpha class
Try a fundamentally different alpha. Candidates:
- **Pairs trading / mean-reversion** (cross-sectional, not
  trend-following)
- **Lower frequency** (monthly cumulative flow with monthly
  rebalancing — much less cost burden)
- **Different universe** (e.g., KOSDAQ small-cap, or KOSPI200 only
  — much more selective)
- **Macro overlay** (US futures signal, FX, rate signal to time the
  Korean market)
- **Volatility-managed beta** (risk parity on KOSPI + cash)

### Option 3: Investigate the failure further before pivoting
Diagnostic ticket asking specifically: "what made 2010 and 2025
work, and can we model that?" This is the same Option B from B010
review — a meta-signal hypothesis for "when does our type of
strategy work?"

### My recommendation: strategic conversation before B012

This is the second consecutive "NOT VIABLE" verdict in two
verification experiments. Three options are all major
direction changes, not patches on the current carrier. Before
designing B012, the user should choose direction.

Concrete recommendation framing:
- Option 1 is the most honest if the user accepts that systematic
  alpha in this hypothesis space is impossible
- Option 2 is the most ambitious but risks another 16-experiment
  cycle of patches on a new hypothesis
- Option 3 is the cheapest informative next step ("what made 2010
  and 2025 different?") and might inform whether Option 2 is even
  worth attempting

If forced to pick: **Option 3 first** (cheap, informative),
**then strategic conversation** about Option 1 vs 2.

## Carrier-evolution log update

- E001-E004, B001: early iterations
- B002: signal-reversal exit (carrier)
- B003: trigger exploration (T3 descriptive winner)
- B004: regime gate exploration (gate-as-savior killed)
- B005: relative-flow alpha (inconclusive)
- B006: T3 trigger PROMOTED
- B007-B008: filter exploration (F2 inconclusive)
- B009: F3 filter PROMOTED per Mode C
- **B010: VERIFY FAIL — carrier T3+F3 regime-conditional, not universal**
- **B011: NOT VIABLE — gate-only also fails over 16 years**

Status as of 2026-05-16: Both active candidate strategies in the
project have failed long-term verification. The carrier (T3+F3) is
on the books per Mode C but understood to be unreliable. No new
promote in pipeline.

## Do not do next
- Adopt either T3+F3 or gate-only as deployable strategy. Both
  proven to lose money over 16 years on this universe.
- Stack more layers on either failed carrier. Pre-registered
  discipline and budget exhaustion both rule this out.
- Try alternative gate window (50d, 100d) for gate-only — that
  would be data-snooping, and gate-only fails for structural
  reasons (whip-saw, concentration, cash drag) that wouldn't be
  fixed by window choice.
- Conclude that "Korean equity systematic alpha is impossible" —
  we have tested ONE hypothesis class. Other hypothesis classes
  may work.

## Follow-up
- **Strategic conversation with user** about Option 1 / 2 / 3 above.
- B012 design depends on user's choice.
- Possible immediate next-step (no Codex required): write a
  diagnostic memo on "what made 2010 / 2025 work" using existing
  data — Option 3, ~1 hour of analysis.
