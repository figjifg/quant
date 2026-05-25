# Pass-3 Manual Validation Summary

Date: 2026-05-25
Phase: KR-STATUS-CORRECTION-LINKAGE-A0 (Pass 3)

## Method

Focused validation sample combining:
- all Pass-2 wrong-candidate rows (revisited under Pass-3 rules),
- new high_validated / medium_needs_manual candidates after stricter scoring,
- remaining Pass-2 no_link rows (revisited),
- raw-pool-only candidates,
- long-window candidates,
- pre-2018 + post-2018 represented.

Body inspection: cached document.xml ZIPs + on-demand fetch via OPENDART.

## Pass-3 manual sample size: **72**
## Eligible (n − no_original − rejected_wrong_candidate): **32**
## Pass-3 linked total (linked_unambiguous + linked_likely): **25**
## Pass-3 sample link rate: **78.1%**
## Pass-3 rejected_wrong_candidate count: **10**
## Pass-3 date-change marker bodies: **59**

## Pass-3 manual judgment distribution

| judgment | count |
|---|---:|
| `linked_unambiguous` | 9 |
| `linked_likely` | 16 |
| `rejected_wrong_candidate` | 10 |
| `multiple_candidates_unresolved` | 0 |
| `manual_review_required` | 7 |
| `no_original_found` | 30 |
| `source_absent` | 0 |

## Comparison vs Pass 2

| metric | Pass 2 | Pass 3 |
|---|---:|---:|
| sample size | 80 | 72 |
| linked total | 43 | 25 |
| eligible | 78 | 32 |
| sample link rate | 55.1% | 78.1% |
| rejected_wrong_candidate | (12 risk) | 10 |

## Notes

- Pass-3 explicitly demoted score-passing-but-body-unsupported rows to
  `rejected_wrong_candidate`. This shrinks the linked pool but reduces the
  effective false-positive risk for `high_validated`.
- A row may move from `linked_likely` (Pass 2) to `rejected_wrong_candidate`
  (Pass 3) if its body cross-check failed; this is intentional.
- `linked_unambiguous` rows must have body-confirmed title or date.
