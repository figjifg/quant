# D3 Failure Modes Register

## Failure mode counts (D1+D2 pipeline through D3 parser)

| Failure mode | Count | Classification policy |
|---|---|---|
| attachment_only (tiny response) | 0 | excluded from parser denominator |
| html_inline (D3a/D3b XML-expected forms, fallback used) | 15 | manual_review_required |
| parser_exception | 0 | manual_review_required, logged |
| missing_xml | 4 | excluded with error logged |
| read_error | 0 | excluded with error logged |
| D3c_skeleton_only (forms outside D3a/D3b) | 54 | NOT parsed, awaits D3c approval |

## Manual review queue size
- 108 rows requiring manual review
- queue file: `d3_manual_review_queue.csv`

## Common extraction errors
- rows with at least one extraction_error: 16

## Confidence policy
- `parser_confidence` = (n_present_required_fields / n_required) − 0.1 × n_extraction_errors, clipped to [0,1]
- D3a required: amount_krw, shares, event_date
- D3b CB/BW required: amount_krw, event_date
- D3b conversion required: shares, event_date
- Confidence < 0.6 or any required field missing → manual_review_required = True

## Confidence observed (D1+D2 samples)

| Wave | mean | max | rows with conf ≥ 0.6 |
|---|---|---|---|
| D3a | 0.037 | 0.667 | 2 / 36 |
| D3b | 0.147 | 0.500 | 0 / 17 |

## Root cause of low confidence (first-pass)

The current label-discovery heuristic assumes:
- each `<TR>` has a label in cell 0 and value(s) in cells 1+

In actual DART body XML, many tables use:
- multi-row headers (column header in row 1, row header in column 1, values in inner cells)
- nested `<TABLE>` inside `<TD>`
- merged cells (`COLSPAN`, `ROWSPAN`) that break the simple per-row label assumption

Result: keyword matches succeed only for the small set of forms where the label happens to land in cell 0. For most disclosures the label exists in the XML but is not in the position the current heuristic searches.

## Mitigation path (D3 precision tuning round)

1. Multi-row label discovery: parse `<THEAD>` + `<TBODY>` separately; treat THEAD cells as column headers; row headers via first-column scan
2. Nested-table flatten: walk `<TABLE>` descendants depth-first
3. Per-ACODE field map: use D2 schema_examples to enumerate exact label strings per ACODE
4. Manual audit pass on 30 samples per D3a/D3b base form

This is documented in `d3_next_wave_recommendation.md` as the recommended next round.