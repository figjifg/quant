# Manual Link Validation Summary

Date: 2026-05-25
Phase: KR-STATUS-CORRECTION-LINKAGE-A0

## Method

Executor-side bs4 body inspection of cached document.xml ZIPs for each
manual-validation-sampled correction. Cross-check against the top-scoring
candidate original by:

- Does body text contain candidate `rcept_dt` (ISO or Korean form)?
- Does body text contain candidate `event_type` title root?
- Does body text contain date-change markers (`정정사유` / `변경사유` /
  `변경된` / `정정된` / `당초`)?
- Does body text contain cancellation markers (`취소` / `철회` / `무효`)?

## Manual validation sample size: **38**

## Period split

| period | count |
|---|---:|
| `pre_2018` | 31 |
| `post_2018` | 7 |

## Category split

| category | count |
|---|---:|
| `suspension_related` | 24 |
| `resumption_related` | 14 |

## Manual judgment distribution

| judgment | count |
|---|---:|
| `correction_linked_unambiguous` | 6 |
| `correction_linked_likely` | 10 |
| `correction_unlinked_requires_manual_review` | 14 |
| `no_original_found` | 8 |
| `cancellation_or_withdrawal` | 0 |

## Correction-changes-effective-date count: **24**

## Interpretation

- `correction_linked_unambiguous` rows = body explicitly references the
  candidate original by title root AND link_confidence = high. Safe to apply
  high-confidence supersession rules in a hypothetical downstream consumer.
- `correction_linked_likely` rows = link_confidence high or medium with one of
  the body cross-checks supporting the link. Still requires manual review
  before any downstream use.
- `correction_unlinked_requires_manual_review` = low / medium link confidence
  without body cross-check support; both correction and candidate remain
  manual_review_required.
- `no_original_found` = no candidate within the 180-day window.
- `cancellation_or_withdrawal` = body contains a cancellation marker;
  conservative downstream consumer MUST hold the prior event as manual-review
  until linkage is resolved manually.

## What this validation does NOT do

- Does NOT certify the link as authoritative for downstream strategy use.
- Does NOT extract a final corrected `effective_date` — that requires re-
  running the parser under supervised manual review.
- Does NOT make any execution / strategy / performance claim.
