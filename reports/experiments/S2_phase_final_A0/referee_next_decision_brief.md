# Referee Next Decision Brief

Date: 2026-05-23 15:42:46

## What is closed

- S2 OPENDART body parser phase = **COMPLETE AS PARTIAL**
- D3a = PARTIAL
- D3b = PARTIAL / NOT C3-ready
- D3c = CLOSED
- C2/C3 = DESIGN-ONLY
- Strategy testing = remains CLOSED (Research Freeze v2 unchanged)
- Performance diagnostics = remains CLOSED
- Production / paper / P08 / live = UNCHANGED

## What is open for Referee future consideration (no executor recommendation)

### Future phase candidates (each requires separate Referee approval)

1. **`S2-D3A-ONE-MORE-PASS-PHASE`** — narrowly targeted parser pass on the 2 deterministic D3a base forms (자기주식취득결과보고서 + 주식소각결정). Estimated 1-2 weeks. End condition: D3a partial coverage for those 2 forms with field rates lifted toward A0 pass.

2. **`S2-D3B-CUSTOM-PARSER-PHASE`** — implement per-ACODE custom parsers for 11324 (CB), 11325 (BW), conversion_request family, plus SECTION/COVER text scanner. Estimated 4-7 weeks. Separate scope, kill gates, manual audit, time budget required.

3. **`S2-D3C-OPEN-PHASE`** — open D3c after D3a + D3b state is resolved. Free-text and html_inline heavy. Estimated effort unknown until D3a/D3b complete.

4. **`S2-MANUAL-AUDIT-PHASE`** — full manual audit (30 samples per event type ≈ 500 disclosures). Was deferred from D5b. Reopen when parser deemed C3-ready candidate.

5. **`C2-C3-DESIGN-FINALIZATION`** — design-only, no wiring. Allowed under current verdict. Spec the not_available / partial / manual_required event_source states and the C3 day-reclassification not_yet_available branch.

### Strategy-side decisions (separate from parser phases)

6. **Research Freeze v2 review** — Current S2 phase closes WITHOUT reopening any strategy. Whether to reopen any strategy at all is a separate Referee verdict on the broader Research Freeze policy.

## What executor will NOT do without Referee approval

- Open any of phases 1-4 above unilaterally
- Wire parser outputs into C2/C3 production
- Treat parser output as strategy-ready
- Perform any strategy testing
- Open P08 / paper / live readiness work

## Executor stance

Executor offers no recommendation on phase priority. Each phase is a Referee scope-vs-effort policy choice. S2 phase officially closes here.

## Hard locks reaffirmed

- No D3c full implementation
- No C2/C3 integration
- No unified all-event event log finalization
- No return backtest
- No NAV / CAGR / Sharpe / hit rate / alpha / excess return / MDD
- No post-event drift / migration / turnover / resume / reversal / flow-return
- No raw return as signal/outcome
- No Round 2 strategy restart
- No flow strategy testing
- No DART body alpha test
- No overhang alpha/filter test
- No production / paper / P08 / live readiness / shadow connection
- No parser result described as strategy-ready