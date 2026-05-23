# S2 Remaining Blockers Register — Final

Date: 2026-05-23 15:42:46

## Open blockers carried forward from S2

| # | Blocker | Owner | Reopen path |
|---|---|---|---|
| 1 | D3a label determinism on 5/7 base forms (subsidiary trust / 취득 결정 / 처분 결정 / 신탁 해지 / 처분 결과) | Future targeted parser pass | Referee approval for narrow D3a continuation |
| 2 | D3b custom parsers (ACODE 11324 / 11325 / conversion_request family) | New phase | Approve `S2-D3B-CUSTOM-PARSER-PHASE` |
| 3 | D3b SECTION/COVER text scanner for event_date | Part of D3b custom phase | Same as #2 |
| 4 | D3c full implementation (additional listing / lockup / major shareholder sale / correction-cancellation) | Future phase | After D3a/D3b resolved |
| 5 | Full manual audit (30 samples per event type) | Future phase | Was deferred from D5b; revisit when D3 parsers C3-ready |
| 6 | C2/C3 integration | Design-only now | After parser PARTIAL → C3-ready transition |
| 7 | G5_000005 DEFERRED-S2 closure | Blocked by C3 | After C3 integration |
| 8 | KR-OVERHANG-AVOID-001 backlog | Blocked by D3b | After D3b custom parsers |
| 9 | KR-DART-BODY-RETURN-001 backlog | Partially unblockable | Treasury-only subset partial after D3a one-more-pass (if approved) |

## Closed during S2

- D3 framework (dispatcher / charset / schema detection / correction linkage / PIT lock) — closed, infrastructure works
- Form taxonomy mapping — 14 event types + 38 base forms + variant normalization rules locked
- Tiny-response / attachment-only classification — 6 flags designed
- Per-ACODE label inventory — 17 ACODEs catalogued from 104 XML samples

## Hard locks

- These blockers do NOT translate into strategy work
- Reopening any blocker requires fresh Referee approval