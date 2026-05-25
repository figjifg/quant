# Measurement-A0 Key Locks

Date: 2026-05-26
Phase: KR-STATUS-MEASUREMENT-A0-HANDOFF-STATE-MANIFEST-A0

Accepted locks across the closed measurement-layer chain (verified across
three independent dimensions + the packet/worklist surface):

## Canonical locked counts

| metric | value |
|---|---:|
| universe_rows | 12,187 |
| usable_html_inline | 12,145 |
| zip_unparseable | 42 |
| no_label_match | 511 |
| label_no_value | 200 |
| blocker_register_rows | 862 |
| parser_nonextracted_rows | 711 |
| correction_rows | 166 |
| correction_zip_subset | 39 |
| non_correction_zip_subset | 3 |

Derived identities: 711 = 511 + 200; 42 = 39 + 3; 862 = 753 + 109; 12,187 = 12,145 + 42.

## Lock dimensions (consistency re-checked this phase)

| lock | result | detail |
|---|---|---|
| count_locks (REF-CLOSE-007) | PASS | 19 reconciliation rows, all PASS=True |
| rowkey_set_locks (REF-CLOSE-008) | PASS | 5 set checks, all PASS=True |
| field_level_fail_closed_locks (REF-CLOSE-009) | PASS | 30 invariant rows, all PASS=True |
| manual_review_packet_lock (REF-CLOSE-010) | PASS | rows=862, unique=862 (expect 862/862) |
| worklist_view_lock (REF-CLOSE-011) | PASS | rows=862, unique=862 (expect 862/862) |
| packet_set==worklist_set | PASS | set equality=True |

## Hard-lock summary (carried, in force)

- Execution / strategy / backtest / performance: CLOSED.
- No source recovery; the 42 zip_unparseable need a separate verdict + download approval.
- No parser feature expansion / code change; parser-design backlog is design-only.
- No C2/C3 / event-log finalization / executable-status table / production / paper / P08 / live / shadow.
- All 862 blocker rows fail-closed; correction rows non-authoritative; rejected_wrong_candidate quarantined; design-only fields (link_validated, supersession_ready) not promoted.
- Manual-review packet + worklist are human-review/navigation only and fail-closed; no outcome columns; blocked_action_boundary warning-only.