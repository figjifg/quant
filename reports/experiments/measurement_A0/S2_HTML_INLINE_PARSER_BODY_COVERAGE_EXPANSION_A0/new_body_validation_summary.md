# New-Body Validation Summary

Date: 2026-05-25
Phase: S2-HTML-INLINE-PARSER-BODY-COVERAGE-EXPANSION-A0
Parser version: `krx_status_html_inline-1.1.0`.

## Method

Sample is drawn ONLY from rows where the parser produced `extracted`
status against newly-acquired bodies (this phase). Body cross-checks via
BeautifulSoup are used to classify each row per Referee taxonomy.

## Holdout sample size: **84**

## Bucket distribution

| bucket | count |
|---|---:|
| `ordinary_resumption` | 50 |
| `period_change_disclosure` | 30 |
| `ordinary_suspension` | 3 |
| `correction_flagged` | 1 |

## Classification distribution

| classification | count |
|---|---:|
| `exact_match` | 82 |
| `acceptable_range_match` | 1 |
| `wrong_date` | 0 |
| `missed_date` | 0 |
| `false_positive` | 0 |
| `body_unavailable` | 0 |
| `unparseable` | 0 |
| `manual_review_required_correctly` | 1 |
| `correction_not_forced_manual_review` | 0 |

## Success rate (exact + acceptable + review): **84 / 84 = 100.0%**
## Wrong+missed: **0**
## False positives: **0**
## Correction not forced manual review (must be 0): **0**

## Interpretation

- The holdout is drawn from NEWLY acquired bodies that prior phases never
  saw. Stability of parser behavior on these rows indicates the parser
  generalises beyond the prior cache.
- A non-zero `correction_not_forced_manual_review` would indicate parser
  regression. (Expected: 0.)
- A non-zero `false_positive` would indicate negative-control leakage on
  bodies that should be out-of-scope.
