# ATTR001 — Influence Map Findings (CORRECTED, supersedes pre-fix numbers)

Diagnostic-only. PRESERVE-ALL. NOT recommendations — an influence map WITHIN dynamic_top100
(not "the Korean market"). Pre-registration: `research/experiments/ATTR001_korean_data_influence_map.md`.
This supersedes the magnitudes in `FINDINGS_pass1.md` (which were contaminated — see §0).

## 0. Audit-first correction (the key event)
A measurement ARTIFACT was caught and fixed before any conclusion. The dynamic_top100 panel
is in_universe-filtered, so a ticker that LEAVES and RE-ENTERS top100 had its per-ticker
`shift(-h)` forward return computed ACROSS the multi-month hole; since re-entry is conditional
on the stock having risen, this injected huge survivorship-positive forward returns (gap>7d
rows averaged +11.6% vs +0.75% normal; pred_ret_5 max 303 = 30,300%). This inflated all
magnitudes and produced absurd event-study numbers (+30σ, +8–53% abnormal).
**Fix:** NaN any forward return whose T→T+h window spans more than ~h trading days of calendar
gap (`h*1.7+7`). After fix: pred_ret_5 max 303→5.25, mean 0.016→0.008. All passes re-run.
Placebos ≈ 0 (p1 +0.0004, p2a −0.0000). **Lesson: dynamic-universe panels need calendar-
consecutive forward returns; this is the same class of bug that produced the S-family
artifact.** (Pre-fix rows are kept in git history; corrected CSVs are authoritative.)

## 1. Corrected influence map (per family — raw observations, caveats in §2)

**B price/volume — dominant structure = short-horizon REVERSAL, real but MODEST.**
Price momentum 3–60d has negative 5d rank-IC; corrected PRESENT 5d IC ≈ −0.017 (t−3.1) for
mom_5 (was −0.045 pre-fix = inflated). reversal_5 mirror +0.017. Real and significant but a
small effect; slightly weaker PRESENT than PAST. within_sector_rs mirrors it.

**A flow / E borrow — positioning signals were CONTRARIAN in PAST, FADED to NEUTRAL in PRESENT.**
foreign cum20: PAST −0.013 → PRESENT +0.005 (t+1.0, NOT significant). borrow_chg20: PAST
−0.033 → PRESENT +0.003. Corrected reading: these were (weak) contrarian predictors in
2018–21 and LOST that influence by 2022+ — they did NOT flip to a positive edge (that was the
artifact). flow signals weak overall (many |IC|<0.01). borrow_ratio (short-interest proxy)
weak-negative, stable.

**C sector — WEAK** (sector_rs/breadth t≈1) → corroborates the E014 closure (sector-level
signals were not the edge). within_sector_rs = the reversal effect, not a sector effect.

