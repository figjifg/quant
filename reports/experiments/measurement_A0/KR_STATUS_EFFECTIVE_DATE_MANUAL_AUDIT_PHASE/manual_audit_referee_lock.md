# KR-STATUS-EFFECTIVE-DATE-MANUAL-AUDIT-PHASE — Referee Lock

Date: 2026-05-25  
Verdict source: Referee verdict opening this phase, 2026-05-25.  
Predecessor: KR-EXECUTABLE-EFFECTIVE-DATE-LINKAGE-A0 CLOSED (commit `0ab7b96`).

## Scope (Referee-fixed)

- Measurement-layer manual audit only.
- Manually inspect sampled OPENDART/KRX exchange-status disclosures.
- Focus: suspension / resumption / delisting / liquidation / managed / alert /
  overheated.
- No full parser build.
- No S2 parser reopen.
- No strategy testing / performance / execution sim / production / paper / P08 /
  live / shadow.

## Executor note on "manual"

The executor is an LLM. "Manual" inspection here means **per-sample human-style
review using tooling that supports text extraction from HTML-inline documents**
(BeautifulSoup + Korean-label search). This is broader than the prior simple-regex
approach but stops short of a production parser build.

## Sample plan (minima per Referee)

- ≥ 40 suspension_related
- ≥ 40 resumption_related
- ≥ 40 delisting
- all liquidation (sparse: 3 in dataset)
- ≥ 30 managed / investment_alert / short_term_overheated combined
- ≥ 20 correction-flagged rows
- both pre-2018 and post-2018
- ≥ 20 rows that failed extraction in prior A0
- include the 2 positive controls from prior A0
- target total: 150-200 disclosures

## Allowed tasks (10)

1. Manual audit sample construction.
2. Manual document inspection (body format + Korean date label search).
3. Effective-date field classification (10+ label categories).
4. rcept_dt relationship classification.
5. Correction / cancellation manual review.
6. Label inventory.
7. Parser feasibility assessment (decision input only; no parser build).
8. Manual-audit reliability tracking (reviewer_confidence + reason for low).
9. Defect & blocker update.
10. Gate status update.

## Required outputs (12)

1. `manual_audit_referee_lock.md` (this file)
2. `manual_sample_plan.csv`
3. `manual_effective_date_audit.csv`
4. `manual_body_format_summary.md`
5. `manual_rcept_dt_relation_summary.md`
6. `correction_manual_review.md`
7. `effective_date_label_inventory.csv`
8. `parser_feasibility_assessment.md`
9. `manual_audit_reliability.md`
10. `effective_date_blocker_update.csv`
11. `manual_audit_gate_status.md`
12. `manual_audit_final_summary.md`

## Gate enum (Referee-permitted)

- `DATA_SOURCE_FAIL`
- `PARTIAL`
- `MANUAL_AUDIT_COMPLETED_BUT_NOT_GENERALIZED`
- `MANUAL_AUDIT_SUPPORTS_PARSER_REOPEN`
- `MANUAL_AUDIT_SUPPORTS_MANUAL_ONLY_PATH`
- `READY_FOR_NEXT_A0_REVIEW`

## Pass criteria

- Sample plan documented, major categories covered, pre+post represented.
- Effective-date evidence manually classified.
- rcept_dt relation measured manually.
- Correction / cancellation samples reviewed.
- Label inventory produced.
- Parser feasibility assessed.
- Defect / blocker update produced.
- Gate status explicitly stated.
- No strategy test / execution sim / performance metric produced.

## Fail / partial gates

- Insufficient document access → PARTIAL.
- Effective-date mostly unavailable → PARTIAL.
- Correction linkage cannot be resolved manually → PARTIAL.
- Inconsistent labels → parser_feasible_with_custom_rules or manual_review_required.
- rcept_dt used as effective_date by default → FAIL.
- Panel / OHLCV used as effective_date proof → FAIL.
- Any strategy metric produced → protocol violation.

## Hard prohibitions

(Standard hard locks, unchanged. See `docs/next_actions.md`.)

## Important boundary

- Manual evidence gathering only.
- Passing this phase does NOT reopen strategy testing.
- Passing this phase does NOT open execution simulation.
- Passing this phase does NOT reopen S2 parser automatically.
- Only informs whether parser-reopen or manual-only is the better next step.

## End condition

- Return manual effective-date audit report only.
- Referee will decide whether to:
  - A. close as manual audit completed,
  - B. require more manual samples,
  - C. open S2 HTML-inline parser reopen phase,
  - D. keep manual-only effective-date path,
  - E. keep all strategy research closed.
