# Accepted Row-Key Lock Table

Date: 2026-05-26
Phase: KR-STATUS-RESIDUAL-ROWKEY-INTEGRITY-AUDIT-A0

Locked at the rcept_no SET level (not just aggregate counts):

| set check | expected size | sets | set equality |
|---|---:|---|---|
| zip_unparseable_set_42 | 42 | universe == register == manifest | PASS |
| correction_zip_set_39 | 39 | adjudication == register == manifest | PASS |
| non_correction_zip_set_3 | 3 | register == manifest | PASS |
| parser_nonextracted_set_711 | 711 | universe == register == taxonomy | PASS |
| correction_set_166 | 166 | links == adjudication == register | PASS |

## 862 register union (overlap preserved, not double-counted)

| component | size |
|---|---:|
| U_753 (universe non-extracted: no_label+label_no_value+zip) | 753 |
| correction_166 (register correction subset) | 166 |
| overlap (corrections that are also universe non-extracted) | 57 |
| union = 753 + 166 - overlap | 862 |
| register_all | 862 |
| union == register_all | PASS |

Register == (U_753 ∪ correction_166) at set level: **PASS**