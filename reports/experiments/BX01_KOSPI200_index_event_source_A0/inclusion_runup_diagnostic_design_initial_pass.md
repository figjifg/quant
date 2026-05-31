# BX01-KOSPI200-INCLUSION-RUNUP-DIAGNOSTIC-BACKTEST-DESIGN-A0 — Initial Pass Report

**For:** Referee gate verdict — NOT self-applied.
**Companion document:** `inclusion_runup_diagnostic_backtest_design_a0.md` (the design specification).

---

## 1. Input artifact list (LOCAL ONLY)

- `data/acquired/bx01_kospi200_index_event_source_a0/events_v3.csv` (220 rows, BX01 authoritative event artifact; UNCHANGED in this phase)
- `data/acquired/bx01_kospi200_rulebook_effective_dt_a0/per_cycle_effective_dt.csv` (10 rows, cycle effective-date table from rulebook-A0)
- `data/acquired/bx01_kospi200_specials_title_enrichment_a0/special_candidate_links.csv` (6 title-linked secondary-triangulated rows)
- `data/acquired/krx_calendar/krx_official_calendar_2010_2026.csv` (4034 trading days 2010-01-04..2026-05-22)
- `data/processed/krx_pit_sector_classifications.csv` (PIT sector for matched-control design label)
- `data/acquired/krx_listed_universe/krx_listed_monthly_snapshots_2010_2026.csv` (PIT listing for ticker resolution; 25.3% panel-coverage gap noted)

**No network access. No downloads. No source recovery. No HWP/PDF/OCR/parser work. No event-table authority change. `events_v3.csv` NOT modified.**

---

## 2. Sample counts (reconciled)

| metric | count |
|---|---|
| events_v3.csv total rows | 220 |
| main inclusion-addition sample | **65** |
| negative-control candidate registry | 68 |
| excluded (with reason logged) | 87 |
| **identity check** | **65 + 68 + 87 = 220 ✓** (preserve-all) |

### 2.1 By source_record_type (main sample)

| source_record_type | count |
|---|---|
| `class_a_direct_primary` | 5 (all 2021-06) |
| `class_b_snapshot_diff_derived` | 54 |
| `class_b_title_linked_secondary` | 6 (KraftON/KakaoBank/KakaoPay/LG에솔/에코프로머티/포스코DX) |
| **total** | **65** |

### 2.2 By sample_role

| sample_role | count |
|---|---|
| `main_inclusion_addition_sample` | 65 |
| `negative_control_candidate_only` | 68 |
| `excluded_with_reason` | 87 |

### 2.3 By cycle (main sample only)

| cycle | total | A direct | B snap | B title-linked |
|---|---|---|---|---|
| 2021-06 | 5 | 5 | 0 | 0 |
| 2021-12 | 10 | 0 | 7 | 3 |
| 2022-06 | 8 | 0 | 7 | 1 |
| 2023-06 | 5 | 0 | 5 | 0 |
| 2023-12 | 8 | 0 | 8 | 0 |
| 2024-06 | 8 | 0 | 6 | 2 |
| 2024-12 | 5 | 0 | 5 | 0 |
| 2025-06 | 9 | 0 | 9 | 0 |
| 2025-12 | 7 | 0 | 7 | 0 |
| **total** | **65** | **5** | **54** | **6** |

Pre-estimate was 65; realised 65; difference 0 → **no halt** (well within 10% halt threshold).

---

## 3. Excluded-row counts and reasons

