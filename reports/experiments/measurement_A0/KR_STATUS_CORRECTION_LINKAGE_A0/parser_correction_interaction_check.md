# Parser ↔ Correction Interaction Check

Date: 2026-05-25
Phase: KR-STATUS-CORRECTION-LINKAGE-A0

## Method

Inspect `parser_validation_results.csv` from
`S2-HTML-INLINE-PARSER-REOPEN-PHASE` for rows where the parser set
`correction_flag = True`.

## Findings

| metric | value |
|---|---:|
| correction-flagged parser rows | 25 |
| correction rows forced to manual_review_required | 25 |
| correction rows that produced parser-extracted dates | 4 |
| extracted-and-still-forced-manual-review | 4 |

## Verdict

- `manual_review_required` coverage: **25/25** — 100%.
- Parser does NOT mark correction output as authoritative.
- Parser preserves `correction_flag` in output schema.
- No defect class `parser_extracts_correction_without_manual_review`
  triggered: `OK`.

## Interpretation

Even when the parser successfully extracts a date from a correction body,
it does NOT silently mark the output as the authoritative effective date.
Downstream consumers MUST treat `manual_review_required = True` rows as
audit-queue items, not as event-log entries.
