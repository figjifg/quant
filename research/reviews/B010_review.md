# Review — B010 (Old-data verification)

## Verdict
**VERIFY FAIL on ALL FOUR pre-registered hypotheses.**

The current B-family carrier (T3 trigger + F3 filter +
combined_flow_5 ranking + signal_reversal exit), promoted through
B003 → B009 on 2018-2026 data, produces **negative raw alpha**
(-0.099 cost-0 net) on 2010-2017 fresh OOS. This is the strongest
possible confirmation of the regime-conditionality concern that has
built across B003-B009 reviews.

Per pre-registered Mode C discipline (see B009 review +
[[feedback-experiment-discipline]]): **the F3 promote (B009 verdict)
is NOT undone — past verdicts stand.** But the carrier's regime-
conditional nature is now PROVEN, not just suspected.

## One-line conclusion
T3+F3 carrier 가 2018-2026 에서 OOS cost-0 +2.42 였는데 2010-2017
fresh OOS 에서 cost-0 -0.10. 같은 carrier, 다른 시대, 정반대 결과.
"이 alpha 는 universal 하지 않다" 가 진단이 아니라 검증된 사실이 됨.

## Headline numbers

### V1 (current carrier, T3+F3) on 2010-2017
| Metric | Value | Pre-registered threshold | Pass |
|---|---:|---|:---:|
| **cost-0 net total return (H1)** | **-0.099** | > 0 | ❌ |
| net total return (H2) | -0.711 | ≥ -0.20 | ❌ |
| positive years (H3) | 1 of 7 | ≥ 4 of 7 | ❌ |
| largest positive year fraction (H4) | 100 % (only 2010 +) | ≤ 80 % | ❌ |
| V1 vs V2 delta (H5 descriptive) | +0.025 | — | (F3 marginally > F1 even in old) |

**Every quantitative hypothesis failed.** Not borderline. Not
ambiguous. Decisive.

## The killer comparison

| Period | V1 cost-0 net | V1 net | Comment |
|---|---:|---:|---|
| 2018-2026 OOS (B009) | **+2.418** | +1.104 | huge positive |
| 2010-2017 fresh OOS (B010) | **-0.099** | -0.711 | slightly negative raw, catastrophic net |

The same carrier produces **opposite-sign cost-0 alpha** in two
different decades. There is no mechanism that explains this except
"the alpha is regime-specific to recent Korean market conditions."

## Year-by-year 2010-2017 (V1)

| Year | V1 net | V1 wins F1? |
|---|---:|:---:|
| **2010** | **+0.247** | ✓ (only positive year) |
| 2011 (Eurozone crisis) | **-0.479** | ✓ (less bad than F1) |
| 2012 | -0.093 | ✓ |
| 2013 (taper tantrum) | -0.374 | ✗ |
| 2014 | -0.048 | ✓ |
| 2015 (China crash) | -0.036 | ✓ |
| 2017 (rally year) | -0.143 | ✗ |

**6 of 7 years negative.** The 2010 +0.247 is real but it's the
single contributor — H4's 100 % concentration tells us we have ONE
year of alpha, not a multi-year edge.

Notable: F3 marginally beats F1 in old data (+0.025 V1-V2 delta on
average across years; majority of yearly H5 deltas are positive for
V1). So F3's mechanism does transfer at the COMPARATIVE level —
but both filters lose money, just F3 loses slightly less.

## What this means strategically

### 1. The 2018-2026 OOS performance was largely a recent-regime artifact

B003 → B005 → B009 reviews repeatedly flagged that the OOS uplift
was 2025-heavy. B010 confirms this is not a one-year artifact in
2025 — it's a multi-decade phenomenon. The signal works in
2010-with-special-conditions, in 2018-2024 mildly, and in 2025
strongly. It does not work as a stable alpha across decades.

### 2. The user's "spike capture" goal is mathematically realized but not in the way we hoped

The carrier captures spikes (2010, 2025, 2026 partial) but loses
in normal years. This is the OPPOSITE of "outperform index moderately
+ catch big spikes" — it's "lose in normal markets, catch big
spikes". Net effect: highly volatile, mostly negative.

### 3. Korean market may have structurally changed

Possible explanations for 2010-2017 vs 2018-2026 gap:
- Foreign / institutional flow data quality, reporting
- Retail dominance growth (especially post-2020 Robinhood-style
  surge in Korea)
- Market microstructure changes (HFT, dark pools, cross-listing)
- Regulatory: shorter settlement, holding-period rules
- Macro: low-rate era 2018-2024 vs higher rates pre-2014

We cannot test these directly without more data, but they're worth
noting as hypotheses for B011 design.

### 4. The "patches stacking" failure mode the user warned about — we narrowly avoided it

If we had only seen 2018-2026 data and kept stacking improvements
(B003 trigger → B007/B009 filter → B011 ranking → ...), we would
have ended up with a multi-layer strategy that "worked" on paper
but was entirely a regime artifact. B010 caught this **exactly
because of the experiment-discipline rule "test on new data, not
patches on old data"**. The discipline saved us from a genuine
catastrophe.

## What survives, what doesn't

### Doesn't survive
- **The hypothesis that 5-day cumulative foreign+institution flow is
  a stable Korean-equity alpha**. Refuted across decades.
- **The trajectory of role exploration on this carrier**. B011 ≠
  ranking exploration. Per B010 ticket pre-commitment.
- **Confidence that the B-family roadmap is on track**. We need to
  step back.

