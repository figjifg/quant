# Worklist Boundary Policy

Date: 2026-05-26
Phase: KR-STATUS-MANUAL-REVIEW-WORKLIST-VIEWS-A0

`blocked_action_boundary` is a WARNING boundary field, NOT approval. It
tells a future human reviewer what would still be required BEFORE any
action — it grants nothing.

| review_bucket | blocked_action_boundary | meaning |
|---|---|---|
| `source_recovery_required` | `requires_separate_source_recovery_verdict_and_download_approval` | body unreadable; needs a separate Referee verdict + explicit download/API approval |
| `parser_table_or_attachment_context` | `requires_future_parser_design_verdict` | needs a separate parser-design/feasibility verdict; parser changes forbidden until then |
| `parser_generic_or_contextual_label` | `requires_future_parser_design_verdict` | needs a separate parser-design/feasibility verdict; parser changes forbidden until then |
| `parser_unhandled_format` | `requires_future_parser_design_verdict` | needs a separate parser-design/feasibility verdict; parser changes forbidden until then |
| `correction_manual_review` | `manual_correction_review_only_non_authoritative` | correction disclosure; human review only; never downstream-authoritative |
| `rejected_wrong_candidate_quarantine` | `quarantine_review_only` | scored candidate not body-confirmed; quarantined; human confirms wrong-candidate |
| `mixed_or_multi_blocker` | `manual_triage_only` | does not fit a single clean bucket; human triage only |

## Boundary is not approval
- No boundary value authorizes recovery, downloads, parser changes,
  adjudication, validation, or any downstream action.
- `blocked_action_boundary` remains WARNING-ONLY, not approval.

## Worklist carries NO outcome columns (REF-OPEN-011 Pass 2)
- The input-packet fail-closed flags (manual_review_required=True;
  executable_or_safe / downstream_authoritative / parsed_clean_and_usable /
  recovered / human_validation_claimed = False) were VERIFIED on the input
  packet (see worklist_integrity_check.csv).
- Worklist rows are navigation-only. They carry NO outcome/status columns
  (no validated / approved / effective_date_final / recovered / parsed /
  safe / executable / authoritative / strategy_ready / execution_ready /
  production_ready). The single carried flag `manual_review_required=True`
  is the fail-closed 'still needs review' navigation marker, not an outcome.