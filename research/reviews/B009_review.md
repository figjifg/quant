# Review — B009 (F3 filter promote)

## Verdict
**PROMOTE per pre-registered 5-criterion logic** (all 5 pass cleanly)

But this PROMOTE comes with a serious caveat surfaced by the
descriptive "excluding 2025 AND 2026" diagnostic: F3 LOSES vs F1
in the only two non-spike, non-partial OOS years (2023, 2024) by
-0.073 cumulative. The pre-registered criteria do not capture this,
because adding a 2026-exclusion criterion after seeing B007 numbers
would be data-snooping.

The user faces a real strategic choice between:
- **F3** (B009 promote per discipline; larger magnitude; concentrated
  in 2025 + 2026; loses in non-spike normal years)
- **F2** (B008 inconclusive due to -0.0005 IS noise; smaller
  magnitude; more robust across all OOS years; better risk-adjusted)

This review presents the verdict honestly with both formal results
in hand.

## One-line conclusion
F3 가 사전 등록 5개 기준 모두 통과. 그러나 2025 AND 2026 둘 다 빼면
F3 OOS delta = -0.073 — non-spike-non-partial 환경에서 F1 보다 손해.
Discipline 으로는 F3 promote 정당하나, "spike + partial year 의존" 이
F3 의 본질이라는 honest 진단.

## Headline numbers

| variant | IS net | OOS net | IS hit | OOS hit | IS trades | OOS trades |
|---|---:|---:|---:|---:|---:|---:|
| F1 baseline (B006 T3) | -0.79256 | +0.78009 | 0.391 | 0.420 | 1189 | 724 |
| **F3 promote** | **-0.78658** | **+1.10419** | 0.398 | 0.430 | 1210 | 731 |
| Δ (F3 − F1) | **+0.00598** | **+0.32410** | +0.007 | +0.010 | +21 | +7 |

Cost-0 OOS:
- F1: +1.875
- F3: +2.418 (Δ +0.543)

## Reproducibility
- B009 F3 metrics match B007 `f3_persistence_4_of_5` within 1e-9 ✓
- B009 F1 metrics match B006 T3 within 1e-9 ✓
- engine.py untouched ✓
- 156 pytest passing ✓

## Pre-registered 5-criterion check

| # | Criterion | Threshold | Actual | Pass |
|---|---|---|---:|:---:|
| 1 | OOS net delta (F3 − F1) | ≥ +0.10 | **+0.324** | ✓ |
| 2 | OOS cost-0 (F3) ≥ F1 | F3 ≥ F1 | F3 +2.418 vs F1 +1.875 | ✓ |
| 3 | OOS year-wins (F3 > F1) | ≥ 2 of 4 | 2 of 4 | ✓ (just barely) |
| 4 | IS net (F3) ≥ F1 | F3 ≥ F1 | -0.7866 vs -0.7926 | ✓ (+0.006) |
| 5 | OOS delta excluding 2025 | > 0 | **+0.148** | ✓ |

**ALL 5 pass.** Per pre-registered rule, F3 promotes.

## Year-by-year breakdown — the most important diagnostic

### IS (2018-2022)
| year | F1 | F3 | F3 − F1 | F3 wins? |
|---|---:|---:|---:|:---:|
| 2018 | -0.284 | -0.281 | +0.003 | ✓ |
| 2019 | -0.056 | -0.172 | **-0.116** | ✗ |
| 2020 | -0.263 | -0.145 | **+0.118** | ✓ |
| 2021 | -0.359 | -0.349 | +0.010 | ✓ |
| 2022 | -0.361 | -0.364 | -0.004 | ✗ |

IS wins: 3 of 5. F3 has the V-recovery fix (2020 +0.118) and small
positives elsewhere, but a substantial 2019 loss (-0.116, F3's
worst single-year delta).

