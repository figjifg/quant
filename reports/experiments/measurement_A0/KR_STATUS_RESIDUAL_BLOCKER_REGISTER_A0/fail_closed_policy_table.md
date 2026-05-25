# Fail-Closed Policy Table

Date: 2026-05-26
Phase: KR-STATUS-RESIDUAL-BLOCKER-REGISTER-A0

Every blocker tag is FAIL-CLOSED: in the absence of explicit, separately-approved
resolution, the row MUST be treated as unusable. What each tag forbids downstream:

| blocker tag | what a future phase MUST NOT infer |
|---|---|
| `source_zip_unparseable` | MUST NOT treat as parsed / extracted / body-available / usable. Body never parsed (corrupt ZIP). |
| `source_recovery_required_separate_approval` | MUST NOT download/repair without a SEPARATE Referee verdict + download approval. |
| `parser_no_label_match` | html_inline body present but parser found NO target label. MUST NOT treat as extracted / safe / value-bearing. |
| `parser_label_no_value` | label found but NO value parsed. MUST NOT treat as an extracted value. |
| `correction_manual_review_required` | Correction disclosure. Parser output NON-authoritative. MUST NOT treat as authoritative by default. |
| `correction_high_validated_design_only` | DESIGN-ONLY validated link. MUST NOT wire / supersede / execute. Still manual review. |
| `correction_body_confirmed_below_high` | Body references candidate but below high bar. MUST NOT treat as confirmed link. |
| `correction_wrong_candidate_quarantined` | Scored candidate NOT supported by body. MUST NOT treat as a link. Quarantined. |
| `correction_no_link_original_not_found` | No local original found. MUST NOT fabricate a link. |
| `correction_no_link_insufficient_evidence` | Candidate(s) too weak. MUST NOT treat as linked. |
| `correction_no_link_cross_category_blocked` | Cross-category original blocked by policy. MUST NOT auto-link. |
| `manual_review_required` | Universal. MUST NOT treat ANY register row as executable / safe / strategy-ready / production-ready / downstream-authoritative. |

## Global fail-closed rules

- No register row is parsed-clean-and-usable, executable, safe, strategy-ready,
  production-ready, or downstream-authoritative — regardless of tag combination.
- A correction row that is parser-`extracted` is STILL
  `correction_manual_review_required` (correction parser output non-authoritative).
- This register is NOT an event log, NOT an executable-status table, NOT downstream
  wiring. It only preserves residual blocker + manual-review state for later local
  review.
