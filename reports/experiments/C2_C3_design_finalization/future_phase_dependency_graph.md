# Future Phase Dependency Graph

Date: 2026-05-23
Scope: design-only — map phase A → phase B prerequisite relationships post S2-close.

## Phase node list

| Phase id | Description | Estimated effort | Current state |
|---|---|---|---|
| `S2-D3A-ONE-MORE-PASS-PHASE` | Targeted parser pass on 2 deterministic D3a forms (취득결과보고서, 주식소각결정) | 1-2 weeks | NOT approved |
| `S2-D3B-CUSTOM-PARSER-PHASE` | ACODE 11324 (CB), 11325 (BW) custom parsers + conversion_request family + SECTION/COVER text scanner | 4-7 weeks | NOT approved |
| `S2-D3C-OPEN-PHASE` | Open D3c (additional listing / lockup / major shareholder sale / correction-cancellation) | unknown until prior phases settle | NOT approved |
| `S2-MANUAL-AUDIT-PHASE` | 30 samples × ~14 event types ≈ 500 disclosures manual audit | 1-2 weeks engineering + 1-2 weeks user audit | NOT approved |
| `C2-C3-DESIGN-FINALIZATION` | Design-only contracts (this phase) | 1-2 days | **ACTIVE / nearing completion** |
| `C2-IMPLEMENTATION-PHASE` | Wire parser → factor chain (treasury subset first) | 2-3 weeks | NOT approved (gated on phases above) |
| `C3-IMPLEMENTATION-PHASE` | Populate `corporate_action_day` enum | 2-3 weeks | NOT approved (gated on C2 first) |
| `FULL-RE-A0-PHASE` | Re-run all 5 audit cards with C2/C3 wired | 1-2 weeks | NOT approved |
| `STRATEGY-REOPEN-REVIEW` | Per-card decision on closed Korean standalone-alpha cards | per-card; weeks each | NOT approved |

## Dependency edges (prerequisite → enabled)

```
C2-C3-DESIGN-FINALIZATION
    └── (provides design contract)
        ├── S2-D3A-ONE-MORE-PASS-PHASE  -- can be approved any time; outputs feed audit + C2
        ├── S2-D3B-CUSTOM-PARSER-PHASE  -- can be approved any time; outputs feed audit + C2
        └── S2-D3C-OPEN-PHASE           -- typically AFTER D3a + D3b state resolved

S2-D3A-ONE-MORE-PASS-PHASE  -->  S2-MANUAL-AUDIT-PHASE (for D3a subset)
S2-D3B-CUSTOM-PARSER-PHASE  -->  S2-MANUAL-AUDIT-PHASE (for D3b subset)
S2-D3C-OPEN-PHASE           -->  S2-MANUAL-AUDIT-PHASE (for D3c subset)

S2-MANUAL-AUDIT-PHASE  -->  C2-IMPLEMENTATION-PHASE (only for audited event types)
C2-IMPLEMENTATION-PHASE  -->  C3-IMPLEMENTATION-PHASE
C3-IMPLEMENTATION-PHASE  -->  FULL-RE-A0-PHASE
FULL-RE-A0-PHASE  -->  STRATEGY-REOPEN-REVIEW
```

## Critical path (longest path to strategy reopen)

If user/Referee wants to reach strategy reopen review:
```
S2-D3B-CUSTOM-PARSER (4-7w)
  → S2-D3C-OPEN (unknown)
    → S2-MANUAL-AUDIT (2-4w)
      → C2-IMPLEMENTATION (2-3w)
        → C3-IMPLEMENTATION (2-3w)
          → FULL-RE-A0 (1-2w)
            → STRATEGY-REOPEN-REVIEW (per-card, weeks each)
```

Minimum critical path = **~16-25 weeks**, assuming serial execution and no kill-gate failures.

## Parallel paths

| Path | Phases in parallel | Total time |
|---|---|---|
| Treasury-only minimal viable path | D3A-ONE-MORE-PASS ∥ MANUAL-AUDIT(treasury) → C2(treasury) → C3 | ~6-8 weeks |
| Overhang minimal viable path | D3B-CUSTOM-PARSER → MANUAL-AUDIT(CB/BW/conv) → C2(overhang) → C3 | ~10-14 weeks |
| Full coverage path | All D3 phases ∥ MANUAL-AUDIT(all) → C2(full) → C3 | ~16-25 weeks |

## Risk gates per phase transition

Each transition between phases requires:
- All required outputs of the predecessor phase committed to origin/main
- Referee verdict accepting the predecessor's pass state
- Explicit kill-gate set for the successor phase
- No silent auto-progression (no transition fires without verdict)

## What this design phase does NOT do

- Does NOT approve any future phase
- Does NOT schedule any future phase
- Does NOT commit user / executor / Referee to any specific path
- Does NOT estimate strategy reopen feasibility (which depends on Research Freeze v2 review separately)

## Reopen conditions for each closed item

| Closed item | Condition to revisit (Referee-only) |
|---|---|
| D3a partial | After `S2-D3A-ONE-MORE-PASS-PHASE` or new evidence |
| D3b partial / NOT C3-ready | After `S2-D3B-CUSTOM-PARSER-PHASE` |
| D3c closed | After D3a + D3b state resolved + Referee approval |
| G5_000005 DEFERRED-S2 | After C3 reclassification populates `corporate_action_day` |
| `corporate_action_day` enum reservation | After Full Re-A0 |
| Round 2 cards | After C3 + Round 2 reopen verdict |
| Korean standalone-alpha cards | After Strategy Reopen Review (per card) |
| Production / paper / P08 / live | Independent track; NOT gated on parser phases |

## Hard locks

- No phase auto-starts
- No phase enables itself by completing a predecessor — the verdict-gating is explicit
- No strategy reopen as a side-effect of parser work
- No production/paper/P08/live moves as a side-effect
