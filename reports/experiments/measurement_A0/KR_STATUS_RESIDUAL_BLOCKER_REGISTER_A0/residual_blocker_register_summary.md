# KR-STATUS-RESIDUAL-BLOCKER-REGISTER-A0 — Summary

Date: 2026-05-26
Opened by Referee directive REF-OPEN-004 (via relay).
Consolidates residual blockers from the recently-closed measurement-layer phases.

## Unique register rows (keyed by rcept_no): **862**

Register = (universe rows: 42 zip_unparseable + 511 no_label_match + 200 label_no_value = 753) ∪ (166 correction rows). The 109 parser-`extracted` correction rows are added because corrections are manual_review_required regardless of parse outcome; the other 57 corrections (39 zip + 11 no_label_match + 7 label_no_value) already fall inside the 753.
  → 862 = 753 + 109.

## Blocker tag counts (multi-label; do NOT sum to register size)

| blocker_tag | count |
|---|---:|
| `manual_review_required` | 862 |
| `parser_no_label_match` | 511 |
| `parser_label_no_value` | 200 |
| `correction_manual_review_required` | 166 |
| `source_zip_unparseable` | 42 |
| `source_recovery_required_separate_approval` | 42 |
| `correction_body_confirmed_below_high` | 40 |
| `correction_no_link_original_not_found` | 37 |
| `correction_high_validated_design_only` | 17 |
| `correction_wrong_candidate_quarantined` | 17 |
| `correction_no_link_insufficient_evidence` | 15 |
| `correction_no_link_cross_category_blocked` | 1 |

## Key overlap: 39 correction zip_unparseable ⊂ 42 universe zip_unparseable (verified corr_zip=39; 3 universe-zip are non-correction).

## Overlap matrix (universe parse_status × correction action / not_correction)

| universe_parse_status | correction_action_or_not | count |
|---|---|---:|
| `body_unavailable` | `not_correction` | 3 |
| `body_unavailable` | `zip_unparseable_requires_source_recovery` | 39 |
| `extracted` | `accepted_high_validated_design_only` | 15 |
| `extracted` | `body_confirms_candidate_but_below_high` | 34 |
| `extracted` | `no_link_insufficient_evidence` | 11 |
| `extracted` | `no_link_original_not_found` | 34 |
| `extracted` | `rejected_wrong_candidate_quarantined` | 15 |
| `label_no_value` | `body_confirms_candidate_but_below_high` | 3 |
| `label_no_value` | `no_link_insufficient_evidence` | 1 |
| `label_no_value` | `no_link_original_not_found` | 3 |
| `label_no_value` | `not_correction` | 193 |
| `no_label_match` | `accepted_high_validated_design_only` | 2 |
| `no_label_match` | `body_confirms_candidate_but_below_high` | 3 |
| `no_label_match` | `no_link_cross_category_blocked` | 1 |
| `no_label_match` | `no_link_insufficient_evidence` | 3 |
| `no_label_match` | `not_correction` | 500 |
| `no_label_match` | `rejected_wrong_candidate_quarantined` | 2 |

## Fail-closed

- Every register row: manual_review_required=True, executable_or_safe=False,
  downstream_authoritative=False, parsed_clean_and_usable=False.
- NOT an event log. NOT an executable-status table. NOT downstream wiring.
- No downloads / API / body repair. No strategy / execution / production.
