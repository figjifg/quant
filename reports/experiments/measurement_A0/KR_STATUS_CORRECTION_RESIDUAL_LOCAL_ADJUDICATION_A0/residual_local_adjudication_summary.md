# KR-STATUS-CORRECTION-RESIDUAL-LOCAL-ADJUDICATION-A0 — Summary

Date: 2026-05-26
Opened by Referee directive REF-OPEN-003 (via relay).
Predecessor: KR-STATUS-CORRECTION-LINKAGE-FULL-UNIVERSE-VALIDATION-A0 (commits e110165 + 041fcc7).

## Purpose

Package the 166 in-scope correction rows into a row-level residual-ACTION ledger + manual-review packet, mapped back to the accepted 5-tier confidence. Local only — NO downloads, NO body repair, NO recovery.

## Accepted 5-tier confidence (control — matches prior exactly)

| confidence | count |
|---|---:|
| `high_validated` | 17 |
| `medium_needs_manual` | 52 |
| `low_needs_manual` | 7 |
| `no_link` | 73 |
| `rejected_wrong_candidate` | 17 |
| **total** | **166** |

## Residual action classes (sum to 166)

| residual_action_class | count |
|---|---:|
| `body_confirms_candidate_but_below_high` | 40 |
| `zip_unparseable_requires_source_recovery` | 39 |
| `no_link_original_not_found` | 37 |
| `accepted_high_validated_design_only` | 17 |
| `rejected_wrong_candidate_quarantined` | 17 |
| `no_link_insufficient_evidence` | 15 |
| `no_link_cross_category_blocked` | 1 |
| **total** | **166** |

## Confidence → action mapping (cross-tab)

| confidence_5tier | residual_action_class | count |
|---|---|---:|
| `high_validated` | `accepted_high_validated_design_only` | 17 |
| `low_needs_manual` | `zip_unparseable_requires_source_recovery` | 7 |
| `medium_needs_manual` | `body_confirms_candidate_but_below_high` | 40 |
| `medium_needs_manual` | `zip_unparseable_requires_source_recovery` | 12 |
| `no_link` | `no_link_cross_category_blocked` | 1 |
| `no_link` | `no_link_insufficient_evidence` | 15 |
| `no_link` | `no_link_original_not_found` | 37 |
| `no_link` | `zip_unparseable_requires_source_recovery` | 20 |
| `rejected_wrong_candidate` | `rejected_wrong_candidate_quarantined` | 17 |

## Hard locks

- Local artifacts only; no downloads / API / body repair / parser expansion.
- All 166 remain manual_review_required; none authoritative / executable /
  strategy-ready. rejected quarantined; high_validated design-only.
- Supersession NOT wired. No C2/C3 / execution / strategy / production.
