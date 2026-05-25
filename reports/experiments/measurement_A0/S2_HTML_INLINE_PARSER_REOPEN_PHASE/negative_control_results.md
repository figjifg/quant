# Negative-control Results

Date: 2026-05-25
Phase: S2-HTML-INLINE-PARSER-REOPEN-PHASE

## Method

- Negative controls = rows whose `event_category` is NOT in
  `{suspension_related, resumption_related}`.
- Parser MUST return `parse_status = out_of_scope_category` for all such rows.
- Any extracted date counts as a false positive.

## Negative-control sample size: **87**

## Per-category parse_status distribution

| category | n | parse_status counts |
|---|---:|---|
| `delisting` | 52 | `out_of_scope_category`:48, `out_of_scope_body_format`:4 |
| `investment_alert` | 1 | `out_of_scope_category`:1 |
| `liquidation` | 3 | `out_of_scope_category`:3 |
| `managed` | 28 | `out_of_scope_category`:27, `out_of_scope_body_format`:1 |
| `other` | 2 | `out_of_scope_category`:2 |
| `short_term_overheated` | 1 | `out_of_scope_category`:1 |

## False positives (parser extracted a date from a negative-control body): **0**


## Interpretation

- A zero false-positive count would indicate that the negative-control gate
  is functioning correctly — the parser refuses to fire on delisting /
  liquidation / managed / alert categories.
- Non-zero false positives MUST be recorded in `parser_defect_ledger.csv`
  under defect class `unsupported_category_false_positive`.
- This phase does NOT expand parser scope to handle these categories.
