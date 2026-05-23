# D3 Response Type Dispatch Test

Verification that the parser dispatches correctly based on (response_type, base_form, ACODE).

## Response type distribution (D1+D2 samples in D3 pipeline)

| Response type | Count |
|---|---|
| dart_xml_structured | 66 |
| html_inline | 38 |

## Dispatch matrix

| Response type | D3a path | D3b path | D3c path |
|---|---|---|---|
| dart_xml_structured | parse_dart_label_value_pairs → parse_treasury | parse_dart_label_value_pairs → parse_cb_bw / parse_conversion_request | skeleton only |
| html_inline | extract_html_label_value_pairs → parse_treasury (fallback) | extract_html_label_value_pairs → parse_cb_bw (fallback) | prototype only (record n_pairs) |
| tiny | attachment_only_excluded_from_denominator | attachment_only_excluded_from_denominator | attachment_only_excluded_from_denominator |
| unknown | manual_review_required | manual_review_required | manual_review_required |

## Charset / schema detection summary
- DART3/DART4 schema detection from `<DOCUMENT xsi:noNamespaceSchemaLocation>` header
- HTML inline branch invoked when first 600 bytes contain `<html`
- Charset auto-detect via `<?xml encoding=...?>`; default UTF-8 if absent