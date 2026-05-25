# Pass-3 Body-Confirmation Rules

Date: 2026-05-25
Phase: KR-STATUS-CORRECTION-LINKAGE-A0 (Pass 3)

## Rationale

Pass-2 manual validation found 12 / 80 (15%) rows where score-based
`link_confidence` was `high` or `medium` but the correction body did NOT
contain the candidate's title root or date. These rows constitute the
"wrong-candidate risk" — scoring suggests a link but the document body does
not support it.

Pass-3 introduces a body-confirmation gate.

## Pass-3 confidence rules (5-tier)

| confidence | conditions |
|---|---|
| `high_validated` | (same_corp ∨ same_stock) ∧ event_type_compat ∧ same_base_form ∧ margin ≥ 1.5 ∧ title_similarity ≥ 0.60 ∧ NOT cross_category ∧ body_format = html_inline ∧ (body_refs_title ∨ body_refs_date) |
| `medium_needs_manual` | (same_corp ∨ same_stock) ∧ event_type_compat ∧ (body partial confirm OR body unavailable with strong score) |
| `low_needs_manual` | (same_corp ∨ same_stock) ∧ title_similarity ≥ 0.30 ∧ body unavailable |
| `no_link` | otherwise |
| `rejected_wrong_candidate` | body retrievable AND body cross-check FAILED AND score was high; or body date conflicts with candidate |

## Body cross-check definitions

- `body_refs_title`: candidate `event_type` token appears in correction body text.
- `body_refs_date`: candidate `rcept_dt_iso` appears in correction body text
  (8-digit form, hyphenated form, or Korean form `YYYY년 M월 D일`).
- `body_conflict`: correction body contains an explicit date for the candidate's
  field that disagrees with the candidate's `rcept_dt`. (Heuristic — not run in
  this Pass.)
- `body_unavailable`: zip download failed OR primary doc was not html_inline.

## What body-confirmation does NOT do

- Does NOT re-extract `effective_date` for downstream use.
- Does NOT mark `high_validated` rows as authoritative for strategy / execution.
- Does NOT promote any link without manual review of supersession candidates.
- Does NOT change parser behaviour on correction rows.
- Does NOT wire into any production / paper / live / P08 / shadow code path.

## What body-confirmation DOES do

- Demotes plausible-by-score-but-unsupported-by-body candidates to
  `rejected_wrong_candidate` to materially reduce wrong-candidate risk.
- Lets the gate state better distinguish "validated-for-sample" from
  "requires-more-work".
