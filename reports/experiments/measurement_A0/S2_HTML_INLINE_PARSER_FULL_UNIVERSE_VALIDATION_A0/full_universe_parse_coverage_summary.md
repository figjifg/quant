# Full-Universe Parse Coverage Summary

Date: 2026-05-25
Phase: S2-HTML-INLINE-PARSER-FULL-UNIVERSE-VALIDATION-A0
Parser version: `krx_status_html_inline-1.0.0`

## In-scope rows parsed: **12187**

## Parse_status distribution

| parse_status | count |
|---|---:|
| `body_unavailable` | 10751 |
| `extracted` | 1327 |
| `no_label_match` | 51 |
| `out_of_scope_body_format` | 34 |
| `label_no_value` | 24 |

## Overall extraction rate: **1327/12187 = 10.9%**
## Extraction rate given body retrieved: **1327/1402 = 94.7%**

## Parser_confidence distribution

| confidence | count |
|---|---:|
| `high` | 1327 |
| `medium` | 24 |
| `low` | 10836 |

## body_format distribution

| body_format | count |
|---|---:|
| `missing` | 10751 |
| `html_inline` | 1402 |
| `unparseable` | 34 |

## By category

| category | total | extracted | no_label | label_no_value | body_unavailable | extraction_rate |
|---|---:|---:|---:|---:|---:|---:|
| `suspension_related` | 8189 | 812 | 18 | 0 | 7342 | 9.9% |
| `resumption_related` | 3998 | 515 | 33 | 24 | 3409 | 12.9% |

## By period

| period | total | extracted | body_unavailable | extraction_rate |
|---|---:|---:|---:|---:|
| `pre_2018` | 5269 | 468 | 4748 | 8.9% |
| `post_2018` | 6918 | 859 | 6003 | 12.4% |

## Correction vs non-correction parse_status split

| segment | extracted | label_no_value | no_label | body_unavailable | other |
|---|---:|---:|---:|---:|---:|
| `correction` | 93 | 4 | 10 | 26 | 33 |
| `non_correction` | 1234 | 20 | 41 | 10725 | 1 |

## Manual_review_required rate: **10953/12187 = 89.9%**

## Body availability gap

- `body_unavailable` rows: **10751** (no cached body and not fetched in this phase).
- Body retrieval rate across in-scope: **1402/12187 = 11.5%**.

Body retrieval gap reflects that prior phases cached ~225 OPENDART document
ZIPs (manual-audit + correction-linkage Pass-2/3 holdouts). The remaining
in-scope rows have NO body at this run. Per Referee verdict:
- Do NOT treat download failure as non-event.
- Do NOT use unavailable body as proof.
- Do NOT silently drop missing documents.

These `body_unavailable` rows are recorded with `parse_status = body_unavailable`
and `manual_review_required = True` and remain in the universe.
