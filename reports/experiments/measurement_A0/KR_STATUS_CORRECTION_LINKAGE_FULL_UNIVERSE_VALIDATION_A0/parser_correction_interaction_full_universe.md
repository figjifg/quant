# Parser–Correction Interaction (Full Universe)

Date: 2026-05-26
Phase: KR-STATUS-CORRECTION-LINKAGE-FULL-UNIVERSE-VALIDATION-A0

## Confirmation (unchanged from Pass 3, re-checked full-universe)

- All **166** in-scope rows are correction-flagged (`is_correction = True`); the
  parser's correction detection fired on **166 / 166**.
- The parser (`krx_status_html_inline-1.1.0`) still forces
  `manual_review_required = True` on every correction row.
- Correction-row parser output is **NOT authoritative by default**.
- This phase did NOT change parser behaviour. The body-confirmation gate is an
  AUDIT overlay; it does not re-extract `effective_date` for downstream use and
  does not promote any correction row to executable / strategy-ready.

## What body-confirmation does here

- For each correction row it inspects the CACHED body (read-only) for a reference
  to the linked candidate's title token or date.
- `high_validated` requires an html_inline body that references the candidate.
- Body `zip_unparseable` / non-html / missing-cache → capped below high_validated
  and flagged source-blocked; remains manual_review_required.

## What body-confirmation still does NOT do

- Does NOT re-extract effective_date for downstream use.
- Does NOT mark any correction row authoritative / executable / strategy-ready.
- Does NOT wire supersession downstream (design-only).
- Does NOT change parser code or shared production code.
