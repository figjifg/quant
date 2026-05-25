# KR-STATUS-CORRECTION-LINKAGE-FULL-UNIVERSE-VALIDATION-A0 — Report

Date: 2026-05-26
Phase opened by: Referee directive REF-OPEN-002 (via relay).
Executor: Claude Code. Referee: Codex.

## Phase name and scope

Measurement-layer correction-linkage FULL-UNIVERSE validation. suspension_related + resumption_related only. Correction-flagged rows + candidate originals only. Existing local artifacts + cached bodies only. No downloads, no API, no acquisition, no parser feature expansion, no downstream wiring, no strategy / performance / execution work.

## Inputs used (paths)

- Cached bodies: `data/acquired/round5_manual_audit_samples/` (read-only).
- Universe + raw pool: pass2 `load_full_universe()` / `load_raw_pool()`.
- Reconciliation baseline: KR_STATUS_CORRECTION_LINKAGE_A0 Pass-3 counts.
- See `prior_phase_input_manifest.md` for the full list.

## Exact in-scope correction row count: **166**

## Cached body-format breakdown

| body_format | count |
|---|---:|
| `html_inline` | 127 |
| `zip_unparseable` | 39 |

## Exact confidence-class counts (post-body, AUTHORITATIVE)

| confidence | count |
|---|---:|
| `high_validated` | 17 |
| `medium_needs_manual` | 52 |
| `low_needs_manual` | 7 |
| `no_link` | 73 |
| `rejected_wrong_candidate` | 17 |
| **total** | **166** |

Counts sum to **166** (gate requires exactly 166).

## Exact source-blocked counts

Source-blocked = body/source could not be cross-checked against the candidate. (`other_manual_review_required` is NOT source-blocked — the body is present and references the candidate, just below the high bar — it is reported under manual-review below.)

| blocked_overlay (source-blocked family) | count |
|---|---:|
| `source_blocked_zip_unparseable` | 39 |
| `source_blocked_non_extracted` | 17 |
| **source-blocked total** | **56** |

Manual-review (body present, not source-blocked):

| blocked_overlay | count |
|---|---:|
| `other_manual_review_required` | 40 |

Note: `source_blocked_non_extracted` = html_inline body present but the candidate's title/date is NOT referenced in the body (maps to the directive's `source_blocked_non_extracted` class; preserves manual-review status). `source_blocked_zip_unparseable` = corrupt cached body (true source defect, overlaps the universe-level 42 zip_unparseable residuals).

## Reconciliation vs prior KR-STATUS-CORRECTION-LINKAGE-A0 (Pass 3)

Prior Pass-3 universe counts were SCORE-ONLY (body gate ran on sample only):
166 = 35 high_validated / 42 medium_needs_manual / 18 low_needs_manual / 71 no_link / 0 rejected_wrong_candidate.

Control check: re-deriving the score-only classifier on all 166 here reproduces Pass 3 EXACTLY:

| confidence | this score-only | Pass-3 | match |
|---|---:|---:|:--:|
| `high_validated` | 35 | 35 | ✓ |
| `medium_needs_manual` | 42 | 42 | ✓ |
| `low_needs_manual` | 18 | 18 | ✓ |
| `no_link` | 71 | 71 | ✓ |
| `rejected_wrong_candidate` | 0 | 0 | ✓ |

Applying the body-confirmation gate full-universe then yields the authoritative post-body counts above.

## Clear explanation of movement between confidence classes

Every row's (score-only → post-body) transition is recorded in `correction_validation_ledger.csv` (`confidence_movement` column). Aggregate transitions (only rows that MOVED):

| score_only → post_body | count |
|---|---:|
| `high_validated → medium_needs_manual` | 12 |
| `low_needs_manual → medium_needs_manual` | 9 |
| `medium_needs_manual → rejected_wrong_candidate` | 8 |
| `high_validated → rejected_wrong_candidate` | 6 |
| `low_needs_manual → no_link` | 3 |
| `medium_needs_manual → low_needs_manual` | 3 |
| `low_needs_manual → rejected_wrong_candidate` | 2 |
| `no_link → rejected_wrong_candidate` | 1 |

Drivers of movement:

- **score-only high_validated → medium/rejected (post-body):** the row's
  candidate was NOT referenced in the (now-available) correction body, or
  the body was `zip_unparseable` (capped below high_validated).
- **score-only high_validated → high_validated:** body confirms the
  candidate title or date (genuine validated link).
- `no_link` is unaffected by body confirmation (no candidate to confirm).

## Supersession readiness count: **17** (design-only)

Supersession is DESIGN-ONLY and NOT wired downstream. Even `supersession_ready = yes` rows remain manual_review_required.

## Confirmations

- medium / low / no_link / blocked rows remain MANUAL-REVIEW-ONLY and are
  NOT authoritative.
- Correction rows are NOT authoritative unless high_validated AND validated
  (link_validated = high_validated = **17**); even those
  stay manual_review_required under the conservative framework.
- All 166 correction rows remain `manual_review_required` (hard lock).
- NO downstream wiring, NO C2/C3, NO execution simulation, NO strategy
  testing occurred. NO downloads / API / acquisition. Cache-only.

## Defects / residuals

- 39 correction rows have `zip_unparseable`
  cached bodies (source defect; cannot body-confirm; capped below
  high_validated; remain manual_review_required). These overlap the
  universe-level 42 zip_unparseable residuals from the reconciliation phase.
- See `defect_ledger.csv` and `no_link_medium_low_root_cause_ledger.csv`.

## Decision requested from Referee

Executor does NOT self-close. Requesting a verdict among:
- **A.** close as correction-linkage full-universe validated (body-gated);
- **B.** require another validation pass (e.g. manual adjudication of the
  source-blocked / non-referenced rows);
- **C.** open a separate residual-source-recovery for the zip_unparseable
  correction bodies (needs its own verdict + download approval);
- **D.** keep all strategy / execution research closed (unchanged).
