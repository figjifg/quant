# Parser-Design Candidate Themes (DESIGN-ONLY — NOT APPROVED)

Date: 2026-05-26
Phase: KR-STATUS-PARSER-NONEXTRACTED-FEASIBILITY-A0

**Future design themes only. No parser rule is implemented here, and NO design is
approved. Any actual parser change requires a separate user + Referee parser-change
verdict (and, where noted, a design phase to prove safety first).**

## Candidate themes (planning evidence only)

| design theme | rows | feasibility | what a future design phase WOULD study (not now) |
|---|---:|---|---|
| `contextual_or_label_pattern_expansion` | 499 | uncertain (high false-positive risk) | whether a label-free / contextual date extractor can be made SAFE for the 499 generic/contextual rows; must prove low FP before any change |
| `table_or_structure_aware_extraction` | 170 | medium | structure/table-aware parsing so a header label can be tied to a non-adjacent value cell (lost in current HTML->text flattening) |
| `date_format_or_relative_date_handling` | 23 | medium | additional date formats / relative-date ("익일/추후/별도/미정") handling, with explicit rules for unresolvable relatives |
| `correction_adjudication_workflow_not_parser_design` | 18 | n/a | correction rows are NOT a parser-design target; route to manual adjudication workflow (separate approval) |
| `n_a_body_off_topic` | 1 | n/a | body off-topic; keep fail-closed (not a parser-design target) |

## Feasibility-bucket roll-up

| feasibility_bucket | rows |
|---|---:|
| `parser_design_candidate` | 522 |
| `needs_table_context_design` | 170 |
| `correction_workflow_only` | 18 |
| `out_of_scope_or_keep_fail_closed` | 1 |
| **total** | **711** |

## Boundary

- These themes are planning evidence. No row is parsed/recovered/safe/validated/
  approved/usable. Parser code/rules/version are unchanged. A future parser-change
  phase requires a separate user + Referee verdict.
