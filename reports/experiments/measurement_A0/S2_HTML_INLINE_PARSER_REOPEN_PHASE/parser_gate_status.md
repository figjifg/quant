# Parser Gate Status

Date: 2026-05-25
Phase: S2-HTML-INLINE-PARSER-REOPEN-PHASE

## Gate state: **HTML_INLINE_PARSER_VALIDATED_FOR_SUSPENSION_RESUMPTION_ONLY**

### Rationale

suspension exact-match 92.5%; resumption exact-match 87.8%; overall 90.7%; negative-control false positives = 0; correction-flagged rows forced to manual review.

## Permitted enum (Referee-fixed)

- `DATA_SOURCE_FAIL`
- `PARTIAL`
- `HTML_INLINE_PARSER_BUILT_BUT_NOT_VALIDATED`
- `HTML_INLINE_PARSER_VALIDATED_FOR_SUSPENSION_RESUMPTION_ONLY`
- `HTML_INLINE_PARSER_REQUIRES_MORE_WORK`
- `READY_FOR_NEXT_A0_REVIEW`

## Numerical inputs

| metric | value |
|---|---:|
| in-scope samples | 108 |
| overall exact match | 90.7% |
| suspension exact match | 92.5% |
| resumption exact match | 87.8% |
| manual_review_required | 14 |
| negative-control false positives | 0 |
| total defect-ledger rows | 14 |
| correction-flagged rows | 25 |

## Important boundary

- Execution simulation is NOT opened.
- Strategy testing is NOT opened.
- Performance diagnostics is NOT opened.
- No card is strategy-ready.
- This gate state is a parser-quality verdict only.
