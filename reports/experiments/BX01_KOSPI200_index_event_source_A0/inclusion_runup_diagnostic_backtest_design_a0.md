# BX01-KOSPI200-INCLUSION-RUNUP-DIAGNOSTIC-BACKTEST-DESIGN-A0 — Design Specification

**Phase:** `BX01-KOSPI200-INCLUSION-RUNUP-DIAGNOSTIC-BACKTEST-DESIGN-A0`
**Directive:** `.codex-claude-relay/codex_outbox/ask_0015.md` (LOCAL-ONLY DESIGN; not approval to run a backtest)
**Date:** 2026-05-31
**Authored by:** Executor (Claude Code, autonomous mode)
**Status:** Pre-registered design specification. NO backtest executed.

---

## 0. Boundary statement (front-loaded)

This document is a **pre-registered design specification only**. It does NOT
constitute strategy, P08 readiness, production / paper / live readiness, or
execution readiness. **No returns, run-up, edge, hit-rate, Sharpe, alpha,
drawdown, PnL, benchmark, placebo statistic, p-value, distribution-tail, or
strategy metric have been computed in this phase or in any prior phase**. The
deliverables are: (a) this design spec, (b) deterministic sample-prep code,
(c) sample preview + registries. Any actual execution of this design requires
a SEPARATE user + Referee decision and a SEPARATE execution phase.

---

## 1. Objective and non-objective

### 1.1 Objective (diagnostic)

Pre-register a narrow, audit-first diagnostic test to ask: **does the KOSPI 200
regular semi-annual review inclusion event exhibit a measurable
announcement-to-effective-date run-up that survives audit-first controls?**
The intended diagnostic answer is one of: signal-present-after-cost,
signal-absent-after-cost, or inconclusive.

### 1.2 Non-objective

- NOT to build a tradable strategy.
- NOT to claim "BX01 mechanism works" or "doesn't work" (only to ask the
  diagnostic question above with caveats).
- NOT to integrate any output into P08_IEF30.
- NOT to authorize paper or live execution.
- NOT to expand into BX02/BX03/BX04/MSCI/FTSE/KOSDAQ150/Bull-Bear new
  rounds.

---

## 2. Sample rules (exact)

### 2.1 Main inclusion-addition sample (65 events)

Inclusion criteria (ALL must hold):
- `source_record_type ∈ {class_a_direct_primary, class_b_snapshot_diff_derived,
  class_b_title_linked_secondary}`.
- `review_cycle ∈ {2021-06, 2021-12, 2022-06, 2023-06, 2023-12, 2024-06,
  2024-12, 2025-06, 2025-12}`.
- `side = addition`.
- `ticker` non-blank.
- `effective_dt_rulebook_derived` non-blank.

Exclusions (with reason):
- All skeleton-only / notice-level-only rows (4 missing Tier 1 + 30 cycle
  meta + 41 special_no_name).
- 2026-06 cycle (effective_dt blank; calendar cutoff).
- Bridge 2022-12 rows (not in Tier 1).
- Deletion-side rows (NOT in main sample; go to negative-control registry).

Realised count (from `prepare_inclusion_runup_diagnostic_sample.py`):
**65 main inclusion-addition events** across 9 cycles. Matches pre-estimate
EXACTLY; no halt.

By source_record_type:
- `class_a_direct_primary` (2021-06 only): **5 PRIMARY**
- `class_b_snapshot_diff_derived`: **54 secondary derived (regular-review attribution preserved with caveat)**
- `class_b_title_linked_secondary`: **6 secondary triangulated (KraftON/KakaoBank/KakaoPay 2021-12; LG에솔 2022-06; 에코프로머티/포스코DX 2024-06)**

### 2.2 Negative-control candidate registry (68 events)

`side = deletion` rows from the same 9 in-scope cycles. Registry only;
**NOT used for main signal computation**. Purpose at execution time: sign /
contamination check — if a "run-up" appears in deletions too, the apparent
signal is a regular-review beta or sample-period artifact, not an inclusion
effect.

