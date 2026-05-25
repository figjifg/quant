# Pass-2 Manual Validation Summary

Date: 2026-05-25
Phase: KR-STATUS-CORRECTION-LINKAGE-A0 (Pass 2)

## Method

Executor-side BeautifulSoup body inspection of cached document.xml ZIPs.
For missing bodies, fetch on-demand via OPENDART document.xml.
Body cross-checks: candidate `rcept_dt` presence (ISO or Korean form),
candidate `event_type` title-root presence, date-change markers
(`정정사유` / `변경사유` / `변경된` / `정정된` / `당초`),
cancellation markers (`취소` / `철회` / `무효`).
Wrong-candidate risk: link_conf ∈ {high, medium}, html_inline body retrieved,
neither title-root nor candidate date present in body.

## Pass-2 manual sample size: **80**
## Cross-category candidates in sample: **7**
## Date-change markers present: **61**
## Wrong-candidate risk flagged: **12**

## Pass-2 manual judgment distribution

| judgment | count |
|---|---:|
| `linked_unambiguous` | 17 |
| `linked_likely` | 26 |
| `multiple_candidates_unresolved` | 3 |
| `correction_unlinked_requires_manual_review` | 32 |
| `original_outside_filtered_status_pool` | 0 |
| `no_original_found` | 2 |
| `linked_wrong_candidate` | 0 |

## Eligible sample (n − no_original_found): **78**
## Pass-2 sample link rate (linked_unambiguous + linked_likely): **43 / 78 = 55.1%**

## Comparison vs Pass 1

| metric | Pass 1 | Pass 2 |
|---|---:|---:|
| sample size | 38 | 80 |
| linked total | 16 | 43 |
| eligible | 30 | 78 |
| sample link rate | 53.3% | 55.1% |

## What this validation does NOT do

- Does NOT certify any link as authoritative.
- Does NOT extract a final corrected `effective_date`.
- Does NOT make any strategy / execution / performance claim.
