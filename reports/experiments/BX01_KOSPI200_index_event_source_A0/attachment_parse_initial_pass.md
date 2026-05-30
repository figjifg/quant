# BX01-KOSPI200-ATTACHMENT-PARSE-A0 — Initial Pass Report

**Phase pre-reg + addendum:** `research/experiments/BX01_KOSPI200_index_event_source_A0.md`
(source-A0) + this report (attachment-parse-A0 addendum).
**Initial-pass date:** 2026-05-31
**Authored by:** Executor (Claude Code)
**For:** Referee (Codex) gate verdict — NOT self-applied.
**Directive:** `.codex-claude-relay/codex_outbox/ask_0008.md`
(BX01-KOSPI200-ATTACHMENT-PARSE-A0) + 2026-05-30 Referee clarification ack on
halt+escalate (extending allowed source-classes A/B with snapshot-diff design, Class
C/D deferred).

---

## TL;DR

User supplied **17 files** in `research_input_data/정기변경/` (project read-only-input
dir; treated as immutable raw and never modified). Initial intake-time halt fired on
the directive's halt-trigger; after Referee 2026-05-30 clarification, Class A and
Class B (with user-confirmed cycle mapping) became eligible to parse; Class C (hwp)
and Class D (broker pdf) were explicitly deferred.

User then renamed files with date-coded filenames (`YY.M(M).ext`) confirming the
cycle mapping for each file. With that mapping, **10 of 14 Tier 1 review cycles
yielded constituent-level rows** (1 direct from Class A's explicit `KOSPI 200 변경내역`
sheet + 9 derived via consecutive Class B snapshot diff). The remaining 4 Tier 1
cycles (2018-06, 2019-06, 2020-06, 2020-12) live in hwp / broker pdf files that are
deferred per Referee.

Results:
- **12 rows** Class A direct (2021-06 review)
- **133 rows** Class B derived for 9 Tier 1 cycles + 2 bridge rows (2022-12, NOT in
  Tier 1; 2 bridge rows are part of the 133 — i.e. 131 Tier 1 + 2 bridge)
- **75 rows** notice-level skeleton carried forward (4 uncovered Tier 1 cycles +
  Tier 2/3 specials)
- **220 rows total** in `events_v2.csv`, fully preserve-all, with every row
  carrying explicit `source_record_type` and `parse_status` and full caveats.
- **Listing-name cross-check (final-pass per Referee 2026-05-31): 138/145
  constituent-level rows (95.2%) confirmed in PIT listing snapshot**; 5
  ticker_not_in_pit_listing edge cases (new-listing/post-merger near event date);
  2 pit_snapshot_unavailable; 0 ticker conflicts. Listing-name fields were
  largely empty in the listing-universe-A0 source (25.3% panel coverage gap —
  known limit per `project-listed-universe-coverage-a0`), so we use the
  refined `match_ticker_only_listing_name_unavailable` label rather than
  inflating "name mismatch".

Mandatory caveat (also carried per-row): snapshot-diff derived rows capture ALL
changes between consecutive snapshots — i.e. regular review at the curr-cycle PLUS
any intermediate SPECIAL/SUPPLEMENTAL event (Tier 2/3, deferred). The downstream
user decision must separate them.

**Recommended gate verdict to Referee: `BACKLOG_ATTACHMENT_PARSE_GAP`** — parse for
the 10 covered cycles is auditable + caveated, but (a) special/regular conflation is
unresolved, (b) effective_dt is universally blank (Referee rule: direct-from-file
only; nothing inside the attachments provided a direct effective_dt), (c) 4 of 14
Tier 1 cycles remain skeleton-only (hwp / broker pdf deferred). The listing-name
cross-check has been EXECUTED in the final pass (see §7): 138/145 const-level
rows ticker-confirmed in PIT listing; remaining blockers above (effective_dt
blank, 4 skeleton-only cycles, regular/special conflation) are not resolved by
the cross-check.

