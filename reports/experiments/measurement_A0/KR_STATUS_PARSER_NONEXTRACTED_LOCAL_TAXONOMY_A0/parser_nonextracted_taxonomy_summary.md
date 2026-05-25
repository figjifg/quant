# KR-STATUS-PARSER-NONEXTRACTED-LOCAL-TAXONOMY-A0 — Summary

Date: 2026-05-26
Opened by Referee directive REF-OPEN-005 (via relay).
Local root-cause taxonomy for the 711 parser non-extracted rows.

## In-scope: **711** non-extracted rows (no_label_match 511 + label_no_value 200)

## Root-cause classes (sum to 711)

| root_cause_class | count |
|---|---:|
| `only_generic_or_contextual_label` | 499 |
| `label_present_but_attachment_or_table_context_required` | 170 |
| `label_present_but_value_in_unhandled_format` | 23 |
| `correction_disclosure_manual_only` | 18 |
| `title_body_mismatch` | 1 |
| **total** | **711** |

## Correction overlap: no_label_match 11 + label_no_value 7 = 18 (all `correction_disclosure_manual_only`)

## Boundaries

- Taxonomy is local/manual-review support ONLY. No parser behaviour changed.
- No effective_date extracted/assigned. parse_status + 511/200 split preserved.
- All 711 fail-closed; no row parsed/executable/safe/strategy-ready.
- Parser-design backlog is DESIGN-ONLY, NOT approved.
