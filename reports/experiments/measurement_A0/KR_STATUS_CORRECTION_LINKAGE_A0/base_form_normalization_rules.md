# Base-Form Normalization Rules

Date: 2026-05-25
Phase: KR-STATUS-CORRECTION-LINKAGE-A0

## Rule set (applied in order)

1. Strip bracketed correction markers from `report_nm`:
   - `[기재정정]`, `[첨부정정]`, `[첨부추가]`, `[변경]`, `[정정]`
   - And parenthesised variants `(기재정정)` etc.
2. Collapse all whitespace runs to a single space; trim.
3. Identify a longest-matching title root from a fixed root list:
   - `주권매매거래정지기간변경`
   - `주권매매거래정지(해제)` / `주권매매거래정지해제`
   - `주권매매거래정지`
   - `주권매매재개`
   - (matching variants without `주권` prefix)
4. If a root matches, set `normalized_base_form` = `<root>` plus the first
   parenthesised reason content (e.g. `주권매매거래정지(불성실공시법인 지정)`).
5. If no root matches, fall back to the cleaned full title as
   `normalized_base_form`.

## Confidence enum

| confidence | condition |
|---|---|
| `high` | root match found |
| `medium` | no root match; full normalized title used as fallback |
| `low` | empty / unrecognisable report_nm |

## Output schema (per row)

- `original_report_nm`
- `normalized_base_form`
- `correction_marker_removed`
- `normalization_confidence`

## What this normalization does NOT do

- Does NOT translate Korean to English.
- Does NOT canonicalise reason synonyms (e.g. 우회상장 vs 합병 by reverse merger).
- Does NOT lemmatise or stem.
- Does NOT make any strategy / execution / performance claim.
- Does NOT auto-supersede prior events; supersession is a separate design rule.
