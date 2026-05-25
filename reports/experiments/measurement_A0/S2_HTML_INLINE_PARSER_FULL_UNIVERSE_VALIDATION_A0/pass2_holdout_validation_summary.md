# Pass-2 Holdout Validation Summary

Date: 2026-05-25
Phase: S2-HTML-INLINE-PARSER-FULL-UNIVERSE-VALIDATION-A0 (Pass 2)

## Method

Pass-2 holdout = all 20 Pass-1 wrong_date period_change rows revisited
+ fresh stratified sample (≥50 ordinary suspension + ≥50 resumption +
≥30 correction + ≥30 negative-control), excluding 195 prior-sample rcepts.

## Pass-2 holdout sample size: **180**

## Bucket distribution

| bucket | count |
|---|---:|
| `ordinary_suspension` | 50 |
| `ordinary_resumption` | 50 |
| `correction_flagged` | 30 |
| `negative_control` | 30 |
| `pass1_wrong_revisit_period_change` | 20 |

## Pass-2 holdout classification distribution

| classification | count |
|---|---:|
| `exact_match` | 118 |
| `acceptable_range_match` | 1 |
| `wrong_date` | 1 |
| `missed_date` | 0 |
| `false_positive` | 0 |
| `body_unavailable` | 0 |
| `manual_review_required_correctly` | 30 |
| `out_of_scope_correctly_blocked` | 30 |
| `correction_not_forced_manual_review` | 0 |

## Period_change fix outcome (Pass-1 wrong rows revisited)

- Pass-1 wrong_date period_change rows revisited: **20**.
- Now correct (`exact_match` or `acceptable_range_match`): **19**.
- Still wrong: **1**.
- Fix rate: **95.0%**.

## Pass-2 success rate (exact + acceptable + blocked + review):

**179 / 180 = 99.4%**

## Regression check (vs Pass 1)

| metric | Pass 1 | Pass 2 |
|---|---:|---:|
| holdout sample | 184 | 180 |
| success rate | 89.1% | 99.4% |
| FP | 0 | 0 |
| wrong_date | 20 | 1 |
| missed_date | 0 | 0 |
| correction_not_forced_manual_review | 0 | 0 |
