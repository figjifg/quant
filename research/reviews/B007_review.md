# Review — B007 (Filter-role exploration on T3 carrier)

## Verdict
**descriptive (no promote)** — per ticket rules. **Both F2 and F3
satisfy all three pre-registered descriptive thresholds**, with F3
winning the pre-registered tiebreak (larger OOS net delta).

Recommend **B008 = single-point promote ticket for F3**, with
explicit honest framing of the F2 vs F3 trade-off so the user can
override the tiebreak if desired.

## One-line conclusion
F3 (지속성 4/5) 가 OOS net delta +0.32, F2 (절대+상대) 가 +0.22 로 둘 다
사전 등록 기준 통과. 사전 등록 tiebreak 으로 F3 가 winner. 그러나 F2 는
OOS 4년 중 3년 이김 (F3 는 2년), F3 는 한 해 (2020 V자) 에서 더 큰 부분
fix 보임. 진정한 "어느 게 좋은 carrier 인가" 결정은 사용자 판단 필요.

## Headline numbers (1× cost)

| variant | IS net | OOS net | IS hit | OOS hit | IS trades | OOS trades |
|---|---:|---:|---:|---:|---:|---:|
| F1 baseline (B006 carrier) | -0.793 | +0.780 | 0.391 | 0.420 | 1189 | 724 |
| **F2 rel + abs** | **-0.793** | **+1.004** | 0.405 | 0.428 | 1176 | 721 |
| **F3 persistence 4/5** | **-0.787** | **+1.104** | 0.398 | 0.430 | 1210 | 731 |

## Cost-0 OOS (raw alpha)

| variant | cost-0 OOS | delta vs F1 |
|---|---:|---:|
| F1 | +1.875 | — |
| **F2** | **+2.230** | **+0.356** |
| **F3** | **+2.418** | **+0.543** |

Both variants substantially **increase** raw alpha, not just cut
costs. The "filter as quality gate" mechanism works for both.

## Pre-registered descriptive criteria

| Criterion | Threshold | F2 actual | F2 pass | F3 actual | F3 pass |
|---|---|---:|:---:|---:|:---:|
| OOS net delta vs F1 | ≥ +0.10 | +0.224 | ✓ | +0.324 | ✓ |
| OOS cost-0 ≥ F1 cost-0 | ≥ +0 | +0.356 | ✓ | +0.543 | ✓ |
| OOS year-wins ≥ 2/4 | ≥ 2 | 3 of 4 | ✓ | 2 of 4 | ✓ |

**Both F2 and F3 satisfy all three pre-registered conditions.**

Per pre-registered tiebreak ("the winner is whichever has the larger
absolute OOS net delta vs F1"): **F3 wins by +0.324 vs F2's +0.224**.

## Year-by-year breakdown (the most important diagnostic)

### OOS (2023-2026)
| year | F1 | F2 | F3 | F2 − F1 | F3 − F1 |
|---|---:|---:|---:|---:|---:|
| 2023 (recovery +18%) | +0.045 | +0.070 | -0.014 | +0.025 | **-0.060** |
| 2024 (correction -10%) | -0.234 | -0.259 | -0.247 | -0.025 | -0.013 |
| **2025 (strong rally)** | +0.914 | **+1.070** | **+1.069** | **+0.156** | **+0.155** |
| 2026 (partial 4mo) | +0.079 | +0.134 | **+0.300** | +0.055 | **+0.221** |

OOS year-wins (variant > F1):
- F2: **3 of 4** — wins 2023, 2025, 2026; loses 2024
- F3: **2 of 4** — wins 2025, 2026; loses 2023, 2024

### IS (2018-2022)
| year | F1 | F2 | F3 | F2 − F1 | F3 − F1 |
|---|---:|---:|---:|---:|---:|
| 2018 (bear -17%) | -0.284 | -0.308 | -0.281 | -0.024 | +0.003 |
| 2019 (+8%) | -0.056 | +0.036 | **-0.172** | +0.092 | **-0.116** |
| **2020 (V +30%)** | **-0.263** | -0.300 | **-0.145** | -0.037 | **+0.118** |
| 2021 (+4%) | -0.359 | -0.340 | -0.349 | +0.020 | +0.010 |
| 2022 (bear -25%) | -0.361 | -0.391 | -0.364 | -0.031 | -0.004 |

IS year-wins:
- F2: 2 of 5
- F3: 3 of 5

## The honest F2 vs F3 trade-off

F2 and F3 are both improvements but in **different ways**:

### F2 — small, stable, broad
- Smaller per-year deltas (mostly ±0.05)
- Wins 3 of 4 OOS years and 2 of 5 IS years (more years won)
- Trade-set Jaccard with F1 = **0.884** — F2 is essentially F1 with
  ~12 % refinement
- **2020 V-recovery: slightly worse** than F1 (-0.300 vs -0.263) —
  the relative-flow gate did NOT fix V-recovery in this composition
  (contrary to B005 hope). The reason: F2 keeps the absolute exit,
  so trades that pass the relative gate but exit on absolute reversal
  can fire suboptimally.

### F3 — larger, concentrated, V-recovery-fixing
- Larger per-year deltas (some +0.22, some -0.12)
- Wins fewer years (2/4 OOS, 3/5 IS) but with bigger amplitudes
- Trade-set Jaccard with F1 = **0.421** — F3 picks substantially
  different trades
- **2020 V-recovery: meaningful fix** (-0.145 vs F1 -0.263, ~45 %
  loss reduction). Persistence 4-of-5 filter avoids 2020's chaos.
- **2019 IS loss is the single biggest concern** (-0.172 vs F1
  -0.056, F3 worse by -0.116). Persistence filter under-performs
  in clean trend years.
- OOS uplift is concentrated in 2025 (+0.155) and 2026 partial
  (+0.221). 2023 and 2024 are negative for F3.

## Trade-set overlap matrix

| | F1 | F2 | F3 |
|---|---:|---:|---:|
| F1 | 1.000 | 0.884 | 0.421 |
| F2 | 0.884 | 1.000 | 0.402 |
| F3 | 0.421 | 0.402 | 1.000 |

F2 ≈ F1 (slight refinement). F3 is substantially different from
both F1 and F2. F3 is selecting a different "kind" of stock-day.

## What this rules in / out

### Confirmed
- **The filter role does carry meaningful information on the T3
  carrier**. Both F2 and F3 substantially improve over F1.
- **Cost-0 alpha is improved**, not just cost-cut. The mechanism
  is "better entry quality", not "lower turnover". (Trade counts
  are nearly identical across F1/F2/F3.)
- **Persistence (sustained 4-of-5-day buying) is a real
  differentiator** — F3 picks a different trade pool with
  meaningfully different (but not strictly better) characteristics.

### Unexpected
- **F2 (relative + absolute) does NOT fix V-recovery** (2020 IS
  -0.300 vs F1 -0.263). This contradicts the B005 finding where
  relative-only fixed 2020 to -0.05. The difference: B005 used
  relative as the alpha (entry + exit + ranking). B007's F2 uses
  relative only as entry filter; the absolute exit triggers at
  bad timing. So **the V-recovery fix from B005 only works if exit
  is also relative**. As an entry filter alone, relative is mostly
  a small refinement of F1 (Jaccard 0.88).

### Honest concerns
- F3's OOS uplift concentrates in 2025 + 2026 (+0.376 sum). The
  2023 + 2024 deltas are negative (-0.073 sum). If we remove 2025
  alone, F3's OOS delta drops from +0.32 to +0.17 (still passing
  the +0.10 bar). If we remove BOTH 2025 and 2026, F3's OOS delta
  goes negative.
