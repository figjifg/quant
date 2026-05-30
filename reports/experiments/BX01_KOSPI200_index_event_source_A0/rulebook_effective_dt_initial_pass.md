# BX01-KOSPI200-RULEBOOK-EFFECTIVE-DT-A0 — Initial Pass Report

**Phase pre-reg + addendum:** `research/experiments/BX01_KOSPI200_index_event_source_A0.md` (carry-forward source-A0 + attachment-parse-A0 pre-reg) + this report (rulebook-effective-dt-A0 addendum).
**Initial-pass date:** 2026-05-31
**Authored by:** Executor (Claude Code)
**For:** Referee (Codex) gate verdict — NOT self-applied.
**Directive:** `.codex-claude-relay/codex_outbox/ask_0009.md` (BX01-KOSPI200-RULEBOOK-EFFECTIVE-DT-A0) + 2026-05-31 Referee halt-review clarification (hybrid (c) framework — secondary KRX-attributed rulebook + derivatives product spec accepted with strict provisional labels).

---

## TL;DR

Two halt-triggers fired during the discovery sub-step:

1. **Primary KRX rulebook access blocked.** The `index.krx.co.kr` 지수산출방법 page is real but the underlying rulebook PDF list is gated behind a JS-rendered OTP-style AJAX form (same OTP pattern that blocked BX01-source-A0 attachment downloads). I have not bypassed it.
2. **KRX calendar coverage cutoff at 2026-05-22.** 2026-06 effective_dt cannot be computed within phase scope.

Referee 2026-05-31 hybrid (c) clarification accepted:
- Mirae Asset Securities-hosted KOSPI200 methodology PDF (2021-11 filename timestamp; KRX publisher attribution; §7.1 semi-annual rule + amendment history pointing to 2019-12-11 cadence change) → **secondary KRX-publisher-attributed rulebook copy** with strict provisional labels.
- Hana Investment Securities-hosted 「장내파생상품 거래설명서」(2020-05-25; KRX-attributed; p8+p15 specifies "결제월의 두 번째 목요일" for KOSPI200 선물 최종거래일) → **secondary broker-hosted KRX-attributed derivatives product spec** with strict provisional labels.
- Local KRX trading calendar (`krx_official_calendar_2010_2026.csv`) → used only for "next trading day after futures last-trade day" lookup. Coverage 2010-01-04 .. 2026-05-22.

Derivation under hybrid (c):
- **9/10 in-calendar Tier 1 cycles** (2021-06 through 2025-12) → effective_dt filled with `confidence=provisional_secondary_rulebook_calendar_confirmed` and full per-row caveats citing the secondary basis classes.
- **2026-06 cycle** → blank with caveat `calendar_coverage_cutoff_2026-05-22__effective_dt_not_computed`; 2026-06-12 KRX press release match recorded only as reconciliation evidence, NOT used as fill basis (per Referee directive).
- **events_v3.csv** = events_v2_xref.csv + 4 added columns (effective_dt_filled / effective_dt_methodology_basis_class / effective_dt_futures_ltd_basis_class / effective_dt_confidence_v3 / effective_dt_caveat_v3). Preserve-all (zero rows dropped; zero prior caveats lost).

**Recommended gate verdict to Referee: `BACKLOG_EFFECTIVE_DT_PARTIAL_SECONDARY_BASIS`** — per Referee's own expected wording. 9 cycles filled under provisional secondary-triangulated basis is a meaningful improvement over the previously 0/220 filled state, but (a) primary KRX access blocked, (b) 2026-06 blank, (c) prior phase blockers intact (4 skeleton Tier 1 cycles + Class B regular/special conflation + Tier 2/3 deferred). NOT `PASS_TO_DIAGNOSTIC_BACKTEST_DESIGN`. NOT `FAIL_CLOSED`.

---

## 1. Discovery + halt-and-escalate sequence

### 1.1 Primary access attempt

- `data.krx.co.kr` and `index.krx.co.kr` methodology pages (지수산출방법) exist and were probed.
- Underlying AJAX list endpoint `/contents/IDX/99/IDX99000001.jspx` returns HTTP 400 Bad Request without the JS-generated `$.otpCode('form', ...)` token. The OTP gating pattern is the same one that blocked BX01-source-A0 attachment downloads from this sandbox.
- No bypass attempted. No paywall touched.

### 1.2 Secondary triangulation

Acquired (public, license-respecting; no scraping):

