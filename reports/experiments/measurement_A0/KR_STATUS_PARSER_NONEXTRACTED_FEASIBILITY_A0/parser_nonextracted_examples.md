# Parser Non-Extracted Feasibility — Inspection Examples

Date: 2026-05-26
Phase: KR-STATUS-PARSER-NONEXTRACTED-FEASIBILITY-A0

**These rows are INSPECTION SAMPLES ONLY — not validation, not approval, not parsed/recovered/safe. Feasibility/design labels are planning evidence only.** A future parser-change phase, if any, needs a separate user + Referee verdict.

## parser_design_candidate (showing 5 samples)

| rcept_no | prior_parse_status | prior_taxonomy_class | body_text_len | n_label_hits | design_theme |
|---|---|---|---:|---:|---|
| 20100330901313 | no_label_match | only_generic_or_contextual_label | 410 | 0 | contextual_or_label_pattern_expansion |
| 20100324900019 | no_label_match | only_generic_or_contextual_label | 572 | 0 | contextual_or_label_pattern_expansion |
| 20100323900700 | no_label_match | only_generic_or_contextual_label | 449 | 0 | contextual_or_label_pattern_expansion |
| 20100323900697 | no_label_match | only_generic_or_contextual_label | 451 | 0 | contextual_or_label_pattern_expansion |
| 20100323900643 | no_label_match | only_generic_or_contextual_label | 557 | 0 | contextual_or_label_pattern_expansion |

## needs_table_context_design (showing 5 samples)

| rcept_no | prior_parse_status | prior_taxonomy_class | body_text_len | n_label_hits | design_theme |
|---|---|---|---:|---:|---|
| 20100329800013 | label_no_value | label_present_but_attachment_or_table_context_required | 286 | 1 | table_or_structure_aware_extraction |
| 20100326801884 | label_no_value | label_present_but_attachment_or_table_context_required | 282 | 1 | table_or_structure_aware_extraction |
| 20100325800898 | label_no_value | label_present_but_attachment_or_table_context_required | 284 | 1 | table_or_structure_aware_extraction |
| 20100324800564 | label_no_value | label_present_but_attachment_or_table_context_required | 290 | 1 | table_or_structure_aware_extraction |
| 20100324800285 | label_no_value | label_present_but_attachment_or_table_context_required | 288 | 1 | table_or_structure_aware_extraction |

## correction_workflow_only (showing 5 samples)

| rcept_no | prior_parse_status | prior_taxonomy_class | body_text_len | n_label_hits | design_theme |
|---|---|---|---:|---:|---|
| 20101126900274 | no_label_match | correction_disclosure_manual_only | 1582 | 0 | correction_adjudication_workflow_not_parser_design |
| 20110318800229 | label_no_value | correction_disclosure_manual_only | 472 | 1 | correction_adjudication_workflow_not_parser_design |
| 20110506800027 | label_no_value | correction_disclosure_manual_only | 481 | 1 | correction_adjudication_workflow_not_parser_design |
| 20130314802024 | label_no_value | correction_disclosure_manual_only | 482 | 2 | correction_adjudication_workflow_not_parser_design |
| 20130117900277 | no_label_match | correction_disclosure_manual_only | 1676 | 0 | correction_adjudication_workflow_not_parser_design |

## out_of_scope_or_keep_fail_closed (showing 1 samples)

| rcept_no | prior_parse_status | prior_taxonomy_class | body_text_len | n_label_hits | design_theme |
|---|---|---|---:|---:|---|
| 20220802600359 | no_label_match | title_body_mismatch | 249 | 0 | n_a_body_off_topic |
