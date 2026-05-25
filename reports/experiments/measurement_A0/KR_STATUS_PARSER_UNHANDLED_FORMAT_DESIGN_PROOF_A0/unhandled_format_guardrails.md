# Unhandled-format design proof — guardrails (PROPOSED, future-only)

These guardrails describe what a FUTURE parser-change phase would have to
prove before any extraction is implemented. Nothing here is implemented,
approved, or applied. Every row stays fail-closed.

## relative_tbd_keep_fail_closed (n=19)
- false-positive risk: blocked_not_evaluable
- required future approval: none_keep_fail_closed
- guardrail: value is a relative/TBD expression (e.g. '…제출일 익일' = day after a future document submission); no absolute date exists to extract; a parser change cannot recover a date that is not present; keep fail-closed

## ambiguous_requires_manual_or_later_design (n=2)
- false-positive risk: high_ambiguous
- required future approval: manual_adjudication_approval_required
- guardrail: a parseable 4-digit date is present but it is the suspension timestamp (정지일시), NOT the resumption date; the resumption value is absent; this is a field-selection / value-absence issue, NOT a date format the parser fails to read; manual confirm

## out_of_scope_keep_fail_closed (n=1)
- false-positive risk: blocked_not_evaluable
- required future approval: none_keep_fail_closed
- guardrail: value is a suspension PERIOD that resolves to 상장폐지/정리매매 (delisting), not a single resumption date; no resumption date exists; out of scope; keep fail-closed

## future_parser_change_candidate_guarded (n=1)
- false-positive risk: medium_requires_additional_guard
- required future approval: parser_change_verdict_after_design_proof_review
- guardrail: 2-digit-year date format ('YY.M.D) the parser's 4-digit patterns miss; a future parser MIGHT add a strict 'YY.M.D rule, but ONLY with century disambiguation (20YY vs 19YY) and confirmation that the matched label-kind is the effective date for this event; reject if >1 distinct date or relative context
