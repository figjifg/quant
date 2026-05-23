# Parser-Output Acceptance Gates

Date: 2026-05-23
Scope: design-only — quantitative gates a future parser run MUST clear before C2/C3 may consume any of its rows.

## Why explicit gates

Without a gate set, C2/C3 cannot decide which parser output to trust. The S2 phase journey showed that parser_confidence alone is insufficient (max 0.667 on D3a, 0.500 on D3b, both with sample-size limitations). Acceptance must be a multi-condition contract.

## Gate set (Referee-locked design)

### Gate 1 — Field extraction threshold

For each (event_type, required_field) pair, extraction rate must meet:

| Required field per event group | Minimum extraction rate for `available_partial` | Minimum extraction rate for `available_verified` |
|---|---|---|
| Treasury group: amount_krw, shares, event_date | ≥ 60% | ≥ 90% |
| CB/BW group: amount_krw, event_date, conversion_price | ≥ 60% | ≥ 90% |
| Conversion group: shares, event_date | ≥ 60% | ≥ 90% |
| D3c group: per-form spec at the time of D3c phase opening | — | — |

Rationale: 60% is the minimum for partial usability (still requires manual audit on remaining 40%); 90% is the strategy-grade bar after manual audit.

### Gate 2 — Manual review threshold

| Use case | Maximum `manual_review_required` rate |
|---|---|
| `available_partial` | ≤ 50% |
| `available_verified` | ≤ 10% |

Rationale: above 50% manual review means most rows go to queue — parser is not adding value yet.

### Gate 3 — Correction linkage threshold

In-sample correction linkage test must pass:
- ≥ 70% of correction rows link to a valid prior original (where prior original is present in test set)
- ≥ 90% of `[기재정정]` rows surface a candidate set non-empty before linkage filter
- 0% linkage to future rows (PIT discipline)

If correction linkage fails, parser output is NOT usable for C3 reclassification (cancellation/amendment status cannot be determined).

### Gate 4 — PIT lock requirement

- `rcept_no` populated on 100% of parsed rows
- `rcept_date` populated on 100% of parsed rows
- `pit_available_at` ≤ next trading day's open (for same-day disclosure handling)
- No row uses `event_date` as PIT substitute
- No row uses any future timestamp

Failure on any of these = hard kill gate (Referee Round 4.1 lock).

### Gate 5 — Confidence calibration requirement

The `parser_confidence` field must be calibrated:
- High confidence (≥ 0.8) rows must have all required fields populated
- No row with confidence ≥ 0.8 may have empty required fields ("unsupported high confidence" kill gate)
- The calibration plot (confidence vs. manual-audit pass rate) must show monotonic improvement

This was OK across all 3 D3 rounds (no kill triggered).

### Gate 6 — Attachment-only denominator treatment

Per Referee directive (Round 4.1):
- `attachment_only_flag = True` rows are EXCLUDED from parser success-rate denominator
- They are counted SEPARATELY as `attachment_only_count` in the A0 report
- They CANNOT be silently included or silently excluded
- C2/C3 design MUST surface them with `event_source = attachment_only`

## Combined acceptance matrix

A row is classified as `available_verified` ⟺ ALL of:
- Gate 1 verified (≥ 90% extraction)
- Gate 2 verified (≤ 10% manual_review)
- Gate 3 verified (≥ 70% in-sample linkage)
- Gate 4 verified (PIT 100%)
- Gate 5 verified (confidence calibrated)
- Gate 6 verified (attachment_only separately accounted)
- `manual_audit_status` = passed

A row is classified as `available_partial` ⟺ ALL of:
- Gate 1 partial threshold met (≥ 60%)
- Gates 3, 4, 5, 6 verified
- `manual_audit_status` = not_audited

Any other state = NOT usable for C2/C3 (see input_state_taxonomy).

## Current S2-close state vs gates

| Event group | Gate 1 | Gate 2 | Gate 3 | Gate 4 | Gate 5 | Gate 6 | Verdict |
|---|---|---|---|---|---|---|---|
| Treasury (D3a) | partial (amount 36.1%, shares 13.9%, event_date 13.9%) — BELOW 60% | 100% manual review — FAIL | 11.1% in-sample (limited test) | PASS | PASS | PASS | NOT `available_partial` |
| CB/BW (D3b) | amount 23.5%, conversion_price 29.4%, event_date 0% — FAIL | 100% manual review — FAIL | partial | PASS | PASS | PASS | NOT `available_partial` |
| Conversion request | mostly ambiguous (html_inline) | FAIL | partial | PASS | PASS | PASS | NOT `available_partial` |
| All D3c types | n/a (parser not implemented) | n/a | n/a | n/a | n/a | n/a | `unsupported_form` |

→ **No event type currently reaches `available_partial`.** All require future phases to lift extraction rates and manual audit to reach the gate.

## Gate review trigger

The gate values above are LOCKED for this design phase. Future Referee verdicts may revise thresholds, but C2/C3 implementation MUST always reference an explicit Referee-approved gate version when consuming parser output.

## Hard locks

- No parser run currently passes any gate for `available_partial`+ state
- No C2/C3 implementation may proceed without an Referee-approved gate-pass verdict
- No strategy testing based on parser output that has not cleared these gates
