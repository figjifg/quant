# Table-Context Future Safety Guardrails (PROPOSED — NOT IMPLEMENTED)

Date: 2026-05-26
Phase: KR-STATUS-PARSER-TABLE-CONTEXT-DESIGN-PROOF-A0

**Proposed FUTURE safety guardrails only. NO parser implementation here. NO design is
approved. Any actual parser change requires a separate user + Referee parser-change
verdict.**

## KEY PROOF FINDING (corrects the prior feasibility optimism)

Read-only table inspection of all 170 rows shows the matched (resumption / release-date)
label's value cell is an explicit **`-` (empty/dash)** — i.e. the resumption/release
date is NOT YET DETERMINED in these suspension disclosures. **0 / 170** had a parseable
date in the matched label's value cell. So:

- There is NO date to extract for the failing field; the value genuinely does not exist
  in the body.
- Table/structure-aware extraction would correctly read the `-` and STILL produce no
  date — it does NOT recover anything here.
- The prior `needs_table_context_design` feasibility label OVER-stated the opportunity:
  these 170 are NOT a parser-design win. All 170 -> `out_of_scope_keep_fail_closed`,
  kept fail-closed.

(Aside, NOT actioned: many of these disclosures DO carry a *suspension* timestamp in an
adjacent cell, e.g. "매매거래정지 일시 | 2010-..-.. HH:MM", which the parser's current
label set misses because the spacing breaks the "정지일" token. Extracting that would be
a DIFFERENT field + a label-pattern theme, not table-context, and would need its own
separate design + parser-change verdict. It is recorded here only as an observation.)

The guardrails below are therefore HYPOTHETICAL — what a table/structure-aware design
WOULD need IF value-bearing cells existed (they did not for these 170):

1. **Strict table-adjacency rule.** Accept a value only from the label cell's immediate
   right-neighbor (same row) or immediate below-neighbor (same column). Reject anything
   farther.
2. **Single-candidate rule.** Accept only if exactly one parseable date is found in the
   adjacent value cell; reject if the adjacent cell has 0 or >1 dates.
3. **Single-label rule.** Reject if the body has more than one table label cell of the
   target kind (ambiguous which event the date belongs to) unless label-kind
   disambiguation is added.
4. **Span guard.** Reject (or specially handle) tables with colspan/rowspan, since
   simple row/column adjacency can misalign cells.
5. **Label-kind / event-type consistency.** The matched label kind (suspension start /
   period / resumption / effective-generic) must be consistent with the disclosure's
   event_category before accepting.
6. **No rcept_dt fallback.** Never substitute rcept_dt as the effective date.
7. **Fail-closed default.** Any row not clearly passing all guards stays
   zip-/non-extracted and fail-closed; the design must prefer a miss over a wrong date.

## Bucket roll-up (proof-only)

| design_proof_bucket | rows |
|---|---:|
| `out_of_scope_keep_fail_closed` | 170 |
| **total** | **170** |

For these 170 there are 0 `future_parser_change_candidate_*` rows (all value cells are
`-`), so NO table-context parser-change is warranted for them — they remain
fail-closed. The guardrails above stand as design notes for any future row set that
DOES have value-bearing table cells.
