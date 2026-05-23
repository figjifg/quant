# S2 Parser A0 Final Report

Date: 2026-05-23 15:42:46
Origin: Referee final verdict (2026-05-23) — S2 phase closes as PARTIAL.

## TL;DR

**S2 OPENDART body parser phase is COMPLETE AS PARTIAL.**

- Generic OPENDART body XML parser is **feasible** but **insufficient** for C3-ready corporate-action event logs.
- D3a treasury parser **partially works** — 2/7 base forms have deterministic labels. **NOT C3-ready**.
- D3b CB/BW/conversion parser **requires per-form custom parsers + SECTION/COVER text scanner** — generic tuning ran 3 rounds (v1/v2/v3) and reached its limit. **NOT C3-ready**.
- D3c (additional listing / lockup / major shareholder sale / correction-cancellation) was **never opened** — remains closed.
- C2 / C3 integration is **NOT approved**.
- **No strategy can be reopened from this S2 result alone.**

## S2 phase journey summary

| Phase | Outcome |
|---|---|
| D1 dry run (45/50 disclosures) | 91.1% endpoint success; 4/4 D2 entry gates PASS |
| D2 schema mapping (63 add'l + KOSDAQ) | 6/6 pass gates; 38 base forms schema-analyzed; natural finding = 2 response types (dart_xml_structured 66 + html_inline 38) |
| D3 v1 first-pass parser | Infrastructure works; mean confidence 0.037 D3a / 0.147 D3b; manual_review 100% |
| D3 v2 precision tuning (multi-row + ACODE) | D3a meaningful improvement (amount +22.2pp), D3b mixed (shares regression -23.5pp, conversion_price +29.4pp) |
| D3 v3 2nd tuning (per-ACODE inventory) | D3a marginal (amount +8.3pp); D3b shares regression NOT recovered; D3b event_date stays 0% |
| D3 triage | D3a labels deterministic in only 2/7 base forms; D3b requires custom parsers + COVER scanner; D3c remains closed |

## Final parser status

| Wave | State | Reason | Reopen path |
|---|---|---|---|
| D3a | **PARTIAL** | 2/7 base forms deterministic on the 36-row sample. Other forms partial or non-deterministic. | Referee-approved targeted parser pass focused on 2 deterministic forms |
| D3b | **PARTIAL / NOT C3-ready** | 3 generic tuning rounds did not recover shares regression or improve event_date 0%. Custom parsers + COVER text scanner required. | NEW phase: `S2-D3B-CUSTOM-PARSER-PHASE` with separate Referee approval, scope, kill gates, manual audit, time budget |
| D3c | **CLOSED** | Never opened; HTML/free-text heavy; awaits D3a+D3b state resolution | Referee approval after D3a/D3b resolved |
| C2 (factor chain) | **DESIGN-ONLY** | Parser outputs not reliable enough for wiring | None until parser PARTIAL → C3-ready transition |
| C3 (corp action day) | **DESIGN-ONLY** | Same as C2 | Same as C2 |

## Hard locks (S2 phase final close)

- No return backtest / NAV / CAGR / Sharpe / hit rate / alpha / excess return / MDD
- No post-event drift / migration / turnover / resume / reversal / flow-return
- No raw return as signal/outcome
- No Round 2 strategy restart
- No flow strategy testing
- No DART body alpha test
- No overhang alpha/filter test
- No production / paper / P08 / live readiness / shadow connection
- No parser result described as strategy-ready
- No D3c full implementation
- No C2/C3 integration
- No unified all-event event log finalization

## What this S2 phase did establish (audit value)

- OPENDART `document.xml` endpoint is reachable from sandbox (91-100% success on 108 samples)
- 2 response types confirmed: `dart_xml_structured` (DART3/DART4 XSD) and `html_inline` (안내공시 / KOSDAQ 시장안내 / 보호예수 등)
- Per-ACODE label inventory built from 104 actual XMLs
- Correction prefix normalization rules locked (`[기재정정]`, `[첨부정정]`, `[첨부추가]`, `[연장결정]`, 자회사/종속회사 suffix, 회차 marker)
- Correction linkage algorithm verified end-to-end (1 in-sample link demonstrated)
- PIT timestamp lock confirmed (rcept_no + rcept_date populated 100%)
- 6 tiny-response / attachment-only classification flags designed and implemented
- D3b feasibility verdict: custom parsers required (4-7 weeks new phase if approved)

## What this S2 phase did NOT establish

- A C3-ready unified corporate-action event log
- Strategy-ready field extractions (manual_review_required remains 100% across all D3a/D3b rows)
- Production parser for any of the 10 Referee event types beyond infrastructure-level dispatch
- Wiring into the P08_IEF30 production system

## Compliance

All Referee Round 4.1 hard locks were respected throughout S2 phase D1/D2/D3 work. No strategy testing was performed. No parser result was ever described as strategy-ready. All 8-9 outputs at every Referee-required checkpoint were produced and published to GitHub main.

## Supporting documents (this directory)

- source_coverage_final.md
- form_coverage_final.md
- parser_status_by_event_type_final.csv
- manual_audit_findings_final.md
- pit_timestamp_lock_final.md
- correction_cancellation_linkage_final.md
- event_log_schema_feasibility_final.md
- c2_c3_readiness_final.md
- s2_remaining_blockers_register.md
- referee_next_decision_brief.md