- `miraeasset_kospi200_methodology.pdf` — Mirae 2016.5 KRX-publisher-attributed methodology. Says **annual** review (June only). Used only as **amendment-history evidence** (NOT as primary basis).
- `miraeasset_kospi200_methodology_v2.pdf` — Mirae 2021-11 KRX-publisher-attributed methodology (14 pages). §7.1 verbatim: *"KOSPI200 지수는 상기 구성종목 선정방법에 따라 매년 2회 정기적으로 구성종목을 변경하며, 정기변경일은 KOSPI200 선물시장 6월, 12월 결제월 최종거래일의 다음 매매거래일입니다."* p3 amendment history: *"'19.12.11 <정기변경 주기 단축> ㅇ연1회(6월) → 연2회(6월, 12월)"*.
- `hana_listed_derivatives_trade_description.pdf` — Hana 2020-05-25 「장내파생상품 거래설명서」. p8 + p15 tabulate: *"코스피200선물 결제월 : 3, 6, 9, 12월; 최종거래일 : 각 결제월의 두 번째 목요일"*. Brokerage-hosted but content reproduces KRX product spec per regulatory mandate.
- `krx_derivatives_rule_amendment_notice.pdf` — next-securities-hosted KRX 「파생상품시장 업무규정 시행세칙 일부개정세칙」 transcript (71 pages). Saved as additional supporting evidence; not used for derivation directly.

All sha256 + URLs + retrieval timestamps in `data/acquired/bx01_kospi200_rulebook_effective_dt_a0/manifest.csv`.

### 1.3 Halt-and-escalate

Two halt+escalate bridges to Referee:

- 2026-05-31 bridge (Q1/Q2/Q3 decisions): "secondary as basis?" + "calendar cutoff?" + "label?". Referee answered (c) hybrid + (i) 9/10 cycles + strict labels including a NEW required derivative source for futures last-trade-day rule.
- 2026-05-31 follow-up bridge: confirmed Hana 거래설명서 + KRX derivatives amendment transcript satisfy the futures-final-trading-day basis under the same hybrid (c) framework + same strict labels.

Bridge files (preserved):
- `.codex-claude-relay/bx01_rulebook_halt_msg.txt` (Q1/Q2/Q3 halt)
- `.codex-claude-relay/bx01_rulebook_halt_extension_msg.txt` (futures LTD follow-up)
- Referee replies in `.codex-claude-relay/codex_reply.md` (overwritten history of bridge sessions)

---

## 2. Derivation method (precisely)

For each in-calendar Tier 1 cycle (year `Y`, month `M ∈ {6, 12}`):

1. `futures_last_trade_day = second_thursday(Y, M)` — from Hana 거래설명서 rule citation.
2. `effective_dt = next_trading_day(futures_last_trade_day, KRX_calendar)` — from Mirae 2021-11 §7.1 + local KRX calendar artifact.
3. `effective_dt_confidence = "provisional_secondary_rulebook_calendar_confirmed"` unless calendar lookup fails or unusual gap.
4. Per-row caveat carries full provenance: methodology source (Mirae 2021-11 §7.1), futures LTD source (Hana 2020-05-25 p8+p15), calendar source (local A0 artifact), basis classes (both `*__primary_KRX_access_blocked`), confidence label.

### 2.1 Computed effective dates (9 cycles)

| Cycle | 2nd Thu (futures LTD) | In calendar? | effective_dt | Confidence |
|---|---|---|---|---|
| 2021-06 | 2021-06-10 | yes | **2021-06-11** | provisional_secondary_rulebook_calendar_confirmed |
| 2021-12 | 2021-12-09 | yes | **2021-12-10** | provisional_secondary_rulebook_calendar_confirmed |
| 2022-06 | 2022-06-09 | yes | **2022-06-10** | provisional_secondary_rulebook_calendar_confirmed |
| 2023-06 | 2023-06-08 | yes | **2023-06-09** | provisional_secondary_rulebook_calendar_confirmed |
| 2023-12 | 2023-12-14 | yes | **2023-12-15** | provisional_secondary_rulebook_calendar_confirmed |
| 2024-06 | 2024-06-13 | yes | **2024-06-14** | provisional_secondary_rulebook_calendar_confirmed |
| 2024-12 | 2024-12-12 | yes | **2024-12-13** | provisional_secondary_rulebook_calendar_confirmed |
| 2025-06 | 2025-06-12 | yes | **2025-06-13** | provisional_secondary_rulebook_calendar_confirmed |
| 2025-12 | 2025-12-11 | yes | **2025-12-12** | provisional_secondary_rulebook_calendar_confirmed |

