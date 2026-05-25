# KR-STATUS-SOURCE-RECOVERY-CANDIDATE-MANIFEST-A0 — Summary

Date: 2026-05-26
Opened by Referee directive REF-OPEN-006 (via relay).
LOCAL manifest of the 42 zip_unparseable source defects. NOT recovery.

## In-scope: **42** source_zip_unparseable rows (correction 39 + non-correction 3)

## Counts

| dimension | key | count |
|---|---|---:|
| total | all | 42 |
| is_correction | correction | 39 |
| is_correction | non_correction | 3 |
| event_category | suspension_related | 23 |
| event_category | resumption_related | 19 |
| source_period | pre_2018 | 25 |
| source_period | post_2018 | 17 |
| correction_action_class (39) | zip_unparseable_requires_source_recovery | 39 |
| underlying_5tier (39 corr) | no_link | 20 |
| underlying_5tier (39 corr) | medium_needs_manual | 12 |
| underlying_5tier (39 corr) | low_needs_manual | 7 |

## Recovery boundary (all 42)

- recovery_performed=False; requires_separate_verdict=True;
  requires_download_approval=True; safe_for_current_use=False.
- All fail-closed (manual_review_required=True; executable_or_safe / downstream_authoritative / parsed_clean_and_usable / strategy_ready / production_ready = False).
- This is a LOCAL manifest only. No downloads / API / body repair. Recovery requires a separate Referee verdict + download approval.
