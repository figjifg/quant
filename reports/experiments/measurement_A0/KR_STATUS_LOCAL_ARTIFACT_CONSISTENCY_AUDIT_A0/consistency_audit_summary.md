# KR-STATUS-LOCAL-ARTIFACT-CONSISTENCY-AUDIT-A0 — Summary

Date: 2026-05-26
Opened by REF-OPEN-007 (via relay).


## Phase name and scope

Measurement-layer LOCAL ARTIFACT CONSISTENCY AUDIT only. Reads existing local reports / CSV / CLOSE_NOTE / docs/next_actions.md. No new data. No downloads / API / credentials / body repair / parser change / rerun / downstream wiring / C2-C3 / event-log / executable-status table / strategy / execution.

## Phase directories audited

- `S2_HTML_INLINE_PARSER_UNIVERSE_RESIDUAL_RECONCILIATION_A0`
- `KR_STATUS_CORRECTION_LINKAGE_FULL_UNIVERSE_VALIDATION_A0`
- `KR_STATUS_CORRECTION_RESIDUAL_LOCAL_ADJUDICATION_A0`
- `KR_STATUS_RESIDUAL_BLOCKER_REGISTER_A0`
- `KR_STATUS_PARSER_NONEXTRACTED_LOCAL_TAXONOMY_A0`
- `KR_STATUS_SOURCE_RECOVERY_CANDIDATE_MANIFEST_A0`

## Count reconciliation (recomputed from source CSVs vs canonical)

| metric | source phase | observed | canonical | match |
|---|---|---:|---:|:--:|
| universe_rows | UNIVERSE_RESIDUAL_RECONCILIATION | 12187 | 12187 | PASS |
| usable_html_inline | UNIVERSE_RESIDUAL_RECONCILIATION | 12145 | 12145 | PASS |
| zip_unparseable | UNIVERSE_RESIDUAL_RECONCILIATION | 42 | 42 | PASS |
| no_label_match | UNIVERSE_RESIDUAL_RECONCILIATION | 511 | 511 | PASS |
| label_no_value | UNIVERSE_RESIDUAL_RECONCILIATION | 200 | 200 | PASS |
| correction_rows | CORRECTION_LINKAGE_FULL_UNIVERSE_VALIDATION | 166 | 166 | PASS |
| correction_rows | CORRECTION_RESIDUAL_LOCAL_ADJUDICATION | 166 | 166 | PASS |
| blocker_register_rows | RESIDUAL_BLOCKER_REGISTER | 862 | 862 | PASS |
| zip_unparseable | RESIDUAL_BLOCKER_REGISTER | 42 | 42 | PASS |
| correction_zip_subset | RESIDUAL_BLOCKER_REGISTER | 39 | 39 | PASS |
| non_correction_zip_subset | RESIDUAL_BLOCKER_REGISTER | 3 | 3 | PASS |
| no_label_match | RESIDUAL_BLOCKER_REGISTER | 511 | 511 | PASS |
| label_no_value | RESIDUAL_BLOCKER_REGISTER | 200 | 200 | PASS |
| parser_nonextracted_rows | PARSER_NONEXTRACTED_LOCAL_TAXONOMY | 711 | 711 | PASS |
| no_label_match | PARSER_NONEXTRACTED_LOCAL_TAXONOMY | 511 | 511 | PASS |
| label_no_value | PARSER_NONEXTRACTED_LOCAL_TAXONOMY | 200 | 200 | PASS |
| zip_unparseable | SOURCE_RECOVERY_CANDIDATE_MANIFEST | 42 | 42 | PASS |
| correction_zip_subset | SOURCE_RECOVERY_CANDIDATE_MANIFEST | 39 | 39 | PASS |
| non_correction_zip_subset | SOURCE_RECOVERY_CANDIDATE_MANIFEST | 3 | 3 | PASS |

## Derived identities

| identity | lhs | rhs | match |
|---|---|---:|:--:|
| parser_nonextracted = no_label_match + label_no_value | 511+200=711 | 711 | PASS |
| zip = correction_zip + non_correction_zip | 39+3=42 | 42 | PASS |
| blocker_register = 753 universe-residual + 109 extracted-correction | 753+109=862 | 862 | PASS |
| universe = usable_html_inline + zip_unparseable | 12145+42=12187 | 12187 | PASS |

## Pass/fail results

| check | result |
|---|---|
| artifact presence | PASS |
| row-count consistency | PASS |
| derived-identity consistency | PASS |
| CLOSE_NOTE consistency | PASS |
| docs/next_actions.md consistency (this phase Active) | PASS |
| hard-lock phrase audit | PASS |

## Hard-lock phrase audit: 175 trigger-token lines scanned; **0** affirmative scope-drift lines flagged.

## Consistency defects: **0**

No inconsistencies found. The 6 recently-closed local artifacts reconcile exactly to the canonical counts and carry no affirmative scope-drift wording.

## Confirmations

- No downloads / API / body repair / parser change occurred.
- No strategy, backtest, execution simulation, C2/C3, event-log finalization, executable-status table, or production/paper/live/P08/shadow work occurred.
