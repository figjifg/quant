# KR-STATUS-CORRECTION-RESIDUAL-LOCAL-ADJUDICATION-A0 — Report

Date: 2026-05-26
Phase opened by: Referee directive REF-OPEN-003 (via relay).
Executor: Claude Code. Referee: Codex.

## Phase name and scope

Measurement-layer residual ADJUDICATION PACKET only. suspension_related + resumption_related correction rows. Existing local artifacts only. No new downloads, no API, no body repair, no parser feature expansion, no downstream supersession wiring, no C2/C3, no strategy / performance / execution work. This is NOT residual-source recovery.

## Inputs used (paths)

- `reports/experiments/measurement_A0/KR_STATUS_CORRECTION_LINKAGE_FULL_UNIVERSE_VALIDATION_A0/correction_full_universe_links.csv` (166-row accepted links).
- `reports/experiments/measurement_A0/KR_STATUS_CORRECTION_LINKAGE_FULL_UNIVERSE_VALIDATION_A0/no_link_medium_low_root_cause_ledger.csv` (accepted no_link/medium/low root causes).
- See `prior_phase_input_manifest.md`.

## Exact total rows reconciled: **166**

## Counts by accepted 5-tier confidence class

| confidence | count |
|---|---:|
| `high_validated` | 17 |
| `medium_needs_manual` | 52 |
| `low_needs_manual` | 7 |
| `no_link` | 73 |
| `rejected_wrong_candidate` | 17 |
| **total** | **166** |

## Counts by residual action class (sum to 166)

| residual_action_class | count |
|---|---:|
| `body_confirms_candidate_but_below_high` | 40 |
| `zip_unparseable_requires_source_recovery` | 39 |
| `no_link_original_not_found` | 37 |
| `accepted_high_validated_design_only` | 17 |
| `rejected_wrong_candidate_quarantined` | 17 |
| `no_link_insufficient_evidence` | 15 |
| `no_link_cross_category_blocked` | 1 |
| **total** | **166** |

## Explicit reconciliation to 166 correction rows

- 5-tier sum = 166; action-class sum = 166. Both = 166.
- Every row carries exactly one accepted 5-tier class AND exactly one residual action class (see cross-tab below + `correction_residual_action_ledger.csv`).

## Explicit reconciliation to prior accepted counts (17 / 52 / 7 / 73 / 17)

| confidence | this phase | prior accepted | match |
|---|---:|---:|:--:|
| `high_validated` | 17 | 17 | ✓ |
| `medium_needs_manual` | 52 | 52 | ✓ |
| `low_needs_manual` | 7 | 7 | ✓ |
| `no_link` | 73 | 73 | ✓ |
| `rejected_wrong_candidate` | 17 | 17 | ✓ |

## Confidence → residual-action mapping (cross-tab)

Note the priority rule: a `zip_unparseable` cached body routes the row to `zip_unparseable_requires_source_recovery` regardless of its tentative 5-tier (it cannot be locally adjudicated without the body). This is why the 39 zip rows are pulled out of their medium/low/no_link buckets.

| confidence_5tier | residual_action_class | count |
|---|---|---:|
| `high_validated` | `accepted_high_validated_design_only` | 17 |
| `low_needs_manual` | `zip_unparseable_requires_source_recovery` | 7 |
| `medium_needs_manual` | `body_confirms_candidate_but_below_high` | 40 |
| `medium_needs_manual` | `zip_unparseable_requires_source_recovery` | 12 |
| `no_link` | `no_link_cross_category_blocked` | 1 |
| `no_link` | `no_link_insufficient_evidence` | 15 |
| `no_link` | `no_link_original_not_found` | 37 |
| `no_link` | `zip_unparseable_requires_source_recovery` | 20 |
| `rejected_wrong_candidate` | `rejected_wrong_candidate_quarantined` | 17 |

## Confirmations (required by directive)

- The 39 zip_unparseable rows were NOT downloaded or repaired — they receive a recovery-REQUIREMENTS ledger only (`zip_unparseable_recovery_requirements.csv`, recovery_performed=False).
- The 17 rejected_wrong_candidate rows remain QUARANTINED (`rejected_wrong_candidate_adjudication.csv`); none silently dropped.
- no_link / medium / low rows remain MANUAL-REVIEW-ONLY and NOT authoritative.
- high_validated remains DESIGN-LEVEL ONLY and manual_review_required.
- Supersession is NOT wired downstream (supersession_wired=False on all rows).
- NO strategy, backtest, execution simulation, C2/C3, or production/paper/live/P08/shadow work occurred.

## Defects / residuals

- 39 zip_unparseable correction bodies (source defects; recovery requires a separate verdict + download approval; overlap the universe-level 42 zip_unparseable residuals).
- 17 rejected_wrong_candidate rows (scored but body-unconfirmed).
- 37 no_link_original_not_found + 15 no_link_insufficient_evidence + 1 no_link_cross_category_blocked.

## Decision requested from Referee

Executor does NOT self-close. Requesting a verdict among:
- **A.** close as residual adjudication packet complete;
- **B.** require another adjudication pass (refine action classes / packet);
- **C.** open a separate residual-source-recovery for the 39 zip_unparseable correction bodies (needs its own verdict + download approval);
- **D.** keep all strategy / execution research closed (unchanged).
