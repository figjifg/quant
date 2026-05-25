# KR-STATUS-PARSER-UNHANDLED-FORMAT-DESIGN-PROOF-A0 — Initial-Pass Report

Read-only, proof-only design analysis of the 23 `label_present_but_value_in_unhandled_format` rows (prior feasibility theme `date_format_or_relative_date_handling`). No parser change; no downloads; every row stays fail-closed.

- target rows: **23** (all label_no_value / parser_design_candidate / parser_change_verdict; all html_inline, all locally available, all resumption-related, 0 corrections).

## Value pattern class (sum = 23)

| value_pattern_class | count |
|---|---:|
| relative_or_tbd_marker | 19 |
| other_ambiguous | 2 |
| date_range_or_period_text | 1 |
| absolute_date_unhandled_format | 1 |

## Design-proof bucket (sum = 23)

| design_proof_bucket | count |
|---|---:|
| relative_tbd_keep_fail_closed | 19 |
| ambiguous_requires_manual_or_later_design | 2 |
| out_of_scope_keep_fail_closed | 1 |
| future_parser_change_candidate_guarded | 1 |

## False-positive risk (sum = 23)

| false_positive_risk | count |
|---|---:|
| blocked_not_evaluable | 20 |
| high_ambiguous | 2 |
| medium_requires_additional_guard | 1 |

## Required future approval (sum = 23)

| required_future_approval | count |
|---|---:|
| none_keep_fail_closed | 20 |
| manual_adjudication_approval_required | 2 |
| parser_change_verdict_after_design_proof_review | 1 |

## Honest headline finding

"Unhandled format" OVERSTATED the parser-design opportunity for these 23 rows.
Only the genuine 2-digit-year-format rows are a date-FORMAT matter, and only one row is a clean (guarded) future parser-change candidate:

- **relative / TBD (the bulk):** the resumption date is defined relative to a future event (e.g. '…제출일 익일' = the day AFTER a future document submission) or is a deadline ('1년 이내 … 限'). No absolute date exists; a parser change cannot recover a date that is not present. Keep fail-closed.
- **absolute date in 2-digit-year format ('YY.M.D):** a real date the parser's 4-digit patterns miss. A future parser MIGHT add a strict rule, but only with century disambiguation and label-kind confirmation — guarded, not approved.
- **date range / period to delisting (…~상장폐지):** a suspension PERIOD that resolves to delisting, not a resumption date. Out of scope; keep fail-closed.
- **parseable date present but NON-target field:** a full 4-digit date IS present but it is the suspension timestamp (정지일시); the resumption value is genuinely absent. This is a field-selection / value-absence issue, NOT a date the parser fails to read — correcting the prior taxonomy's 'date-like fragment not parser-recognized' framing for these rows. Manual.

All evidence is hypothetical / proof-only. No effective date is accepted; no parser change is made; all 23 rows remain fail-closed. This phase does NOT self-close.
