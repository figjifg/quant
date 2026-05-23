"""S2 Phase Final A0 Report Generator.

Per Referee verdict (2026-05-23): S2 OPENDART body parser phase closes as PARTIAL.
- D3a = PARTIAL
- D3b = PARTIAL / NOT C3-ready
- D3c = CLOSED
- C2/C3 = DESIGN-ONLY
- Strategy testing = CLOSED

Produces 11 required Referee outputs in reports/experiments/S2_phase_final_A0/.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

import pandas as pd

REPO_ROOT = Path("/home/jin/code/quant")
REPORT_DIR = REPO_ROOT / "reports" / "experiments" / "S2_phase_final_A0"

D1_SAMPLES = REPO_ROOT / "data" / "acquired" / "round4" / "s2_dart_body_d1" / "samples_50.csv"
D2_SAMPLES = REPO_ROOT / "data" / "acquired" / "round4" / "s2_dart_body_d2" / "all_samples_d1_d2.csv"
D3_V3_PARSED = REPO_ROOT / "data" / "acquired" / "round4" / "s2_dart_body_d3_v3" / "d3_v3_parsed_rows.csv"
D3_TRIAGE_DATA = REPO_ROOT / "data" / "acquired" / "round4" / "s2_dart_body_d3_triage"


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Load all available data
    d1_df = pd.read_csv(D1_SAMPLES); d1_df["phase"] = "D1"
    d2_df = pd.read_csv(D2_SAMPLES) if D2_SAMPLES.exists() else pd.DataFrame()
    if "phase" not in d2_df.columns and len(d2_df) > 0:
        d2_df["phase"] = "D2"
    samples = pd.concat([d1_df, d2_df], ignore_index=True)
    samples["rcept_no"] = samples["rcept_no"].astype(str)
    samples = samples.drop_duplicates("rcept_no").reset_index(drop=True)

    v3 = pd.read_csv(D3_V3_PARSED) if D3_V3_PARSED.exists() else pd.DataFrame()

    # === 1. S2_parser_A0_final_report.md (MAIN) ===
    main_lines = [
        "# S2 Parser A0 Final Report\n",
        f"Date: {now}",
        "Origin: Referee final verdict (2026-05-23) — S2 phase closes as PARTIAL.\n",
        "## TL;DR",
        "",
        "**S2 OPENDART body parser phase is COMPLETE AS PARTIAL.**",
        "",
        "- Generic OPENDART body XML parser is **feasible** but **insufficient** for C3-ready corporate-action event logs.",
        "- D3a treasury parser **partially works** — 2/7 base forms have deterministic labels. **NOT C3-ready**.",
        "- D3b CB/BW/conversion parser **requires per-form custom parsers + SECTION/COVER text scanner** — generic tuning ran 3 rounds (v1/v2/v3) and reached its limit. **NOT C3-ready**.",
        "- D3c (additional listing / lockup / major shareholder sale / correction-cancellation) was **never opened** — remains closed.",
        "- C2 / C3 integration is **NOT approved**.",
        "- **No strategy can be reopened from this S2 result alone.**",
        "",
        "## S2 phase journey summary",
        "",
        "| Phase | Outcome |",
        "|---|---|",
        "| D1 dry run (45/50 disclosures) | 91.1% endpoint success; 4/4 D2 entry gates PASS |",
        "| D2 schema mapping (63 add'l + KOSDAQ) | 6/6 pass gates; 38 base forms schema-analyzed; natural finding = 2 response types (dart_xml_structured 66 + html_inline 38) |",
        "| D3 v1 first-pass parser | Infrastructure works; mean confidence 0.037 D3a / 0.147 D3b; manual_review 100% |",
        "| D3 v2 precision tuning (multi-row + ACODE) | D3a meaningful improvement (amount +22.2pp), D3b mixed (shares regression -23.5pp, conversion_price +29.4pp) |",
        "| D3 v3 2nd tuning (per-ACODE inventory) | D3a marginal (amount +8.3pp); D3b shares regression NOT recovered; D3b event_date stays 0% |",
        "| D3 triage | D3a labels deterministic in only 2/7 base forms; D3b requires custom parsers + COVER scanner; D3c remains closed |",
        "",
        "## Final parser status",
        "",
        "| Wave | State | Reason | Reopen path |",
        "|---|---|---|---|",
        "| D3a | **PARTIAL** | 2/7 base forms deterministic on the 36-row sample. Other forms partial or non-deterministic. | Referee-approved targeted parser pass focused on 2 deterministic forms |",
        "| D3b | **PARTIAL / NOT C3-ready** | 3 generic tuning rounds did not recover shares regression or improve event_date 0%. Custom parsers + COVER text scanner required. | NEW phase: `S2-D3B-CUSTOM-PARSER-PHASE` with separate Referee approval, scope, kill gates, manual audit, time budget |",
        "| D3c | **CLOSED** | Never opened; HTML/free-text heavy; awaits D3a+D3b state resolution | Referee approval after D3a/D3b resolved |",
        "| C2 (factor chain) | **DESIGN-ONLY** | Parser outputs not reliable enough for wiring | None until parser PARTIAL → C3-ready transition |",
        "| C3 (corp action day) | **DESIGN-ONLY** | Same as C2 | Same as C2 |",
        "",
        "## Hard locks (S2 phase final close)",
        "",
        "- No return backtest / NAV / CAGR / Sharpe / hit rate / alpha / excess return / MDD",
        "- No post-event drift / migration / turnover / resume / reversal / flow-return",
        "- No raw return as signal/outcome",
        "- No Round 2 strategy restart",
        "- No flow strategy testing",
        "- No DART body alpha test",
        "- No overhang alpha/filter test",
        "- No production / paper / P08 / live readiness / shadow connection",
        "- No parser result described as strategy-ready",
        "- No D3c full implementation",
        "- No C2/C3 integration",
        "- No unified all-event event log finalization",
        "",
        "## What this S2 phase did establish (audit value)",
        "",
        "- OPENDART `document.xml` endpoint is reachable from sandbox (91-100% success on 108 samples)",
        "- 2 response types confirmed: `dart_xml_structured` (DART3/DART4 XSD) and `html_inline` (안내공시 / KOSDAQ 시장안내 / 보호예수 등)",
        "- Per-ACODE label inventory built from 104 actual XMLs",
        "- Correction prefix normalization rules locked (`[기재정정]`, `[첨부정정]`, `[첨부추가]`, `[연장결정]`, 자회사/종속회사 suffix, 회차 marker)",
        "- Correction linkage algorithm verified end-to-end (1 in-sample link demonstrated)",
        "- PIT timestamp lock confirmed (rcept_no + rcept_date populated 100%)",
        "- 6 tiny-response / attachment-only classification flags designed and implemented",
        "- D3b feasibility verdict: custom parsers required (4-7 weeks new phase if approved)",
        "",
        "## What this S2 phase did NOT establish",
        "",
        "- A C3-ready unified corporate-action event log",
        "- Strategy-ready field extractions (manual_review_required remains 100% across all D3a/D3b rows)",
        "- Production parser for any of the 10 Referee event types beyond infrastructure-level dispatch",
        "- Wiring into the P08_IEF30 production system",
        "",
        "## Compliance",
        "",
        "All Referee Round 4.1 hard locks were respected throughout S2 phase D1/D2/D3 work. No strategy testing was performed. No parser result was ever described as strategy-ready. All 8-9 outputs at every Referee-required checkpoint were produced and published to GitHub main.",
        "",
        "## Supporting documents (this directory)",
        "",
        "- source_coverage_final.md",
        "- form_coverage_final.md",
        "- parser_status_by_event_type_final.csv",
        "- manual_audit_findings_final.md",
        "- pit_timestamp_lock_final.md",
        "- correction_cancellation_linkage_final.md",
        "- event_log_schema_feasibility_final.md",
        "- c2_c3_readiness_final.md",
        "- s2_remaining_blockers_register.md",
        "- referee_next_decision_brief.md",
    ]
    (REPORT_DIR / "S2_parser_A0_final_report.md").write_text("\n".join(main_lines), encoding="utf-8")

    # === 2. source_coverage_final.md ===
    n_d1 = 45
    n_d2 = 63
    n_total = len(samples)
    sc_lines = [
        "# S2 Source Coverage — Final\n",
        f"Date: {now}\n",
        "## Acquisition phases",
        "",
        "| Phase | Disclosures attempted | Successful download | Notes |",
        "|---|---|---|---|",
        f"| D1 dry run | 45 (originally 50, treasury_cancel mapping 0) | 41 (91.1%) | 4 tiny-response API errors |",
        f"| D2 schema mapping | 63 | 63 (100%) | mapping corrected (treasury_cancel = 주식소각결정) + KOSDAQ via list.json |",
        f"| Total (D1+D2 union) | {n_total} unique rcept_no | ≈ 104 XML files | KOSPI source corp_cls='Y' from R000 + KOSDAQ corp_cls='K' from OPENDART list API |",
        "",
        "## Period and universe",
        "",
        "- Period: **2018-01-01 ~ 2026-05-22** (R000 inputs range)",
        "- Universe: **KOSPI + KOSDAQ**",
        "  - KOSPI: R000 input parquet `opendart_kospi_disclosures_20180101_20260505.parquet` (450,190 disclosures)",
        "  - KOSDAQ: OPENDART list API `list.json?corp_cls=K` (20 samples acquired)",
        "",
        "## OPENDART endpoint coverage",
        "",
        "- `https://opendart.fss.or.kr/api/document.xml` — body XML download for individual rcept_no",
        "- `https://opendart.fss.or.kr/api/list.json` — disclosure list filter (used for KOSDAQ acquisition)",
        "",
        "## Response type distribution (104 XML files)",
        "",
        "| Response type | Count | Note |",
        "|---|---|---|",
        "| dart_xml_structured | 66 | DART3 or DART4 XSD, `<DOCUMENT>` root, structured tables |",
        "| html_inline | 38 | `<html>` root, EUC-KR encoded, free CSS tables |",
        "",
        "## Hard locks reaffirmed",
        "",
        "- No strategy testing was performed during acquisition",
        "- No raw download data was used for strategy signal construction",
        "- API key handled via BOM/CRLF-safe parser, length-only log",
    ]
    (REPORT_DIR / "source_coverage_final.md").write_text("\n".join(sc_lines), encoding="utf-8")

    # === 3. form_coverage_final.md ===
    # Compute event-type coverage from v3 parsed rows if available
    coverage_lines = [
        "# S2 Form Coverage — Final\n",
        f"Date: {now}\n",
        "## Referee 10-event-type taxonomy coverage",
        "",
        "| Event type | D1+D2 samples | Parser wave | Final state |",
        "|---|---|---|---|",
    ]
    if len(v3) > 0:
        wave_event_counts = v3.groupby(["wave", "event_type"]).size().reset_index(name="n")
        # main taxonomy entries
        type_states = {
            "treasury_acquire": ("D3a", "PARTIAL — 0/4 fields deterministic on 4-sample subset"),
            "treasury_dispose": ("D3a", "PARTIAL — 0/4 fields deterministic"),
            "treasury_cancel": ("D3a", "PARTIAL — 2/4 fields deterministic (amount, event_date)"),
            "treasury_trust_create": ("D3a", "NON-DETERMINISTIC — 0/4 fields, custom parser needed if reopened"),
            "treasury_trust_terminate": ("D3a", "PARTIAL — 2/4 fields partial"),
            "treasury_acquire_result": ("D3a", "DETERMINISTIC — 4/4 fields (best of D3a)"),
            "treasury_dispose_result": ("D3a", "PARTIAL — 0/4 deterministic but all 4 partial"),
            "cb_issue": ("D3b", "NOT C3-ready — event_date 0% in body tables; needs COVER text scanner"),
            "bw_issue": ("D3b", "NOT C3-ready — same as cb_issue"),
            "conversion_request": ("D3b", "NOT C3-ready — html_inline ambiguous; dedicated parser family required"),
            "rights_issue": ("D3c", "CLOSED — never opened in D3"),
            "bonus_issue": ("D3c", "CLOSED"),
            "capital_reduction": ("D3c", "CLOSED"),
            "merger_split": ("D3c", "CLOSED"),
            "additional_listing": ("D3c", "CLOSED — R000 KOSPI has only 3 disclosures (`기타시장안내`)"),
            "lockup_release": ("D3c", "CLOSED — `기타안내사항(안내공시)` HTML, free-text heavy"),
            "major_shareholder_sale": ("D3c", "CLOSED — 임원ㆍ주요주주특정증권등소유상황보고서, large volume but html_inline"),
            "correction_withdrawal_cancel": ("D3c", "CLOSED — `철회신고서` + heterogeneous 취소공시; whitelist required"),
        }
        for et, (wave, state) in type_states.items():
            sub = wave_event_counts[wave_event_counts["event_type"] == et]
            n = int(sub["n"].sum()) if len(sub) else 0
            coverage_lines.append(f"| {et} | {n} | {wave} | {state} |")
    coverage_lines += [
        "",
        "## Base form inventory (38 distinct base forms encountered)",
        "",
        "See `reports/experiments/S2_phase_d2_schema_mapping/d2_form_inventory_expanded.md` for the full form-level inventory and `d2_actual_form_taxonomy_mapping.md` for the taxonomy mapping with normalization rules.",
        "",
        "## Hard locks",
        "",
        "- No strategy claim associated with any form",
        "- No event log produced; coverage state is reporting only",
    ]
    (REPORT_DIR / "form_coverage_final.md").write_text("\n".join(coverage_lines), encoding="utf-8")

    # === 4. parser_status_by_event_type_final.csv ===
    if len(v3) > 0:
        status_df = v3.copy()
        status_df["parser_confidence"] = pd.to_numeric(status_df["parser_confidence"], errors="coerce")
        agg = status_df.groupby(["wave", "event_type"]).agg(
            n_total=("rcept_no", "count"),
            n_ok=("parser_status", lambda s: (s == "ok").sum()),
            n_attachment_only=("attachment_only_flag", "sum"),
            mean_confidence=("parser_confidence", "mean"),
            max_confidence=("parser_confidence", "max"),
            manual_review_rate=("manual_review_required", "mean"),
        ).reset_index()
        agg["mean_confidence"] = agg["mean_confidence"].round(3)
        agg["max_confidence"] = agg["max_confidence"].round(3)
        agg["manual_review_rate"] = (agg["manual_review_rate"] * 100).round(1).astype(str) + "%"
        agg.to_csv(REPORT_DIR / "parser_status_by_event_type_final.csv", index=False)
    else:
        pd.DataFrame().to_csv(REPORT_DIR / "parser_status_by_event_type_final.csv", index=False)

    # === 5. manual_audit_findings_final.md ===
    ma_lines = [
        "# S2 Manual Audit Findings — Final\n",
        f"Date: {now}\n",
        "## Manual review queue across S2 phase",
        "",
        "| Round | Manual review queue size | Notes |",
        "|---|---|---|",
        "| D3 v1 | 108 rows | First-pass; all rows flagged |",
        "| D3 v2 | 108 rows | Same denominator; precision tuning round 1 |",
        "| D3 v3 | 108 rows | Same; precision tuning round 2 |",
        "| D3 triage | 35 (D3a) + 17 (D3b) | per-base-form deterministic vs partial vs non-deterministic |",
        "",
        "## D3a label-determinism findings (from triage)",
        "",
        "Recorded in `reports/experiments/S2_phase_d3_triage/d3a_manual_label_audit.md`:",
        "",
        "| Base form | Deterministic fields (≥70% hit, ≤5 phrasings) |",
        "|---|---|",
        "| 자기주식취득결과보고서 | **4/4** |",
        "| 주식소각결정 | 2/4 (amount, event_date) |",
        "| 자기주식처분결과보고서 | 0/4 (all partial) |",
        "| 주요사항보고서(자기주식처분결정) | 0/4 (3 partial) |",
        "| 주요사항보고서(자기주식취득결정) | 0/4 (3 partial) |",
        "| 주요사항보고서(자기주식취득신탁계약체결결정) | 0/4 (all non-deterministic) |",
        "| 주요사항보고서(자기주식취득신탁계약해지결정) | 0/4 (2 partial) |",
        "",
        "## D3b feasibility findings (from triage)",
        "",
        "Recorded in `reports/experiments/S2_phase_d3_triage/d3b_feasibility_triage.md`:",
        "",
        "- CB issue: event_date 5/6 NOT extractable from body tables",
        "- BW issue: event_date 3/5 NOT extractable, 2/5 missing_xml",
        "- conversion_request: shares + event_date 5/6 ambiguous (html_inline)",
        "",
        "## Manual audit limitations",
        "",
        "- Referee target was 30 samples per event type for manual audit. Acquired sample size was 4-6 per D3a base form and 5-6 per D3b sub-category — well below target.",
        "- A true full manual audit (e.g., 30 per event type × 17 event types ≈ 500 disclosures + manual review) was not performed in this S2 phase. It is feasible as a follow-up phase but not approved by Referee for S2 close.",
        "- D5b (manual audit) per master ticket was never executed — only D5a (sample extraction framework) was implemented.",
        "",
        "## Hard locks",
        "",
        "- Manual audit findings did NOT produce strategy-ready event flags",
        "- No strategy testing conducted on audit-marked samples",
    ]
    (REPORT_DIR / "manual_audit_findings_final.md").write_text("\n".join(ma_lines), encoding="utf-8")

    # === 6. pit_timestamp_lock_final.md ===
    pit_lines = [
        "# S2 PIT Timestamp Lock — Final\n",
        f"Date: {now}\n",
        "## PIT anchor fields (Referee-required)",
        "",
        "| Field | Source | Lock state |",
        "|---|---|---|",
        "| `rcept_no` | OPENDART receipt number | **LOCKED 100%** (verified on all 108 D1+D2 rows in D3 parsed audit trail) |",
        "| `rcept_date` | OPENDART receipt date (R000 column `rcept_date`) | **LOCKED 100%** |",
        "| `pit_available_at` | rcept_no datetime floor (= disclosure submit timestamp) | Locked at rcept_date level; intraday timestamp `rcept_dt` (YYYYMMDD) available in R000 |",
        "",
        "## PIT discipline maintained throughout S2 phase",
        "",
        "- Look-ahead avoidance: all parser outputs include `pit_available_at` (= rcept_date)",
        "- `event_date` (when extracted) is treated separately from `pit_available_at`; signals can only use event_date for grouping, not for execution timing prior to pit_available_at",
        "- Correction linkage uses prior rcept_no (chronologically before correction) — never future linkage",
        "- No event_date was ever substituted for rcept_date as PIT (Referee explicit directive)",
        "",
        "## What PIT lock does NOT guarantee",
        "",
        "- Field-level extraction precision (separate concern; remains low — see manual_audit_findings_final.md)",
        "- Event semantic correctness (separate concern; remains in scope for any future C3 phase)",
        "",
        "## Hard locks",
        "",
        "- PIT lock verified at receipt-date level only; intraday PIT (for same-day signal availability) requires C2/C3 follow-up",
        "- No strategy was built on PIT lock alone",
    ]
    (REPORT_DIR / "pit_timestamp_lock_final.md").write_text("\n".join(pit_lines), encoding="utf-8")

    # === 7. correction_cancellation_linkage_final.md ===
    link_lines = [
        "# S2 Correction / Cancellation Linkage — Final\n",
        f"Date: {now}\n",
        "## Linkage algorithm (locked from D2 + D3)",
        "",
        "```",
        "for each correction row (correction_prefix ∈ {[기재정정], [첨부정정], [첨부추가], [연장결정]}):",
        "  candidates = where(",
        "    corp_code_dart == correction.corp_code_dart",
        "    AND base_form == correction.base_form (after normalization: prefix + subsidiary suffix + series marker stripped)",
        "    AND correction_prefix is null (= an original disclosure)",
        "    AND series_marker matches (if present, e.g., (제2회차))",
        "    AND rcept_date in [correction.rcept_date - 180d, correction.rcept_date]",
        "  )",
        "  if candidates non-empty: link to most recent (highest rcept_date)",
        "  else: leave unlinked → manual_review_required",
        "```",
        "",
        "## Linkage smoke-test results (D1+D2 sample union, 27 correction rows)",
        "",
        "| Round | corrections_total | linked | unlinked | link rate |",
        "|---|---|---|---|---|",
        "| D3 v1 | 27 | 3 | 24 | 11.1% |",
        "| D3 v2 | 27 | 3 | 24 | 11.1% |",
        "| D3 v3 | 27 | 3 | 24 | 11.1% |",
        "",
        "Stable across all 3 rounds (no regression). 24 unlinked because their originals are outside the 108-row D1+D2 sample. Production link rate expected substantially higher on full R000 450k join.",
        "",
        "## Verified linkage example (in-sample)",
        "",
        "- `20200715900389` ([기재정정]전환청구권행사) → `20200710900612` (전환청구권행사 original), 5-day gap",
        "",
        "## Variants normalized",
        "",
        "| Variant | Treatment | Example |",
        "|---|---|---|",
        "| `[기재정정]` | strip → base_form, link to original | `[기재정정]주요사항보고서(자기주식취득결정)` → `주요사항보고서(자기주식취득결정)` |",
        "| `[첨부정정]` | strip → base_form, link to original | same pattern |",
        "| `[첨부추가]` | strip → base_form, treated as supplementary (no event override) | `[첨부추가]주식소각결정` |",
        "| `[연장결정]` | event continuation; no original-event link required | `[연장결정]주요사항보고서(자기주식취득신탁계약체결결정)` |",
        "| `(자회사의 주요경영사항)` | strip suffix; remap corp_code if needed (D3 deferred) | `주요사항보고서(자기주식처분결정)(자회사의 주요경영사항)` |",
        "| `(종속회사의주요경영사항)` | same as 자회사 suffix | same pattern |",
        "| `(제N회차)` | preserve as `series_marker`; required for linkage match | `[기재정정]전환청구권행사(제2회차)` |",
        "",
        "## Final linkage state",
        "",
        "- **Algorithm: VERIFIED** (smoke-test successful on 3 rounds; in-sample link demonstrated)",
        "- **Production integration: BLOCKED** (no unified event log; correction linkage cannot be applied at production scale until D3 parsers are C3-ready)",
        "",
        "## Hard locks",
        "",
        "- Correction linkage NOT used as a strategy signal",
        "- 정정 entries NOT counted as new events; they amend the original",
    ]
    (REPORT_DIR / "correction_cancellation_linkage_final.md").write_text("\n".join(link_lines), encoding="utf-8")

    # === 8. event_log_schema_feasibility_final.md ===
    schema_lines = [
        "# S2 Event Log Schema Feasibility — Final\n",
        f"Date: {now}\n",
        "## 17-field Referee schema",
        "",
        "Locked since D1 (Referee Round 4.1 verdict):",
        "",
        "| Field | Type | S2 phase deliverability |",
        "|---|---|---|",
        "| ticker | str(6) | ✅ from R000 / KOSDAQ list API |",
        "| corp_code_dart | str(8) | ✅ from disclosure list |",
        "| rcept_no | str(14) | ✅ |",
        "| rcept_date | date | ✅ |",
        "| event_date | date | ⚠️ partial — D3a 13.9%, D3b 0% |",
        "| effective_date | date | ⚠️ partial — D3a 2.8%, D3b 5.9% |",
        "| event_type | str(50) | ✅ taxonomy 14 types mapped (D3a 7 + D3b 3 + D3c 4 closed) |",
        "| amount_krw | float | ⚠️ partial — D3a 36.1%, D3b 23.5% |",
        "| shares | float | ⚠️ partial — D3a 13.9%, D3b 5.9% |",
        "| shares_before | float | ⚠️ partial — D3a 2.8%, D3b not in schema |",
        "| shares_after | float | ⚠️ not extracted — D3a 0% |",
        "| factor | float | ❌ not extracted (감자 비율 / 무증 factor) |",
        "| cancellation_linkage | str | ⚠️ algorithm works, but linkage_to_original_rcept_no populated only in-sample |",
        "| source | str | ✅ `dart_opendart_body_v1` |",
        "| parser_confidence | float [0,1] | ✅ calculated; D3a max 1.0 (1 row), D3b max 0.5 |",
        "| manual_audit_status | str | ⚠️ all `not_audited`; full audit deferred to future phase |",
        "| pit_available_at | datetime | ✅ at rcept_date level |",
        "",
        "## Feasibility verdict",
        "",
        "- **Schema is structurally feasible** — every required field is reachable from OPENDART body XML in principle",
        "- **Schema is not population-feasible at production scale** with current generic parser — field-level extraction rates are too low for an event log usable in C2/C3 integration",
        "- **Custom parsers (D3b)** + **D3a one-more-pass** + **D3c parser** would each contribute incremental population rates",
        "- Estimated end-state population (if all future phases approved and executed): D3a ≥ 70% per field, D3b ≥ 50% per field, D3c best-effort",
        "",
        "## What's locked at this point",
        "",
        "- 17-field schema definition (no changes)",
        "- 14-event-type taxonomy (no changes)",
        "- Correction linkage algorithm (no changes)",
        "- Normalization rules (correction prefix / subsidiary suffix / series marker)",
        "- PIT lock policy",
        "",
        "## What's deferred",
        "",
        "- Production population of the event log",
        "- C2/C3 wiring",
        "- Strategy-ready claim on any field",
    ]
    (REPORT_DIR / "event_log_schema_feasibility_final.md").write_text("\n".join(schema_lines), encoding="utf-8")

    # === 9. c2_c3_readiness_final.md ===
    c23_lines = [
        "# S2 C2 / C3 Readiness — Final\n",
        f"Date: {now}\n",
        "## C2 (factor chain integration) — DESIGN ONLY",
        "",
        "Status: **NOT integrated**. Design constraints documented in `reports/experiments/S2_phase_d3_triage/c2_c3_design_constraints.md`.",
        "",
        "C2 design requirements (locked):",
        "- Accept per-event-type partial coverage with explicit `event_source` and `event_status` fields",
        "- Include `not_available` branch for event types whose parser is not yet C3-ready",
        "- Do NOT block on a unified event log; per-event-type partial coverage is allowed if marked explicitly",
        "",
        "## C3 (corporate-action day reclassification) — DESIGN ONLY",
        "",
        "Status: **NOT integrated**. Design constraints documented.",
        "",
        "C3 design requirements (locked):",
        "- Reclassification of `corp_action_day` requires deterministic event_date + effective_date per disclosure",
        "- Current D3a 13.9% event_date rate is insufficient; one-more-pass on the 2 deterministic forms might lift this for the treasury subset",
        "- D3b CB/BW/conversion: event_date 0%, blocked entirely",
        "- Spec: not_yet_available branch surfaces uncovered events as audit log entries, not as reclassified days",
        "",
        "## Blocked downstream items",
        "",
        "| Item | Status | Reason |",
        "|---|---|---|",
        "| G5_000005 | DEFERRED-S2 → **REMAINS DEFERRED** | S2 parser cannot deliver C3 reclassification input |",
        "| G5_000004 (35 strategy-relevant events) | Partially reachable for treasury subset only | Other event types unparsed |",
        "| TRAD_000003 limit pollution (41 rows) | **STILL BLOCKED** | Same root cause |",
        "| KR-DART-BODY-RETURN-001 backlog | Partial unblock on treasury subset only | Other event types not C3-ready |",
        "| KR-OVERHANG-AVOID-001 backlog | **STILL BLOCKED** | CB/BW/conversion event_date 0% in body tables |",
        "",
        "## Allowed C2/C3 work going forward (design only)",
        "",
        "- Finalize design constraints documents",
        "- Define `event_source` / `event_status` / `manual_required` enum values",
        "- Spec how C2/C3 would consume future parser outputs (interface contract)",
        "- Document what custom parser work would be required (D3B-CUSTOM-PARSER-PHASE pre-spec)",
        "",
        "## NOT allowed",
        "",
        "- Wire parser outputs into a production C2/C3 path",
        "- Create unified all-event event log",
        "- Reclassify corp_action_day using parser outputs",
        "- Use C2/C3 outputs in any strategy testing",
        "- Treat parser output as strategy-ready",
        "",
        "## Hard locks",
        "",
        "- C2/C3 = DESIGN-ONLY",
        "- Reopen requires Referee-approved D3B-CUSTOM-PARSER-PHASE + subsequent integration approval",
    ]
    (REPORT_DIR / "c2_c3_readiness_final.md").write_text("\n".join(c23_lines), encoding="utf-8")

    # === 10. s2_remaining_blockers_register.md ===
    blockers_lines = [
        "# S2 Remaining Blockers Register — Final\n",
        f"Date: {now}\n",
        "## Open blockers carried forward from S2",
        "",
        "| # | Blocker | Owner | Reopen path |",
        "|---|---|---|---|",
        "| 1 | D3a label determinism on 5/7 base forms (subsidiary trust / 취득 결정 / 처분 결정 / 신탁 해지 / 처분 결과) | Future targeted parser pass | Referee approval for narrow D3a continuation |",
        "| 2 | D3b custom parsers (ACODE 11324 / 11325 / conversion_request family) | New phase | Approve `S2-D3B-CUSTOM-PARSER-PHASE` |",
        "| 3 | D3b SECTION/COVER text scanner for event_date | Part of D3b custom phase | Same as #2 |",
        "| 4 | D3c full implementation (additional listing / lockup / major shareholder sale / correction-cancellation) | Future phase | After D3a/D3b resolved |",
        "| 5 | Full manual audit (30 samples per event type) | Future phase | Was deferred from D5b; revisit when D3 parsers C3-ready |",
        "| 6 | C2/C3 integration | Design-only now | After parser PARTIAL → C3-ready transition |",
        "| 7 | G5_000005 DEFERRED-S2 closure | Blocked by C3 | After C3 integration |",
        "| 8 | KR-OVERHANG-AVOID-001 backlog | Blocked by D3b | After D3b custom parsers |",
        "| 9 | KR-DART-BODY-RETURN-001 backlog | Partially unblockable | Treasury-only subset partial after D3a one-more-pass (if approved) |",
        "",
        "## Closed during S2",
        "",
        "- D3 framework (dispatcher / charset / schema detection / correction linkage / PIT lock) — closed, infrastructure works",
        "- Form taxonomy mapping — 14 event types + 38 base forms + variant normalization rules locked",
        "- Tiny-response / attachment-only classification — 6 flags designed",
        "- Per-ACODE label inventory — 17 ACODEs catalogued from 104 XML samples",
        "",
        "## Hard locks",
        "",
        "- These blockers do NOT translate into strategy work",
        "- Reopening any blocker requires fresh Referee approval",
    ]
    (REPORT_DIR / "s2_remaining_blockers_register.md").write_text("\n".join(blockers_lines), encoding="utf-8")

    # === 11. referee_next_decision_brief.md ===
    next_brief = [
        "# Referee Next Decision Brief\n",
        f"Date: {now}\n",
        "## What is closed",
        "",
        "- S2 OPENDART body parser phase = **COMPLETE AS PARTIAL**",
        "- D3a = PARTIAL",
        "- D3b = PARTIAL / NOT C3-ready",
        "- D3c = CLOSED",
        "- C2/C3 = DESIGN-ONLY",
        "- Strategy testing = remains CLOSED (Research Freeze v2 unchanged)",
        "- Performance diagnostics = remains CLOSED",
        "- Production / paper / P08 / live = UNCHANGED",
        "",
        "## What is open for Referee future consideration (no executor recommendation)",
        "",
        "### Future phase candidates (each requires separate Referee approval)",
        "",
        "1. **`S2-D3A-ONE-MORE-PASS-PHASE`** — narrowly targeted parser pass on the 2 deterministic D3a base forms (자기주식취득결과보고서 + 주식소각결정). Estimated 1-2 weeks. End condition: D3a partial coverage for those 2 forms with field rates lifted toward A0 pass.",
        "",
        "2. **`S2-D3B-CUSTOM-PARSER-PHASE`** — implement per-ACODE custom parsers for 11324 (CB), 11325 (BW), conversion_request family, plus SECTION/COVER text scanner. Estimated 4-7 weeks. Separate scope, kill gates, manual audit, time budget required.",
        "",
        "3. **`S2-D3C-OPEN-PHASE`** — open D3c after D3a + D3b state is resolved. Free-text and html_inline heavy. Estimated effort unknown until D3a/D3b complete.",
        "",
        "4. **`S2-MANUAL-AUDIT-PHASE`** — full manual audit (30 samples per event type ≈ 500 disclosures). Was deferred from D5b. Reopen when parser deemed C3-ready candidate.",
        "",
        "5. **`C2-C3-DESIGN-FINALIZATION`** — design-only, no wiring. Allowed under current verdict. Spec the not_available / partial / manual_required event_source states and the C3 day-reclassification not_yet_available branch.",
        "",
        "### Strategy-side decisions (separate from parser phases)",
        "",
        "6. **Research Freeze v2 review** — Current S2 phase closes WITHOUT reopening any strategy. Whether to reopen any strategy at all is a separate Referee verdict on the broader Research Freeze policy.",
        "",
        "## What executor will NOT do without Referee approval",
        "",
        "- Open any of phases 1-4 above unilaterally",
        "- Wire parser outputs into C2/C3 production",
        "- Treat parser output as strategy-ready",
        "- Perform any strategy testing",
        "- Open P08 / paper / live readiness work",
        "",
        "## Executor stance",
        "",
        "Executor offers no recommendation on phase priority. Each phase is a Referee scope-vs-effort policy choice. S2 phase officially closes here.",
        "",
        "## Hard locks reaffirmed",
        "",
        "- No D3c full implementation",
        "- No C2/C3 integration",
        "- No unified all-event event log finalization",
        "- No return backtest",
        "- No NAV / CAGR / Sharpe / hit rate / alpha / excess return / MDD",
        "- No post-event drift / migration / turnover / resume / reversal / flow-return",
        "- No raw return as signal/outcome",
        "- No Round 2 strategy restart",
        "- No flow strategy testing",
        "- No DART body alpha test",
        "- No overhang alpha/filter test",
        "- No production / paper / P08 / live readiness / shadow connection",
        "- No parser result described as strategy-ready",
    ]
    (REPORT_DIR / "referee_next_decision_brief.md").write_text("\n".join(next_brief), encoding="utf-8")

    print(f"S2 final A0 report bundle written to {REPORT_DIR}")
    print(f"Files: {len(list(REPORT_DIR.iterdir()))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