### 2.2 Blank cycle (1)

| Cycle | Rule applies? | Rule computes | effective_dt | Confidence |
|---|---|---|---|---|
| 2026-06 | yes | 2026-06-11 + 1 trading day | (BLANK) | blocked_calendar_coverage_cutoff |

2026-06 caveat (per Referee Q2):
> "calendar_coverage_cutoff_2026-05-22__effective_dt_not_computed__secondary_press_reconciliation_suggests_2026-06-12_but_primary_calendar_support_missing; calendar fetch not authorized in this phase per Referee Q2 directive"

### 2.3 Reconciliation check (NOT used as fill basis)

KRX press release for bbsSeq=1090 (2026-05-22) explicitly states effective date "6월 12일" (June 12, 2026). My rule predicts second Thursday of June 2026 = 2026-06-11 (Thursday); next trading day = 2026-06-12 (Friday). **The rule + secondary-basis derivation MATCHES the KRX press release's explicit effective date.** Used only as reconciliation evidence — NOT used to fill 2026-06 (per Referee directive forbidding press-news fill basis).

This match is strong corroboration that the rule + secondary basis is internally consistent with primary KRX press release output.

---

## 3. Outputs

```
data/acquired/bx01_kospi200_rulebook_effective_dt_a0/
  raw/
    krx_methodology_root.html              endpoint discovery (KRX official)
    krx_methodology_list.json              endpoint probe / OTP-gating documented
    miraeasset_kospi200_methodology.pdf    secondary; 2016.5 annual rule pre-amendment (amendment-history use only)
    miraeasset_kospi200_methodology_v2.pdf secondary; 2021-11 semi-annual rule §7.1 (METHODOLOGY BASIS)
    hana_listed_derivatives_trade_description.pdf  secondary; 2020-05-25 p8+p15 (FUTURES LTD BASIS)
    krx_derivatives_rule_amendment_notice.pdf      secondary; KRX rule amendment transcript (supporting)
  manifest.csv                             provenance + sha256 for all 6 raw artifacts
  per_cycle_effective_dt.csv               10 cycles × 22-col basis table (9 filled + 1 blank)

data/acquired/bx01_kospi200_index_event_source_a0/
  events_v3.csv                            events_v2_xref.csv + 5 new effective_dt_*  cols (220 rows, preserve-all)
  reconciliation_v3.csv                    per-cycle counts + basis evidence + residual blockers

reports/experiments/BX01_KOSPI200_index_event_source_A0/
  rulebook_effective_dt_initial_pass.md    THIS FILE

src/audit/bx01/
  derive_effective_dt.py                   NEW — derivation pipeline
```

---

## 4. PIT / tradability assessment (updated)

| Field | Before (attachment-parse phase) | After (this phase) | Rule applied |
|---|---|---|---|
| `effective_dt` (const-level rows, 9 cycles) | 0/133 | **133/133** under provisional secondary basis | Mirae §7.1 + Hana p8/p15 + local calendar |
| `effective_dt` (const-level rows, 2026-06 cycle) | 0/10 | 0/10 (blank with caveat) | calendar coverage cutoff |
| `effective_dt` (bridge 2022-12) | 0/2 | 0/2 (not_applicable; not in this phase scope) | n/a |
| `effective_dt` (skeleton 75 rows) | 0/75 | 0/75 (not_applicable) | n/a |

**Updated PIT execution rule guidance (recommended for any later TEST design — NOT in this phase scope):**
- Announcement date: KRX REG_DT from notice metadata (unchanged).
- Effective date: `provisional_secondary_rulebook_calendar_confirmed` per row for 9 cycles; 2026-06 still blank.
- Conservative execution-date rule remains: `execution_date = next trading session close where session_date > announcement_dt`. Same-day execution from announcement FORBIDDEN.

The "Strategy Card" timing inputs that the BX01 mechanism would need (announcement → effective gap, run-up window) are now PARTIALLY available for downstream design discussion, but ONLY at provisional secondary basis with strong caveat.

---

## 5. Reconciliation report

See `reconciliation_v3.csv` for the full sectioned table. Highlights:

