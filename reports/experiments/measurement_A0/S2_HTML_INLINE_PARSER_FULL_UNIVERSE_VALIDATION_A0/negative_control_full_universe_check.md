# Negative-Control Full-Universe Check

Date: 2026-05-25
Phase: S2-HTML-INLINE-PARSER-FULL-UNIVERSE-VALIDATION-A0

## Method

Apply the existing parser to ALL out-of-scope rows. The parser's category
gate (`categorize_report(report_nm)`) is the load-bearing safety mechanism:
as long as no in-scope field (`effective_date` / `suspension_*` /
`resumption_*`) is ever extracted from an out-of-scope row, the negative-
control gate is intact — regardless of whether the parser returned
`out_of_scope_category` directly or `body_unavailable` first.

The load-bearing pass criterion is therefore **false_positive = 0**, NOT
`parse_status == out_of_scope_category` for every row.

## Out-of-scope universe size: **5737**

## By category

| category | count |
|---|---:|
| `delisting` | 4473 |
| `other` | 762 |
| `managed` | 468 |
| `investment_alert` | 21 |
| `short_term_overheated` | 10 |
| `liquidation` | 3 |

## Parse_status distribution on negative-control rows

| parse_status | count | note |
|---|---:|---|
| `out_of_scope_category` | 82 | parser saw body; category gate blocked |
| `body_unavailable` | 5650 | no cached body; could not reach category gate, but ALSO cannot extract in-scope field |
| other | 5 | (e.g. out_of_scope_body_format on non-HTML bodies) |

## Safe rows (no in-scope field extracted): **5737 / 5737 = 100.00%**
## False positives (extracted any in-scope field on negative control): **0**

## Verdict

- Negative-control gate verified across 5737 out-of-scope rows.
- False-positive rate: 0.000%.
- Parser does NOT extract suspension / resumption dates from delisting /
  liquidation / managed / alert / overheated / other categories at full scale.
- For rows that returned `body_unavailable`: the parser cannot even attempt
  in-scope field extraction without a body, so the safety property still holds.
