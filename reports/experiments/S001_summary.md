# S001 Summary

Status: FAIL at S001-0 audit gate. S000 recalculation is required before any
S-family promotion or S002 execution log.

## Decision Guardrails

- `r1d_lt_m3` remains the main standalone candidate.
- `r3d_lt_m7` remains a crisis sub-signal, not champion.
- `volume_z` remains rejected.
- `P08_IEF30` remains the frozen primary.
- P08 + S satellite combination is not allowed before standalone validation.
- S001 PASS only authorizes S002 experimental execution log. It does not
  promote a paper candidate by itself.

## Sub-Ticket Register

| Sub-ticket | Generated status | Required status for S001 PASS |
|---|---|---|
| S001-0 Metric / Implementation Audit | FAIL | PASS; no recalculation-required FAIL |
| S001-A Distribution / Attribution Audit | PASS | PASS |
| S001-B Real Sleeve Daily NAV Simulation | PASS | PASS |
| S001-C Execution / Capacity Stress | small-capacity tactical sleeve | PASS |
| S001-D Robustness / Placebo | FAIL | PASS |
| S001-E Tax Model | PASS | PASS |
| S001-F Mechanism Analysis | DIAGNOSTIC_ONLY | Diagnostic support; no contradiction |

## S001-0 Blocking Findings

S001-0 found recalculation-required failures:

- Entry/exit alignment: 1,533 bad entry rows and 1,353 bad exit rows versus the
  raw KRX trading calendar.
- Filtered-row execution: 1,533 rows match the filtered ticker next row instead
  of raw calendar T+1.
- Adjusted price: max absolute trade return is 297.75, so corporate-action or
  price-adjustment handling must be audited before accepting S000.
- Overlap/leverage: max 18 new signals on one day and max 122 active positions
  under per-trade treatment.
- Random control: date-count match rate is 0.109737, so rebound-day effects are
  not controlled.

## Overall PASS Criteria

1. S001-0 has no FAIL item requiring S000 recalculation.
2. Return unit audit confirms decimal per-trade means.
3. Signal T close, entry T+1 open, and exit horizon are KRX-calendar safe.
4. Dynamic-universe membership is PIT safe.
5. Price adjustment/open-close treatment is documented and consistent.
6. Duplicate and consecutive signal handling is explicit.
7. Real sleeve NAV is net positive with no leverage.
8. `r1d_lt_m3` survives top trade/date/crisis exclusions.
9. Random/placebo controls are materially worse.
10. Tax and execution/capacity stress remain acceptable.

## Overall FAIL Criteria

1. Timing or implementation leakage requires S000 recalculation.
2. Filtered-row execution created non-KRX execution jumps.
3. Result depends on a few trades, dates, or 2020.
4. Real sleeve NAV fails after costs and cash drag.
5. Placebos match or beat the candidate.
6. Threshold/holding result is a one-point tune.
7. Capacity fails tactical sleeve scale.
8. Tax/execution assumptions erase ordinary implementation net returns.

## Next

- S001 PASS -> start S002 experimental execution log.
- S001 FAIL -> close S-family as diagnostic finding or move to backlog unless a
  corrected S000 rerun is explicitly ticketed.
- Paper candidate promotion requires S001-B/C/D/E PASS after S001-0 passes.
- P08 + S satellite can be considered only after standalone validation.