### 2.3 Excluded rows (87)

Full `sample_exclusion_log.csv`:
- 75 `skeleton_only_or_notice_level_only_not_constituent_level`
- 10 `cycle_excluded__effective_dt_rulebook_derived_blank_calendar_cutoff` (2026-06)
- 2 `cycle_excluded__bridge_only_not_in_tier1` (2022-12)

220 events_v3 total = 65 main + 68 neg + 87 excluded ✓ (preserve-all check).

---

## 3. Timing model

Every main-sample row carries these design-only labels (NO prices read):

| Field | Definition |
|---|---|
| `announcement_dt` | KRX notice REG_DT (primary; from notice_index.json via events_v3). |
| `effective_dt_design` | = `effective_dt_rulebook_derived` (provisional secondary basis for Class B; primary for Class A 2021-06). |
| `entry_dt_design` | First local trading session strictly AFTER `announcement_dt` (PIT-safe; same-day forbidden). |
| `exit_dt_candidate_T_plus_5` | announcement_dt + 5 trading days (label). |
| `exit_dt_candidate_T_plus_10` | announcement_dt + 10 trading days (label). |
| `exit_dt_candidate_effective_minus_1` | effective_dt_design - 1 trading day (label). |

Canonical `effective_dt` column in events_v3.csv **remains untouched** at
blank — `effective_dt_design` is a SEPARATE design-time field.

---

## 4. Local-only data dependencies

The execution phase (NOT authorized by this directive) would need:

| Data | Local source | PIT status |
|---|---|---|
| Daily close (KRX equity) | NOT loaded here; would come from existing local panels | PIT-required at execution time |
| Adjusted total return | optional; W000 KR total-return artifact | PIT-required |
| KOSPI 200 membership history | `events_v3.csv` + snapshots | partial (4 missing Tier 1 still skeleton) |
| Sector PIT | `data/processed/krx_pit_sector_classifications.csv` | PIT-snapshotted, used as label in `pit_sector_label_for_matched_control_design` |
| Listing universe PIT | `data/acquired/krx_listed_universe/krx_listed_monthly_snapshots_2010_2026.csv` | 25.3% panel-coverage gap (known limit) |
| Trading calendar | `data/acquired/krx_calendar/krx_official_calendar_2010_2026.csv` | covers 2010-01-04..2026-05-22 |

---

## 5. Cost model (for later execution phase)

Project standard, after-tax:
- commission: **1.5 bps / leg**
- slippage: **5 bps / leg**
- sell-tax (KR): **20 bps**
- round-trip floor: **~33 bps**

Diagnostic-only check: any apparent run-up must clear this 33 bps floor in
the after-cost summary, else the diagnostic verdict is signal-absent-after-cost.

---

## 6. Matched-control design

For each main-sample event row, the execution phase would draw a
date × sector × cap-bucket × liquidity-bucket matched control peer.

Design (per row in `control_matching_design_registry.csv`):
- **match_dim_1**: `date = announcement_dt`
- **match_dim_2**: `sector = <PIT sector label at announcement_dt>` (KRX PIT
  classification)
- **match_dim_3**: `market_cap_bucket = (defer to execution phase via PIT
  listing panel; quintile from KOSPI listed universe at announcement_dt - 1)`
- **match_dim_4**: `liquidity_bucket = (defer to execution phase via PIT
  volume panel; quintile from announcement_dt - 60..announcement_dt - 1
  rolling average traded value)`
- **match_dim_5**: `index_membership = KOSPI200_constituent_status_at_announcement_dt-1`
  (excludes existing KOSPI 200 constituents from the control pool)
- **control_pool_definition**: all KOSPI-listed non-KOSPI200 names on
  announcement_dt - 1 with the same sector AND size quintile AND liquidity
  quintile.
- **exclusion_from_pool**: `<self_ticker>` (no self-inclusion).

NO peer selected in this design phase. The execution phase would perform
deterministic PIT panel join.

---

## 7. Placebo design (design only; NOT executed)