### Survives
- **Mode C discipline**. We honestly applied criteria, got a clear
  fail, accept the verdict. Past promotes (T3, F3) stand as
  historical record but inform future caution.
- **Role-based architecture**. R001's modularity made it trivial to
  test the carrier on new data — V2 (T3+F1) was a clean comparison
  with no new code.
- **The infrastructure**. Loader extension to old panel was
  ~20 lines + tests. Engine untouched. Old-data verification took
  ~1 day of human-Codex collaboration.
- **The user's instinct to demand verification**. Without B010,
  we would still be optimistic about an artifact.

## Multiple-testing budget closed

Cumulative variant comparisons on 2018-2026: ~27. B010 introduced
3 new variants on FRESH data (2010-2017, never used). Total
cumulative now ~30 with the variant work split across two regimes.

The 2018-2026 dataset is now formally "burned" for further patches.
Any future work either:
- Uses entirely new data (e.g., a third regime)
- Tests a fundamentally new alpha hypothesis
- OR moves to a different research question

We should NOT add more roles / candidates to T3+F3 carrier on
2018-2026 — it would inflate testing without meaningful information
gain.

## Possible B011 directions

Per B010 pre-commitment ("VERIFY FAIL → reconsider carrier
definition; B011 should be either signal redesign or a different
data exploration"):

### Option 1: Signal redesign — different alpha hypothesis class
Move beyond 5-day foreign+institution flow ratios. Possible
hypotheses worth considering (each would be a fresh ticket with
proper pre-registration):

- **Price-based momentum** with flow as confirmation only (not
  primary signal)
- **Cross-sectional rank momentum** (recent N-day return,
  cross-sectionally normalized)
- **Volatility-managed momentum** (risk parity at portfolio level)
- **Relative strength among foreign vs institutional** — divergence
  signal rather than agreement signal
- **Lower-frequency signals** — monthly or weekly cumulative flow
  rather than 5-day, with longer holding (different alpha decay
  assumption)

### Option 2: Period diagnostic — what changed 2010-2017 vs 2018-2026?
Don't redesign yet. First understand WHY the carrier failed in old
data. This is itself a research question worth a ticket. Subdivide
2018-2026 by years to see at what date the carrier started "working":

- 2018: ?
- 2019: ?
- 2020: ?
- ...

If the carrier was already working in 2018 but failing in 2017, the
break is around 2017-2018. If the carrier was failing in 2018 too
and only started working in 2020 or 2025, the picture changes.
This is a cheap, fast diagnostic with high information value.

### Option 3: Pause and rethink
Take a step back. Don't write B011 immediately. Discuss with the
user: given B010's verdict, what's the project's overall direction?

- Continue trying to find a Korean-equity flow-based alpha?
- Pivot to a different alpha class entirely?
- Accept that simple regime-following (B004 (c) gate-only) may be
  the most honest answer for the user's stated goal?
- Research the "what changed" question first before deciding?

### My recommendation: **Option 2 → then Option 3 → then Option 1**

Reasons:
1. **Option 2 is cheap and informative**. Re-running V1 on 2018-2026
   per-year (we already have this data from B009) takes ~1 hour.
   Tells us when the alpha started.
2. **Option 3 should follow Option 2's findings**. Knowing when the
   alpha started gives us much richer context for the strategic
   conversation.
3. **Option 1 (new alpha hypothesis) without Option 2/3 risks
   another patch-stacking spiral**. Better to understand the failure
   first.

If we go to Option 1 directly, we should pre-commit to writing a
new ticket from scratch with a genuinely different alpha, NOT
modifying the existing carrier.

## Carrier-evolution log update

For the historical record:

- E001-E004: early exit-rule iterations on absolute signal
- B001: market-cap normalization (killed)
- B002: signal-reversal exit promoted as carrier
- B003: trigger exploration (descriptive, T3 emerged but deferred)
- B004: regime gate exploration (inconclusive, gate-as-savior killed)
- B005: relative-flow alpha redesign (inconclusive)
- B006: T3 acceleration trigger PROMOTED
- B007: filter exploration (descriptive, F2 vs F3 trade-off emerged)
- B008: F2 promote attempt → inconclusive (-0.0005 IS noise)
- B009: F3 promote per discipline (Mode C verdict-integrity)
- **B010: VERIFY FAIL — 2010-2017 cost-0 V1 = -0.099. Carrier
  regime-conditional, not universal alpha.**

Carrier as of 2026-05-16: T3 + F3 (still on the books per Mode C,
but understood now as regime-conditional, not universal).

## Do not do next
- Adopt T3+F3 as deployable strategy on real money. It does not
  work in normal market conditions.
- Add more layers to T3+F3 on 2018-2026 data. Multiple-testing
  budget is exhausted on this dataset.
- Undo B009 F3 promote retroactively. Mode C protects historical
  verdicts.
- Conclude that "all flow-based alpha is impossible" — we tested
  ONE specific definition (5-day cumulative absolute, log-scaled
  via traded value).
- Conclude that "F3 helped" — the F3 vs F1 delta in old data is
  +0.025, marginal. F3 was promoted on 2018-2026 evidence; that
  evidence is itself now suspect.

## Follow-up
- **Recommend Option 2 → 3 → 1 sequence**.
- **B011 candidate** = "When did the alpha start working?" — a
  diagnostic ticket using already-existing 2018-2026 data, no new
  code, no Codex run needed (could be analyzed directly from
  existing reports/experiments/B009 outputs).
- After B011's diagnostic, hold a strategic conversation about
  project direction (Option 3) before designing any new alpha
  experiment (Option 1).
