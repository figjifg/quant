# D2 Tiny-Response / Attachment-Only Fallback Design

Per Referee D2 mandatory addition (d), 6 classification flags defined for non-body disclosures.

## Flags (D3 parser pipeline)

| Flag | Trigger | Meaning |
|---|---|---|
| `tiny_response_flag` | HTTP 200 + body ≤ 500 bytes | OPENDART API returned no body XML (likely attachment-only filing) |
| `attachment_only_flag` | tiny_response_flag OR `<DOCUMENT>` absent | Body content is in PDF/HWP attachment, not in the body XML |
| `html_scrape_fallback_possible` | dart_url page contains structured table | DART web page (`dsaf001/main.do`) can be scraped instead of body XML |
| `pdf_only_flag` | Attachment listing returns only PDF/HWP MIME | No machine-readable body or HTML; manual or OCR required |
| `not_parseable_body` | ZIP corrupted OR XML malformed | Download succeeded but parser cannot read |
| `manual_review_required` | (attachment_only AND not_pdf_parseable) OR not_parseable_body | Surface to user audit log |

## D1+D2 observed counts
- tiny_response_flag (D2 download only): 0
- attachment_only_flag (D2 download only): 0
- not_parseable_body (D2 download only): 0
- D1 had 4 tiny-response failures retroactively classified as `tiny_response_flag = True, attachment_only_flag = True`

## Parser denominator policy

- Disclosures with `attachment_only_flag = True` are EXCLUDED from parser success-rate denominator (Referee directive: classified, not treated as parser failures).
- Such disclosures are counted in a separate `attachment_only_count` field in the D6 A0 report.
- PDF parsing / OCR is OUT OF SCOPE for current S2 phase (Referee S2 scope: parser modules only).

## HTML scrape fallback (D3 prerequisite)

- For `attachment_only_flag = True` AND `html_scrape_fallback_possible = True`, D3 may extract structured table from `dart_url`.
- BUT: D3 parser implementation is NOT YET approved by Referee. HTML scraper is design-only in D2; implementation deferred to post-D2 Referee decision.