| reason | count |
|---|---|
| `skeleton_only_or_notice_level_only_not_constituent_level` | 75 (4 skeleton Tier 1 cycles' notice rows + 30 cycle meta + 41 special title-only no-name) |
| `cycle_excluded__effective_dt_rulebook_derived_blank_calendar_cutoff` | 10 (2026-06 cycle 5 add + 5 del) |
| `cycle_excluded__bridge_only_not_in_tier1` | 2 (2022-12 bridge 1 add + 1 del) |
| **total** | **87** |

---

## 4. Proof that no return / run-up / strategy metric was computed

The sample-prep code at `src/audit/bx01/prepare_inclusion_runup_diagnostic_sample.py`:

- Reads only CSV metadata columns (no price columns are read).
- Computes only date labels (announcement_dt, effective_dt_design, entry_dt_design, three exit candidates).
- Tags caveat columns (source_record_type / effective_dt_confidence / title_link_status / conflation_status / sample_role).
- Writes preview / registry / exclusion / manifest CSVs.
- Does NOT import any price-reading module, returns library, statistics library beyond `csv`/`hashlib`/`pathlib`/`datetime`.
- Does NOT compute returns, run-ups, Sharpe, hit rates, p-values, or any other quantitative result.

Verified by grep: 0 occurrences of `return`, `pct_change`, `Sharpe`, `pvalue`, `hit_rate`, `placebo`, `runup`, `run-up`, `runup`, or analogous metric calculation in the sample-prep code.

---

## 5. Proof of forbidden-action compliance

| Forbidden action | Status |
|---|---|
| External network / API / downloads / source recovery | ❌ none performed |
| HWP / PDF / OCR / binary / parser work | ❌ none performed |
| Event-table authority change / events_v3.csv modification | ❌ events_v3.csv UNCHANGED |
| authoritative events_v4.csv creation | ❌ not created |
| research_input_data/ or data/raw/ modification | ❌ unchanged |
| Price return / run-up / edge / hit-rate / Sharpe / alpha / placebo / strategy | ❌ none computed |
| Backtest execution | ❌ not executed |
| signals.csv / trades.csv / portfolio / P08 / production / paper-live / execution | ❌ none |
| Strategy / promotion / "works" claim | ❌ design only; explicit "no backtest executed" boundary in §0 + §13 of design doc |
| Use of title-derived rows as primary | ❌ all 6 title-linked rows tagged `class_b_title_linked_secondary` with `title_link_status=high_secondary_triangulated` |
| Deletion-side recovery | ❌ deletions are registry-only |
| Closed-family / BX02-04 / Bull-Bear / push | ❌ none |
| Self-close / Closed-Frozen / next-phase open | ❌ awaiting Referee gate |

---

## 6. Repo state

### 6.1 git status

`git status --short` per Referee ask_claude_53 procedural guard reporting:

- **pre-existing Referee relay-maintenance dirty file (OUT OF SCOPE for this phase, NOT touched by Executor):**
  - `M codex_claude_referee_relay.py`
- **this phase's new files (staged before commit):**
  - `data/acquired/bx01_kospi200_inclusion_runup_diagnostic_design_a0/` (5 CSVs)
  - `reports/experiments/BX01_KOSPI200_index_event_source_A0/inclusion_runup_diagnostic_backtest_design_a0.md`
  - `reports/experiments/BX01_KOSPI200_index_event_source_A0/inclusion_runup_diagnostic_design_initial_pass.md`
  - `src/audit/bx01/prepare_inclusion_runup_diagnostic_sample.py`
  - `.gitignore` (exception for new acquired/ subdir)
  - `docs/next_actions.md` (Active update)

### 6.2 git show --check HEAD

To be reported in the commit message after staging.

---

## 7. Recommended gate (NOT self-applied)

**Recommended: `DESIGN_READY_FOR_SEPARATE_DIAGNOSTIC_EXECUTION_DECISION`** (per directive expected wording).

Rationale:
- Design specification complete, audit-first 12-item checklist filled. ✅
- 65 main inclusion-addition events (matches pre-estimate; > 12 minimum). ✅
- LOCAL-ONLY; no forbidden action. ✅
- No backtest execution; no return / run-up / edge / strategy / placebo statistic computed. ✅
- Caveat tags applied per row (source_record_type / effective_dt_confidence / title_link_status / conflation_status / sample_role). ✅
- ≥12 named weaknesses; pre-registered success + kill criteria. ✅
- events_v3.csv UNCHANGED; preserve-all reconciliation 65 + 68 + 87 = 220. ✅

NOT `BACKLOG_DIAGNOSTIC_DESIGN_LOCAL_DATA_GAP` — local data sufficient for the design + sample preview + control-matching registry (peer selection deferred to execution phase per spec).

NOT `NOT_CLOSE_READY_FORBIDDEN_COMPUTATION` — verified §4.

NOT `NOT_CLOSE_READY_SCOPE_BREACH` — verified §5.

The actual execution of this design would be a SEPARATE phase under SEPARATE user + Referee decision.

---

## 8. Boundary statement

This phase:
- DID NOT compute any return / run-up / edge / Sharpe / alpha / hit-rate / placebo / p-value / strategy metric.
- DID NOT execute any backtest.
- DID NOT read price columns.
- DID NOT use external network / API / downloads / source recovery.
- DID NOT parse hwp / broker pdf / OCR / binary documents.
- DID NOT modify `events_v3.csv` or canonical `effective_dt`.
- DID NOT create authoritative `events_v4.csv`.
- DID NOT modify `research_input_data/` or `data/raw/`.
- DID NOT open backtest / Bull-Bear / P08 / closed-family / parser-measurement-layer.
- DID NOT label any row strategy-ready / executable / approved / production-ready / paper-ready.
- DID NOT self-close. DID NOT move to Closed/Frozen. DID NOT open downstream phase.
- DID NOT push.
- DID NOT modify `codex_claude_referee_relay.py` (pre-existing Referee relay-maintenance dirty file; out of scope per ask_claude_53).

Frozen P08_IEF30 — untouched. Measurement-layer DECIDED STANDBY — untouched. Closed families — untouched. Bear's BX02 / BX03 / BX04 verdicts — intact.
