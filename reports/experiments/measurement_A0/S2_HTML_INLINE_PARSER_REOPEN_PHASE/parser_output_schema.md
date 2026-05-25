# Parser Output Schema

Date: 2026-05-25
Phase: S2-HTML-INLINE-PARSER-REOPEN-PHASE

## `ParseResult` (one row per disclosure)

| field | type | description |
|---|---|---|
| `rcept_no` | str | OPENDART receipt id |
| `rcept_dt` | str | OPENDART filing date `YYYYMMDD` (filing-only; NEVER effective_date) |
| `stock_code` | str | KRX 6-digit issuer code |
| `corp_name` | str | issuer name as filed |
| `report_nm` | str | original Korean disclosure title |
| `event_category` | str | suspension_related / resumption_related / delisting / managed / investment_alert / liquidation / short_term_overheated / other |
| `body_format` | str | html_inline / structured_xml / other / unparseable / missing |
| `parsed_effective_date` | str ISO or None | best-effort effective date for in-scope categories |
| `parsed_suspension_start` | str ISO or None | suspension start (suspension_related only) |
| `parsed_suspension_end` | str ISO or None | suspension end (range only) |
| `parsed_resumption_date` | str ISO or None | resumption date (resumption_related only) |
| `parsed_resumption_time` | str HH:MM or None | resumption time if found in body |
| `date_label_used` | str | the Korean label that supplied the chosen date |
| `raw_text_window` | str | ±30/+100 char context window around the chosen label |
| `parser_confidence` | str | high / medium / low |
| `manual_review_required` | bool | True if correction-flagged or low/medium confidence |
| `parse_status` | str | enum below |
| `correction_flag` | bool | True if `[기재정정]` etc. detected in `report_nm` |
| `notes` | str | free-text annotation |

## `parse_status` enum

| value | meaning |
|---|---|
| `extracted` | at least one in-scope date extracted with high confidence |
| `label_no_value` | in-scope label found but no parseable date — medium confidence |
| `no_label_match` | no in-scope label matched body text |
| `out_of_scope_category` | event_category not in `{suspension_related, resumption_related}` |
| `out_of_scope_body_format` | body format is not `html_inline` |
| `body_unavailable` | no zip bytes / unparseable zip / empty document |
| `no_extraction` | default initial state — should be replaced by one of the above |

## Forbidden defaults

- `parsed_effective_date` MUST NOT be silently filled from `rcept_dt`.
- `parser_confidence = high` MUST NOT be claimed without a body-supplied date.
- `manual_review_required = False` MUST NOT be claimed for correction-flagged rows.

## Downstream consumption boundary

- Parser output is research / measurement-layer evidence only.
- No execution simulation may consume it.
- No strategy gate may key off `parsed_effective_date`.
- No paper / live / shadow / P08 / production code may import this parser.
