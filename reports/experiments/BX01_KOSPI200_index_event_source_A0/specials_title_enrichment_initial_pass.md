# BX01-KOSPI200-SPECIALS-TITLE-ENRICHMENT-A0 — Initial Pass Report

**Phase pre-reg + addendum:** carry-forward + this report.
**Initial-pass date:** 2026-05-31
**Authored by:** Executor (Claude Code, autonomous mode per user 2026-05-31)
**For:** Referee gate verdict — NOT self-applied.
**Directive:** `.codex-claude-relay/codex_outbox/ask_0011.md` (option 3 from
tier2-tier3 close options).

---

## TL;DR

**Scope: 6 KOSPI 200 main-index special-inclusion notices**, all confirmed
matching the directive's required set (bbsSeq 758/759/773/789/907/921 across
3 affected Class B cycles 2021-12 / 2022-06 / 2024-06).

**Title → company → ticker linking: 6/6 confirmed.** All 6 titles match the
deterministic patterns ("〈name〉 신규상장에 따른" / "〈name〉 이전상장에 따른");
all 6 names exact-match a constituent in a subsequent KOSPI 200 snapshot (i.e.,
the company is verifiably in the index after the special). All 6 candidate
links labeled `addition_candidate_title_derived` per directive — secondary /
triangulated / NOT primary.

**Conflation status (per affected Class B cycle):**
- 2021-12: 3 specials → 3 linked → ALL ADDITIONS LINKED.
- 2022-06: 1 special → 1 linked → ALL ADDITIONS LINKED.
- 2024-06: 2 specials → 2 linked → ALL ADDITIONS LINKED.
- Deletions / replacements REMAIN UNRESOLVED in all 3 cycles (cannot be
  inferred from title alone).

