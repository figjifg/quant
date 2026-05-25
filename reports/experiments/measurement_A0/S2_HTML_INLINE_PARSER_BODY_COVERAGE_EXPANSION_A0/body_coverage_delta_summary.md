# Body Coverage Delta Summary

Date: 2026-05-25
Phase: S2-HTML-INLINE-PARSER-BODY-COVERAGE-EXPANSION-A0
Parser version: `krx_status_html_inline-1.1.0`.

## Acquisition summary

| metric | value |
|---|---:|
| target body_unavailable rows | 10744 |
| already_cached at start | 0 |
| attempted | 5000 |
| download_success | 4996 |
| html_inline | 4996 |
| structured_xml | 0 |
| attachment_only | 0 |
| other_format | 0 |
| zip_unparseable | 4 |
| api_no_document | 0 |
| rate_limited | 0 |
| credential_or_api_error | 0 |
| retry_needed_after_retries | 0 |
| not_attempted (budget) | 5744 |

## Coverage delta on target rows (before → after)

| state | before | after |
|---|---:|---:|
| body_unavailable | 10744 | 5744 |
| body_available | 0 | 5000 |
| extracted | 0 | 4526 |
| no_label_match | 0 | 296 |
| label_no_value | 0 | 174 |
| out_of_scope_body_format | 0 | 4 |

## Coverage shift: **5000 / 10744 = 46.5%** of body_unavailable targets now have a body.

## By event_category (post parser_status)

| category | extracted | no_label_match | label_no_value | body_unavailable |
|---|---:|---:|---:|---:|
| `suspension_related` | 1593 | 0 | 0 | 5744 |
| `resumption_related` | 2933 | 296 | 174 | 0 |

## By period

| period | extracted | body_unavailable |
|---|---:|---:|
| `pre_2018` | 2448 | 1988 |
| `post_2018` | 2078 | 3756 |

## Correction vs non-correction

| segment | extracted | body_unavailable |
|---|---:|---:|
| correction | 4 | 11 |
| non_correction | 4522 | 5733 |

## By priority bucket

| bucket | total | extracted | body_unavailable |
|---|---:|---:|---:|
| `P0_correction_high_medium` | 3 | 3 | 0 |
| `P1_resumption` | 3404 | 2933 | 0 |
| `P2_period_change` | 2701 | 1590 | 1108 |
| `P3_ordinary_suspension` | 4636 | 0 | 4636 |
| `P4_pre2018` | 0 | 0 | 0 |
| `P5_post2018` | 0 | 0 | 0 |

## Universe-level coverage estimate

- In-scope universe: 12,187 (from prior phase).
- Body available before this phase: ~1,402 (cached) + 41 (other formats).
- Body acquired this phase: 4996.
- **Body available now (estimate): ~6398 / 12,187 = 52.5%**.

## body_unavailable preserved

- 5744 target rows remain `body_unavailable` after this phase.
- Per Referee: these rows MUST NOT be treated as parsed / executable / safe.
- They are preserved in `post_acquisition_parser_outputs.csv` with
  `parse_status = body_unavailable` and `manual_review_required = True`.
