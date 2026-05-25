# KR-STATUS-CORRECTION-LINKAGE-A0 — Pass 3 Referee Lock

Date: 2026-05-25
Verdict source: Referee verdict opening Pass 3, 2026-05-25.
Pass 1 commit: `3d09033`; Pass 2 commit: `565f0d3` (both accepted as evidence; phase NOT closed).

## State

**PASS 3 REQUIRED / CORRECTION_LINKAGE_REQUIRES_MORE_WORK** — Pass 2 reduced no_link 123→70 and grew the high/medium candidate pool materially, but sample link rate stayed at 55.1% (below 60% bar) and wrong-candidate risk was 12 / 80 = 15%. Pass 3 is a narrower validation-quality pass.

## Pass-3 objective

- Reduce wrong-candidate risk.
- Resolve or better classify the remaining 70 no_link rows.
- Distinguish "no link because source truly absent" vs "no link because scoring too weak".
- Determine whether a sample link rate above 60% is achievable without unacceptable false positives.
- Decide whether correction linkage can become sample-validated, or must remain manual-review-only.

## Pass-3 levers (narrower than Pass 2)

- Stricter scoring penalties:
  - heavy long-window penalty (>365d additional -1.0).
  - raw-pool-only-without-same-base-form additional -1.0.
  - missing paren_reason match when correction has paren_reason -1.0.
  - generic title root -0.5 (e.g. bare `매매거래정지`).
  - cross-category extra -0.5 (on top of the Pass-2 -1.5).
- Body-confirmation requirement:
  - `high_validated` requires body cross-check support (title root OR candidate date in body).
  - if body unavailable → cap at `medium_needs_manual`.
  - if body conflict → `rejected_wrong_candidate`.
- Recalibrated 5-tier confidence enum:
  - `high_validated`, `medium_needs_manual`, `low_needs_manual`, `no_link`, `rejected_wrong_candidate`.

## Pass-3 outputs (12)

1. `pass3_referee_lock.md` (this file)
2. `pass3_wrong_candidate_root_cause.md`
3. `pass3_scoring_variants.csv`
4. `pass3_body_confirmation_rules.md`
5. `pass3_candidate_links_recalibrated.csv`
6. `pass3_remaining_no_link_ledger.csv`
7. `pass3_manual_validation_sample.csv`
8. `pass3_manual_validation_summary.md`
9. `pass3_supersession_readiness.md`
10. `pass3_defect_delta.csv`
11. `pass3_gate_status.md`
12. `pass3_final_summary.md`

## Pass-3 pass-criteria

- Wrong-candidate risk materially reduced or explicitly quarantined.
- High-confidence candidates have low observed false-positive risk.
- Remaining no_link rows well classified.
- Supersession readiness clearly separated from manual_review rows.
- Correction parser output remains non-authoritative.
- Gate status explicitly stated.
- No strategy test / execution sim / performance metric.

## Pass-3 gate enum (Referee-permitted)

- `DATA_SOURCE_FAIL`
- `PARTIAL`
- `CORRECTION_LINKAGE_DESIGNED_BUT_NOT_VALIDATED`
- `CORRECTION_LINKAGE_VALIDATED_FOR_SAMPLE_ONLY`
- `CORRECTION_LINKAGE_REQUIRES_MORE_WORK`
- `READY_FOR_NEXT_A0_REVIEW`

`READY_FOR_NEXT_A0_REVIEW` requires high-confidence links demonstrably safe + low wrong-candidate risk + well-classified no_link + supersession design-only or explicitly gated.

## Pass-1 + Pass-2 artifacts preserved

Pass-1 outputs (12) and Pass-2 outputs (12) remain untouched.

## Hard prohibitions

(Unchanged. See `docs/next_actions.md`.)
