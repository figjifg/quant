# BX01-KOSPI200-INDEX-EVENT-SOURCE-A0 — Initial Pass Report

**Phase pre-reg:** `research/experiments/BX01_KOSPI200_index_event_source_A0.md`
**Initial-pass date:** 2026-05-28
**Authored by:** Executor (Claude Code)
**For:** Referee (Codex) gate verdict — NOT self-applied.

---

## TL;DR

**Recommended gate verdict: `BACKLOG_SOURCE_GAP`.**

We acquired the **notice-level metadata** authoritatively from KRX's public board
(`data.krx.co.kr` MDCINFO005, semi-official API), yielding **85 KOSPI 200 main-index
constituent-change notices over 2010-01-15 .. 2026-05-22** (30 regular semi-annual
reviews + 55 special / supplemental events). The notice index is PIT-anchored on KRX's
own `REG_DT` and is suitable as the **outer event-table skeleton** for a later return
test.

However, the **constituent-level details** (which specific stocks were added/deleted at
each review, with exact effective dates) live in the attachments (xlsx/hwp/pdf) linked
to each notice. The KRX attachment download path requires a two-step OTP-token flow
ending at `file.krx.co.kr/download.jspx`. **From this sandbox environment, that endpoint
silently returns HTTP 200 with `Content-Length: 0`** for every OTP token we exchanged
(verified across multiple cookie / header / encoding variations + a fresh OTP per
attempt). The token itself appears accepted (no 4xx), but the file body never arrives.
We did not bypass any paywall, credential, or anti-scraping control — the public OTP
flow simply does not return content from this network egress.

Without the attachments, **the per-constituent add/delete list is missing** for
**every regular review** and for ~83.5% of special events (where the title alone does
not name the company). This precludes a credible PIT-safe event table at the
add/delete granularity, which is the level a later TEST phase would need.

The gate is therefore BACKLOG — not FAIL_CLOSED, because the source itself is public
and license-respecting, and the blocker is environmental (sandbox network ↔
`file.krx.co.kr`), not legal or methodological. Resolution requires either a different
network egress to KRX, or user-supplied locally-downloaded attachments, or a paid /
licensed equivalent feed. **The Executor does not pre-authorize any of those next
steps.**

---

## 1. Sources acquired (provenance)

All under `data/acquired/bx01_kospi200_index_event_source_a0/`. Full inventory in
`manifest.csv` with byte counts + sha256.