Within-cycle random-date permutation:
- For each cycle, randomly draw 1000 placebo `announcement_dt` values from
  trading days inside the cycle's announcement-to-effective window
  (or a fixed 30-day pre-effective window).
- Apply the same entry/exit/cost/matched-control pipeline to each placebo
  draw.
- The OBSERVED diagnostic statistic (which would be computed in the execution
  phase) must sit OUTSIDE the placebo distribution's central 90% (5th–95th
  percentile) for the signal to be considered non-spurious by this control.

NOT EXECUTED in this design phase.

---

## 8. Negative-control design (deletion side)

68 deletion-side rows from the same 9 cycles are registered as
`negative_control_candidate_only` in `negative_control_candidate_registry.csv`.

At execution time: if the same run-up calculation applied to deletions
produces a comparable positive run-up, the apparent inclusion signal is
contaminated by review-period regular-review beta or sample-period drift —
NOT an inclusion-specific effect.

---

## 9. Pre-registered success criteria

For the (future) execution phase, the diagnostic would be considered
**signal-present-after-cost** if AND ONLY IF ALL of:

1. **Cost-positive run-up on Class A direct primary additions** (n=5,
   2021-06 only): post-cost arithmetic mean run-up announcement→effective_dt
   exceeds 0 by > 33 bps with > 60% positive hit rate. (Caveat: n=5 is too
   small for inference; this is a sanity bar.)
2. **Matched-control adjustment**: after subtracting the matched non-included
   peer's same-window return, the post-cost spread mean > 0 and beats the
   placebo distribution's 90th percentile.
3. **Negative control fails to replicate**: deletion-side run-up matched-
   adjusted mean is NOT positive (no run-up on deletion side).
4. **Window robustness**: signal direction the same under all three exit
   candidates (T+5 / T+10 / effective-1).
5. **Subsample stability**: signal direction the same when restricted to
   `class_a_direct_primary` only AND when restricted to `class_b_title_linked_secondary` only.
6. **Cycle-level non-concentration**: signal NOT driven by a single cycle —
   no cycle contributes more than 40% of the aggregate post-cost edge.

---

## 10. Pre-registered kill criteria

Diagnostic is **signal-absent-after-cost** if ANY of:

1. Cost-positive run-up fails on Class A direct primary.
2. Matched-control-adjusted spread negative or non-significant vs placebo.
3. Negative-control deletion run-up positive and comparable magnitude.
4. Window robustness fails (different sign under different exits).
5. > 60% of post-cost edge from a single cycle.
6. Class B title-linked subset (n=6) shows materially different sign from
   Class B non-title-linked subset (n=54) — suggests timing attribution
   issue rather than mechanism.

---

## 11. Weakness / caveat list (≥12 named)

1. **6 residual blockers carry forward**: primary KRX rulebook + derivatives
   spec access blocked, 2026-06 calendar cutoff, 4 skeleton Tier 1 cycles,
   Class B regular/special deletion-side conflation, Tier 2/3 specials
   structured-source deferred.
2. **Class B addition rows attributed by snapshot diff, not direct parse**:
   may include intermediate-special timing (partially mitigated by title-
   linking for 6 of 60 rows; 54 remain regular-review attribution with caveat).
3. **`effective_dt_design`** is **provisional secondary** for Class B
   (Mirae 2021-11 §7.1 + Hana 2020-05-25 p8/p15 + local calendar; not
   primary KRX-confirmed).
4. **Title-linked rows** are `high_secondary_triangulated`, NOT primary.
5. **Listing-universe panel** has 25.3% coverage gap — sector / cap /
   liquidity matched-control pool will be incomplete for some rows.
6. **n=5 for Class A direct primary** is too small for inferential
   statistics; serves as sanity bar only.
7. **Sample period** is 2021-06..2025-12 — entirely within a regime that
   may differ from pre-2021 and may not generalize.
8. **No 2018-2020 coverage** (4 missing Tier 1 cycles still skeleton),
   so the 2020 COVID regime is excluded — sample bias risk.
