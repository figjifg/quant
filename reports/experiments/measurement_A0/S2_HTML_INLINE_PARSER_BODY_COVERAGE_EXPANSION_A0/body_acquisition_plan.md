# Body Acquisition Plan

Date: 2026-05-25
Phase: S2-HTML-INLINE-PARSER-BODY-COVERAGE-EXPANSION-A0

## Target body_unavailable rows: **10744**

## Priority buckets

| bucket | count |
|---|---:|
| `P0_correction_high_medium` | 3 |
| `P1_resumption` | 3404 |
| `P2_period_change` | 2701 |
| `P3_ordinary_suspension` | 4636 |
| `P4_pre2018` | 0 |
| `P5_post2018` | 0 |

## Acquisition order (Referee-mandated)

1. **P0** — correction-flagged rows with Pass-3 `high_validated` or
   `medium_needs_manual` confidence. Highest priority because they may
   become design-supported authoritative-use evidence under the closed
   correction policy.
2. **P1** — resumption_related body_unavailable rows. Lower-volume but
   load-bearing for the resumption_date field.
3. **P2** — period_change_disclosure suspension body_unavailable rows.
   Verified by Pass-2 parser fix; broader coverage validates the fix at scale.
4. **P3** — ordinary suspension_related body_unavailable rows.
5. **P4** — older pre-2018 body_unavailable rows.
6. **P5** — post-2018 body_unavailable rows.

Acquisition stops at `DOWNLOAD_BUDGET` and reports partial.

## Download budget (this run): **5000**
## Throttle: **0.12 s** between requests (~8 req/s nominal).
## Max retries on transient error: **1**.

## What this plan does NOT do

- Does NOT silently exclude any row. Rows beyond the budget receive an
  explicit `not_attempted_in_this_run` log entry.
- Does NOT request bodies for out-of-scope categories.
- Does NOT request bodies for already-cached rows.
- Does NOT commit credentials. OPENDART_API_KEY is loaded from
  `research_input_data/.env` at runtime and never written to repo files.