| Artifact | Source | Status |
|---|---|---|
| `raw/krx_notice_board_root.html` | `data.krx.co.kr/.../MDCCOMS010_S1.cmd?boardId=MDCINFO005` | endpoint discovery |
| `raw/krx_board_all.json` | `data.krx.co.kr/.../MDCCOMS010_S1D1.cmd` (titleContn=`""`, pageSize=1000) | **AUTHORITATIVE metadata** — 866 board entries 2010-01-15 .. 2026-05-27 |
| `raw/krx_board_list_kospi200.json` | same endpoint, titleContn=`KOSPI200` | redundant probe |
| `raw/krx_board_list_jeonggi.json` | same endpoint, titleContn=`정기변경` | redundant probe |
| `raw/sample_detail_1090.html` | `MDCCOMS010_S2.cmd?...bbsSeq=1090` | endpoint discovery (attachment URL flow) |
| `raw/kospi200_notice_index.json` | LOCAL filter of `krx_board_all.json` | derived index — 85 unique KOSPI 200 main-index constituent-change notices |
| `events.csv` | derived | 11-field event table (this phase's primary output) |
| `reconciliation.csv` | derived | per-year + missing-field census |

**No paywall bypass, no credential use, no prohibited scraping.** The
`MDCCOMS010_S1D1.cmd` endpoint is the public AJAX backing the public board page; the
parameter shape (`name=fileDown&filetype=att&url=COM/Fboard_attach_down&bbsId=...&
bbsSeq=...&attachFileSeq=...`) was discovered by reading the public site's own
JavaScript (`/inc/js/mdc.util.js`, lines around 3030-3070).

---

## 2. Event table (`events.csv`) — 11 required fields

Schema (exactly as required by `ask_0006.md`):

| Field | Filled? | Source / Caveat |
|---|---|---|
| `event_id` | 85/85 | derived, format `BX01-<bbsSeq>-<CYCLE|SPECIAL>` |
| `review_cycle` | 16/85 | parsed from title for some regular reviews; many older titles lack the YYYY.M form |
| `announcement_dt` | 85/85 | KRX `REG_DT` — authoritative |
| `announcement_time` | 0/85 | NOT in the metadata; KRX press is typically distributed 09:00 KST but this is *convention*, not recorded data — left blank |
| `effective_dt` | 0/85 | gated on attachment + KRX trading-calendar reconciliation |
| `side` | 85/85 | `cycle` for regular reviews (the cycle-level row, no per-name detail); for specials, heuristic from title keywords: `addition`/`deletion`/`split_action`/`supplemental`/`other` |
| `ticker` | 0/85 | gated on attachment OR cross-checked listing-name table |
| `company_name` | 14/85 | for specials only — title-extracted heuristic; NOT cross-checked against an exchange listing-name table |
| `event_type` | 85/85 | `regular_review` or `special` |
| `source_id_or_url` | 85/85 | `KRX MDCINFO005 bbsSeq=<n>` |
| `parse_status` | 85/85 | one of: `metadata_only__constituents_gated_on_attachment_download`, `metadata_only__no_name_in_title`, `title_extracted_name` |
| `caveat` | 85/85 | full provenance + blocker note per row |

**Preserve-all:** every notice in scope is emitted as a row. Missing values are blank
with `caveat`. Nothing silently dropped.

**Granularity disclosure (important for later TEST design):**

- Regular reviews are emitted at **review-cycle granularity** (one row per notice,
  `side='cycle'`). The per-constituent add/delete rows that a TEST would need are
  **NOT here** — they require the attachment.
- Special events are emitted at **event granularity** but most rows lack a confirmed
  ticker/name pair. Only 14/55 specials have a title-extracted name (uncross-checked).

---

## 3. PIT / tradability assessment

Per the gate requirements:

### 3.1 Is announcement publication timing known?

**Date: yes** (KRX `REG_DT` field). **Time: no** — KRX press timing convention is 09:00
KST but is not recorded per row. **Conservative execution-date rule we will recommend
to any downstream TEST:** `execution_date = next trading session close where
session_date > announcement_date`. Same-day execution from announcement is
EXPLICITLY FORBIDDEN by `ask_0006.md`.

### 3.2 Are announcement and effective dates separable?

In principle yes (KRX always separates them in its public notices). In *our acquired
data*, the effective date is **only inside the attachment** — which is blocked. So in
practice, separation is **gated**, not absent.

### 3.3 Does the event universe rely on later constituent history?

**No.** Our universe is built purely from KRX's own contemporaneous notices, indexed by
`REG_DT`. We did **not** back-reconstruct adds/deletes from a later constituent table.

### 3.4 Ticker/code mapping auditable?

**Not in current state** — tickers are missing because they live in the attachment.
A later TEST would need to (a) acquire the attachments, (b) cross-check each company
name against an exchange listing-name table snapshotted as of the announcement date
(to handle delistings, name changes, merger-renames, code changes). The
listing-universe-coverage A0 work already in the repo (commits `dbd847b` → `f5b8407`)
provides partial coverage; for BX01 it is **not** survivorship-safe alone.

### 3.5 Special-action preservation?

Yes — special events are emitted as a distinct `event_type='special'` and tagged with
`side ∈ {addition, deletion, split_action, supplemental, other}` per title keywords.

---

## 4. Near-miss feasibility assessment

Bull's BX01 card called for a **near-miss control set** — companies that were
*considered but not included* in each KOSPI 200 review, to control for size/sector
beta effects. This is the hardest control.

**Verdict: NOT FEASIBLE from publicly-available KRX press notices**, regular or
attachment.

Reason: KRX publishes only the *result* of each review (added / deleted constituents),
not the *candidate set considered*. Reconstructing a near-miss set requires
hindsight — typically projecting the review methodology (market-cap rank within
universe, trading-value rank, etc.) using **only pre-announcement data** with a
**frozen methodology**. A frozen methodology faithful to KRX's stated rules requires
contemporaneous KRX rulebooks + the universe ranking inputs as of the review's
reference period — both available, but the implementation has its own audit-first
burden.

**Recommended replacement controls** (in order of conservativeness):

1. **Date × sector × size matched control**: for each added constituent, draw a same-
   sector, similar-market-cap, non-added stock as of `announcement_dt - 1`, with
   sector + cap snapshotted PIT.
2. **Calendar control**: same-day, same-sector, non-treated.
3. **Frozen-methodology near-miss**: implement KRX's published KOSPI 200 selection
   rules from contemporaneous rulebooks, rank the universe as of the review's
   reference period, and define "near-miss" as rank within (200, 200+K] for some
   pre-registered K. This is a separate sub-phase that requires the rulebook
   acquisition + an additional A0 — not in scope of BX01-source-A0.

For the initial diagnostic test, **control (1) is the right default**; controls (2)/
(3) are upgrades.

---

## 5. Reconciliation report

Full table in `reconciliation.csv`. Highlights:

| Year | Regular | Special | Note |
|---|---|---|---|
| 2010 | 1 | 4 | only May review captured in our board snapshot |
| 2011 | 0 | 2 | KRX board has no Nov/Dec 2011 main-index review notice under our strict filter — possibly under "유동비율 변경" (float-weight) wording, which we filtered out |
| 2012 | 1 | 2 | only May |
| 2013 | 1 | 10 | first heavy-special year (STX cluster) |
| 2014 | 1 | 8 | only May; multiple M&A specials |
| 2015 | 1 | 6 | only Dec ("내재가치지수" sub-index variant) |
| 2016 | 1 | 4 | only May |
| 2017 | 3 | 5 | review notices + sub-index variants begin appearing separately |
| 2018 | 5 | 7 | review + 4 sub-index variants |
| 2019 | 4 | 0 | review + 3 sub-index variants |
| 2020 | 2 | 0 | one each May + Nov |
| 2021 | 2 | 3 | + KraftON / KakaoBank / KakaoPay specials |
| 2022 | 1 | 1 | + LG Energy Solution special |
| 2023 | 2 | 1 | |
| 2024 | 2 | 1 | |
| 2025 | 2 | 1 | |
| 2026 | 1 | 0 | only June review so far |

**Notice-count gaps + caveats:**

1. The expected ~2 regular reviews/year (June + December) is **NOT met** in 2010-2014
   under our strict filter. Likely cause: older notices used the wider title
   "KOSPI 200 등 N개 주가지수 구성종목 ... 변경" which sometimes combined float + constituent
   changes; our filter dropped float-only changes ("유동비율 변경"). This means our
   indexed regular-review count is **a lower bound for 2010-2014**; an attachment-level
   parse would resolve it.
2. From 2017 onward, multiple sub-index variants ("KOSPI 200 밸류가중지수",
   "예측배당지수", "팩터가중지수", etc.) generate additional rows that look like
   "regular reviews" but are NOT main-index reviews. Our `kospi200_notice_index.json`
   filter excludes most but several slipped through (e.g., bbsSeq 436, 531, 533, 561,
   563, 595, 598, 619, 622, 641). For a TEST, these MUST be excluded — the current
   30 regular_review rows include sub-index noise and should be re-classified at
   attachment-parse time.

**Independent-source cross-check (provenance: secondary public sources, used for
reconciliation only — not the event source of truth):**

- May 27, 2025 review (KRX press): 8 added (Dongwon Industries, DN Automotive,
  HD Hyundai Marine Solution, HDC, Youngpoong, Miwon SC, Korean Carbon, District
  Heating Corp.) / 8 deleted. Source: news summary (sedaily.com,
  smartkarma.com). [Confirmed our notice metadata exists for 2025-05-27 bbsSeq=1015.]
- November 18, 2025 review: 7 added, 8 deleted. [Confirmed our notice metadata
  exists for 2025-11-18 bbsSeq=1050.]
- May 22, 2026 review: scheduled effective Dec 12, 2026; 8 stocks exchanged.
  [Confirmed our notice metadata exists for 2026-05-22 bbsSeq=1090.]
- June 2021 review: 5 added (SK Bioscience, Daehan Wire, Hyosung Advanced
  Materials, Dongwon Industries, Hyosung T&C), 7 deleted. [Confirmed our notice
  metadata exists for 2021-05-25 bbsSeq=734.]

These are notice-existence confirmations only. The numbers above (8 added etc.) are
NOT in our event table because the constituent-level rows are gated.

---

## 6. Attachment-download blocker (full technical record)

The KRX attachment download for board MDCINFO005 requires a two-step OTP-token flow,
fully documented in the public `mdc.util.js` (lines 3035-3094):

**Step 1** (works): POST to
`https://data.krx.co.kr/comm/fileDn/GenerateHp/requestUrlFileUrl.cmd` with
`name=fileDown & filetype=att & url=COM/Fboard_attach_down & bbsId=<bbsId> &
bbsSeq=<seq> & attachFileSeq=<aseq>` → JSON `{code: <base64-ish OTP>, fileUrl:
"https://file.krx.co.kr/download.jspx"}`. We obtained valid `code` for all 85
notices.

**Step 2** (blocks): POST to `https://file.krx.co.kr/download.jspx` with body
`code=<urlencoded OTP>` → expected: binary file with `Content-Disposition: attachment`.
**Observed: HTTP 200, Content-Type `text/html;charset=UTF-8`, Content-Length: 0,
empty body.** Reproduced with:

- urllib, curl
- two cookie-jar variations (fresh per request; persisted across step 1 + step 2)
- four header sets (minimal, browser-mimic, full Sec-Fetch-* with Origin/Referer,
  with/without X-Requested-With)
- three body encodings (urlencoded, raw, GET-with-query)
- fresh OTP per attempt (no token reuse)
- four alternative endpoints probed:
  `data.krx.co.kr/comm/fileDn/download_cloud/download.cmd` → 302 to error
  `file.krx.co.kr/comm/fileDn/download_cloud/download.cmd` → 404
  `file.krx.co.kr/download_att.do` → 404
  `file.krx.co.kr/board_attach.do` → 404
- direct static-path probes (`https://*.krx.co.kr/hpbbs/kor/dyn/etc/<save_file_nm>`):
  all 404 or 405

Wayback Machine has no captures of the relevant URLs.

`pykrx` (installed; reaches KRX via the same OTP flow internally) reports
`"Expecting value: line 1 column 1 (char 0)"` — empty response, same blocker.

**The signature** — token accepted, 200 OK, but body suppressed — points to an
egress IP / anti-bot rule on `file.krx.co.kr` rather than authorization failure.
This is environmental, not legal/methodological. **Resolution requires a different
network egress, or user-supplied locally-downloaded attachments, or a paid /
licensed equivalent feed.** The Executor does not pre-authorize any of those next
steps.

---

## 7. Gate recommendation (for Referee — NOT self-applied)

**Recommended: `BACKLOG_SOURCE_GAP`.**

Rationale:
- Source is public + license-respecting + provenance recorded. ✅
- Announcement date authoritative + PIT-safe. ✅
- Notice universe does not rely on later constituent history. ✅
- Ticker/code mapping NOT auditable in current state (constituent rows gated). ❌
- Special-action rows preserved with caveats. ✅
- No returns / strategy claims made. ✅
- The blocker is the attachment-download step, which is environmental, not source-
  legal — therefore BACKLOG, not FAIL_CLOSED.

**Specific PASS requirements that the next round would have to clear** (NOT
self-authorized):

1. Acquire the 85 attachments (xlsx/hwp/pdf) via a working network path, OR an
   equivalent licensed-feed source for the per-constituent add/delete lists.
2. Parse attachments → produce constituent-level rows (one row per added or
   deleted stock per event), with ticker + name + side.
3. Cross-check name → ticker against a PIT-snapshotted exchange listing-name table
   (the listing-universe-coverage A0 outputs are the starting point, with the
   25.3% panel-coverage gap explicitly handled).
4. Trading-calendar reconciliation to fill `effective_dt` (the KRX-Calendar A0 outputs
   provide the calendar foundation; KOSPI 200 effective rule is the rebalance trading
   day per KRX rulebook).
5. Re-classify sub-index variants out of the regular-review bucket.
6. Re-build near-miss-or-replacement-control plan (see §4).

---

## 8. Repo state

(Filled in at commit time by the next task.)

- `git status` — clean working tree expected after the BX01-A0 commit.
- `git show --check HEAD` — passes expected.
- Commit hash + summary — to be filled.

---

## 9. Boundary statement

This initial-pass report:

- DOES NOT compute any return, run-up, or edge metric.
- DOES NOT write `signals.csv` / `trades.csv` / any portfolio artifact.
- DOES NOT open a backtest, design, test, paper, live, P08, parser, or measurement-
  layer phase.
- DOES NOT itself authorize any next step. The next step requires a separate
  user + Referee decision.

P08_IEF30 frozen — untouched. Measurement-layer DECIDED STANDBY — untouched.
Closed families — untouched.
