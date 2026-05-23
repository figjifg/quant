# D3 Failure Modes Register (v2)

| Mode | Count | Policy |
|---|---|---|
| attachment_only | 0 | excluded from denominator |
| html_inline in D3a/D3b | 15 | manual_review |
| parser_exception | 0 | manual_review + logged |
| missing_xml | 4 | excluded + logged |
| D3c_skeleton_only | 54 | not parsed (awaits D3c approval) |

## Confidence observed
- D3a mean=0.157, max=1.000
- D3b mean=0.147, max=0.500

## Label discovery strategy used (v2)
- Strategy A: row-pair (cell 0 = label, cell 1+ = value)
- Strategy B: column-header + row-header composition
- Strategy C: flat-adjacency (i, i+1) pair fallback
- COLSPAN/ROWSPAN expanded to 2D grid before strategies applied
- Nested <TABLE> handled via BeautifulSoup descendant walk
- ACODE-specific keyword hints applied first, generic fallback second