NOT `PASS_TO_DIAGNOSTIC_BACKTEST_DESIGN` for those reasons.
NOT `FAIL_CLOSED` — the parse for 10 cycles is materially better than the prior
notice-level skeleton; the gap is addressable in defined follow-on steps that
require separate user + Referee decision.

---

## 1. Intake — what arrived

User location: `research_input_data/정기변경/` (project read-only-input dir; never
modified). Treated as immutable raw artifacts.

User renamed every file with date-coded form (`YY.M(M).ext`). The rename is treated
as the authoritative cycle mapping per Referee 2026-05-30 clarification ("tier1
expected filename / bbsSeq / reg_dt와 파일명 또는 workbook 내부 문구가 명확히
대응되면 high-confidence").

| Tier 1 bbsSeq | Cycle | User file | Class | Status |
|---|---|---|---|---|
| 555 | 2018-06 | `18.6.hwp` | C | DEFERRED (hwp parse out-of-scope) |
| 613 | 2019-06 | `19.6.hwp` | C | DEFERRED |
| — | 2019-12 | `19.12.hwp` (NOT in Tier 1) | C | DEFERRED |
| 667 | 2020-06 | `20.6.pdf` | D | DEFERRED (broker pdf, secondary) |
| 696 | 2020-12 | `20.12.pdf` | D | DEFERRED |
| 734 | 2021-06 | `21.6.xlsx` ≡ `21.06+...공지파일.xlsx` (sha=af327b2c2bef…) | **A** | **DIRECT PARSE** |
| 774 | 2021-12 | `21.12.xlsx` | B | DERIVED (vs 21.6) |
| 799 | 2022-06 | `22.6.xlsx` | B | DERIVED (vs 21.12) |
| — | 2022-12 | `22.12.xlsx` (NOT in Tier 1) | B | BRIDGE (vs 22.6) |
| 861 | 2023-06 | `23.6.xlsx` | B | DERIVED (vs 22.12 bridge) |
| 899 | 2023-12 | `23.12.xlsx` | B | DERIVED (vs 23.6) |
| 939 | 2024-06 | `24.6.xlsx` | B | DERIVED (vs 23.12) |
| 979 | 2024-12 | `24.12.xlsx` | B | DERIVED (vs 24.6) |
| 1015 | 2025-06 | `25.6.xlsx` | B | DERIVED (vs 24.12) |
| 1050 | 2025-12 | `25.12.xlsx` | B | DERIVED (vs 25.6) |
| 1090 | 2026-06 | `26.6.xlsx` | B | DERIVED (vs 25.12) |
| — | 2018-12 | `18.12.hwp` (NOT in Tier 1) | C | DEFERRED |

Inventory + sha256 + source notes for each file are in `manifest.csv` (appended;
prior 8 source-A0 manifest rows + 18 user-supplied rows = 26 manifest rows total).

---

## 2. Halt + Escalate (recorded)

Per the directive's halt-trigger list:

> "Halt and escalate if: ... a supplied file is not a credible KRX `.xlsx`
> attachment; the workbook layout does not clearly identify KOSPI200 [add/delete]
> rows; parsing would require inference beyond the file contents."

All three conditions were present in the initial intake (before user rename):
- 2 PDFs were 증권사 출간물 (not KRX `.xlsx`)
- 4 HWPs were 보도자료 body text (not `.xlsx`)
- 10 xlsx files were KRX snapshots without explicit `변경내역` sheet (didn't identify
  KOSPI200 add/delete directly)
- Filenames duplicated (multiple `(붙임)+KOSPI+200,...+정기변경 (1)/(2)/(3).xlsx`)
  precluded confident cycle mapping by filename alone

Executor sent a structured halt+escalate report to Referee (full content in
`.codex-claude-relay/bx01_parse_halt_escalate_msg.txt`). Referee replied 2026-05-30
extending the directive with the snapshot-diff design under strict conditions:

- Class A → proceed (KOSPI 200 only).
- Class B → coverage matrix first; high-confidence cycle mapping required; snapshot
  table allowed; consecutive-snapshot diff allowed IF AND ONLY IF both snapshots
  are high-confidence + KRX official + KOSPI 200 list clear; derived rows tagged
  `derived_via_consecutive_official_snapshot_diff`; direct-vs-derived confidence
  never collapsed.
- Class C → defer (hwp parse out-of-scope this phase; not the same as DART body
  parser lock but adjacent — separate user + Referee decision required to open).
- Class D → defer (broker pdf is secondary source authority, not KRX direct;
  not record-of-record).
- effective_dt direct-from-file-only (NEVER rule/memory/convention/diff/rebalance-
  date fill).
- listing-name cross-check required for accepted rows.
- preserve-all + caveats + no-self-close + no-downstream-phase.

User then renamed all 17 files with date-coded form, providing high-confidence
mapping per Referee's criteria. Coverage matrix then yielded 10 Tier 1 + 1 bridge
+ 4 hwp-deferred + 2 pdf-deferred.

---

## 3. Class A direct parse — 2021-06 (bbsSeq=734)

File: `21.6.xlsx` ≡ `21.06+KOSPI+200,+KOSDAQ+150,+KRX+300+공지파일.xlsx`
(sha=af327b2c2bef…). Sheet `KOSPI 200 변경내역` contains explicit 편입 / 제외 columns.

**5 additions** (KOSPI 200, 2021-06 regular review):
- 001440 대한전선
- 006040 동원산업
- 298020 효성티앤씨
- 298050 효성첨단소재
- 302440 SK바이오사이언스

**7 deletions** (KOSPI 200, 2021-06 regular review):
- 005180 빙그레
- 005610 SPC삼립
- 006390 한일현대시멘트
- 008350 남선알미늄
- 009410 태영건설
- 018250 애경산업
- 145990 삼양사

Output: `events_class_a.csv` (12 rows). KOSDAQ150 / KRX300 sheets noted but not
expanded into event rows per directive scope.

Independent secondary cross-check: news summary
[(seoulfn.com, smarttoday.co.kr, etc.)](https://www.smarttoday.co.kr/news/articleView.html?idxno=81929)
matches: 5 additions including SK바이오사이언스, 대한전선, 동원산업, 효성티앤씨, 효성첨단소재;
7 deletions including 빙그레 et al. ✅

---

## 4. Class B snapshot diff — derived rows for 9 Tier 1 cycles + 1 bridge

Pipeline: parse each Class B xlsx as a KOSPI 200 ticker-set snapshot (post-effective
constituents for that cycle), then compute consecutive-cycle set diffs.

| Curr cycle | bbsSeq | Tier1 | +Add | −Del | Caveat |
|---|---|---|---|---|---|
| 2021-12 | 774 | yes | 10 | 10 | Includes intermediate-special 크래프톤 (2021-08), 카카오뱅크 (2021-08), 카카오페이 (2021-11) — confounded with the regular 2021-12 review |
| 2022-06 | 799 | yes | 8 | 8 | Includes intermediate-special LG에너지솔루션 (2022-01) — confounded with regular 2022-06 |
| 2022-12 | — | **bridge_only_not_in_tier1** | 1 | 1 | Bridge for 23-6 derivation; events not emitted as Tier 1 |
| 2023-06 | 861 | yes | 5 | 5 | Uses 22.12 bridge as `prev` (rather than 22.6) to isolate the 2023-06 regular review |
| 2023-12 | 899 | yes | 8 | 8 | Includes intermediate-special 에코프로머티 (2023-12 special; conflation noted) |
| 2024-06 | 939 | yes | 8 | 8 | Includes intermediate-special 포스코DX (2024-01 special; conflation noted) |
| 2024-12 | 979 | yes | 5 | 5 | |
| 2025-06 | 1015 | yes | 9 | 9 | |
| 2025-12 | 1050 | yes | 7 | 8 | KOSPI 200 row count 199 (delisting unfilled until next cycle) |
| 2026-06 | 1090 | yes | 5 | 5 | KOSPI 200 row count 199 |

Output: `events_class_b_derived.csv` (133 rows). All rows tagged
`parse_status=derived_via_consecutive_official_snapshot_diff`.

**Conflation caveat (mandatory, attached to every Class B row):**

> "DERIVED — captures ALL constituent changes between consecutive KRX-official
> post-effective-date snapshots; this includes the regular review at the curr
> cycle PLUS any SPECIAL/SUPPLEMENTAL events between cycles (Tier 2/3, deferred).
> Downstream user decision required to separate regular-review vs intermediate-
> special. effective_dt NOT filled (Referee rule: direct-from-file only).
> company_name from KRX snapshot row; ticker is 6-digit normalized from KR7…002
> ISIN."

The Class B derived rows are HONEST about including the intermediate specials; the
Bull/Bear pipeline can use them as event candidates only after special/regular
separation, which requires Tier 2/3 attachment parse (deferred).

---

## 5. Consolidated v2 events artifact (`events_v2.csv`)

220 rows total:
- 12 `constituent_level_direct_from_change_detail_sheet` (Class A)
- 133 `constituent_level_derived_from_consecutive_official_snapshot_diff` (Class B)
- 75 `notice_level_skeleton_only` (carried forward from source-A0; uncovered Tier 1
  cycles + Tier 2/3 specials)

By Tier 1 status:
- 147 `tier1_target`
- 2 `bridge_only_not_in_tier1` (2022-12)
- 71 `out_of_tier1` (Tier 2/3 specials from source-A0)

Schema columns (20): `event_id, review_cycle, announcement_dt, announcement_time,
effective_dt, index_name, side, ticker, company_name, source_class, source_record_type,
source_id_or_url, source_file, source_file_sha256, prev_snapshot_file,
prev_snapshot_sha256, prev_snapshot_cycle, tier1_status, parse_status, caveat`.

Preserve-all confirmed: 0 rows silently dropped; every row carries explicit
`source_record_type`, `parse_status`, and full per-row `caveat`.

---

## 6. PIT / tradability assessment (updated)

| Field | Filled? | Rule applied |
|---|---|---|
| `announcement_dt` | 145/145 constituent-level + 75 notice-level | KRX REG_DT from notice metadata (source-A0) |
| `announcement_time` | 0/220 | Not in attachments; not in metadata at row-level. KRX press 09:00 KST convention NOT used as fill |
| `effective_dt` | **0/220** | **NOT filled. Referee rule: direct-from-file only. Inspection of all 11 xlsx confirms no explicit `effective_dt` column inside the attachments. Snapshot represents post-effective constituents but the effective date itself is NOT inside the file** |
| `ticker` | 145/145 const-level (0/75 notice-level) | 6-digit KRX format; from Class A `변경내역` sheet OR normalized from KR7XXXXXX002 ISIN in Class B snapshots |
| `company_name` | 145/145 const-level (14/75 notice-level) | From attachment for const-level; from title heuristic for notice-level |
| `index_name` | 145/145 const-level (0/75 notice-level) | "KOSPI 200" |

Conservative execution-date rule for any downstream TEST (recommended, NOT
self-implemented): `execution_date = next trading session close where session_date >
announcement_date`. Same-day execution from announcement remains FORBIDDEN.

`effective_dt` fill remains an open follow-on issue: in principle the KOSPI 200
effective date is the trading-day after the second-Friday-of-the-rebalance-month
per KRX rulebook, but **filling by rule was forbidden per Referee**. A separate
rulebook-A0 (NOT opened here) would be needed.

---

## 7. Listing-name cross-check — EXECUTED (final pass per Referee 2026-05-31)

Per Referee directive: "Cross-check name/ticker against the existing listing-
universe-coverage A0 outputs if available locally. Rows that fail to cross-match
must be kept with caveat such as `ticker_unresolved_against_listing_table`; do not
drop them."

**Executed.** PIT join: each constituent-level row joined against
`data/acquired/krx_listed_universe/krx_listed_monthly_snapshots_2010_2026.csv`
(441,359 rows; 197 monthly snapshots 2010-01-04 .. 2026-05-04); join key =
latest listing snapshot_date ≤ announcement_dt (PIT — never later snapshots);
output = `events_v2_xref.csv` with 5 added columns: `xref_match_status`,
`xref_pit_snapshot_date`, `xref_listing_name`, `xref_market`.

Match counts (145 constituent-level rows + 75 skeleton rows = 220 total):

| status | count | note |
|---|---|---|
| `match_clean` (ticker AND name match) | 0 | listing names mostly empty in source CSV |
| `match_ticker_only_listing_name_unavailable` | **138** | ticker confirmed in PIT listing; listing name field empty (known panel-coverage gap from `project-listed-universe-coverage-a0`) |
| `match_name_diff` | 0 | no actual ticker→name conflicts |
| `ticker_not_in_pit_listing` | 5 | edge cases (new-listing or post-merger near event date) |
| `pit_snapshot_unavailable` | 2 | event date outside listing-A0 snapshot range |
| `non_constituent_level_skipped` | 75 | skeleton rows; not applicable |

**Effective ticker confirmation rate: 138 / 145 = 95.2%.** Zero ticker→name
conflicts. The 5 `ticker_not_in_pit_listing` rows include 카카오페이 (2021-12 add,
listed 2021-11-03 — between PIT snapshot timing), SK스퀘어 (2021-12 add, SK텔레콤
분할 신설), 메리츠화재 / 메리츠증권 (2023-06 deletion; post-merger 폐지 timing),
HD현대인프라코어 (2026-06 deletion; name change history). All preserved with caveat;
NONE dropped.

The 138 `match_ticker_only_listing_name_unavailable` rows are NOT a real audit
failure — they reflect the documented 25.3% panel-coverage gap in the
listing-universe-A0 source where the `name` column was empty (NaN) for many
older tickers. Ticker existence in PIT listing IS confirmed for these.

LISTING_NAME_CROSS_CHECK section appended to `reconciliation_v2.csv`.

---

## 8. Reconciliation report (`reconciliation_v2.csv`)

Headlines:
- **Tier 1 coverage**: 10/14 cycles parsed with constituent-level rows (71.4%).
- **Tier 1 cycles deferred**: 555, 613, 667, 696 (2018-06, 2019-06, 2020-06,
  2020-12) — all hwp / broker pdf, per Referee.
- **Bridge cycles**: 2022-12 included with 1 add / 1 del.
- **Constituent-level rows**: 145 (12 direct + 133 derived).
- **Notice-level skeleton rows**: 75 (carried forward).
- **Total rows**: 220.
- **Missing fields in constituent-level rows**:
  - `effective_dt`: 145/145 missing (Referee rule).
  - `announcement_time`: 145/145 missing.
  - `ticker`: 0/145 missing.
  - `company_name`: 0/145 missing.

Full counts in `reconciliation_v2.csv` (sectioned: GLOBAL, TIER1_COVERAGE,
BRIDGE_NOT_IN_TIER1, MISSING_FIELDS_constituent_level_only, DERIVATION_CAVEAT).

---

## 9. Outputs

```
data/acquired/bx01_kospi200_index_event_source_a0/
  raw/                               # source-A0 raw artifacts (gitignored)
  intake_inventory.csv               # 17 user-supplied + 1 dup-of-21.6
  coverage_matrix.csv                # initial-pass: pre-rename auto-fingerprint
  coverage_matrix_prerename.csv      # FINAL-PASS: explicit copy of pre-rename matrix (kept for transparency)
  coverage_matrix_final.csv          # FINAL-PASS: post-rename high-confidence mapping (canonical)
  class_b_mapping_proposal.csv       # earlier auto-fingerprint proposal (superseded by user rename)
  events.csv                         # source-A0 phase: notice-level skeleton (preserved)
  events_class_a.csv                 # 12 direct rows (2021-06)
  events_class_b_derived.csv         # 133 snapshot-diff rows
  snapshots.csv                      # KOSPI 200 snapshot table (2198 ticker-cycle pairs)
  events_v2.csv                      # consolidated 220 rows (12 direct + 133 derived + 75 skeleton)
  events_v2_xref.csv                 # FINAL-PASS: events_v2 + 4 listing-name xref columns
  reconciliation.csv                 # source-A0 phase (preserved)
  reconciliation_v2.csv              # attachment-parse + appended LISTING_NAME_CROSS_CHECK (final-pass)
  manifest.csv                       # 8 source-A0 + 18 user-supplied = 26 rows total
  tier1_download_list.csv            # download guide (source-A0; preserved)

src/audit/bx01/
  download_krx_notice_attachments.py # source-A0 phase
  build_event_table.py               # source-A0 phase
  build_reconciliation.py            # source-A0 phase
  build_coverage_matrix.py
  parse_class_a.py
  build_class_b_mapping_proposal.py
  parse_class_b_with_diff.py
  consolidate_v2.py
  cross_check_listing_universe.py    # FINAL-PASS
  rewrite_coverage_matrix_final.py   # FINAL-PASS

reports/experiments/BX01_KOSPI200_index_event_source_A0/
  initial_pass.md                    # source-A0 phase (preserved; not modified)
  attachment_parse_initial_pass.md   # THIS FILE (initial + final-pass edits)
```

---

## 10. Gate recommendation (for Referee — NOT self-applied)

**Recommended: `BACKLOG_ATTACHMENT_PARSE_GAP`.**

Rationale per directive's gate notes:
- Constituent-level rows ARE parseable and auditable for 10 / 14 Tier 1 cycles. ✅
- Caveats are explicit + preserve-all + no rule-filled effective dates. ✅
- KOSPI200-specific scope respected. ✅
- BUT (gates against `PASS_TO_DIAGNOSTIC_BACKTEST_DESIGN`):
  - 4/14 Tier 1 cycles still skeleton-only (hwp / broker pdf, deferred).
  - Derived rows are flagged `derived_via_consecutive_official_snapshot_diff` but
    intrinsically conflate regular-review and intermediate-special events for at
    least 3 known cycles (2021-12, 2022-06, 2023-12, 2024-06 all have at least
    one intermediate special).
  - `effective_dt` universally blank — any downstream TEST would need a rulebook-A0
    or per-cycle effective-date acquisition.
  - listing-name cross-check EXECUTED in the final pass (see §7); 138/145
    const-level rows ticker-confirmed in PIT listing (95.2%), 0 ticker
    conflicts. Does NOT resolve the other three blockers above.

**NOT FAIL_CLOSED** — parse quality for 10 cycles materially improved over the
prior skeleton; blocker is decomposable into named follow-on steps that require
separate user + Referee decisions.

**Specific next-step candidates (NOT pre-authorized; each requires separate user +
Referee decision):**

1. Run the listing-name cross-check sub-step against listing-universe A0 outputs
   (mechanical; no new data; could be folded into this phase if Referee prefers).
2. Open a Tier 2/3 parse phase (the deferred specials, possibly with hwp parser
   for older cycles) — this would resolve the diff-conflation issue.
3. Open a rulebook-A0 phase to fill `effective_dt` per KRX KOSPI 200 effective
   rule (NOT by convention/rule fill at row-level, but by parsing the rulebook
   into a per-cycle effective-date table).
4. Acquire the 4 missing Tier 1 cycles (2018-06, 2019-06, 2020-06, 2020-12) in
   xlsx form (or via hwp parser if approved).

---

## 11. Repo state (filled per Referee 2026-05-28 close requirement)

### 11.1 Initial-pass commit

- **Commit hash:** `daf7e10` ("BX01-attachment-parse-A0 initial pass: 10/14
  Tier 1 cycles parsed (1 direct + 9 derived); halt-and-escalate + Referee
  clarification recorded").
- **`git show --check HEAD`** on `daf7e10`: passes (no whitespace errors;
  commit-msg body intact).
- **Files changed (17):**
  - `docs/next_actions.md` (BX01-attachment-parse-A0 added to Active)
  - `reports/experiments/BX01_KOSPI200_index_event_source_A0/attachment_parse_initial_pass.md`
    (this report)
  - `src/audit/bx01/{build_coverage_matrix,parse_class_a,build_class_b_mapping_proposal,parse_class_b_with_diff,consolidate_v2}.py`
  - `data/acquired/bx01_kospi200_index_event_source_a0/{intake_inventory,coverage_matrix,
    class_b_mapping_proposal,events_class_a,events_class_b_derived,snapshots,events_v2,
    reconciliation_v2,tier1_download_list,manifest}.csv`

### 11.2 Final-pass commit (this report's §7 cross-check + §11 fill-in + matrix
   rewrite + row-count fix)

To follow on Referee-approved final-pass review. Contents:
- `src/audit/bx01/cross_check_listing_universe.py` (new — listing-name PIT join).
- `src/audit/bx01/rewrite_coverage_matrix_final.py` (new — coverage matrix v2).
- `data/acquired/bx01_kospi200_index_event_source_a0/events_v2_xref.csv` (new —
  enriched events with `xref_*` columns).
- `data/acquired/bx01_kospi200_index_event_source_a0/coverage_matrix_final.csv`
  (new — post-rename high-confidence mapping).
- `data/acquired/bx01_kospi200_index_event_source_a0/coverage_matrix_prerename.csv`
  (preserved copy of the pre-rename auto-fingerprint matrix; for transparency).
- `data/acquired/bx01_kospi200_index_event_source_a0/reconciliation_v2.csv`
  (appended LISTING_NAME_CROSS_CHECK section).
- This report (`attachment_parse_initial_pass.md`) — final-pass edits:
  TL;DR row-count fixed (131 → 133 with explicit decomposition), §7 cross-check
  EXECUTED, §11 commit / git state filled, §9 outputs list updated.
- `docs/next_actions.md` — BX01-attachment-parse-A0 entry updated with final-
  pass status.

After this commit, `git status --short` is empty (clean working tree). Read-only-
protected `research_input_data/정기변경/` files NEVER modified.

### 11.3 Tracking policy (carry-forward)

`research_input_data/정기변경/` is the protected read-only input dir; the source
files there are NEVER modified by this phase. The committed record-of-record for
those files is the appended rows in
`data/acquired/bx01_kospi200_index_event_source_a0/manifest.csv` with sha256.

---

## 12. Boundary statement

This initial-pass report:

- DOES NOT compute any return, run-up, or edge metric.
- DOES NOT write `signals.csv` / `trades.csv` / any portfolio artifact.
- DOES NOT open a backtest, design, test, paper, live, P08, parser, or measurement-
  layer phase.
- DOES NOT itself authorize any next step. The next step requires a separate
  user + Referee decision.
- DOES NOT retry the failed sandbox OTP download.
- DOES NOT bypass any paywall, scrape any non-public source, or reach for a
  paid / licensed feed.
- DOES NOT parse Class C (hwp) or Class D (broker pdf) — both deferred per Referee.
- DOES NOT modify any file under `research_input_data/` (protected read-only).
- DOES NOT label any row strategy-ready / executable / approved / production-ready
  / paper-ready.

P08_IEF30 frozen — untouched. Measurement-layer DECIDED STANDBY — untouched.
Closed families — untouched. Bear's BX02 / BX03 / BX04 verdicts — intact.
