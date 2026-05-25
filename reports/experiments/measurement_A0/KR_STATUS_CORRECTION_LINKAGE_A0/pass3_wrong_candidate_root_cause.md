# Pass-3 Wrong-Candidate Root-Cause Audit

Date: 2026-05-25
Phase: KR-STATUS-CORRECTION-LINKAGE-A0 (Pass 3)

## Wrong-candidate cases in Pass-2 manual sample: **12**

## Root-cause distribution (a row may have multiple reasons)

| reason | count |
|---|---:|
| `title_root_absent_in_body` | 12 |
| `candidate_date_absent_in_body` | 12 |
| `long_window_false_match` | 4 |
| `cross_category_false_match` | 2 |

## Per-row detail

See `pass3_wrong_candidate_root_cause_detail.csv` (next to this file)
for the 12-row CSV with correction_rcept_no, candidate_rcept_no, score,
title_similarity, body_format, and the parsed root_cause tokens.

## Pass-3 mitigations

- `cross_category_false_match` → cross-category candidates carry an
  additional -0.5 Pass-3 penalty on top of Pass-2's -1.5; capped at
  `medium_needs_manual` even when body-confirmed.
- `raw_pool_false_match` → raw-pool-only candidates without `same_base_form`
  carry an additional -1.0 penalty.
- `long_window_false_match` → candidates with `days_prior > 365` carry an
  additional -1.0 penalty.
- `weak_title_similarity` → `high_validated` requires `title_similarity ≥ 0.60`.
- `title_root_absent_in_body` / `candidate_date_absent_in_body` → body
  cross-check is now a hard requirement for `high_validated`. Failed
  cross-check downgrades to `rejected_wrong_candidate` when score was high.
