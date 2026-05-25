# Completion Coverage Delta Summary

Date: 2026-05-25
Phase: S2-HTML-INLINE-PARSER-BODY-COVERAGE-COMPLETION-A0
Parser version: `krx_status_html_inline-1.1.0` (no feature change).

## Acquisition summary (this run)

| metric | value |
|---|---:|
| remaining target rows | 5744 |
| already_cached at start of this run | 162 |
| attempted | 5582 |
| download_success | 5579 |
| html_inline | 5579 |
| structured_xml | 0 |
| attachment_only | 0 |
| other_format | 0 |
| zip_unparseable | 3 |
| api_no_document | 0 |
| rate_limited | 0 |
| credential_or_api_error | 0 |
| retry_needed_after_retries | 0 |
| not_attempted_due_to_budget | 0 |

## Coverage delta on remaining target rows (before → after)

| state | before | after |
|---|---:|---:|
| body_unavailable | 5744 | 0 |
| body_available | 0 | 5744 |
| extracted | 0 | 5577 |
| no_label_match | 0 | 164 |
| label_no_value | 0 | 0 |
| out_of_scope_body_format | 0 | 3 |

## Coverage shift on remaining: **5744 / 5744 = 100.0%**

## By event_category

| category | extracted | no_label | label_no_value | body_unavailable |
|---|---:|---:|---:|---:|
| `suspension_related` | 5577 | 164 | 0 | 0 |
| `resumption_related` | 0 | 0 | 0 | 0 |

## By period

| period | extracted | body_unavailable |
|---|---:|---:|
| `pre_2018` | 1938 | 0 |
| `post_2018` | 3639 | 0 |

## Correction vs non-correction

| segment | extracted | body_unavailable |
|---|---:|---:|
| correction | 8 | 0 |
| non_correction | 5569 | 0 |

## period_change vs ordinary suspension

| segment | extracted | body_unavailable |
|---|---:|---:|
| `period_change` | 1107 | 0 |
| `ordinary_suspension` | 4470 | 0 |

## By prior priority bucket

| bucket | total | extracted | body_unavailable |
|---|---:|---:|---:|
| `P0_correction_high_medium` | 0 | 0 | 0 |
| `P1_resumption` | 0 | 0 | 0 |
| `P2_period_change` | 1108 | 1107 | 0 |
| `P3_ordinary_suspension` | 4636 | 4470 | 0 |
| `P4_pre2018` | 0 | 0 | 0 |
| `P5_post2018` | 0 | 0 | 0 |

## Universe-level body coverage estimate

- In-scope universe: 12,187.
- Body available before this run (estimate): 6,398 ≈ 52.5%.
- Body acquired this run: 5579.
- **Body available now (estimate): ~11977 / 12,187 = 98.3%**.

## body_unavailable remaining (preserved)

- 0 target rows remain `body_unavailable` after this phase.
- Per Referee: these rows MUST NOT be treated as parsed / executable / safe.
- They are preserved in `completion_parser_outputs.csv` with
  `parse_status = body_unavailable` and `manual_review_required = True`.
