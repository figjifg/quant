# Correction Handling Status

Date: 2026-05-25
Phase: S2-HTML-INLINE-PARSER-REOPEN-PHASE

## Method

- Correction marker regex: `[기재정정] | [첨부정정] | [첨부추가] | [변경] | [정정]`.
- Any match in `report_nm` sets `correction_flag = True`.
- Correction-flagged rows ALWAYS get `manual_review_required = True`,
  regardless of extraction confidence.
- This parser does NOT attempt to link a correction to its original report
  (S2 `corp_code + base_form + series_marker` join dependency).

## Correction-flagged rows in sample: **25**
## Forced to manual review: **25 / 25**

## Category breakdown

| category | count |
|---|---:|
| `delisting` | 13 |
| `suspension_related` | 6 |
| `resumption_related` | 2 |
| `managed` | 2 |
| `other` | 2 |

## Parse_status on correction-flagged rows

| parse_status | count |
|---|---:|
| `out_of_scope_category` | 12 |
| `out_of_scope_body_format` | 7 |
| `extracted` | 4 |
| `no_label_match` | 2 |

## What this parser does NOT do

- Does NOT link `[기재정정]` to the original report.
- Does NOT supersede prior events.
- Does NOT mark prior events as cancelled.
- Does NOT call corrections authoritative.

Correction linkage is a separate proposed phase
(`KR-STATUS-CORRECTION-LINKAGE-A0`) and is NOT opened by this phase.
