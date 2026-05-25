# Parser-Design Backlog Candidates (DESIGN-ONLY — NOT APPROVED)

Date: 2026-05-26
Phase: KR-STATUS-PARSER-NONEXTRACTED-LOCAL-TAXONOMY-A0

**These are DESIGN-ONLY candidates derived from the local root-cause taxonomy. They
are NOT approved for any parser change. No parser code may be modified without a
separate Referee verdict opening a parser-design/expansion phase.**

| root cause | rows | hypothetical future handling (DESIGN-ONLY, NOT APPROVED) |
|---|---:|---|
| `label_present_but_value_in_unhandled_format` | 23 | a future phase *might* study additional date formats / relative-date handling — NOT now |
| `label_present_but_attachment_or_table_context_required` | 170 | value likely in attachment/table; out of html-inline scope; needs separate verdict |
| `label_present_but_empty_value` | 0 | genuinely empty value cell; likely irrecoverable without source |
| `only_generic_or_contextual_label` | 499 | body on-topic but no exact date label; manual review |
| `title_body_mismatch` | 1 | body not on status-event topic in recognizable terms; manual review |
| `body_text_too_short_or_malformed` | 0 | short/malformed body; likely source defect |
| `correction_disclosure_manual_only` | 18 | correction rows; manual-only; never auto-parsed |
| `other_nonextracted_manual_review` | 0 | unclassified; manual review |

## Hard boundary

- This table does NOT authorize parser changes, extraction upgrades, or any
  reclassification. Every row remains `no_label_match` / `label_no_value`,
  fail-closed, manual_review_required.
