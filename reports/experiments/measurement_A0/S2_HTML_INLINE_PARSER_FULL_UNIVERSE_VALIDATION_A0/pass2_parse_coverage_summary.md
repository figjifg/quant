# Pass-2 Parse Coverage Summary

Date: 2026-05-25
Phase: S2-HTML-INLINE-PARSER-FULL-UNIVERSE-VALIDATION-A0 (Pass 2)
Parser version: `krx_status_html_inline-1.1.0`

## Pass-2 in-scope rows parsed: **12187**

## Pass-2 parse_status distribution

| parse_status | Pass 1 | Pass 2 | delta |
|---|---:|---:|---:|
| `body_unavailable` | 10751 | 10744 | -7 |
| `extracted` | 1327 | 1331 | +4 |
| `label_no_value` | 24 | 26 | +2 |
| `no_label_match` | 51 | 51 | +0 |
| `out_of_scope_body_format` | 34 | 35 | +1 |

## Period-change disclosures

- Period-change `report_nm` rows in universe: **3030**.
- Period-change rows extracted: **320**.
- Period-change rows that took the new 1.1.0 after-change path: **320**.

## Extracted: Pass 1 = 1327 → Pass 2 = 1331 (delta = +4).

## Important boundary

- Behavior change is narrow: only period_change_disclosure rows take a
  different path. Ordinary suspension / resumption behavior unchanged.
- No new parser scope. No new categories. No rcept_dt fallback.
