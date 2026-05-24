# KR-EXECUTABLE-EFFECTIVE-DATE-LINKAGE-A0 — Final Summary

Date: 2026-05-25  
Predecessor: KR-EXECUTABLE-STATUS-PRE2018-EXTENSION-A0 CLOSED.

## Scope respected

- Measurement-layer effective-date linkage audit only.
- Bounded sample (no full body parser).
- No strategy testing.
- No performance diagnostics.
- No execution simulation.
- No production / paper / P08 / live / shadow.

## What was delivered

Code artifacts:
- `src/audit/measurement_a0/p_effective_date_linkage.py`

Data artifacts (gitignored):
- `data/acquired/round5_effective_date_samples/` (per-sample document.xml cache, if any)

Reports (this dir, 12 outputs):
1. `effective_date_referee_lock.md`
2. `status_event_universe_summary.md`
3. `effective_date_source_inventory.md`
4. `effective_date_sample_plan.csv`
5. `effective_date_sample_audit.csv`
6. `dart_body_sample_check.md`
7. `rcept_dt_vs_effective_date_analysis.md`
8. `correction_cancellation_effective_date_check.md`
9. `effective_date_linkage_rule_design.md`
10. `effective_date_defect_ledger.csv`
11. `effective_date_gate_status.md`
12. `effective_date_final_summary.md` (this file)

## Universe

- Combined 2010+ status events: **17924** (pre-2018: 7,150 + post-2018: 10,774).

## Sample audit headline

- Samples audited: **113** (stratified by category × period).
- Body+title extraction rate: **1.8%**.

## Body format breakdown

| format | count |
|---|---:|
| `html` | 111 |
| `unparseable` | 2 |

## rcept_dt vs effective_date relation

| relation | count |
|---|---:|
| `effective_date_unknown` | 111 |
| `effective_date_after_rcept_dt` | 1 |
| `effective_date_unparseable` | 1 |

## Defect ledger

- Total defects: **5**.
- Classes: effective_date_unextracted_majority / rcept_dt_default_forbidden /
  body_download_failures / correction_linkage_partial / html_inline_unparsed.

## Effective-date linkage gate state: **PARTIAL**

## Pass criteria evaluation

| criterion | status |
|---|---|
| Combined 2010+ status-event universe summarised | YES |
| Effective-date source options documented | YES (5 method classes + priority order) |
| Sample audit covers major event categories and periods | YES (stratified plan executed) |
| rcept_dt vs effective_date relationship measured | YES (per-sample relation classified) |
| Correction / cancellation handling assessed | YES (design rules documented) |
| Conservative future linkage rules defined | YES (rule precedence + decision matrix) |
| Defect ledger produced | YES |
| Gate status explicitly stated | YES |
| No strategy test / execution sim / performance metric produced | YES |

## Hard locks (preserved)

- No return / NAV / Sharpe / CAGR / MDD / alpha / strategy / execution sim
  / production / paper / P08 / live / shadow.
- No rcept_dt defaulted to effective date.
- No panel / OHLCV used as effective-date proof.
- No card is strategy-ready.
- No credential committed.

## Awaiting Referee

Per Referee-defined exit conditions, Referee will decide whether to:
- A. close as effective-date linkage audited,
- B. require another sample / body audit,
- C. open intraday halt source backlog,
- D. open official limit-lock source acquisition,
- E. keep all strategy research closed.
