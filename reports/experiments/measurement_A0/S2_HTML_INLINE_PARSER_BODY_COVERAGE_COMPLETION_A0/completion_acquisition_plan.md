# Completion Acquisition Plan

Date: 2026-05-25
Phase: S2-HTML-INLINE-PARSER-BODY-COVERAGE-COMPLETION-A0

## Remaining body_unavailable rows (prior not_attempted): **5744**
## Already cached now (skip): **162**
## To attempt this run: **5582**
## Download budget cap (this run): **6000**
## Throttle: **0.12 s** between requests (~8 req/s nominal).
## Max retries: **1**.

## Priority bucket distribution (from prior phase)

| bucket | count |
|---|---:|
| `P0_correction_high_medium` | 0 |
| `P1_resumption` | 0 |
| `P2_period_change` | 1108 |
| `P3_ordinary_suspension` | 4636 |
| `P4_pre2018` | 0 |
| `P5_post2018` | 0 |

## Acquisition order

Same priority order as expansion phase: P0 → P1 → P2 → P3 → P4 → P5.
If budget is large enough to cover everything, all rows are attempted.

## Terminal status taxonomy (every row receives one)

- `already_cached` — body present from prior expansion or other phase.
- `success` (with body_format ∈ html_inline / structured_xml / attachment_only / other) — new download succeeded.
- `api_no_document` — OPENDART returned <status>013 (no document).
- `zip_unparseable` — downloaded data not a valid ZIP.
- `rate_limited` — HTTP 429.
- `credential_or_api_error` — HTTP 401/403.
- `retry_needed` — transient error after retry budget exhausted.
- `not_attempted_due_to_budget` — beyond COMPLETION_BUDGET.