9. **Deletion-side rows** are conflated; the negative-control logic ASSUMES
   deletion-side run-up is a contamination signal, but Class B deletions may
   themselves be intermediate-special-driven (e.g., M&A / 관리종목).
10. **Cost model** is point-estimate; doesn't include bid-ask, partial-fill
    risk, KOSPI 200 inclusion-day flow impact, or short-leg cost (long-only
    so short cost N/A).
11. **PIT sector classification** is from `krx_pit_sector_classifications.csv`
    — quality depends on the underlying source; may have lag.
12. **No primary deletion-side parse**: if deletions correlate with M&A
    or sector concentration in our sample period, even the matched-control
    correction may not fully separate the mechanism.
13. **Title-link confidence asymmetry**: KRX 2021-08+ specials have high
    title-link match; older specials don't carry title evidence — so
    confidence is asymmetric across the sample.

---

## 12. Audit-first 12-item checklist

Per project `docs/audit_first_framework.md`:

| # | Item | Status for this design |
|---|---|---|
| 1 | Data lineage | ✅ events_v3 + per_cycle_effective_dt + special_candidate_links + KRX calendar + sector PIT all locally sourced; manifest documents sha256 |
| 2 | Point-in-time availability | ✅ announcement_dt = REG_DT; entry_dt = next trading day after announcement_dt; matched control uses PIT-snapshotted listing |
| 3 | Survivorship safety | ⚠️ partial — listing universe panel 25.3% coverage gap; documented as weakness #5 |
| 4 | Corporate action handling | ⚠️ regular/special conflation for 54/60 Class B addition rows; 6 title-linked + 5 Class A direct = clean; documented as weakness #2 |
| 5 | Calendar / tradability | ✅ KRX trading calendar PIT-confirmed; 2026-06 excluded for calendar cutoff |
| 6 | Daily NAV | n/a — design only; would apply at execution time |
| 7 | No implicit leverage | ✅ long-only, single-position-per-event design |
| 8 | Benchmark alignment | ✅ matched-control design uses PIT non-KOSPI200 peer; not KOSPI 200 index returns |
| 9 | Random / placebo control | ✅ within-cycle random-date permutation 1000 draws (design; not executed) |
| 10 | Concentration / top-contributor audit | ✅ kill criterion #5 captures single-cycle concentration > 60% |
| 11 | Cost / tax / turnover | ✅ 33 bps round-trip floor; success criterion #1 explicitly applies post-cost |
| 12 | Capacity / execution | ⚠️ flow-impact-on-inclusion-day not modeled; documented as weakness #10 |

---

## 13. Explicit "no backtest executed" boundary

This phase has produced ONLY:
- This design specification markdown.
- `src/audit/bx01/prepare_inclusion_runup_diagnostic_sample.py` (deterministic, local-only, NO return computation).
- `data/acquired/bx01_kospi200_inclusion_runup_diagnostic_design_a0/` 5 CSVs:
  - `inclusion_runup_sample_preview.csv` (65 main inclusion-addition rows)
  - `negative_control_candidate_registry.csv` (68 deletion-side rows)
  - `control_matching_design_registry.csv` (65 design rows, no peer selected)
  - `sample_exclusion_log.csv` (87 excluded rows w/ reason)
  - `manifest.csv` (10-col provenance schema)
- `reports/experiments/BX01_KOSPI200_index_event_source_A0/inclusion_runup_diagnostic_design_initial_pass.md` (companion initial pass report)

NO price column read. NO return / run-up / edge / Sharpe / hit-rate / placebo
statistic / p-value / strategy metric computed in this phase. `events_v3.csv`
UNCHANGED. Canonical `effective_dt` column UNCHANGED.

Any actual execution of this design requires a SEPARATE user + Referee
decision and a SEPARATE execution phase. The Referee's expected execution-phase
gate verdicts in the close note will determine the next step.

Frozen P08_IEF30 — untouched. Measurement-layer DECIDED STANDBY — untouched.
Closed families — untouched. Bear's BX02 / BX03 / BX04 verdicts — intact.
