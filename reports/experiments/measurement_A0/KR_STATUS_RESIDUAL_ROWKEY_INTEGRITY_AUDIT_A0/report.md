# KR-STATUS-RESIDUAL-ROWKEY-INTEGRITY-AUDIT-A0 — Report

Date: 2026-05-26
Phase opened by: Referee directive REF-OPEN-008 (via relay).
Executor: Claude Code. Referee: Codex.

## Phase name and scope

Local row-key (rcept_no) integrity audit only. Verifies the accepted count locks hold at the SET level (exact rcept_no set equality + duplicate-key + union/overlap), not merely as aggregate counts. Existing local CSV/MD only; no new data; no edits to closed artifacts; mismatches recorded not patched; no CLOSE_NOTE (executor does not self-close).

## Input artifacts used

- `reports/experiments/measurement_A0/S2_HTML_INLINE_PARSER_UNIVERSE_RESIDUAL_RECONCILIATION_A0/universe_body_status_reconciled.csv`
- `reports/experiments/measurement_A0/KR_STATUS_CORRECTION_LINKAGE_FULL_UNIVERSE_VALIDATION_A0/correction_full_universe_links.csv`
- `reports/experiments/measurement_A0/KR_STATUS_CORRECTION_RESIDUAL_LOCAL_ADJUDICATION_A0/correction_residual_action_ledger.csv`
- `reports/experiments/measurement_A0/KR_STATUS_RESIDUAL_BLOCKER_REGISTER_A0/residual_blocker_register.csv`
- `reports/experiments/measurement_A0/KR_STATUS_PARSER_NONEXTRACTED_LOCAL_TAXONOMY_A0/parser_nonextracted_taxonomy_ledger.csv`
- `reports/experiments/measurement_A0/KR_STATUS_SOURCE_RECOVERY_CANDIDATE_MANIFEST_A0/source_recovery_candidate_manifest.csv`

## Duplicate-key results

| ledger | key | rows | unique | duplicates | result |
|---|---|---:|---:|---:|---|
| universe_body_status_reconciled | rcept_no | 12187 | 12187 | 0 | PASS |
| correction_full_universe_links | correction_rcept_no | 166 | 166 | 0 | PASS |
| correction_residual_action_ledger | correction_rcept_no | 166 | 166 | 0 | PASS |
| residual_blocker_register | rcept_no | 862 | 862 | 0 | PASS |
| parser_nonextracted_taxonomy_ledger | rcept_no | 711 | 711 | 0 | PASS |
| source_recovery_candidate_manifest | rcept_no | 42 | 42 | 0 | PASS |

## Row-key SET reconciliation (exact set equality)

| set check | expected | sets | sizes | set equality |
|---|---:|---|---|---|
| zip_unparseable_set_42 | 42 | universe == register == manifest | 42/42/42 | PASS |
| correction_zip_set_39 | 39 | adjudication == register == manifest | 39/39/39 | PASS |
| non_correction_zip_set_3 | 3 | register == manifest | 3/3 | PASS |
| parser_nonextracted_set_711 | 711 | universe == register == taxonomy | 711/711/711 | PASS |
| correction_set_166 | 166 | links == adjudication == register | 166/166/166 | PASS |

## Subset matrix

| child set | parent set | child | parent | subset? | n outside |
|---|---|---:|---:|---|---:|
| correction_zip_39 | zip_42 | 39 | 42 | PASS | 0 |
| non_correction_zip_3 | zip_42 | 3 | 42 | PASS | 0 |
| zip_42 | body_unavailable_universe | 42 | 42 | PASS | 0 |
| correction_166 | register_all_862 | 166 | 862 | PASS | 0 |
| parser_nonextracted_711 | register_all_862 | 711 | 862 | PASS | 0 |
| zip_42 | register_all_862 | 42 | 862 | PASS | 0 |

## 862 register union (overlap preserved, not double-counted)

| component | size |
|---|---:|
| U_753 (universe non-extracted: no_label+label_no_value+zip) | 753 |
| correction_166 (register correction subset) | 166 |
| overlap (corrections that are also universe non-extracted) | 57 |
| union = 753 + 166 - overlap | 862 |
| register_all | 862 |
| union == register_all | PASS |

Overlap (corrections that are also universe non-extracted) by parse_status: {'body_unavailable': 39, 'label_no_value': 7, 'no_label_match': 11} (expected: body_unavailable 39 + no_label_match 11 + label_no_value 7 = 57).

## Status / safety consistency (no row-key mismatch silently changes status)

| check | shared/rows | disagreements | result |
|---|---:|---:|---|
| parse_status agree universe vs register (shared keys) | 862 | 0 | PASS |
| parse_status agree universe vs taxonomy (shared keys) | 711 | 0 | PASS |
| register.manual_review_required all == True | 862 | 0 | PASS |
| register.executable_or_safe all == False | 862 | 0 | PASS |
| register.downstream_authoritative all == False | 862 | 0 | PASS |
| taxonomy.manual_review_required all == True | 711 | 0 | PASS |
| taxonomy.executable_or_safe all == False | 711 | 0 | PASS |
| taxonomy.downstream_authoritative all == False | 711 | 0 | PASS |
| manifest.manual_review_required all == True | 42 | 0 | PASS |
| manifest.executable_or_safe all == False | 42 | 0 | PASS |
| manifest.downstream_authoritative all == False | 42 | 0 | PASS |

## Overall result

- duplicate-key: PASS
- set reconciliation: PASS
- subset matrix: PASS
- 862 union/overlap: PASS
- status/safety consistency: PASS
- **total mismatches recorded: 0**

**CLEAN PASS — the accepted count locks hold at the rcept_no SET level.**

## Confirmations

- No downloads / API / credentials / body repair / parser change / rerun.
- No candidate / body confirmation rerun; no source recovery; no parser-design.
- No edits to prior closed-phase outputs; mismatches recorded not patched.
- No CLOSE_NOTE created. No strategy / execution / C2-C3 / event-log / executable-status table / production / paper / live / P08 / shadow work.

## Decision requested from Referee

Executor does NOT self-close. Requesting a verdict among:
- **A.** close as row-key integrity audit complete (locks hold at set level);
- **B.** require another integrity pass (widen checks / add ledgers);
- **C.** authorize correction of a recorded row-key mismatch (would target a closed phase's artifact — needs explicit approval; none found this pass);
- **D.** keep all strategy / execution research closed (unchanged).
