# D3 Next Referee Decision Brief

Date: 2026-05-23 15:32:39

## Triage summary
- D3a: PARTIAL (2/7 base forms with deterministic labels)
- D3b: PARTIAL / NOT C3-ready (Referee pass targets MISSED on shares and event_date)
- D3c: CLOSED
- C2/C3 integration: design-only constraints documented

## Decision points for Referee

### Decision 1: D3a one-more-pass
- This triage shows D3a labels are deterministic on 2/7 base forms.
- Per Referee rule: deterministic → one more targeted parser pass allowed.
- Question: approve one final D3a parser pass with manual-audit-driven labels? OR lock D3a as PARTIAL?

### Decision 2: D3b custom parsers
- Feasibility study shows D3b needs:
  - ACODE 11324 / 11325 custom parsers
  - conversion_request separate parser family
  - SECTION/COVER text scanner for event_date
- Estimated effort: 4-7 weeks
- Question: approve D3b custom parser implementation? OR lock D3b as permanently PARTIAL?

### Decision 3: S2 phase end
- Per original Referee S2 phase scope, the end condition is the S2 parser A0 report.
- The D3 triage may be the natural stopping point — D3a partial + D3b partial = honest A0 outcome.
- Question: declare S2 phase complete with current PARTIAL state and produce the S2 parser A0 final report? OR continue D3a/D3b work?

### Decision 4: C2/C3 design
- Design constraints documented; no wiring permitted.
- Question: allow C2/C3 design-only work to proceed in parallel? OR hold until D3 state is finalized?

## Hard prohibitions (continuing)

- No D3c full implementation
- No unified all-event event log finalization
- No strategy testing / return outcome / strategy-ready claim
- No production / paper / P08 / live readiness / shadow connection

## Executor stance

Executor offers no preference among Decisions 1-4. Each is a Referee policy choice about scope vs effort. Reporting facts only.