### OOS (2023-2026)
| year | F1 | F3 | F3 − F1 | F3 wins? |
|---|---:|---:|---:|:---:|
| 2023 | +0.045 | -0.014 | **-0.060** | ✗ |
| 2024 | -0.234 | -0.247 | -0.013 | ✗ |
| 2025 | +0.914 | +1.069 | **+0.155** | ✓ |
| 2026 (4mo) | +0.079 | +0.300 | **+0.221** | ✓ |

OOS wins: 2 of 4. F3's wins concentrate in 2025 (spike) and 2026
(partial year). 2023 and 2024 (the "normal" OOS years) are both
negative for F3.

### The descriptive "excluding 2025 AND 2026" check

Sum of (F3 − F1) for OOS years 2023, 2024 only:
- 2023: -0.060
- 2024: -0.013
- **Sum: -0.073**

**F3 LOSES vs F1 in OOS years that aren't 2025 spike or 2026 partial.**

This is the honest concentration concern. Pre-registered criterion 5
(excluding 2025 alone) passes (+0.148) because 2026 carries the load.
But excluding both spike and partial-year, F3 underperforms F1 in
real money.

By contrast, F2's same metric (from B008):
- 2023: +0.025
- 2024: -0.025
- **Sum: 0.0**

F2 is essentially neutral in non-spike-non-partial years (vs F3's
-0.073). F2 doesn't lose to F1 in normal years.

## F2 vs F3 with both formal results in hand

| | F2 (B008) | F3 (B009) |
|---|---|---|
| Promote criteria | 4 of 5 (criterion 4 by -0.0005 = noise) | **5 of 5** |
| OOS net delta | +0.224 | +0.324 |
| OOS cost-0 delta | +0.356 | +0.543 |
| OOS year-wins (4 yrs) | 3 of 4 | 2 of 4 |
| Information Ratio | **0.39** | 0.32 |
| Worst single-year delta | -0.037 | **-0.116** |
| Trade-pool similarity to F1 | 0.884 | 0.421 |
| 2020 V-recovery | -0.037 (no fix) | **+0.118 (partial fix)** |
| Excluding 2025 AND 2026 OOS | **0.0** (neutral) | **-0.073** (loses) |

### Strategic interpretation

**F3 is "spike + partial-year alpha"** — wins big when 2025-style
spike or fresh partial-year data hits, loses in normal OOS years.
Higher magnitude but worse robustness.

**F2 is "consistent small refinement"** — wins more years, smaller
magnitudes, doesn't lose in normal years. Better risk-adjusted but
smaller absolute upside.

The user's stated goal is "outperform index moderately + catch big
spikes". F2 better fits "outperform moderately" (3/4 OOS wins, 0.0
in normal years means doesn't lose). F3 better fits "catch big
spikes" (bigger 2025/2026 gains). Neither perfectly serves both
parts of the goal.

## Three paths forward

### Path A: Strict discipline → F3 promotes (per pre-registered rule)
- F3 is the official new filter carrier
- B007 + B008 + B009 verdict chain: F3 wins by formal criteria
- Risk: future borderline cases (like F2's -0.0005 IS) get nothing
  while F3's hidden 2026 dependence is rewarded
- Honest disclaimer in carrier change: "F3 promoted per criteria;
  -0.073 in non-spike-non-partial OOS noted as caveat"

### Path B: Override F3 with F2 based on quality-of-evidence analysis
- F2 has better Information Ratio, more years won, no normal-year
  losses
- F3's 2026 dependence is real concern (4-month partial year is
  most uncertain piece of OOS)
- B007 6-metric analysis (4 of 6 favor F2) supplemented by B009's
  -0.073 in 2023+2024 makes the F2 case even stronger
- Risk: overriding pre-registration precedent twice in a row weakens
  the discipline

### Path C: Promote NEITHER, move on to ranking/exit role
- Both filters had concerning patterns (F2 borderline, F3 concentrated)
- Filter role on T3 carrier doesn't carry strong differentiation we
  fully trust
