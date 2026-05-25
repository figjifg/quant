# Manual-Review Packet Schema

Date: 2026-05-26
Phase: KR-STATUS-RESIDUAL-MANUAL-REVIEW-PACKET-CONSOLIDATION-A0

## Key

- Row-level, keyed by **`rcept_no`**, over the accepted 862 blocker-register rows.

## Columns (manual_review_packet.csv)

- Identity/context: rcept_no, rcept_dt, stock_code, event_category, is_correction.
- Parser/source annotations: parse_status, residual_class, blocker_tags,
  taxonomy_root_cause, source_recovery_class.
- Correction annotations: correction_confidence_5tier, correction_action_class,
  correction_supersession_ready.
- Triage: review_bucket, review_priority_note.
- Fail-closed (carried, never relaxed): manual_review_required=True,
  executable_or_safe=False, downstream_authoritative=False,
  parsed_clean_and_usable=False, recovered=False, human_validation_claimed=False.

## Review buckets (conservative, one per row; priority-ordered)

1. `source_recovery_required` — corrupt-ZIP body (residual_class=zip_unparseable);
   dominant: needs source recovery (separate verdict + download approval).
2. `rejected_wrong_candidate_quarantine` — correction action
   rejected_wrong_candidate_quarantined.
3. `correction_manual_review` — other correction rows (non-authoritative).
4. `parser_table_or_attachment_context` — non-correction; taxonomy
   label_present_but_attachment_or_table_context_required.
5. `parser_generic_or_contextual_label` — non-correction; taxonomy
   only_generic_or_contextual_label.
6. `parser_unhandled_format` — non-correction; taxonomy
   label_present_but_value_in_unhandled_format.
7. `mixed_or_multi_blocker` — does not fit a single clean bucket (e.g.
   title_body_mismatch).

## Boundaries

- Human-review-only and fail-closed. The packet INDEXES blockers; it does NOT fix,
  recover, parse, or mark any row usable. supersession_ready / link_validated values
  carried from prior phases remain DESIGN-ONLY (not authority/safety/readiness/wired).
