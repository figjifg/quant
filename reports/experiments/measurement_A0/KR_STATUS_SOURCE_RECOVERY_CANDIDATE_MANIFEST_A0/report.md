# KR-STATUS-SOURCE-RECOVERY-CANDIDATE-MANIFEST-A0 — Report

Date: 2026-05-26
Phase opened by: Referee directive REF-OPEN-006 (via relay).
Executor: Claude Code. Referee: Codex.

## Phase name and scope

Measurement-layer source-recovery candidate MANIFEST (local artifact consolidation) only. The 42 source_zip_unparseable rows (39 correction + 3 non-correction). Existing local artifacts only. No downloads, no API, no credentials, no body repair, no file replacement, no parser feature expansion / code change, no candidate/body rerun, no downstream wiring, no C2/C3, no event-log finalization, no executable-status table, no strategy / performance / execution work. THIS IS NOT RECOVERY.

## Inputs used (paths)

- `reports/experiments/measurement_A0/KR_STATUS_RESIDUAL_BLOCKER_REGISTER_A0/residual_blocker_register.csv` (the 42 zip rows).
- `reports/experiments/measurement_A0/S2_HTML_INLINE_PARSER_UNIVERSE_RESIDUAL_RECONCILIATION_A0/universe_residual_ledger.csv` (rcept_dt / event_category / source_period / reason).
- `reports/experiments/measurement_A0/KR_STATUS_CORRECTION_RESIDUAL_LOCAL_ADJUDICATION_A0/correction_residual_action_ledger.csv` + `reports/experiments/measurement_A0/KR_STATUS_CORRECTION_LINKAGE_FULL_UNIVERSE_VALIDATION_A0/correction_full_universe_links.csv` (correction action class / corp_name / underlying 5-tier).
- See `prior_phase_input_manifest.md`.

## Exact source counts

- source_zip_unparseable: **42**
- correction zip subset: **39**
- non-correction zip: **3**

## Exact correction action-class distribution among the 39 correction zip rows

| correction_action_class | count |
|---|---:|
| `zip_unparseable_requires_source_recovery` | 39 |

Underlying linkage confidence (had bodies been readable) of the 39 correction rows (context only):

| underlying_confidence_5tier | count |
|---|---:|
| `no_link` | 20 |
| `medium_needs_manual` | 12 |
| `low_needs_manual` | 7 |

## Full counts

| dimension | key | count |
|---|---|---:|
| total | all | 42 |
| is_correction | correction | 39 |
| is_correction | non_correction | 3 |
| event_category | suspension_related | 23 |
| event_category | resumption_related | 19 |
| source_period | pre_2018 | 25 |
| source_period | post_2018 | 17 |
| correction_action_class (39) | zip_unparseable_requires_source_recovery | 39 |
| underlying_5tier (39 corr) | no_link | 20 |
| underlying_5tier (39 corr) | medium_needs_manual | 12 |
| underlying_5tier (39 corr) | low_needs_manual | 7 |

## Recovery boundary flags (all 42)

- recovery_required=True; **recovery_performed=False**;
  **requires_separate_verdict=True**; **requires_download_approval=True**;
  **safe_for_current_use=False**.

## Confirmations (required by directive)

- recovery_performed=False for ALL 42.
- NO download / API / credential / body repair occurred (pure read of local CSVs).
- Every row remains fail-closed: manual_review_required=True, executable_or_safe=False, downstream_authoritative=False, parsed_clean_and_usable=False, strategy_ready=False, production_ready=False, safe_for_current_use=False.
- This is a LOCAL MANIFEST ONLY, NOT recovery.
- FUTURE recovery requires a separate Referee verdict PLUS explicit download approval.
- NO parser behaviour changed; NO row became parsed / extracted / safe.
- NO strategy, backtest, execution simulation, C2/C3, event-log finalization, executable-status table, or production/paper/live/P08/shadow work occurred.

## Defects / residuals (preserved, fail-closed)

- 42 corrupt cached document.xml ZIPs (BadZipFile). Locally irrecoverable (no body text to inspect); MUST be re-fetched from source under a future approved recovery. Overlap the universe-level 42 zip_unparseable residuals (REF-CLOSE-001).

## Decision requested from Referee

Executor does NOT self-close. Requesting a verdict among:
- **A.** close as source-recovery candidate manifest complete;
- **B.** require another manifest pass (refine metadata / schema / packet);
- **C.** open an actual source-recovery phase for the 42 zip rows (would need its own verdict + explicit download/API approval — NOT requested here);
- **D.** keep all strategy / execution research closed (unchanged).
