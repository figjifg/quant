# Completion Validation Summary

Date: 2026-05-25
Phase: S2-HTML-INLINE-PARSER-BODY-COVERAGE-COMPLETION-A0
Parser version: `krx_status_html_inline-1.1.0` (used as-is).

## Method

Sample drawn from rows extracted against newly-acquired completion bodies.
Body cross-checks classify each row per Referee taxonomy.

## Holdout sample size: **88**

## Bucket distribution

| bucket | count |
|---|---:|
| `ordinary_suspension` | 50 |
| `period_change_disclosure` | 30 |
| `correction_flagged` | 8 |

## Classification distribution

| classification | count |
|---|---:|
| `exact_match` | 80 |
| `acceptable_range_match` | 0 |
| `wrong_date` | 0 |
| `missed_date` | 0 |
| `false_positive` | 0 |
| `body_unavailable` | 0 |
| `unparseable` | 0 |
| `manual_review_required_correctly` | 8 |
| `correction_not_forced_manual_review` | 0 |

## Success rate (exact + acceptable + review): **88 / 88 = 100.0%**
## Wrong+missed: **0**
## False positives: **0**
## Correction not forced manual review (must be 0): **0**

## Comparison vs Expansion-phase holdout

| metric | Expansion (84 rows) | Completion (88 rows) |
|---|---:|---:|
| success rate | 100.0% | 100.0% |
| FP | 0 | 0 |
| wrong+missed | 0 | 0 |
| correction_not_forced | 0 | 0 |
