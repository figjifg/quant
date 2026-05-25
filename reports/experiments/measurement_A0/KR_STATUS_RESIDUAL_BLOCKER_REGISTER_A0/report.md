# KR-STATUS-RESIDUAL-BLOCKER-REGISTER-A0 — Report

Date: 2026-05-26
Phase opened by: Referee directive REF-OPEN-004 (via relay).
Executor: Claude Code. Referee: Codex.

## Phase name and scope

Measurement-layer residual BLOCKER REGISTER (local artifact consolidation) only. suspension_related + resumption_related status rows. Existing local artifacts only. No downloads, no API, no body repair, no parser feature expansion, no candidate/body rerun, no downstream wiring, no C2/C3, no all-event event-log finalization, no executable-status final table, no strategy / performance / execution work.

## Inputs used (paths)

- `reports/experiments/measurement_A0/S2_HTML_INLINE_PARSER_UNIVERSE_RESIDUAL_RECONCILIATION_A0/universe_body_status_reconciled.csv` (12,187-row universe body status).
- `reports/experiments/measurement_A0/KR_STATUS_CORRECTION_RESIDUAL_LOCAL_ADJUDICATION_A0/correction_residual_action_ledger.csv` (166-row correction residual actions).
- Context: full-universe links + KR_STATUS_CORRECTION_LINKAGE_A0. See `prior_phase_input_manifest.md`.

## Exact row counts from each source artifact

| source artifact | rows | relevant counts |
|---|---:|---|
| universe_body_status_reconciled.csv | 12,187 | extracted 11,434 / no_label_match 511 / label_no_value 200 / body_unavailable(zip) 42 |
| correction_residual_action_ledger.csv | 166 | 17/40/17/37/15/1/39 by action |

## Exact unique rows in the blocker register: **862**

Register key = **`rcept_no`** (combined single key; corrections are status rows, so `correction_rcept_no` == `rcept_no`; `is_correction` flags them). Membership = (universe non-extracted residuals: 42 + 511 + 200 = 753) ∪ (166 correction rows) = 753 + 109 parser-extracted corrections = **862**.

## Exact count by blocker tag (multi-label)

| blocker_tag | count |
|---|---:|
| `manual_review_required` | 862 |
| `parser_no_label_match` | 511 |
| `parser_label_no_value` | 200 |
| `correction_manual_review_required` | 166 |
| `source_zip_unparseable` | 42 |
| `source_recovery_required_separate_approval` | 42 |
| `correction_body_confirmed_below_high` | 40 |
| `correction_no_link_original_not_found` | 37 |
| `correction_high_validated_design_only` | 17 |
| `correction_wrong_candidate_quarantined` | 17 |
| `correction_no_link_insufficient_evidence` | 15 |
| `correction_no_link_cross_category_blocked` | 1 |

## Exact overlap counts

| residual set | count | notes |
|---|---:|---|
| universe zip_unparseable | 42 | tag `source_zip_unparseable` |
| └ correction zip_unparseable subset | 39 | ⊂ 42; 3 universe-zip are non-correction |
| no_label_match | 511 | of which 11 are corrections |
| label_no_value | 200 | of which 7 are corrections |
| correction manual-review rows | 166 | all `correction_manual_review_required` |
| └ correction parser-extracted (clean body, still manual-review) | 109 | added to register |

## Overlap matrix (universe parse_status × correction action / not_correction)

| universe_parse_status | correction_action_or_not | count |
|---|---|---:|
| `body_unavailable` | `not_correction` | 3 |
| `body_unavailable` | `zip_unparseable_requires_source_recovery` | 39 |
| `extracted` | `accepted_high_validated_design_only` | 15 |
| `extracted` | `body_confirms_candidate_but_below_high` | 34 |
| `extracted` | `no_link_insufficient_evidence` | 11 |
| `extracted` | `no_link_original_not_found` | 34 |
| `extracted` | `rejected_wrong_candidate_quarantined` | 15 |
| `label_no_value` | `body_confirms_candidate_but_below_high` | 3 |
| `label_no_value` | `no_link_insufficient_evidence` | 1 |
| `label_no_value` | `no_link_original_not_found` | 3 |
| `label_no_value` | `not_correction` | 193 |
| `no_label_match` | `accepted_high_validated_design_only` | 2 |
| `no_label_match` | `body_confirms_candidate_but_below_high` | 3 |
| `no_label_match` | `no_link_cross_category_blocked` | 1 |
| `no_label_match` | `no_link_insufficient_evidence` | 3 |
| `no_label_match` | `not_correction` | 500 |
| `no_label_match` | `rejected_wrong_candidate_quarantined` | 2 |

## Register key explanation

The register is **row-level by `rcept_no`** (a single combined key). Corrections share the same key space; `is_correction=True` distinguishes them. A row may carry multiple blocker tags (e.g. a correction whose body is zip_unparseable carries `source_zip_unparseable` + `source_recovery_required_separate_approval` + `correction_manual_review_required` + `manual_review_required`).

## This is NOT ...

- NOT an event log / all-event finalization.
- NOT an executable-status table.
- NOT downstream wiring / C2 / C3.
It is a local register that preserves residual-blocker + manual-review state.

## Confirmations

- All blockers are FAIL-CLOSED: every register row has manual_review_required=True, executable_or_safe=False, downstream_authoritative=False, parsed_clean_and_usable=False, strategy_ready=False, production_ready=False.
- No downloads / API / body repair occurred (pure read of local CSVs).
- No strategy, backtest, execution simulation, C2/C3, or production/paper/live/P08/shadow work occurred.
- The 39 correction zip rows reconcile exactly as a subset of the 42 universe zip rows.

## Defects / residuals (preserved, fail-closed)

- 42 zip_unparseable (source defects; source recovery needs separate verdict + download approval).
- 511 no_label_match + 200 label_no_value (usable html_inline but non-extracted; manual review only).
- 166 correction rows (all manual_review_required; non-authoritative).

## Decision requested from Referee

Executor does NOT self-close. Requesting a verdict among:
- **A.** close as residual blocker register complete;
- **B.** require another consolidation pass (refine tags / policy / packet);
- **C.** open a separate residual-source-recovery for the 42 zip_unparseable rows (needs its own verdict + download approval);
- **D.** keep all strategy / execution research closed (unchanged).
