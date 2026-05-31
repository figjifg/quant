# BX01-KOSPI200-SPECIALS-TITLE-ENRICHMENT-A0 — Close Note

**Date:** 2026-05-31
**Channel:** Referee close-housekeeping directive `ask_claude_09.md`
**Authored by:** Executor (Claude Code) for the record.

---

## Final status string (exact, per Referee directive)

`CLOSED AS BACKLOG_TITLE_ENRICHMENT_PARTIAL_SECONDARY_LINKS / 6 OF 6 SCOPED SPECIAL ADDITIONS TITLE-LINKED AS SECONDARY-TRIANGULATED CANDIDATES / ADDITION-SIDE CLASS B CONFLATION PARTIALLY SEPARATED FOR 2021-12 2022-06 2024-06 / DELETIONS-REPLACEMENTS REMAIN UNRESOLVED / EVENTS_V3 UNCHANGED / NO PRIMARY PARSE OR BACKTEST OPENED`

---

## Accepted commit

- Initial-pass commit: `065848e5a18bf288019c00190f9ebc74b6dd8629`
  (subject: "BX01-specials-title-enrichment-A0 initial pass: 6/6 title-linked
  at high_secondary_triangulated; addition-side conflation partially separated
  for 3 Class B cycles; deletions remain unresolved")
- Close-housekeeping commit: see commit log entry for this close pass
  (Expected scope: `docs/next_actions.md` +
  `reports/experiments/BX01_KOSPI200_index_event_source_A0/specials_title_enrichment_close_note.md`).

---

## Scope accepted

- KOSPI 200 main index only.
- Six scoped special-inclusion notices only:
  - bbsSeq 758, 759, 773, 789, 907, 921.
- Affected Class B cycles:
  - 2021-12
  - 2022-06
  - 2024-06
- bbsSeq 1020 remains out-of-scope ESG sub-index caveat only.

---

## Artifact state accepted (paths + row counts)

`data/acquired/bx01_kospi200_specials_title_enrichment_a0/`:

| File | Rows (data only) | Cols |
|---|---:|---:|
| `title_enrichment_targets.csv` | 7 (6 scoped + 1 ESG sub-index caveat) | 6 |
| `title_name_extractions.csv` | 6 | 5 |
| `listing_name_crosscheck.csv` | 6 | 8 |
| `special_candidate_links.csv` | 6 | 9 |
| `conflation_reconciliation_title_enriched.csv` | 3 | 6 |

`reports/experiments/BX01_KOSPI200_index_event_source_A0/`:

| File | Lines |
|---|---:|
| `specials_title_enrichment_initial_pass.md` | 256 |
| `specials_title_enrichment_close_note.md` | (this file) |

Accepted CSV artifacts are NOT changed by this close pass. `events_v3.csv` is
NOT modified. No `events_v4.csv` produced.

---

## Candidate-link state accepted (6 of 6, secondary-triangulated only)

| bbsSeq | Ticker | Listing name | Affected Class B cycle | events_v3.csv matching event_id |
|---:|---:|---|---|---|
| 758 | 323410 | 카카오뱅크 | 2021-12 | `BX01-DIFF-774-0006` |
| 759 | 259960 | 크래프톤 | 2021-12 | `BX01-DIFF-774-0005` |
| 773 | 377300 | 카카오페이 | 2021-12 | `BX01-DIFF-774-0009` |
| 789 | 373220 | LG에너지솔루션 | 2022-06 | `BX01-DIFF-799-0026` |
| 907 | 450080 | 에코프로머티 | 2024-06 | `BX01-DIFF-939-0070` |
| 921 | 022100 | 포스코DX | 2024-06 | `BX01-DIFF-939-0067` |

Every link is accepted only as `addition_candidate_title_derived` with
`high_secondary_triangulated` confidence. No link is primary, authoritative,
validated, approved, executable, strategy-ready, production-ready, or
paper-ready.

---

## Reconciliation state accepted (per affected Class B cycle)

| Class B cycle | Addition-side unresolved before | Title-linked candidates | Remaining unresolved (addition side) | Reconciliation status |
|---|---:|---:|---:|---|
| 2021-12 | 3 | 3 | 0 | ALL_ADDITIONS_LINKED__deletions_replacements_may_remain_unresolved |
| 2022-06 | 1 | 1 | 0 | ALL_ADDITIONS_LINKED__deletions_replacements_may_remain_unresolved |
| 2024-06 | 2 | 2 | 0 | ALL_ADDITIONS_LINKED__deletions_replacements_may_remain_unresolved |

Deletion / replacement side remains UNRESOLVED for all three cycles.
Material secondary progress on the addition side; not a full event-table
recovery; not a backtest/design PASS.

---

## bbsSeq 1020 caveat (preserved)

bbsSeq 1020 (2025-06-04, "코스피 200 ESG 지수 수시변경 안내") is a KOSPI 200
**ESG sub-index** notice and **NOT** KOSPI 200 main-index evidence. It is
carried in `title_enrichment_targets.csv` only as
`scope_flag=out_of_scope_subindex_ESG_caveat_only` and contributes nothing
to the candidate-link or reconciliation tables.

---

## Unresolved deletion / replacement boundary (preserved)

Title alone cannot identify which constituent left each affected Class B
cycle or at which event date the departure occurred. Snapshot diffs show a
ticker disappeared between consecutive official snapshots, but whether that
disappearance happened at the regular review or at an intermediate
special/supplemental event cannot be inferred from the special-notice title
text. Resolving the deletion / replacement side requires a separate future
user + Referee decision, likely involving a primary-source parse path such
as HWP, broker PDF, or user-supplied attachment review. This close opens no
such path.

---

## Hard locks preserved (verbatim)

- Title-derived evidence is **secondary and triangulated only**.
- Title-derived evidence may help explain why Class B regular-review windows
  were conflated.
- Title-derived evidence must NOT be used as a primary constituent parse.
- Title-derived evidence must NOT rewrite `events_v3.csv` into an
  authoritative recovered table.
- Title-derived evidence does NOT authorize any downstream modeling or
  execution work.
- No downstream strategy, backtest, P08, production, paper-live, execution,
  portfolio, signal/trade, or event-log authority is opened by this close
  (preserve D).
- No primary parse, authoritative, validated, approved, executable,
  strategy-ready, production-ready, or paper-ready claim attaches to any
  row in this phase's artifacts.
- No external network access, no API call, no download, no source recovery.
- No HWP parser, broker PDF parser, OCR, binary document parser, or new
  parser infrastructure work.
- No rulebook re-acquisition, no calendar extension, no 2026-06
  effective-date fill, no convention/news/memory/rebalance fill of
  canonical `effective_dt`.
- No Bull / Bear workflow, no P08 ops, no measurement-layer reopening, no
  DART/parser reopening, no closed-family reopening, no BX02 / BX03 / BX04
  expansion, no MSCI / FTSE / KOSDAQ 150 expansion.
- `research_input_data/` files NOT modified by this phase.
- `data/raw/` NOT modified by this phase.
- No push performed.
- This close does NOT self-promote, does NOT open the next phase, and does
  NOT carry approval authority for any work beyond the accepted state above.

---

## No next phase opened

No follow-on phase is opened by this close. Resuming any of the
deletion/replacement-side recovery candidates (HWP parser phase, broker PDF
parse phase, user-supplied attachment review for the 6 specials, primary
KRX re-acquisition, or measurement-layer reopening) requires a separate
explicit user + Referee decision.

Frozen P08_IEF30 remains untouched. Measurement-layer DECIDED STANDBY
(2026-05-26 user-accepted) remains untouched. Closed families remain
untouched. Bear's BX02 / BX03 / BX04 verdicts remain intact.
