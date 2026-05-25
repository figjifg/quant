# KR-STATUS-PARSER-NONEXTRACTED-LOCAL-TAXONOMY-A0 — Report

Date: 2026-05-26
Phase opened by: Referee directive REF-OPEN-005 (via relay).
Executor: Claude Code. Referee: Codex.

## Phase name and scope

Measurement-layer parser non-extracted LOCAL ROOT-CAUSE TAXONOMY only. suspension_related + resumption_related status rows. Existing local artifacts + cached bodies (read-only) only. No downloads, no API, no body repair, no parser feature expansion / code change / extraction upgrade, no candidate/body rerun, no downstream wiring, no C2/C3, no event-log finalization, no executable-status table, no strategy / performance / execution work.

## Inputs used (paths)

- `reports/experiments/measurement_A0/S2_HTML_INLINE_PARSER_UNIVERSE_RESIDUAL_RECONCILIATION_A0/universe_body_status_reconciled.csv` (the 711 non-extracted rows).
- `reports/experiments/measurement_A0/KR_STATUS_CORRECTION_RESIDUAL_LOCAL_ADJUDICATION_A0/correction_residual_action_ledger.csv` (166 correction ids → 11/7 overlap).
- Cached bodies: `data/acquired/round5_manual_audit_samples/` (read-only).
- Parser read-only helpers extract_body_from_zip / find_label_hits (no parser change). See `prior_phase_input_manifest.md`.

## Exact source counts

- no_label_match: **511**
- label_no_value: **200**
- total: **711**

## Exact correction overlap

- no_label_match correction rows: **11**
- label_no_value correction rows: **7**
- total correction overlap: **18** (all classified `correction_disclosure_manual_only`).

## Exact root-cause counts (sum to 711)

| root_cause_class | count |
|---|---:|
| `only_generic_or_contextual_label` | 499 |
| `label_present_but_attachment_or_table_context_required` | 170 |
| `label_present_but_value_in_unhandled_format` | 23 |
| `correction_disclosure_manual_only` | 18 |
| `title_body_mismatch` | 1 |
| **total** | **711** |

## Method (read-only)

For each row, the cached body was loaded read-only via the parser's `extract_body_from_zip`, and labels re-found via `find_label_hits` (the SAME helpers the parser uses — not modified). Corrections → `correction_disclosure_manual_only` (manual-only regardless of body). no_label_match non-corrections classified by body content (short/malformed; domain-token-present-but-no-exact-label; or off-topic). label_no_value non-corrections classified by the after-label window (relative/unhandled date format; attachment/table context; or empty value).

## Required statements

- Root-cause taxonomy is LOCAL / MANUAL-REVIEW SUPPORT ONLY.
- NO parser behaviour changed (only read-only helpers called).
- NO effective_date was extracted or assigned.
- NO row became parsed, executable, safe, strategy-ready, production-ready, or downstream-authoritative. parse_status + 511/200 split preserved.
- NO downloads / API / body repair occurred.
- NO strategy, backtest, execution simulation, C2/C3, event-log finalization, executable-status table, or production/paper/live/P08/shadow work occurred.

## Defects / residuals (preserved, fail-closed)

- All 711 rows remain non-extracted, manual_review_required, fail-closed.
- The root cause is diagnostic only; a parser-design backlog (`parser_design_backlog_candidates.md`) is DESIGN-ONLY and NOT approved.

## Decision requested from Referee

Executor does NOT self-close. Requesting a verdict among:
- **A.** close as parser non-extracted local taxonomy complete;
- **B.** require another taxonomy pass (refine root-cause heuristics);
- **C.** open a separate parser-design / feasibility phase for one or more root-cause classes (would need its own verdict; parser changes still forbidden until then);
- **D.** keep all strategy / execution research closed (unchanged).