- Move on to ranking-role or exit-role exploration on the original
  B006 T3 + F1 carrier (no filter change)
- Most conservative path; most preserves discipline; least progress

### My recommendation: Path A (F3 promote per discipline)

Reasons:
1. **F3 passes all 5 pre-registered criteria cleanly**. The
   discipline that's served us well (B003 → B006 promote, B005
   inconclusive correctly identified) demands we honor the formal
   verdict.
2. **The 2026 concentration concern was honestly disclosed before
   the result** (B009 ticket explicitly added the descriptive
   "excluding 2025 AND 2026" metric). We pre-committed to NOT
   making it a criterion. Adding it as a kill condition now would
   be retro-cherry-picking.
3. **F2 was overridden once (B007 tiebreak)** based on quality
   analysis. Overriding F3 again based on similar reasoning would
   weaken every future single-point promote.
4. **F3's larger magnitude + V-recovery fix** are real and may be
   what the user wants strategically. The OOS net delta of +0.32
   = ~+10% annualized over 3.4 years. That's a meaningful real
   improvement.
5. **Risk is acknowledged**: F3 may underperform in 2027 normal
   years if the 2025+2026 pattern doesn't repeat. The promote is
   "this is our best evidence-based carrier change today", not "we
   are confident in F3 forever".

The user may legitimately disagree and pick Path B (F2 override) or
Path C (move on). Discipline-first reasoning leans Path A.

## What this changes for the project

**If Path A is accepted**, the new B-family carrier becomes:
- Filter: **`filter_persistence_4_of_5` (F3)** ← promoted
- Trigger: `trigger_acceleration` (T3) — B006 carrier
- Ranking: `rank_by_combined_flow_5`
- Exit: `exit_signal_reversal`

Memory will be updated to reflect F3 as the new filter carrier.

## What survives, what doesn't (across B007 + B008 + B009)

### Survives
- **The filter role carries real information on T3 carrier**. Both
  F2 and F3 substantially beat F1 on raw metrics.
- **Persistence (4-of-5 daily buying) is a genuinely different
  alpha source** (Jaccard 0.42 with F1 — picks different stocks).
- **Pre-registration discipline still operating** — F2 marginal
  fail on criterion 4 was honestly flagged as inconclusive, F3
  passes are honestly recognized.

### Refuted / qualified
- **B005's relative-flow V-recovery fix doesn't transfer cleanly**
  to filter-on-absolute-alpha context (B007 F2: 2020 IS -0.300 vs
  F1 -0.263). Persistence (F3) gives a partial V-recovery fix
  (+0.118 in 2020) instead.
- **F3 is NOT universal alpha** — loses in non-spike-non-partial
  OOS years.
- **The regime-conditionality finding** (B003+B004+B005 conclusion)
  still holds. F3 marginally improves on the conditional alpha but
  doesn't change its fundamentally regime-dependent nature.

## Multiple-testing budget update

Cumulative: ~26 prior + 1 (B009 single-point) = 27.

## Do not do next
- Add a 2026-exclusion criterion to B009 retroactively. That
  would invalidate the formal verdict.
- Test F2 + F3 combined (apply both filters). Stacking violates
  one-role-per-experiment.
- Re-test F2 with relaxed criterion 4 to "save" it. Pre-registration
  is what makes verdicts meaningful.
- Adopt F3 informally without explicit user decision on Path A vs
  B vs C.

## Follow-up

Pending the user's choice between Path A / B / C:

- If Path A (recommended): update memory + carrier evolution log;
  next ticket = B010 = ranking or exit exploration on the new
  T3 + F3 carrier.
- If Path B: F2 promotes informally with documented override;
  B010 = ranking/exit exploration on T3 + F2.
- If Path C: B010 = ranking/exit exploration on T3 + F1 (the
  unchanged B006 carrier); F2 and F3 noted as filter alternatives
  not promoted.
