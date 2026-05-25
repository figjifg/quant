# Hard-Lock Compliance Check (zip_unparseable source recovery)

Date: 2026-05-26
Phase: KR-STATUS-ZIP-UNPARSEABLE-SOURCE-RECOVERY-A0

| hard lock | status |
|---|---|
| Target set = exactly the 42 zip_unparseable rows (39 corr + 3 non-corr) | PASS (asserted) |
| No download/API for any non-target rcept_no | PASS (loop iterates the 42 only) |
| Existing corrupt cache preserved UNCHANGED (recovered files in a NEW dir) | PASS |
| OPENDART key used for this phase only; NEVER printed/committed/logged | PASS (attempt log records an endpoint label, not the URL+key) |
| Parser `krx_status_html_inline-1.1.0` used READ-ONLY; no parser code/rule/version change | PASS |
| Re-parse results are phase-local evidence only | PASS |
| Unrecovered/unreadable rows remain zip_unparseable | PASS |
| All 42 rows fail-closed (manual_review_required=True; executable/safe/authoritative/validated/approved/strategy_ready=False) | PASS |
| source_recovery_status recorded as availability evidence ONLY (not authority) | PASS |
| NO parser design / manual adjudication / validation / approval | PASS |
| NO downstream supersession wiring / C2 / C3 / event-log / executable-status table | PASS |
| NO strategy / backtest / execution simulation / performance | PASS |
| NO production / paper / P08 / live / shadow | PASS |
| NO rcept_dt as effective date or fallback | PASS |
| New artifacts cataloged (DATA_CATALOG_NOTE.md + artifact inventory sha256) | PASS |
| Executor does NOT self-close; no CLOSE_NOTE this pass | PASS |
