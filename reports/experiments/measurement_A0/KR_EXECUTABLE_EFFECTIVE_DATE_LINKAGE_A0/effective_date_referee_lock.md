# KR-EXECUTABLE-EFFECTIVE-DATE-LINKAGE-A0 — Referee Lock

Date: 2026-05-25  
Verdict source: Referee verdict opening this phase, 2026-05-25.  
Predecessor: KR-EXECUTABLE-STATUS-PRE2018-EXTENSION-A0 CLOSED (commit `03d5d25`).

## Scope (Referee-fixed)

- Measurement-layer effective-date linkage audit only.
- Link or evaluate whether OPENDART/KRX exchange-status `rcept_dt` can be mapped to
  actual effective status dates.
- Focus on suspension, resumption, delisting transition, liquidation / 정리매매,
  managed / alert status where available.
- No strategy testing.
- No performance diagnostics.
- No execution simulation.
- No production / paper / P08 / live readiness / shadow.

## Reason

- rcept_dt is filing date, not necessarily the effective trading-status date.
- New hard lock from KR-EXECUTABLE-STATUS-PRE2018-EXTENSION-A0 close: no rcept_dt
  treated as effective status date without a separate effective-date linkage audit.

## Allowed tasks (9)

1. Event universe construction (combine pre-2018 + 2018+ events; 17,924 total).
2. Effective-date source inventory.
3. Sample-based effective-date audit (bounded, no full parser).
4. DART body / document check on sampled events only.
5. rcept_dt vs effective_date comparison.
6. Correction / cancellation handling.
7. Build effective-date linkage rules (design only).
8. Build defect ledger.
9. Gate status update.

## Sample plan (per Referee minimums)

- ≥ 30 suspension_related
- ≥ 30 resumption_related
- ≥ 30 delisting
- all liquidation samples (small count)
- ≥ 20 managed / investment_alert / short_term_overheated combined
- include both pre-2018 and 2018+ events

## Required outputs (12)

1. `effective_date_referee_lock.md` (this file)
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
12. `effective_date_final_summary.md`

## Gate enum (Referee-permitted)

- `DATA_SOURCE_FAIL`
- `PARTIAL`
- `EFFECTIVE_DATE_SAMPLE_AUDITED_BUT_NOT_GENERALIZED`
- `EFFECTIVE_DATE_LINKAGE_RULES_DEFINED_BUT_EXECUTION_STILL_CLOSED`
- `READY_FOR_NEXT_A0_REVIEW`

## Pass criteria

- Combined 2010+ status-event universe summarised.
- Effective-date source options documented.
- Sample audit covers major event categories and both pre-2018 / 2018+ periods.
- rcept_dt vs effective_date relationship measured on sample.
- Correction / cancellation handling assessed.
- Conservative future linkage rules defined.
- Defect ledger produced.
- Gate status explicitly stated.
- No strategy test / execution sim / performance metric produced.

## Fail / partial gates

- If effective date cannot be extracted from sample, mark PARTIAL.
- If body/document access fails broadly, mark PARTIAL and record S2 dependency.
- If rcept_dt is used as effective date by default, FAIL.
- If panel / OHLCV date used as effective-date proof, FAIL.
- If cancellation / correction ignored, FAIL.
- If any strategy metric produced, protocol violation.

## Hard prohibitions

- No return backtest.
- No NAV / CAGR / Sharpe / hit rate / alpha / excess return / MDD.
- No post-event drift / migration return / turnover return / resume return / reversal
  return / flow-return.
- No raw jump alpha.
- No price-only mean reversion.
- No generic value / quality / momentum / RS ranking.
- No DART body alpha test.
- No overhang filter alpha test.
- No flow strategy testing.
- No execution simulation.
- No executable assumption from panel presence.
- No survivorship-safe claim unless explicitly supported.
- No unknown status treated as executable.
- No panel absence treated as non-tradable.
- No OHLCV signature treated as suspension proof.
- No rule-derived limit candidate treated as official lock evidence.
- No rcept_dt treated as effective status date without audit.
- No production / paper / P08 / live readiness / shadow connection.
- No card may be described as strategy-ready.

## Important boundary

- Effective-date linkage A0.
- Passing this phase does NOT reopen strategy testing.
- Passing this phase does NOT open execution simulation automatically.
- Only clarifies whether status event filing dates can be mapped to effective dates.
- Execution-simulation readiness still requires separate Referee review.

## End condition

- Return effective-date linkage A0 report only.
- Do not recommend strategy testing.
- Do not recommend production or paper tracking.
- Referee will decide whether to:
  - A. close as effective-date linkage audited,
  - B. require another sample / body audit,
  - C. open intraday halt source backlog,
  - D. open official limit-lock source acquisition,
  - E. keep all strategy research closed.
