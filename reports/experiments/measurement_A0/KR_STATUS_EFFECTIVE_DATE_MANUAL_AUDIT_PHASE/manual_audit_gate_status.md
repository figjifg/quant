# Manual-Audit Gate Status

Date: 2026-05-25  
Phase: KR-STATUS-EFFECTIVE-DATE-MANUAL-AUDIT-PHASE

## Gate state: **MANUAL_AUDIT_SUPPORTS_PARSER_REOPEN**

### Rationale

manual audit of 195 samples reached 56.4% extraction rate; parser feasibility = parser_feasible_html_inline. Conditions support a future S2-HTML-INLINE-PARSER-REOPEN-PHASE verdict (NOT automatic — separate Referee).

## Permitted enum (Referee-fixed)

- `DATA_SOURCE_FAIL`
- `PARTIAL`
- `MANUAL_AUDIT_COMPLETED_BUT_NOT_GENERALIZED`
- `MANUAL_AUDIT_SUPPORTS_PARSER_REOPEN`
- `MANUAL_AUDIT_SUPPORTS_MANUAL_ONLY_PATH`
- `READY_FOR_NEXT_A0_REVIEW`

## Numerical inputs

| metric | value |
|---|---:|
| samples reviewed | 195 |
| extraction rate (explicit_*) | 56.4% |
| body_format html_inline | 188 |
| body_format structured_xml | 0 |
| body_format download_failed | 0 |
| body_format unparseable | 7 |
| parser feasibility | parser_feasible_html_inline |

## Important boundary

- Strategy testing is NOT opened.
- Execution simulation is NOT opened.
- S2 parser reopen is NOT triggered automatically.
- Manual-audit result is decision input ONLY.
