# BX01-KOSPI200-MISSING-TIER1-XLSX-ACQUIRE-A0 — Initial Pass Report

**Phase pre-reg + addendum:** carry-forward from prior BX01 phases +
this report.
**Initial-pass date:** 2026-05-31
**Authored by:** Executor (Claude Code, autonomous mode per user authorization
2026-05-31 + Referee `ask_0010.md` directive)
**For:** Referee gate verdict — NOT self-applied.

---

## TL;DR

Attempted to acquire 4 missing Tier 1 KOSPI200 regular-review xlsx attachments
(bbsSeq 555/613/667/696; cycles 2018-06/2019-06/2020-06/2020-12) under
user-authorized Executor-side public network access.

**Outcome: 0/4 acquired** via public network. All probed paths blocked,
exactly as the prior BX01-source-A0 phase documented. Per Referee directive,
a small documented probe of the OTP path is acceptable; one probe (bbsSeq=555)
confirmed the same 0-byte response → route stopped + recorded.

**Recommended gate verdict: `BACKLOG_MISSING_TIER1_STRUCTURED_SOURCE_GAP`**
(Referee's own expected wording for this case).

---

## 1. Probes executed (all per directive's "small documented probe")

| Attempt class | URL/call template | Observed result | Blocker class |
|---|---|---|---|
| OTP 2-step | data.krx.co.kr `requestUrlFileUrl.cmd` → `file.krx.co.kr/download.jspx` | HTTP 200 + `Content-Length: 0` (empty body) on step 2 | `BLOCKED_OTP_SANDBOX_EGRESS_ANTI_BOT_SAME_AS_BX01_SOURCE_A0` |
| Direct static `data.krx.co.kr/hpbbs/...` | per 4 save_file_nm | HTTP 404 | `STATIC_PATH_NOT_AVAILABLE` |
| Direct static `kind.krx.co.kr/...` | per 4 save_file_nm | HTTP 405 Method Not Allowed | `STATIC_PATH_405` |
| Direct static `open.krx.co.kr/...` | per 4 save_file_nm | HTTP 404 | `STATIC_PATH_NOT_AVAILABLE` |
| Direct static `global.krx.co.kr/...` | per 4 save_file_nm | HTTP 404 | `STATIC_PATH_NOT_AVAILABLE` |
| Wayback Machine | `archive.org/wayback/available?url=<detail_page>` | `archived_snapshots: {}` | `NO_WAYBACK_COVERAGE` |
| FinanceDataReader | `fdr.SnapDataReader('KRX/INDEX/STOCK/1028')` | "Expecting value: line 1 column 1 (char 0)" — empty JSON | `BLOCKED_SAME_OTP_PATH_VIA_LIBRARY` |
| Wikipedia ko | `ko.wikipedia.org/wiki/KOSPI_200` (fetched 135870 bytes) | no 정기변경 history section (grep returned -1) | `NO_PUBLIC_HISTORY_TABLE` |
| namuwiki | `namu.wiki/w/KOSPI200` (WebFetch) | HTTP 403 Forbidden | `NO_PUBLIC_HISTORY_TABLE_AUTH_REQUIRED` |
| Korean news search | WebSearch broker/news mirrors for 2018-06/2019-06/2020-06/2020-12 specific results | recent (2023+) articles only; no structured add/del tables for target cycles | `NO_STRUCTURED_NEWS_MIRROR` |

All attempts logged in
`data/acquired/bx01_kospi200_missing_tier1_xlsx_acquire_a0/attempt_log.csv`
(40 attempt rows = 4 cycles × 10 attempt classes — 7 KRX-direct/library probes
+ 3 supplementary checks: Wikipedia ko / namuwiki / Korean news search). Per
Referee directive, the OTP path was probed once (bbsSeq=555) → identical
0-byte result as prior BX01-source-A0 → route stopped + recorded. No
aggressive retry.

Note on the 4 raw detail-page HTMLs (each ~453 KB) committed in `raw/`:
these are the KRX detail-page TEMPLATE returned for each bbsSeq — the
actual notice body + attachment list are loaded via JS AJAX after page
load, so the HTML contains only KRX boilerplate / template chrome and NOT
the target structured xlsx content. They are committed as endpoint-discovery
evidence (provenance trail for the OTP probe + static-path probes), NOT as
usable content.

---

## 2. User-supplied files for these 4 cycles — DEFERRED per directive

User already supplied attachments for these 4 cycles in
`research_input_data/정기변경/` during the BX01-attachment-parse-A0 phase:

| bbsSeq | cycle | user file | class | this-phase status |
|---|---|---|---|---|
| 555 | 2018-06 | `18.6.hwp` | C — KRX hwp press release | DEFERRED per ask_0010 "No parsing HWP in this phase" |
| 613 | 2019-06 | `19.6.hwp` | C — KRX hwp press release | DEFERRED per ask_0010 |
| 667 | 2020-06 | `20.6.pdf` | D — secondary broker PDF | DEFERRED per ask_0010 "No broker PDF constituent parsing in this phase" |
| 696 | 2020-12 | `20.12.pdf` | D — secondary broker PDF | DEFERRED per ask_0010 |

Inventoried (sha256 + path), not parsed.

---

## 3. Outputs

```
data/acquired/bx01_kospi200_missing_tier1_xlsx_acquire_a0/
  raw/
    detail_bbsSeq555.html     KRX detail page (JS-only body; endpoint discovery)
    detail_bbsSeq613.html     same
    detail_bbsSeq667.html     same
    detail_bbsSeq696.html     same
  attempt_log/
    step1_555.json            OTP step 1 response (valid OTP token issued)
    step2_555.bin             OTP step 2 result (0 bytes)
  manifest.csv                6 rows with full provenance schema
                              (10 cols: filename / local_path / bytes / sha256 /
                              source_url / final_url / retrieved_at_utc /
                              source_class / license_note / parse_status)
  attempt_log.csv             40 rows (4 cycles × 10 attempt classes:
                              7 KRX-direct/library probes +
                              3 supplementary checks)
  coverage_matrix.csv         4 rows; all `krx_xlsx_acquired=NO`
reports/experiments/BX01_KOSPI200_index_event_source_A0/
  missing_tier1_xlsx_acquire_initial_pass.md  THIS FILE
```

No `events_v4.csv` or constituent rows produced (no structured source acquired).
events_v3.csv (from rulebook-A0 phase) remains the authoritative event artifact.

---

## 4. Reconciliation: change to BX01 state

| State | Before this phase | After this phase |
|---|---|---|
| 4 missing Tier 1 cycles | skeleton-only | skeleton-only (unchanged) |
| events_v3.csv row count | 220 | 220 (unchanged) |
| effective_dt_rulebook_derived filled rows | 133 | 133 (unchanged) |
| Residual blockers | 6 | 6 (unchanged) |
| New evidence | n/a | comprehensive documented impossibility of acquisition from this sandbox via known public paths |

---

## 5. Gate recommendation (for Referee — NOT self-applied)

**Recommended: `BACKLOG_MISSING_TIER1_STRUCTURED_SOURCE_GAP`** (Referee's
expected wording from ask_0010 gate expectations).

Rationale:
- Per Referee gate expectations: "If no structured source is acquired, likely
  gate is `BACKLOG_MISSING_TIER1_STRUCTURED_SOURCE_GAP`."
- No bypass / no scraping / no paid feed / no OTP retry beyond single probe.
- All public paths exhausted within the directive's allowed scope.
- Existing user-supplied hwp/pdf for these 4 cycles preserved as inventory-only
  per directive ("No parsing HWP", "No broker PDF constituent parsing").

NOT FAIL_CLOSED — the acquisition path is gated environmentally (sandbox ↔
KRX anti-bot), not source-legal. The 4 missing cycles remain accessible to
the user via browser (as the user did for the 17 prior files in
attachment-parse-A0).

NOT a backtest gate — directive explicitly carries forward the no-backtest
hard lock.

---

## 6. Next-step candidates (NOT pre-authorized; each requires separate
Referee directive after gate sign-off)

