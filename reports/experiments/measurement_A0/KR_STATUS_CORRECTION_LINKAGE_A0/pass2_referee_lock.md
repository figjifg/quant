# KR-STATUS-CORRECTION-LINKAGE-A0 — Pass 2 Referee Lock

Date: 2026-05-25
Verdict source: Referee verdict opening Pass 2, 2026-05-25.
Pass 1 commit: `3d09033` (accepted as pass-1 evidence; phase NOT closed).

## State

**PASS 2 REQUIRED / CORRECTION_LINKAGE_REQUIRES_MORE_WORK** — pass 1 found 53.3%
sample link rate and 123 / 166 no_link at default 180-day window. Candidate-search
expansion required before any close decision.

## Pass-2 scope

- Measurement-layer correction-linkage A0 only.
- suspension_related + resumption_related only.
- HTML-inline status disclosures only.
- correction-flagged rows + candidate originals only.

## Pass-2 objective

Diagnose & reduce the 123 no_link cases. Test causes:

1. overly narrow search universe,
2. insufficient window,
3. cross-category original events,
4. corp_code / stock_code gaps,
5. title normalization weakness,
6. attachment-only / body-only original references,
7. genuinely unlinked correction disclosures.

## Pass-2 expansion levers

- Raw OPENDART pblntfty=I pool (~726k rows: 300,829 pre-2018 + 425,294 post-2018).
- Cross-category compatibility matrix:
  - correction suspension → original suspension / delisting / liquidation / managed
    / short_term_overheated / other, with token gates.
  - correction resumption → original resumption / suspension / other.
- Window sensitivity: 30 / 90 / 180 / 365 / 730 days.
- Matching feature additions: corp_name_norm match, event_type_compat (compatible
  roots), proximity score, title similarity.

## Pass-2 pass-criteria

- The no_link population is materially explained, even if not fully resolved.
- Candidate search expansion is tested transparently.
- Manual validation sample link rate improves above Pass 1 OR the failure mode is
  clearly explained.
- Cross-category linkage necessity is quantified.
- Wrong-candidate risk is measured.
- Parser correction interaction remains safe.
- Supersession rules remain design-only.
- Gate status explicitly stated.
- No strategy test / execution sim / performance metric produced.

## Pass-2 gate enum (Referee-permitted)

- `DATA_SOURCE_FAIL`
- `PARTIAL`
- `CORRECTION_LINKAGE_DESIGNED_BUT_NOT_VALIDATED`
- `CORRECTION_LINKAGE_VALIDATED_FOR_SAMPLE_ONLY`
- `CORRECTION_LINKAGE_REQUIRES_MORE_WORK`
- `READY_FOR_NEXT_A0_REVIEW`

`READY_FOR_NEXT_A0_REVIEW` may only be claimed if (a) sample link rate materially
improves, (b) wrong-candidate risk is low, (c) no_link root causes are
well-classified, (d) correction rows remain safely blocked from authoritative use.

## Pass-2 outputs (12)

1. `pass2_referee_lock.md` (this file)
2. `pass2_expanded_candidate_pool.md`
3. `pass2_candidate_links.csv`
4. `pass2_window_sensitivity.csv`
5. `pass2_cross_category_matrix.md`
6. `pass2_no_link_root_cause_ledger.csv`
7. `pass2_manual_validation_sample.csv`
8. `pass2_manual_validation_summary.md`
9. `pass2_link_scoring_update.md`
10. `pass2_defect_delta.csv`
11. `pass2_gate_status.md`
12. `pass2_final_summary.md`

## Pass-1 artifacts preserved

Pass-1 outputs (12 files) remain in place untouched. Pass-2 adds new files only.

## Hard prohibitions

(Unchanged. See `docs/next_actions.md`.)
