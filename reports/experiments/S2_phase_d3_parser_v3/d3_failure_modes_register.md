# D3 Failure Modes Register (v3)

| Mode | Count | Policy |
|---|---|---|
| attachment_only | 0 | excluded from denominator |
| html_inline within D3a/D3b | 15 | manual_review |
| parser_exception | 0 | manual_review + logged |
| missing_xml | 4 | excluded + logged |
| D3c_skeleton_only | 54 | NOT parsed |

## Confidence observed (v3)
- D3a mean=0.185, max=1.000
- D3b mean=0.147, max=0.500

## v3 mitigations applied
- &cr; carriage-return entity normalized in cell text (prevented label-keyword false negatives)
- ACODE-specific label hints expanded with actual sample labels (e.g., '1. 취득예정주식(주)' exact match)
- D3b shares keyword set re-broadened to recover v1 captures while keeping v2 ACODE precision
- D3b event_date keyword set expanded (이사회결의일/결의일/발행결의일/결정일)