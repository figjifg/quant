# DART Body Sample Check

Date: 2026-05-25  
Phase: KR-EXECUTABLE-EFFECTIVE-DATE-LINKAGE-A0

## Bounded sample

- Samples audited: **113**
- Method: bounded `document.xml` download per sample (no full body parser).

## Body format breakdown

| format | count |
|---|---:|
| `html` | 111 |
| `unparseable` | 2 |

## Extraction method breakdown

| method | count |
|---|---:|
| `unavailable` | 109 |
| `official_body_date` | 2 |
| `body_unavailable` | 2 |

## Interpretation

- `download_failed`: OPENDART document.xml endpoint returned no data for the sample.
- `xml` / `html`: body downloaded; extraction depends on regex patterns matching.
- `unparseable`: ZIP could not be opened.
- `official_body_date`: regex matched one of the canonical Korean date fields
  (효력발생일 / 적용일 / 정지일 / 해제일 / 폐지일 / 정리매매 기간 / 재개일).
- `title_date_hint`: report_nm contained a `YYYY-MM-DD` style date.
- `body_unavailable` / `unavailable`: no extractable date.

## S2 dependency

S2 OPENDART Body Parser Phase is CLOSED AS PARTIAL. This phase intentionally
uses only **simple regex** patterns, NOT the full S2 parser. As a result:

- Some DART body XML structures use ACODE-specific table layouts that the
  simple regex misses.
- The `unavailable` count is expected to be material.
- For broader coverage, a future phase would need to either complete the S2
  parser or fall back to manual review.

## Hard locks (preserved)

- No full S2 body parser invoked.
- No alpha / strategy / execution simulation.
- No `rcept_dt` treated as effective date.