**Recommended gate: `BACKLOG_TITLE_ENRICHMENT_PARTIAL_SECONDARY_LINKS`** (per
directive: "If all 6 special-notice additions are title-linked but deletions/
replacements remain unresolved: still likely BACKLOG_TITLE_ENRICHMENT_PARTIAL_
SECONDARY_LINKS").

---

## 1. Step 1 — Scope verification

Loaded `kospi200_notice_index.json`. All 6 directive-scoped bbsSeq present:

| bbsSeq | reg_dt | affected Class B cycle | title (truncated) |
|---|---|---|---|
| 758 | 2021-08-31 | 2021-12 | 카카오뱅크 신규상장에 따른 KOSPI 200 등 수시변경 안내 |
| 759 | 2021-08-31 | 2021-12 | 크래프톤 신규상장에 따른 KOSPI 200 등 수시변경 안내 |
| 773 | 2021-11-24 | 2021-12 | 카카오페이 신규상장에 따른 코스피200 등 수시변경 안내 |
| 789 | 2022-02-22 | 2022-06 | LG에너지솔루션 신규상장에 따른 코스피200 등 수시변경 안내 |
| 907 | 2023-12-08 | 2024-06 | 에코프로머티 신규상장에 따른 코스피200 등 수시변경 안내 |
| 921 | 2024-01-23 | 2024-06 | 포스코DX 이전상장에 따른 코스피 200 등 수시변경 안내 |

bbsSeq=1020 (KOSPI 200 ESG sub-index 수시변경 2025-06-04) carried in
`title_enrichment_targets.csv` as out-of-scope ESG sub-index caveat
(`scope_flag=out_of_scope_subindex_ESG_caveat_only`).

→ Count check: PASS (6/6 in scope; 1 sub-index caveat preserved).

---

## 2. Step 2 — Title name extraction

Deterministic regex rules applied:

| rule_id | pattern | matches |
|---|---|---|
| `new_listing` | `^(.+?)\s*신규상장에\s*따른` | 5 (758, 759, 773, 789, 907) |
| `transfer_listing` | `^(.+?)\s*이전상장에\s*따른` | 1 (921) |

All 6 → `extraction_confidence=high` (deterministic exact pattern match).
Per-row caveat: "title-derived only; secondary/triangulated; not authoritative
parse".

Extracted names:
- 758 → "카카오뱅크"
- 759 → "크래프톤"
- 773 → "카카오페이"
- 789 → "LG에너지솔루션"
- 907 → "에코프로머티"
- 921 → "포스코DX"

`title_name_extractions.csv` (5 cols × 6 rows).

---

## 3. Step 3 — Listing-name cross-check

Local artifacts used (per directive, LOCAL ONLY):
- `data/acquired/bx01_kospi200_index_event_source_a0/snapshots.csv` (KOSPI 200
  ticker-cycle snapshots from BX01-attachment-parse-A0; primary signal: the
  ticker is verifiably a KOSPI 200 constituent after the special).
- `data/acquired/krx_listed_universe/krx_listed_monthly_snapshots_2010_2026.csv`
  (PIT listing fallback if not in KOSPI 200 snapshot).

Method: `kospi200_snapshot_exact_name` (preferred, exact name match against
post-effective KOSPI 200 snapshot constituent list). All 6 → matched in
KOSPI 200 snapshots with `high_secondary_triangulated` confidence.

Resulting (name → ticker) candidate pairs:
- 카카오뱅크 → 323410
- 크래프톤 → 259960
- 카카오페이 → 377300
- LG에너지솔루션 → 373220
- 에코프로머티 → 450080
- 포스코DX → 022100

`listing_name_crosscheck.csv` (8 cols × 6 rows).

---

## 4. Step 4 — Candidate links to Class B snapshot-diff rows

For each (special bbsSeq, candidate ticker, affected Class B cycle), looked up
the corresponding addition row in `events_v3.csv` filtered by:
- `source_record_type=constituent_level_derived_from_consecutive_official_snapshot_diff`
- `review_cycle=<affected cycle>`
- `ticker=<candidate ticker>`
- `side=addition`

Result: **6/6 matched** to existing Class B derived addition rows. The 6
special-attributable additions were thus already present in events_v3.csv but
attributed to the regular review by Class B's snapshot diff — this phase
now provides title-derived secondary evidence that these were SPECIAL
intermediate events, not regular review additions.

`special_candidate_links.csv` (9 cols × 6 rows). Every row tagged
`side=addition_candidate_title_derived` and
`source_basis=title_name_extraction + kospi200_snapshot_exact_name`.

Per directive: this is NOT a parsed event log; it is a CANDIDATE LINK proposal.
Existing events_v3.csv rows are NOT silently reclassified — both the original
Class B derived row AND the candidate link proposal coexist, with the link
providing secondary/triangulated evidence that the addition's TIMING was the
special event date rather than the regular review effective date.

---

## 5. Step 5 — Conflation reconciliation (title-enriched)

`conflation_reconciliation_title_enriched.csv` (6 cols × 3 rows):

| Class B cycle | unresolved specials BEFORE | linked | remaining | status |
|---|---|---|---|---|
| 2021-12 | 3 | 3 | 0 | ALL_ADDITIONS_LINKED__deletions_replacements_may_remain_unresolved |
| 2022-06 | 1 | 1 | 0 | ALL_ADDITIONS_LINKED__deletions_replacements_may_remain_unresolved |
| 2024-06 | 2 | 2 | 0 | ALL_ADDITIONS_LINKED__deletions_replacements_may_remain_unresolved |

Caveat (per row): "title-derived = secondary/triangulated; addition-side only;
deletion/replacement remain inferable only from primary parse."

**Impact on Class B regular/special separation:**
- For each of the 3 cycles, the **addition** side of conflation is now
  PARTIALLY ATTRIBUTABLE via title-derived secondary evidence to the special
  event date.
- The **deletion** side of each cycle's snapshot diff remains conflated.
  Snapshots show a stock disappeared between snapshots, but whether the
  disappearance happened at the regular review or at an intermediate
  special/supplemental event cannot be inferred from title alone.
- A primary parse of the special-notice attachments (hwp/no_attach) would
  be required to resolve the deletion side. That is a separate phase
  decision.

---

## 6. NO events_v4 produced

Per directive: "If producing an events-v4-style artifact, it must be clearly
named `proposed` and must preserve all prior BX01 rows/provenance."

This phase produces ONLY the 5 candidate-link/reconciliation artifacts above.
NO events_v4.csv created. `events_v3.csv` remains the authoritative BX01
event artifact UNCHANGED (220 rows; 133 effective_dt_rulebook_derived; 6
residual blockers — UNCHANGED).

The `special_candidate_links.csv` is the proposal artifact; it links to
existing v3 rows by `matching_class_b_event_id` and does NOT overwrite or
silently reclassify any v3 row.

---

## 7. Outputs

```
data/acquired/bx01_kospi200_specials_title_enrichment_a0/
  title_enrichment_targets.csv             7 rows × 6 cols (6 scoped + 1 sub-index caveat)
  title_name_extractions.csv               6 rows × 5 cols
  listing_name_crosscheck.csv              6 rows × 8 cols
  special_candidate_links.csv              6 rows × 9 cols
  conflation_reconciliation_title_enriched.csv  3 rows × 6 cols

reports/experiments/BX01_KOSPI200_index_event_source_A0/
  specials_title_enrichment_initial_pass.md  THIS FILE
```

---

## 8. Gate recommendation (for Referee — NOT self-applied)

**Recommended: `BACKLOG_TITLE_ENRICHMENT_PARTIAL_SECONDARY_LINKS`**
(directive's expected wording for "all 6 special-notice additions are
title-linked but deletions/replacements remain unresolved").

Rationale:
- All 6 directive-scoped special additions title-linked at
  `high_secondary_triangulated` confidence. ✅
- Addition side of 3 Class B cycles' conflation partially separated via
  secondary/triangulated evidence. ✅
- Deletion / replacement side REMAINS UNRESOLVED for all 3 cycles. ❌
- NOT primary parse, NOT authoritative. ✅
- NOT FAIL_CLOSED — material progress on the addition side.
- NOT a backtest gate (no-backtest carried forward).

---

## 9. Next-step candidates (NOT pre-authorized; require separate Referee
   directive)

To resolve the deletion / replacement side of Class B conflation, a primary
parse would be needed. Candidates:
1. HWP parser phase (would also cover the 16 hwp specials + 4 missing Tier 1
   hwp; DART body-parser standby-lock adjacent).
2. Broker PDF parse phase (per-file halt+escalate; would cover the 1 pdf
   special + 2 Tier 1 broker pdfs).
3. Manual user-supplied attachment for the 6 specials specifically.
4. Backlog / standby.

NONE opened by this report.

---

## 10. Repo state

- Initial-pass commit (this phase): to be filled at commit time below.
- Working tree before commit: clean.
- `research_input_data/` files NEVER modified.
- No push.

---

## 11. Boundary statement

This phase:
- DID NOT use external network (local-only per directive).
- DID NOT parse hwp / broker pdf / OCR / binary documents.
- DID NOT modify `research_input_data/`.
- DID NOT open backtest / Bull-Bear / P08 / closed-family / parser-measurement-layer.
- DID NOT compute any return / run-up / edge / strategy / portfolio.
- DID NOT label any row primary / authoritative / validated / approved /
  executable / strategy-ready / production-ready / paper-ready (every
  candidate row is `addition_candidate_title_derived` / secondary /
  triangulated).
- DID NOT modify events_v3.csv. DID NOT produce events_v4.csv.
- DID NOT self-close. DID NOT move to Closed/Frozen. DID NOT open downstream phase.
- DID NOT push.

Frozen P08_IEF30 — untouched. Measurement-layer DECIDED STANDBY — untouched.
Closed families — untouched. Bear's BX02 / BX03 / BX04 verdicts — intact.
