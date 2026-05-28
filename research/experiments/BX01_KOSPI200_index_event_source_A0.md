# BX01-KOSPI200-INDEX-EVENT-SOURCE-A0 — Pre-registration

**Phase ID:** `BX01-KOSPI200-INDEX-EVENT-SOURCE-A0`
**Opened:** 2026-05-28
**Decision channel:** user → Codex (Referee) direct authorization quote `"bx01로 진행하자.
외부 작업은 익스큐터한테 부탁해서 진행하면 될거야. 외부 네트워크 접근도 허용할께."` +
parallel claude-session confirmation `"BX01 source acquisition phase 열기 (KRX index notices)"`
+ `"내가 요청했어"`. Phase-opening directive carried verbatim from
`.codex-claude-relay/codex_outbox/ask_0006.md` (Referee-authored, user-authorized).
**Role:** Executor (Claude Code) runs the source acquisition + event-table A0 validation;
Referee gates; user decides next step.

---

## Status (this file is the source of truth for the phase scope)

This phase is **DIAGNOSTIC-ONLY**. It does **not** open or pre-authorize any of:

- backtest / return / run-up / edge calculation,
- `signals.csv` / `trades.csv` / portfolio / P08 / production / paper / live / execution /
  allocation work,
- parser / measurement-layer reopening,
- DART body parser work,
- MSCI / FTSE / KOSDAQ150 scope expansion,
- closed-family reopening,
- paywall bypass / credential use / prohibited scraping,
- same-day execution assumption from announcement date,
- any row labeled strategy-ready / executable / approved / production-ready / paper-ready.

**Frozen P08_IEF30 untouched. Measurement-layer DECIDED STANDBY untouched.**

---

## Hypothesis (handed forward from the Bull/Bear round; not tested here)

Bull's BX01 card claimed: stocks newly added to KOSPI200 at a semi-annual review experience
a measurable long-only run-up between announcement and effective date, driven by rule-bound
buying from KOSPI200-tracking passive ETFs and KOSPI200-benchmarked index funds; after 33
bps round-trip cost and a date×sector×size matched control, the run-up is distinguishable
from a matched non-inclusion control.

Bear's verdict on BX01: **BACKLOG** — mechanism distinct and falsifiable, but not runnable
without source acquisition + event-table A0 validation + frozen near-miss controls; the
effect may also be pre-announcement leakage / momentum / size beta rather than forced
flow.

**This phase tests neither the hypothesis nor any return.** It only asks: **can a
point-in-time, auditable KOSPI200 review event table be built from public,
license-respecting sources, with the structure that a later TEST phase would need?**

---

## Failure mode being tested (in this A0 phase)

Whether the event table can be reconstructed PIT-safely. Specifically:

1. Are official KOSPI200 review announcements available with **publication dates** (not
   just effective dates)?
2. Are announcement and effective dates **separable** for every event?
3. Does the event universe rely on **later constituent history** (e.g., today's
   constituents back-reconstructed) — disallowed — or on contemporaneous notices —
   required?
4. Is the ticker/code mapping **auditable** across the period (handle splits, mergers,
   delistings, code changes)?
5. Are **special/supplemental** actions (intra-period replacements due to delisting,
   M&A, suspension) preserved as a distinct event type?
6. Can a **near-miss control set** (candidates evaluated but not included) be reconstructed
   from contemporaneous data WITHOUT using post-announcement constituent knowledge?

If any of these cannot be met, the gate verdict will be `BACKLOG_SOURCE_GAP` or
`FAIL_CLOSED`. The decision is made by Referee on review; this phase does not self-close.

---

## Source priority

1. **KRX official press / notice** (krx.co.kr, open.krx.co.kr): primary, license-respecting,
   public — official record of semi-annual review announcement + effective dates +
   constituent changes.
2. **KRX Index / index.krx.co.kr**: index-specific notices for KOSPI200 schedule and
   constituent changes.
3. **Public secondary sources** (Wikipedia, KOFIA, news archives) for **reconciliation
   only** — counts and sample verification, not the event source of truth.

**Excluded:** any paywalled service; any source requiring credentialed scraping. Use of
secondary sources is recorded with explicit provenance and never replaces a primary KRX
notice.

---

## Target coverage

- **Years:** 2010 – 2026 (subject to source availability).
- **Events of interest:** KOSPI200 *regular* semi-annual reviews + *special/supplemental*
  intra-period actions (replacements due to delisting, M&A, suspension).
- **Out of scope:** KOSDAQ150, MSCI, FTSE, capping / weight rebalances that do not change
  constituents.

---

## Required outputs (carried from `ask_0006.md`)

1. This pre-registration file (scope, sources, constraints, no-backtest status).
2. **Raw artifact inventory** — source URL/path, retrieval timestamp, file path, sha256,
   file type, license/access note. Stored under
   `data/acquired/bx01_kospi200_index_event_source_a0/`.
3. **Parsed event table** with these 11 fields:
   `event_id, review_cycle, announcement_dt, announcement_time, effective_dt, side,
   ticker, company_name, event_type, source_id_or_url, parse_status, caveat`.
   Missing / ambiguous rows preserved with caveats, never silently dropped.
4. **PIT / tradability assessment:** publication timing, conservative execution-date rule
   if timing is unknown, effective-date semantics, delisted/code-changed name retention.
5. **Near-miss feasibility assessment:** can a near-miss control set be built using only
   pre-announcement data with a frozen methodology? If not, recommend replacement
   controls (e.g., calendar-matched non-included same-sector/size).
6. **Reconciliation report:** counts by year/review, missing/ambiguous fields, independent-
   source sample reconciliation if available, unresolved source gaps.
7. **Gate recommendation** for Referee (not self-applied):
   - `PASS_TO_DIAGNOSTIC_BACKTEST_DESIGN` if the table is sufficiently PIT-safe + auditable.
   - `BACKLOG_SOURCE_GAP` if sources are incomplete or ambiguous.
   - `FAIL_CLOSED` if reconstruction without hindsight or with license/source issues is
     infeasible.
8. `git status`, `git show --check HEAD`, commit/hash summary in the initial-pass report.

---

## Outputs directory layout

```
data/acquired/bx01_kospi200_index_event_source_a0/
  raw/                       # immutable source artifacts
  manifest.csv               # one row per artifact: url, retrieved_at, path, sha256, type, license_note
  events.csv                 # 11-field parsed event table
  reconciliation.csv         # per-source/per-year counts + missing/ambiguous
reports/experiments/BX01_KOSPI200_index_event_source_A0/
  initial_pass.md            # PIT, near-miss, reconciliation, gate recommendation
```

---

## Gate (for Referee review only — not self-applied)

PASS requires **all** of:

- event source is public/license-respecting and provenance is recorded,
- announcement and effective dates are separated for every event,
- event universe does not rely on later constituent history,
- ticker/code mapping is auditable,
- missing and special-action rows are preserved with caveats, not silently dropped,
- no returns or strategy claims were made in this phase.

FAIL / BACKLOG is acceptable and must be preserved with reasons. **The Executor does not
self-close; Referee assigns the gate verdict on review.**

---

## Reporting

After the initial pass:

1. Bridge `reports/experiments/BX01_KOSPI200_index_event_source_A0/initial_pass.md` to
   Codex (Referee) via `claude_to_codex_bridge.py` with a request for gate verdict.
2. Do **not** open a downstream design / backtest / test phase. Any next step requires a
   separate user + Referee decision.