| Section | Key | Value |
|---|---|---|
| GLOBAL | total events_v3 rows | 220 |
| GLOBAL | effective_dt filled | 133 (9 cycles × const-level rows) |
| GLOBAL | effective_dt blank | 10 (2026-06 cycle 5 add + 5 del) |
| GLOBAL | effective_dt not_applicable | 77 (skeleton 75 + bridge 2 + Class A 2021-06's 12 also include the 2021-06 filling though – wait re-check) |

Wait, the Class A 2021-06 12 rows DO fall in cycle 2021-06 which is filled. Let me restate:

- 145 constituent-level rows total (12 Class A + 133 Class B-derived = 145; 145 = 12 direct + 121 Tier1 derived + 12 non-Tier1 derived... actually let me recompute: 133 derived = 131 in Tier1 + 2 bridge = 133, and 12 direct in Tier1 2021-06; total Tier1 const rows = 12 + 131 = 143, plus 2 bridge = 145).
- Of the 145 const-level rows:
  - 9 of the 10 Tier1 cycles are filled = 143 - (2026-06 cycle's 10 rows) = 133 filled
  - 2026-06 cycle 10 rows blank
  - 2 bridge rows (2022-12) not_applicable (out of rulebook scope)
- 75 skeleton rows = not_applicable

Total: 133 filled + 10 blank + (2 + 75) = 133 + 10 + 77 = 220 ✓

(See `reconciliation_v3.csv` for canonical counts.)

---

## 6. Residual blockers (preserved + new)

Carry-forward from prior phases:
1. 4 Tier 1 cycles (2018-06 / 2019-06 / 2020-06 / 2020-12) — hwp / broker pdf deferred.
2. Class B regular vs intermediate-special conflation — preserved as caveat.
3. Tier 2 / Tier 3 specials — deferred.

New (this phase):
4. Primary KRX rulebook access — BLOCKED (sandbox OTP path).
5. Primary KRX derivatives product spec access — BLOCKED.
6. 2026-06 calendar coverage cutoff at 2026-05-22.

These five together prevent any `PASS_TO_DIAGNOSTIC_BACKTEST_DESIGN` verdict.

---

## 7. Gate recommendation (for Referee — NOT self-applied)

**Recommended: `BACKLOG_EFFECTIVE_DT_PARTIAL_SECONDARY_BASIS`** (Referee's own expected wording).

Rationale:
- Material progress: 9 cycles' effective_dt filled with strict secondary-triangulated provenance. ✅
- All Referee-required strict labels applied per row. ✅
- 0 convention/news/memory fills. ✅
- Reconciliation against the 2026-06 KRX press release date is PERFECT (rule predicts 2026-06-12; press says 2026-06-12). ✅
- 5 residual blockers above remain. → not PASS. → not FAIL.

**NOT FAIL_CLOSED** — derivation method is auditable + rule-cited + calendar-confirmed.

**NOT PASS_TO_DIAGNOSTIC_BACKTEST_DESIGN** — secondary basis + 4 skeleton cycles + diff conflation + 2026-06 blank.

---

## 8. Repo state

### 8.1 Initial-pass commit (this phase)

To be filled at commit time below.

### 8.2 Tracking policy

`research_input_data/` files unchanged (read-only protected dir — never touched). `raw/` artifacts under `data/acquired/bx01_kospi200_rulebook_effective_dt_a0/raw/` are committable as small public PDFs + sha256 manifest (cumulative ~2.2 MB; not gitignored under the bx01 exception). The derived CSVs (events_v3.csv, per_cycle_effective_dt.csv, reconciliation_v3.csv) are tracked.

---

## 9. Boundary statement

This initial-pass report:

- DOES NOT compute any return, run-up, edge metric, or strategy.
- DOES NOT write signals.csv / trades.csv / portfolio / P08 / paper / live / execution artifact.
- DOES NOT open a backtest / design / test phase.
- DOES NOT bypass any paywall / scrape any non-public source / reach for a paid feed.
- DOES NOT retry the failed sandbox OTP attachment-download path.
- DOES NOT fill effective_dt by convention / memory / news / rebalance-date convention.
- DOES NOT use 2026-06-12 press release as a fill basis (reconciliation only).
- DOES NOT extend the KRX calendar in this phase (per Referee Q2).
- DOES NOT parse hwp / Class C / Class D / Tier 2 / Tier 3.
- DOES NOT modify any file under `research_input_data/` (read-only protected).
- DOES NOT label any row strategy-ready / executable / approved / production-ready / paper-ready.
- DOES NOT self-close or move the phase to Closed/Frozen.

P08_IEF30 frozen — untouched. Measurement-layer DECIDED STANDBY — untouched. Closed families — untouched. Bear's BX02 / BX03 / BX04 verdicts — intact.
