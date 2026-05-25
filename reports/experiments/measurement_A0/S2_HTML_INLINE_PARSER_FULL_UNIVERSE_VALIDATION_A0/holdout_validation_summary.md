# Holdout Validation Summary

Date: 2026-05-25
Phase: S2-HTML-INLINE-PARSER-FULL-UNIVERSE-VALIDATION-A0

## Method

Stratified holdout sample drawn from full-universe parser output.
Excludes rows used in prior 195-sample manual audit and 195-row parser
validation sample. For sampled rows lacking cached body, bodies are
downloaded on-demand from OPENDART (capped budget). Each row receives a
holdout classification per Referee taxonomy.

## Holdout sample size: **184**

## Bucket distribution

| bucket | count |
|---|---:|
| `suspension_related_extracted` | 50 |
| `resumption_related_extracted` | 50 |
| `no_label_or_label_no_value` | 30 |
| `negative_control` | 30 |
| `correction_flagged` | 24 |

## Holdout classification distribution

| classification | count |
|---|---:|
| `exact_match` | 80 |
| `acceptable_range_match` | 0 |
| `wrong_date` | 20 |
| `missed_date` | 0 |
| `false_positive` | 0 |
| `body_unavailable` | 0 |
| `manual_review_required_correctly` | 54 |
| `out_of_scope_correctly_blocked` | 30 |
| `correction_not_forced_manual_review` | 0 |

## Success rate (exact_match + acceptable_range + blocked + review): **164 / 184 = 89.1%**
## False-positive count on negative controls: **0**
## Wrong-date / missed-date count: **20**
## Correction-not-forced-manual-review (must be 0 for pass): **0**
## Body unavailable in sample: **0**

## Comparison vs prior parser-reopen validation

| metric | prior (108 samples) | this holdout |
|---|---:|---:|
| sample size | 108 | 184 |
| extracted/correct outcome | ~92% (overall exact match) | 89.1% success rate |
| false positives on neg controls | 0 | 0 |

## Interpretation

- Holdout sample uses different sampling buckets than the original parser
  validation. `success rate` here aggregates exact_match + acceptable_range +
  correctly-blocked-out-of-scope + correctly-forced-manual-review.
- A non-zero `false_positive` count would indicate negative-control gate leakage.
- A non-zero `correction_not_forced_manual_review` would indicate parser
  correction-handling failure at scale.