- 2026 is a partial year (4 months only) with the largest single
  delta (+0.221). High uncertainty.
- F3 has a large 2019 IS loss (-0.116 vs F1) that we don't fully
  understand.

## Multiple-testing budget update

Cumulative variant comparisons: ~21 prior + 2 new (F2, F3 vs F1) =
~23. The single-point B008 promote ticket adds 1 more.

## Recommendation — B008 single-point promote

Per pre-registered tiebreak: **B008 = F3 single-point promote**.

But the honest framing is that **F2 and F3 represent different
trade-offs** and the user has legitimate reason to override the
tiebreak:

| | F2 | F3 |
|---|---|---|
| OOS magnitude | smaller (+0.22) | larger (+0.32) |
| OOS year robustness | better (3/4) | worse (2/4) |
| 2020 V-recovery | no fix | partial fix |
| 2019 IS | improved | worsened |
| Trade-pool similarity to F1 | very similar | very different |
| Single-year concentration | 2025 + 2026 | 2025 + 2026 (more so) |
| Interpretation | "F1 with quality refinement" | "different alpha mechanism" |

**Default per discipline: F3.** If the user prefers stability/
robustness (F2's 3/4 year wins) over magnitude (F3's larger absolute
uplift), F2 is the legitimate alternative.

If F3 is chosen and B008 fails to satisfy promote criteria (because
the OOS concentration in 2025+2026 looks worse under formal
re-registration), the natural fallback is **B009 = F2 single-point
promote**.

## What survives, what doesn't

- **The new T3 + F1 carrier (from B006) is no longer the best**.
  F2 and F3 both improve on it. The current "official" carrier
  status is unsettled until B008 resolves.
- **B005's relative-flow finding is partially refuted in this
  context** — relative as entry filter alone doesn't deliver the
  V-recovery fix. The fix only worked when relative was also the
  alpha + exit (B005). Adding relative as a filter on absolute
  alpha gives a small refinement, not a transformation.
- **Persistence (4-of-5) is a real new alpha source**. Different
  trade pool, meaningful improvement, partial V-recovery fix.
- **Regime-conditionality survives**. Both F2 and F3 still have
  most of their OOS uplift in 2025 + 2026. The fundamental
  regime-conditional nature of the underlying signal is not fixed
  by either filter.

## Do not do next
- Try to combine F2 + F3 (apply both filters). That's stacking
  two changes simultaneously and inflates testing pressure.
- Test F3 with relative exit (i.e., become an alpha redesign
  again). If we want to redesign alpha, do a fresh ticket per
  experiment-discipline rules.
- Adopt either F2 or F3 informally without going through B008.
- Re-test variants with different persistence thresholds (3-of-5,
  5-of-5). Pre-registered F3 = 4-of-5 only.

## Follow-up
- **B008 candidate** — single-point promote ticket for F3 per
  pre-registered tiebreak. User may override to F2 if preference
  is for robustness over magnitude.
- After B008, the next role to explore is ranking or exit on the
  newly chosen carrier (depending on B008 verdict).
