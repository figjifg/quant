# Manual Body Format Summary

Date: 2026-05-25  
Phase: KR-STATUS-EFFECTIVE-DATE-MANUAL-AUDIT-PHASE

## Body format breakdown

| format | count |
|---|---:|
| `html_inline` | 188 |
| `unparseable` | 7 |

## Method

- `bs4.BeautifulSoup(text, 'html.parser').get_text()` used to extract plain
  body text from each document.xml ZIP member.
- Body format classified heuristically from the first 500 characters of the
  largest document in the ZIP.

## Interpretation

- `html_inline`: KRX 안내공시 form — body is HTML-with-styling, requires bs4
  to extract plain text. Most KRX status disclosures fall here.
- `structured_xml`: DART3/DART4 XSD schemas with explicit table rows —
  amenable to per-ACODE parsing (S2 PARTIAL).
- `download_failed`: OPENDART document.xml endpoint returned no data.
- `unparseable`: ZIP could not be opened.
