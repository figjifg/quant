# BX01-KOSPI200-TIER2-TIER3-SPECIALS-PARSE-A0 — Initial Pass Report

**Phase pre-reg + addendum:** carry-forward from prior BX01 phases + this report.
**Initial-pass date:** 2026-05-31
**Authored by:** Executor (Claude Code, autonomous mode per user 2026-05-31
authorization + Referee `ask_claude_06.md` directive)
**For:** Referee gate verdict — NOT self-applied.

---

## TL;DR

**Target count verified: 55 Tier 2/3 specials EXACT match** between
`kospi200_notice_index.json` (source-A0) and `events_v3.csv` `BX01-*-SPECIAL`
rows. No discrepancy → no halt on count.

**Source-format finding (decisive):** the 55 specials' attach distribution is
**16 hwp + 1 pdf + 38 no_attach + 0 xlsx/csv/HTML-table**. Per directive scope
("Parse clearly structured sources only: `.xlsx`, `.csv`, and HTML tables"),
**0 of 55 specials have a parseable source within the directive's allowed
format set**, regardless of network access.

Single probes confirm prior phase blockers persist (OTP 0-byte; static 404/405;
Wayback empty).

**Recommended gate: `BACKLOG_TIER2_TIER3_STRUCTURED_SOURCE_GAP`**
(directive's expected wording for "no structured Tier 2/3 sources acquired/
parsed").

**Conflation reconciliation (post-Referee 2026-05-31 main-index scope
cleanup):** of 55 specials, **48 fall pre-2021-06** (i.e., BEFORE Class B
parsing started — they cannot affect Class B regular/special conflation by
construction). The remaining **7 fall inside Class B windows** (2021-12: 3
main-index / 2022-06: 1 main-index / 2024-06: 2 main-index / 2025-12: 1
**ESG SUB-INDEX VARIANT — out-of-scope for KOSPI 200 main-index
conflation**). Therefore **6 main-index-relevant unresolved specials** + 1
sub-index variant caveat. Class B main-index regular/special conflation
persists for **3 of 9 Class B cycles** (2021-12 / 2022-06 / 2024-06).
2025-12 is now main-index-clean with a sub-index caveat.

---

## 1. Step 1 — Canonical Tier 2/3 target list + count verification

Built from existing local BX01 artifacts:
- `data/acquired/bx01_kospi200_index_event_source_a0/raw/kospi200_notice_index.json` —
  55 special-tagged notices.
- `data/acquired/bx01_kospi200_index_event_source_a0/events_v3.csv` — 55
  rows with `event_id` ending `-SPECIAL`.
- `data/acquired/bx01_kospi200_index_event_source_a0/raw/krx_board_all.json` —
  full board metadata; used to extract `attach_file_info` per bbsSeq.

| Source | Count | bbsSeq overlap |
|---|---|---|
| notice_index.json specials | 55 | base set |
| events_v3.csv -SPECIAL rows | 55 | identical |
| set intersection | 55 (perfect match) | no discrepancy |

→ No count-discrepancy halt. **Target = 55 as Referee expected.**

`target_list.csv` (11 cols × 55 rows): bbsSeq / event_id_in_v3 / reg_dt /
title / event_class / event_sub_class / attach_file_info /
class_b_conflation_window / class_b_conflation_window_note /
current_source_status_in_bx01 / directive_status_for_this_phase.

### 1.1 Sub-class distribution (from title heuristics carried from source-A0):

| sub-class | count |
|---|---|
| `special_change_pre_2017_naming` (특별변경) | 18 |
| `special_inclusion` (신규상장/이전상장/특례편입) | 13 |
| `special_deletion` (관리종목/상장폐지/피흡수합병) | 11 |
| `special_split` (인적분할/기업분할) | 9 |
| `supplemental_intra_period_change` (수시변경) | 4 |

### 1.2 Attach-format distribution (CRITICAL for directive scope):

| ext | count | directive treatment |
|---|---|---|
| `xlsx` / `csv` / HTML-table | **0** | (allowed; not present) |
| `hwp` | 16 | DEFERRED — "No HWP parser phase in this directive" |
| `pdf` | 1 | DEFERRED — broker PDF parse requires halt+escalate per file |
| `no_attach` | 38 | DEFERRED — no structured source exists; only title metadata |

**0/55 specials have a directive-allowed structured-source attachment.** This
is independent of network blocking — it's a SOURCE-FORMAT finding, not an
acquisition failure.

---

## 2. Step 2 — Source probes (small documented sample)

Per directive: "A small documented probe is allowed; if the same 0-byte/blocked
pattern appears, stop that route and record it."

Probed single sample (oldest special, bbsSeq=159 / 2010-01-22 / hwp attach):

| Attempt class | Observed | Blocker class | Route action |
|---|---|---|---|
| OTP 2-step (`data.krx.co.kr` step 1 → `file.krx.co.kr/download.jspx` step 2) | HTTP 200 + Content-Length: 0 (empty body) on step 2; step 1 successfully issued OTP token | `BLOCKED_OTP_SANDBOX_EGRESS_ANTI_BOT_SAME_AS_BX01_SOURCE_A0_AND_MISSING_TIER1_A0` | stopped + recorded |
| Direct static `data.krx.co.kr/{hpbbs,kor}/dyn/etc/<save>` | HTTP 404 | `STATIC_PATH_NOT_AVAILABLE` | stopped + recorded |
| Direct static `kind.krx.co.kr/{hpbbs,kor}/dyn/etc/<save>` | HTTP 405 Method Not Allowed | `STATIC_PATH_405` | stopped + recorded |
| Wayback Machine `archive.org/wayback/available?url=<detail_page>` | `archived_snapshots: {}` | `NO_WAYBACK_COVERAGE` | stopped + recorded |

`attempt_log.csv` extends the probe outcomes (recorded from prior phases for
the same blockers) to all 55 targets × 4 attempt classes = **220 attempt
rows**. No aggressive retry; one probe per route confirms the universal
pattern.

Probe artifacts saved:
- `attempt_log/step1_159.json` — valid OTP token issued.
- `attempt_log/step2_159.bin` — 0 bytes confirming downstream block.

---

## 3. Step 3 — Inventory of user-supplied files for these specials

`research_input_data/정기변경/` contains user-supplied files from
BX01-attachment-parse-A0:
- 18.6.hwp / 18.12.hwp / 19.6.hwp / 19.12.hwp (KRX 보도자료 hwp; regular reviews)
- 20.6.pdf / 20.12.pdf (broker PDFs; regular reviews)
- 21.6.xlsx through 26.6.xlsx (regular reviews + 22.12 bridge)

**NONE of the user-supplied files correspond to a Tier 2/3 SPECIAL event** — all
17 files are REGULAR review attachments. The 55 specials remain entirely
unrepresented in the user-supplied set.

→ No user-supplied path to Tier 2/3 specials in current state.

---

## 4. Step 4 — Coverage matrix

`coverage_matrix.csv` (10 cols × 55 rows): per-event status. Headlines:

- **0/55 acquired**. All rows `acquired=NO`.
- 16 rows blocker: `format_HWP__directive_explicitly_forbids_HWP_parser_phase__deferred`.
- 1 row blocker: `format_PDF__directive_requires_halt_escalate_per_file__not_invoked`.
- 38 rows blocker: `no_attachment_only_title_metadata__no_structured_source_exists_to_acquire`.
- `parsed_row_count` for every row: 0.

---

## 5. Step 5 — Conflation reconciliation per Class B cycle

`conflation_reconciliation.csv` (6 cols × 9 Class B cycles):

| Class B cycle | main-index specials in window | parsed | unparsed | status | notes |
|---|---|---|---|---|---|
| 2021-12 | 3 | 0 | 3 | UNRESOLVED | bbsSeq 758/759 (2021-08; KraftON/KakaoBank specials) + 773 (2021-11; KakaoPay) |
| 2022-06 | 1 | 0 | 1 | UNRESOLVED | bbsSeq 789 (2022-02; LG에너지솔루션 신규상장) |
| 2023-06 | 0 | 0 | 0 | no_intermediate_specials_pure_regular_review | clean |
| 2023-12 | 0 | 0 | 0 | clean | |
| 2024-06 | 2 | 0 | 2 | UNRESOLVED | bbsSeq 907 (2023-12 에코프로머티) + bbsSeq 921 (2024-01 포스코DX) |
| 2024-12 | 0 | 0 | 0 | clean | |
| 2025-06 | 0 | 0 | 0 | clean | |
| 2025-12 | 0 | 0 | 0 | no_main_index_intermediate_specials__subindex_variant_deferred | window had bbsSeq=1020 (코스피 200 ESG 지수 수시변경) — ESG SUB-INDEX VARIANT, NOT main-index constituent change; deferred per Referee 2026-05-31 cleanup |
| 2026-06 | 0 | 0 | 0 | clean | |

**Class B regular/special conflation status (post-Referee 2026-05-31
main-index scope cleanup):**
- **3 of 9 Class B cycles** (2021-12 / 2022-06 / 2024-06) have main-index
  intermediate specials inside their window AND those specials remain
  unparsed in this phase. Main-index conflation persists for these 3.
- **6 of 9 Class B cycles** are main-index clean (no main-index
  intermediate specials inside their window). Of those 6, 1 (2025-12)
  carries a SUB-INDEX caveat (bbsSeq=1020 ESG sub-index variant), 5
  (2023-06 / 2023-12 / 2024-12 / 2025-06 / 2026-06) were already clean
  per the rulebook-A0 carry-forward.
- Total: 6 main-index-relevant unresolved specials + 1 sub-index variant
  caveat. (Previous over-statement of "7 in window all UNRESOLVED" /
  "4 cycles UNRESOLVED" corrected per Referee 2026-05-31 review.)

The 48 pre-2021-06 specials fall BEFORE Class B parsing started; they never
caused Class B conflation by construction, and are out of conflation scope
even though they're inside the Tier 2/3 target set.

---

## 6. Outputs

```
data/acquired/bx01_kospi200_tier2_tier3_specials_parse_a0/
  raw/                          (empty — no structured source acquired)
  attempt_log/
    step1_159.json              OTP step 1 evidence (token issued)
    step2_159.bin               OTP step 2 result (0 bytes)
  target_list.csv               55 rows (canonical Tier 2/3 target list)
  attempt_log.csv               220 rows (55 × 4 attempt classes)
  manifest.csv                  2 rows (OTP step1/step2 evidence)
  coverage_matrix.csv           55 rows (all acquired=NO)
  conflation_reconciliation.csv 9 rows (3 UNRESOLVED main-index + 5 clean
                                  + 1 sub-index caveat = 6 main-index-clean total)

reports/experiments/BX01_KOSPI200_index_event_source_A0/
  tier2_tier3_specials_parse_initial_pass.md  THIS FILE
```

**NO `tier2_tier3_candidate_events.csv` produced** (no rows parsed).
**NO `events_v4.csv` produced** (no rows to add). `events_v3.csv` remains
the authoritative BX01 event artifact.

---

## 7. PIT / tradability impact

events_v3.csv state UNCHANGED (220 rows; 133 effective_dt_rulebook_derived
filled; 6 residual blockers). The conflation_reconciliation.csv documents
that Class B regular/special conflation is now **explicitly mapped** but
unresolved for **3 of 9 cycles** (main-index): 2021-12 / 2022-06 / 2024-06.
2025-12 carries a sub-index variant deferred caveat (bbsSeq=1020 ESG sub-
index, not main-index).

---

## 8. Gate recommendation (for Referee — NOT self-applied)

**Recommended: `BACKLOG_TIER2_TIER3_STRUCTURED_SOURCE_GAP`** (directive's
expected wording).

Rationale:
- 0/55 Tier 2/3 specials have a directive-allowed structured-source
  attachment (xlsx/csv/HTML-table). The source format mix is 16 hwp + 1 pdf +
  38 no-attach + 0 xlsx.
- Single probes confirm prior network blockers persist.
- No HWP parsing per directive. No broker PDF parsing without halt+escalate
  (not invoked).
- No bypass / no aggressive retry.
- NOT FAIL_CLOSED: source is real (KRX board), the blocker is format + same
  environmental OTP gating; not source-legal.
- NOT a backtest gate (no-backtest carried forward).

---

## 9. Next-step candidates (NOT pre-authorized; require separate Referee
   directive after gate sign-off)