Per directive autonomous-mode sequencing note: "If this phase closes cleanly,
the natural next candidate is C, Tier 2/3 parse." That direction is preserved.

Other candidates that this phase made more salient:
- User-supply pattern for 2018-2020 xlsx (same approach as
  BX01-attachment-parse-A0 phase) — user could download the 4 cycles via
  browser and place in `research_input_data/정기변경/`; new phase would be
  the parse-only continuation.
- HWP parser phase (option D from rulebook-A0 close) — would resolve 2018-06
  and 2019-06 using the user-supplied hwp files. DART body-parser standby
  lock-adjacent — needs separate user + Referee decision.
- Broker PDF parsing phase — would resolve 2020-06 and 2020-12 using the
  user-supplied PDFs. Different source authority class — needs separate
  user + Referee decision.

NONE of these are opened by this report.

---

## 7. Repo state

- Initial-pass commit (this phase): to be filled at commit time below.
- Working tree before commit: clean except for new artifacts.
- `research_input_data/` files NEVER modified.
- No push pending this phase (per directive: no push without user
  authorization).

---

## 8. Boundary statement

This phase:
- Did NOT bypass any paywall / login / OTP / anti-bot control.
- Did NOT modify any file under `research_input_data/`.
- Did NOT parse any hwp or broker PDF (deferred per directive).
- Did NOT open Tier 2/3 / Bull-Bear / P08 / closed-family / parser-measurement-layer.
- Did NOT compute any return / run-up / edge / strategy / portfolio.
- Did NOT label any row strategy-ready / executable / approved / production-ready / paper-ready.
- Did NOT self-close. Did NOT move to Closed/Frozen. Did NOT open downstream phase.

Frozen P08_IEF30 — untouched. Measurement-layer DECIDED STANDBY — untouched.
Closed families — untouched. Bear's BX02 / BX03 / BX04 verdicts — intact.
