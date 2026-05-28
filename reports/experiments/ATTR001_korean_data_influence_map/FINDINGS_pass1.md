> **SUPERSEDED (2026-05-28):** the magnitudes below were contaminated by a dynamic-universe
> forward-return artifact (re-entry survivorship). See `FINDINGS_corrected.md` for the fixed,
> authoritative findings. This file is kept for the honest audit trail.

# ATTR001 — Influence Map Findings, Pass 1 (cross-section: flow / price-volume / total-return)

Diagnostic-only. PRESERVE-ALL (nothing dropped). NOT recommendations — an influence map.
Pre-registration: `research/experiments/ATTR001_korean_data_influence_map.md`. Pass 1 =
21 signals (families A flow, B price/volume, D total-return) × 3 regimes × 5 horizons = 315
rows in `influence_map_pass1.csv`. Families C/E/F/G = later passes.

## Methodology validity
- Placebo (within-date ticker permutation) 5d IC ≈ **0.0002** (max |.| 0.0083) → the measured
  rank-IC is not a spurious artifact of the pipeline. Good.
- IC = close-to-close prediction; decile = T+1-open executability net cost (1.5+5 / 1.5+5 / 20bps).
- Scope = dynamic_top100 panel → "influence WITHIN the panel", NOT "the Korean market".

## What the map shows (raw observations — caveats below; no discovery language)
1. **Dominant structure = short-horizon REVERSAL.** Price momentum (3/5/10/20/60d) all have
   NEGATIVE 5d rank-IC (≈ −0.03…−0.06; PRESENT t ≈ −6…−9). reversal_5 (its negation) is the
   strongest positive (5d IC +0.038, t+8; 10d long-only top-decile +6.0% net-cost — see cost
   caveat). Total-return momentum (D) mirrors this (reversal), slightly weaker.
2. **Regime-conditional (PAST 2018–21 vs PRESENT 2022+):**
   - The core reversal is **fairly STABLE** across regimes (most IC5 shifts small, ±0.01–0.03).
   - **Foreign FLOW changed regime:** cumulative foreign net-buy (cum3/5/20) went from
     negative/contrarian IC in PAST (−0.01…−0.03) to ≈0/positive in PRESENT (cum20 +0.013,
     t+3.4; shift +0.023). I.e., foreign cumulative buying's relation to forward returns
     flipped/weakened — a genuine present-regime shift. Corroborates the prior finding that
     KR flow signals are regime-conditional, not universal (see signal_regime_conditionality).
   - Long-horizon (60d) momentum-reversal WEAKENED present (−0.062 → −0.031).
   - turnover_chg5 and volume_surge flipped sign PAST(+)→PRESENT(−).
3. **Flow signals are weak overall** (|IC5| ≈ 0.004–0.013; several t<2 in present = not
   distinguishable from noise). Institution flow weakly positive; foreign flow weak/regime-shifting.
4. **Volatility (20d): positive present IC (+0.024, t+4.4), LO10 +6.0%** — high-vol names
   outperformed short-term present (likely reversal-correlated; small-sample risk).

## Honest caveats (validity_risk_annotated — NOT used to discard)
- **Small IC**: magnitudes ~0.01–0.06 are small daily cross-section signal; large t-stats
  come from ~1000–2000 day samples, NOT from a large per-signal edge. Large t ≠ tradable.
- **Decile/LO numbers are OPTIMISTIC on cost**: computed as single-period holds with one
  round-trip cost; a real reversal book rebalances ~daily → far higher turnover/cost. The
  +6% LO10 for reversal/vol is NOT a tradable return — it is the F-family lesson (reversal
  has IC but turnover/cost-limited capacity).
- dynamic_top100 = liquidity-biased; flow is vendor-ESTIMATED (수급금액추정여부 all-True);
  거래대금추정여부==True rows excluded from headline; TR proxy (yfinance) covers ~50% rows
  (D-family reduced N).
- Diagnostic-only. KR short not executable → long-short decile is statistical only.

## Status
All 315 rows preserved with status labels (165 measured_valid / 150 measured_with_caveat).
Nothing discarded. Pass 2 (sector PIT, borrow-balance, market/macro conditional, event-study)
to follow under the same locked pre-registration. Executor + Referee to analyze jointly.
