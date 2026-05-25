# HTML-Inline Parser Design

Date: 2026-05-25
Phase: S2-HTML-INLINE-PARSER-REOPEN-PHASE
Module: `src/parsers/krx_status_html_inline.py`

## Scope (Referee-fixed)

- Categories: `suspension_related` + `resumption_related` only.
- Body format: `html_inline` only.
- Target fields: `effective_date`, `suspension_start`, `suspension_end`,
  `resumption_date`, `resumption_time`.

## Pipeline

```
zip_bytes
  -> extract_body_from_zip()        # extract + decode + format-detect
  -> detect_body_format(text)       # html_inline / structured_xml / other / unparseable
  -> if not html_inline: return out_of_scope_body_format
  -> if category not in {suspension_related, resumption_related}: return out_of_scope_category
  -> bs4.get_text(separator=" ", strip=True)
  -> _normalize_for_scan(text)      # collapse NBSP / `：`->`:` / whitespace
  -> find_label_hits(text, max_hits=40)
        for each label in FLAT_LABELS (longest-first per kind):
            find label position, walk ahead 80 chars, look for:
                - date range (delimited / korean / 부터-까지)
                - single date (delimited / korean)
  -> arbitrate hits by category:
        suspension_related: suspension_period > suspension_start > effective_generic
        resumption_related: resumption_date > effective_generic
  -> if hit has iso_date:        parse_status=extracted, confidence=high
     elif label present no date: parse_status=label_no_value, confidence=medium
     else:                       parse_status=no_label_match, confidence=low
  -> if correction marker in report_nm: manual_review_required=True
```

## Label inventory (drawn from manual-audit `effective_date_label_inventory.csv`)

| kind | labels |
|---|---|
| `suspension_start` | 매매거래정지일, 거래정지일, 정지일, 매매거래정지(개시)일 |
| `suspension_period` | 매매거래정지기간, 거래정지기간, 정지기간 |
| `resumption_date` | 매매재개일, 거래재개일, 정지해제일, 해제일, 재개일, 해제예정일, 재개예정일 |
| `effective_generic` | 효력발생일, 적용일, 지정일, 변경일 |

Longest-prefix-first scan order prevents `정지일` substring-shadowing
`매매거래정지일`.

## Date format support

- Delimited: `YYYY-MM-DD`, `YYYY.MM.DD`, `YYYY/MM/DD` (single-digit MM/DD ok).
- Korean: `YYYY년 M월 D일`.
- Range (delimited): `YYYY-MM-DD ~ YYYY-MM-DD` (separators: `~ ∼ - ― —`).
- Range (Korean): `YYYY년 M월 D일 ~ YYYY년 M월 D일`.
- Range (부터-까지): `YYYY년 M월 D일부터 [Y년] M월 D일까지`.
- Compact `YYYYMMDD` intentionally NOT consumed near labels (frequent
  collision with rcept_no digits).
- Invalid calendar dates (e.g. month=13) rejected via `datetime.date()`.

## Confidence scoring

| confidence | condition |
|---|---|
| `high` | explicit in-scope label with parseable date or range |
| `medium` | in-scope label present but no parseable date |
| `low` | no in-scope label match |

## Manual review forcing

- Any `report_nm` matching `[기재정정]|[첨부정정]|[첨부추가]|[변경]|[정정]` →
  `manual_review_required = True` regardless of extraction outcome.
- Correction linkage to original report is NOT attempted in this phase
  (depends on S2 `corp_code + base_form + series_marker` join).

## Negative-control gate

- `event_category not in {suspension_related, resumption_related}` →
  `parse_status = out_of_scope_category`; no fields populated.
- This explicitly prevents the parser from extracting suspension/resumption dates
  out of a delisting / liquidation / managed / alert body, even if the body text
  contains a label-like substring.

## What this parser does NOT do

- Does NOT parse delisting / liquidation / managed / alert / overhang.
- Does NOT parse structured-XML schemas (S2 D3a/D3b territory).
- Does NOT link corrections.
- Does NOT make any strategy / execution / performance claim.
- Does NOT fallback to `rcept_dt` for `effective_date` (forbidden).
- Does NOT touch ops / paper / live / P08 / shadow code paths.
