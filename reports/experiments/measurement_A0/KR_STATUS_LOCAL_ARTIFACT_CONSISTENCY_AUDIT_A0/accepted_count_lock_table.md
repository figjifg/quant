# Accepted Count Lock Table

Date: 2026-05-26
Phase: KR-STATUS-LOCAL-ARTIFACT-CONSISTENCY-AUDIT-A0

Canonical accepted counts (locked across the 6 phases):

| metric | canonical value |
|---|---:|
| universe_rows | 12,187 |
| usable_html_inline | 12,145 |
| zip_unparseable | 42 |
| no_label_match | 511 |
| label_no_value | 200 |
| blocker_register_rows | 862 |
| parser_nonextracted_rows | 711 |
| correction_rows | 166 |
| correction_zip_subset | 39 |
| non_correction_zip_subset | 3 |

## Derived identities

| identity | lhs | rhs | match |
|---|---|---:|---|
| parser_nonextracted = no_label_match + label_no_value | 511+200=711 | 711 | PASS |
| zip = correction_zip + non_correction_zip | 39+3=42 | 42 | PASS |
| blocker_register = 753 universe-residual + 109 extracted-correction | 753+109=862 | 862 | PASS |
| universe = usable_html_inline + zip_unparseable | 12145+42=12187 | 12187 | PASS |