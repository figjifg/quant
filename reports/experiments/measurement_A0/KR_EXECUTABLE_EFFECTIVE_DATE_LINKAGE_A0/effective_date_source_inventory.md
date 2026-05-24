# Effective-Date Source Inventory

Date: 2026-05-25  
Phase: KR-EXECUTABLE-EFFECTIVE-DATE-LINKAGE-A0

## Candidate methods for determining actual effective status date

| method | classification | description |
|---|---|---|
| `report_nm` date hints | `title_date_hint` | report_nm may contain explicit dates (e.g., '거래정지(YYYY-MM-DD)') or period markers |
| DART document.xml body | `official_body_date` | document body may include 효력발생일 / 정지일 / 해제일 / 폐지일 / 정리매매기간 fields |
| Attachment / document title | `title_date_hint` | attachment titles often include 'YYYY.MM.DD' format date hints |
| Linked correction reports | `correction_linkage` | a `[기재정정]` report may carry the actual effective date that the original report omitted |
| KRX official-status event wording | `title_date_hint` + body | many KRX events have boilerplate Korean phrases linking to specific dates |
| Listed-universe terminal date (W001 v2) | `lifecycle_terminal_context` | terminal_date is derived from S3 events; circular for delisting linkage |
| Panel / OHLCV date | `panel_context_only` | NOT proof of effective date; supporting context only |
| (unavailable for some) | `unavailable` | no extractable date hint anywhere |
| (manual review required) | `requires_manual_review` | text indicates a date but format is ambiguous |

## Method priority (highest → lowest)

1. **`official_body_date`** (DART document.xml extractable date) — authoritative
   when available; subject to S2 body-parser limitations (CLOSED AS PARTIAL).
2. **`title_date_hint`** (date in report_nm or attachment title) — usable
   with regex extraction but may be ambiguous (filing date vs effective
   date vs reference date).
3. **`correction_linkage`** — only when the corrected report explicitly
   updates the prior date.
4. **`lifecycle_terminal_context`** — circular for delisting; useful only
   as cross-validation, not as primary source.
5. **`panel_context_only`** — NOT proof; only supporting.

## Hard rules

- `rcept_dt` MUST NOT be used as effective date by default.
- Panel / OHLCV date MUST NOT be used as primary effective-date evidence.
- `unavailable` / `requires_manual_review` MUST remain unknown — downstream
  code MUST NOT silently default to executable.