If Class B conflation resolution is the goal, the natural follow-on phases
(none opened by this report) would be:

1. **HWP parser phase** (option D from rulebook-A0 close options) — would
   address the 16 hwp specials + the 4 missing Tier 1 hwp from earlier; but
   inherently parser-infrastructure work + DART body-parser standby-lock-
   adjacent per prior Referee notes.
2. **Broker PDF parse phase (per-file halt+escalate)** — would address the
   1 pdf special + the 2 broker pdf Tier 1 from earlier; but requires
   halt+escalate per file with extraction method per this directive.
3. **Title-extraction enrichment phase (NEW)** — leverage existing
   `title_extracted_name` (14/55 already populated in events_v3.csv) +
   listing-name cross-check to PARTIALLY identify intermediate specials
   for the **3 UNRESOLVED main-index Class B cycles** (2021-12 / 2022-06 /
   2024-06). The 2025-12 sub-index caveat (bbsSeq=1020) is separate scope.
   This would NOT be a primary parse;
   it would be a secondary triangulation similar to the rulebook-A0
   hybrid (c). Would need a fresh directive.
4. **G — backlog + standby.**

NONE of these are opened by this report. Per directive: "Do not open the
next phase."

---

## 10. Repo state

- Initial-pass commit (this phase): to be filled at commit time below.
- Working tree before commit: clean.
- `research_input_data/` files NEVER modified.
- No push.

---

## 11. Boundary statement

This phase:
- DID NOT bypass any paywall / login / OTP / anti-bot control.
- DID NOT modify any file under `research_input_data/`.
- DID NOT parse hwp or broker PDF.
- DID NOT open Tier 1 acquisition / Bull-Bear / P08 / closed-family / parser-measurement-layer.
- DID NOT compute any return / run-up / edge / strategy / portfolio.
- DID NOT label any row strategy-ready / executable / approved / production-ready / paper-ready.
- DID NOT self-close. DID NOT move to Closed/Frozen. DID NOT open downstream phase.
- DID NOT push.

Frozen P08_IEF30 — untouched. Measurement-layer DECIDED STANDBY — untouched.
Closed families — untouched. Bear's BX02 / BX03 / BX04 verdicts — intact.
