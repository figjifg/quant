# D3b Custom Parser Decision

Date: 2026-05-23 15:32:39
Scope: feasibility decision only. NO custom parser implementation per Referee.

## Question 1: ACODE 11324 / 11325 need custom parsers?

- v3 parser amount_krw extraction (D3b): 23.5% (with current generic + ACODE-specific keyword stack)
- v3 parser conversion_price extraction: 29.4%
- v3 parser shares extraction: 5.9% (below v1 baseline 29.4%)
- v3 parser event_date extraction: 0.0%

These ACODEs use multi-tier `<TABLE>` structures where:
- `(A)` and `(B)` annotation columns split values between '대상자별' and aggregate rows
- `1차/2차/3차` columns expand into multi-period series
- Some target labels (event_date in particular) sit in `<COVER>` text, NOT in any `<TABLE>` row

**Decision: YES** — ACODE 11324 and 11325 need form-specific custom parsers that:
1. parse `<COVER>` / `<SECTION>` text for event_date (이사회 결의(결정)일 free-text date)
2. handle `(A)` / `(B)` annotation columns explicitly
3. dispatch on 'mass발행' vs '특정인 대상자' structure

## Question 2: conversion_request without ACODE needs separate parser family?

- conversion_request samples in D1+D2: 6 rows
- ACODE field on these rows in v3 audit trail: typically None (form '전환청구권행사' is published under different form code)

**Decision: YES** — conversion_request needs its own parser family because:
- No ACODE → cannot dispatch via ACODE_HINTS map
- 회차 marker `(제N회차)` is critical and resides in report_nm, not body
- 전환청구일 / 청구일 typically appear as label-value but in a smaller, simpler table than CB/BW

## Question 3: SECTION/COVER text scanner required?

- v3 audit shows event_date 0% on D3b — root cause: in CB/BW 발행결정 body, event_date (이사회결의일) often lives in `<COVER>` block as free-text date, not in a table.

**Decision: YES** — A SECTION/COVER text scanner is required for D3b event_date. Pattern target:
  `이사회\s*결의(결정)?일\s*[:\s]*(\d{4})[년\.\-]\s*(\d{1,2})[월\.\-]\s*(\d{1,2})`

## Estimated effort for D3b custom parser stack

| Component | Estimated effort |
|---|---|
| ACODE 11324 (CB) custom parser | 1-2 weeks |
| ACODE 11325 (BW) custom parser | 1-2 weeks (similar to CB) |
| conversion_request parser family | 1 week |
| SECTION/COVER text scanner | 3-5 days |
| Manual audit on 20-50 samples per type | 1-2 weeks user time |
| **Total** | **4-7 weeks** |

## Compliance

- This document is a FEASIBILITY decision only. No custom parser implementation per Referee restriction.
- No strategy / no return outcome / no parser-strategy-ready language.
- Referee approval required before implementing.