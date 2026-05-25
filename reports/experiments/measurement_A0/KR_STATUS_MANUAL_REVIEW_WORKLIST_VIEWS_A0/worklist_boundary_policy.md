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
- Worklist views are human-navigation-only and fail-closed. Every row
  remains manual_review_required=True with all usability/authority flags False.