**F market/macro (time-series market-timing, NOT cross-section) — modest, rate/FX-driven.**
us3mo_chg20 negative (PRESENT ts-corr −0.067; 20d tercile hi−lo −0.032) = rising US short
rates → lower KR universe returns; dxy_chg5 and usdkrw_chg5 similar negative; breadth weak
positive. vix_level PAST ts-corr +0.31 is still dominated by the 2020 vol-spike episode
(annotated, not a stable signal). Market-timing is weak/regime-sensitive (consistent with
only D013's macro GATE surviving, not a macro-timing alpha).

**G events (event-study, t+1, title/flag presence only) — now SANE, modest positive.**
earnings: +1.4%/5d, +2.9%/20d abnormal (t+7.6, n=6004) = textbook post-earnings-announcement
drift; treasury_stock/buyback +3.3%/5d (t+6.0, n=1061); large_holder +1.2%/5d (t+12.3,
n=16157); others noisy/small-n. Post-fix these are plausible event magnitudes (vs the +8–53%
artifact). Notably, post-fix the EVENT signals look like the most real, sane influence — but
see the R-family caveat below.

## 2. Honest caveats (validity_risk_annotated — NOT used to discard)
- All effects are SMALL (IC ~0.01–0.02). Large t come from large n (≈1–2k days / 6k–16k
  events), not large edges. Large t ≠ tradable.
- **Residual tail:** post-fix pred_ret_5 still has a tail (max 5.25 = limit-up streaks);
  rank-IC is robust to it, but decile/mean magnitudes remain slightly tail-sensitive.
- Decile/long-only numbers = single-period one-round-trip cost → OPTIMISTIC; a reversal book
  rebalances ~daily (high turnover/cost) — the F-family capacity lesson.
- Events: title/flag PRESENCE only (no body parser, no magnitude); PEAD/buyback are well-known
  + capacity/cost-limited; control = universe-mean (not sector/cap-matched); events overlap.
  The R-family closed on title-only insufficiency — these event effects do NOT contradict
  that (they are known, presence-level, not a tradable extracted-magnitude edge).
- Macro = market-timing on overlapping returns (autocorrelation overstates significance).
- Scope = dynamic_top100 (liquidity-biased) → "influence WITHIN the panel". Flow vendor-
  estimated. TR proxy (yfinance) ~50% coverage. KR short not executable (long-short statistical).

## 3. Synthesis (diagnostic, not a recommendation)
Within dynamic_top100, regime-conditionally: (a) short-horizon REVERSAL is the dominant,
real-but-modest cross-section structure, stable-ish (slightly weaker present); (b) POSITIONING
signals (foreign flow, borrow change) were weak-contrarian in PAST and FADED to neutral in
PRESENT — the clearest "regime change" is positioning LOSING influence, not gaining a new
edge; (c) SECTOR-level signals are weak (E014 corroborated); (d) MACRO is weak market-timing
(rates/FX negative), not an alpha; (e) EVENT presence (earnings drift, buyback, large-holder)
shows sane modest positive abnormal returns — known effects, presence-level, R-family caveat.
Nothing here is a strategy. Preserve-all: every signal/regime/horizon row retained with status.

## 4. Referee-required enhancements (completed — pre-registration compliance)
- **A) Artifact-fix audit table** (`artifact_fix_audit_table.csv`): per horizon, the gap-guard
  NaN'd 28,532 (1d) … 124,702 (20d) rows; raw forward-return max 283–380 → guarded 1.2–7.5;
  raw mean ≈ 2× guarded. Confirms the survivorship inflation + the fix.
- **B) data_gated rows** (`data_gated_rows.csv`): KR fundamentals (value/quality/shareholder-
  yield) + borrow fee/rebate/restriction/buy-in preserved as `data_gated` (not measured, reason
  given) — per pre-reg.
- **C) FDR / q-values** added to all maps. 16 cross-section signals are q<0.10 in PRESENT 5d —
  **but every surviving IC is tiny (−0.04…+0.03); they pass FDR only because n≈1000–2000 days,
  NOT because of economic size.** Surviving FDR ≠ tradable. Strongest q: borrow_ratio
  (−0.040, q≈4e-14), within_sector_rs (−0.031), vol_surge, mom_20, vol_20.
- **D) Liquidity-bucket breakdown** (`liquidity_bucket_breakdown.csv`): 5d IC by 20d-traded-value
  tercile, market-cap tercile, and the 거래대금추정==True diagnostic slice.
- **E) Event MATCHED control** (`influence_map_pass2c_events_matched.csv`, same date × sector ×
  cap-tercile): **event effects SHRINK markedly vs the universe-mean control** — earnings
  +1.42%→**+0.36%** (most of the apparent abnormal was sector/cap beta, not the event), contract
  +4.69%→+1.50%; treasury/buyback +3.33%→**+2.09%** and large_holder +1.18%→+0.94% hold better
  (more event-specific). BUT n_unique_ticker is small (e.g. earnings 327 tickers / 849 dates) →
  events cluster, t-stats overstated by overlap. Net: events are MODEST + presence-level +
  clustered + known (PEAD/buyback) — plausible, not a clean tradable edge (R-family caveat).

## 4b. Wording refinements (per Referee joint analysis)
- NOT "positioning as a family faded": precisely, **foreign-flow and borrow-CHANGE 5d influence
  faded from weak-contrarian (PAST) to near-neutral (PRESENT); but borrow_RATIO level stays
  significantly negative in PRESENT** (short-interest pressure proxy, strongest q in the map).
- within_sector_rs is the reversal/relative-price effect, NOT a sector effect (sector-level RS
  weak → E014 corroborated).
- Events: "plausible, not yet robust" — matched-control shrinkage + clustering confirm this.
- Macro pass: only ts-corr + tercile-conditional were computed; beta-adjusted / interaction
  (pre-reg-listed) were NOT separately computed → documented CAVEAT, not claimed.

## 5. Status
All rows across passes preserved with status labels (incl. data_gated); nothing discarded.
Engine artifact fix applied to all passes; all 6 Referee-required enhancements completed.
Diagnostic-only — no strategy / P08 / production / closed-family reopening. Ready for Referee
final sign-off.
