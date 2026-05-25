# KR-STATUS-CORRECTION-LINKAGE-A0 — Referee Lock

Date: 2026-05-25  
Verdict source: Referee verdict opening this phase, 2026-05-25.  
Predecessor: `S2-HTML-INLINE-PARSER-REOPEN-PHASE` CLOSED AS
HTML-INLINE-PARSER-VALIDATED FOR SUSPENSION / RESUMPTION ONLY / EXECUTION STILL
CLOSED (commit `03a2dc9`).

## Scope (Referee-fixed)

- Measurement-layer correction-linkage A0 only.
- Build and audit correction-linkage logic for OPENDART/KRX exchange-status
  disclosures.
- Initial scope limited to:
  - `suspension_related`,
  - `resumption_related`,
  - HTML-inline status disclosures,
  - correction-flagged rows and their original reports,
  - parser outputs from `S2-HTML-INLINE-PARSER-REOPEN-PHASE`.
- No delisting parser.
- No liquidation parser.
- No managed / alert parser.
- No DART body alpha.
- No overhang parser.
- No all-event event log finalization.
- No C2/C3 wiring.
- No strategy testing.
- No performance diagnostics.
- No execution simulation.
- No production / paper / P08 / live / shadow.

## Executor note on "manual"

The executor is an LLM. "Manual validation" here means **per-sample human-style
review using tooling that supports text extraction from HTML-inline documents**
(BeautifulSoup + Korean-label search), as previously accepted in
`KR-STATUS-EFFECTIVE-DATE-MANUAL-AUDIT-PHASE`. Cross-referencing prior reports is
done via deterministic candidate-search + bs4 body inspection, not by a human
reviewer.

## Allowed tasks (10)

1. Correction-flagged universe construction.
2. Base-form normalization.
3. Series-marker extraction.
4. Candidate original-report search (default 180-day window + 30/90/365 sensitivity).
5. Link scoring (transparent components, link_confidence enum).
6. Manual validation sample (≥ correction-flagged rows from parser-validation
   sample + at least 30 additional suspension / resumption correction rows; pre +
   post 2018).
7. Supersession rule design (design-only).
8. Parser interaction check (does the parser preserve correction_flag and force
   manual review?).
9. Defect ledger (12 enumerated defect classes).
10. Gate status update.

## Required outputs (12)

1. `correction_linkage_referee_lock.md` (this file)
2. `correction_universe_summary.md`
3. `base_form_normalization_rules.md`
4. `correction_candidate_links.csv`
5. `link_scoring_design.md`
6. `manual_link_validation_sample.csv`
7. `manual_link_validation_summary.md`
8. `supersession_rule_design.md`
9. `parser_correction_interaction_check.md`
10. `correction_linkage_defect_ledger.csv`
11. `correction_linkage_gate_status.md`
12. `correction_linkage_final_summary.md`

## Correction-linkage gate enum (Referee-permitted)

- `DATA_SOURCE_FAIL`
- `PARTIAL`
- `CORRECTION_LINKAGE_DESIGNED_BUT_NOT_VALIDATED`
- `CORRECTION_LINKAGE_VALIDATED_FOR_SAMPLE_ONLY`
- `CORRECTION_LINKAGE_REQUIRES_MORE_WORK`
- `READY_FOR_NEXT_A0_REVIEW`

## Pass-criteria

- Correction-flagged universe summarised.
- Base-form normalization documented.
- Candidate original links generated.
- Link scoring design explicit.
- Manual validation sample completed.
- Supersession rules documented (design-only).
- Parser correction interaction checked.
- Defect ledger produced.
- Gate status explicitly stated.
- No strategy test / execution sim / performance metric produced.

## Fail / partial gates

- Corrections cannot be linked reliably → PARTIAL or REQUIRES_MORE_WORK.
- Multiple original candidates common → REQUIRES_MORE_WORK.
- Correction changes effective date and original cannot be superseded safely →
  REQUIRES_MORE_WORK.
- Parser output from correction rows treated as authoritative → FAIL.
- `rcept_dt` used as `effective_date` fallback → FAIL.
- Any strategy metric produced → protocol violation.

## Allowed code artifacts

- Small linkage / scoring script under `src/audit/measurement_a0/`.
- Small helper functions for report_nm normalization if needed.
- NO strategy code. NO performance code. NO execution simulation wiring.
- NO C2/C3 wiring. NO production / paper / P08 / live code modification.

## Hard prohibitions

(Standard hard locks. See `docs/next_actions.md`.)

## Important boundary

- Correction-linkage A0.
- Passing this phase does NOT reopen strategy testing.
- Passing this phase does NOT open execution simulation automatically.
- Passing this phase does NOT complete S2 globally.
- Passing this phase only clarifies whether correction-flagged suspension /
  resumption status disclosures can be linked to originals.

## End condition

- Return correction-linkage A0 report only.
- Referee will decide whether to:
  - A. close as correction linkage validated for sample,
  - B. require another correction-linkage pass,
  - C. open full-universe parser validation,
  - D. open delisting / liquidation manual expansion,
  - E. keep all strategy research closed.
