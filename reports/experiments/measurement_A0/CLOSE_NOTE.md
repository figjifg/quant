# Measurement-layer A0 Initial Pass — Final Close Note

Date: 2026-05-23  
Origin: Referee verdict (2026-05-23) accepting the initial pass.  
Commit accepted: `78543b4` on origin/main.

## Verdict

**CLOSED AS PARTIAL / DEFECT-FOUND.**

The Bull New Hypothesis Intake → Measurement-layer A0 initial pass is complete. All 5
cards delivered. All 20 artifacts preserved.

## Card-by-card final status

| Card | Status | Headline |
|---|---|---|
| `KR-FIELD-METADATA-CONTRACT-A0-001` | **ACCEPTED / PARTIAL-GUARDED** | 27 datasets / 372 columns / 0 UNKNOWN / 196 ALLOW / 176 ALLOW_WITH_GUARD / 0 QUARANTINE / 31 ambiguity defects |
| `KR-CALENDAR-PANEL-ALIGN-A0-001` | **ACCEPTED / PARTIAL** | 0 off-calendar / 0 missing / 0 duplicate. T+1 reproducible vs union calendar. Authoritative KRX calendar source **UNRESOLVED** — execution simulation remains CLOSED |
| `KR-OHLCV-UNIT-INVARIANT-A0-001` | **ACCEPTED / DEFECT-FOUND** | 4.9M rows / 58,649 OHLC violations / 53,556 nonpos / 0 negative. Pattern = OHL=0 / close>0 (vendor non-trading-row convention). Quarantine mandatory |
| `KR-LISTED-UNIVERSE-COVERAGE-BACKLOG-001` | **DATA BACKLOG** | Official listed-universe / lifecycle source required before A0 |
| `KR-EXECUTABLE-STATUS-BACKLOG-001` | **DATA BACKLOG** | Official executable-status / halt / limit-lock source required before A0 |

## Referee-locked rules from this close

### Field metadata
- All `ALLOW_WITH_GUARD` fields require a documented guard at the call site before any
  future strategy use. The 176 ALLOW_WITH_GUARD entries are not strategy-ready by
  themselves.
- The 31 ambiguity defects are not strategy evidence and must not be reinterpreted as
  such.

### Calendar
- The audit's working union calendar is **not** an authoritative KRX source.
- T+1 reproducibility holds only relative to the working calendar.
- Execution simulation remains CLOSED until an authoritative source is acquired
  (a candidate future phase: `KR-KRX-CALENDAR-SOURCE-ACQUISITION-A0`, NOT active).

### OHLCV
- All rows matching the OHL=0 / `close>0` signature MUST be quarantined per
  `KR_OHLCV_UNIT_INVARIANT_A0/invalid_row_quarantine_rules.md`.
- These rows MUST NOT be treated as a price observation, halt evidence, suspension
  evidence, or alpha signal.

### P2 backlogs
- Both registers remain DATA BACKLOG. No A0 starts on either until an official source is
  acquired AND a fresh Referee verdict opens the audit.

## Artifact preservation

All 20 files under `reports/experiments/measurement_A0/` are preserved. They are
referenced contracts and defect tables, not implementation. They must NOT be:
- deleted,
- rewritten to soften findings,
- reinterpreted as strategy evidence,
- combined with any return / NAV / Sharpe / alpha output downstream.

The 3 reproducible builds under `src/audit/measurement_a0/` are likewise preserved.

## Possible future phases (none active)

The Referee enumerated 4 candidate next phases. None is auto-started. Each requires a
fresh verdict.

| Candidate | Purpose | Referee comment |
|---|---|---|
| `KR-OHLCV-QUARANTINE-ENFORCEMENT-A0` | Verify OHL=0 / nonpos / invalid OHLC rows are excluded or explicitly guarded in all downstream code paths | **Recommended next infrastructure step** if the user chooses to continue. Smaller than source acquisition. Measurement-layer only. Does not require strategy testing. Verifies known bad rows cannot leak. Do NOT auto-start. |
| `KR-KRX-CALENDAR-SOURCE-ACQUISITION-A0` | Acquire or reconcile authoritative KRX trading calendar | Closes calendar-source ambiguity. Measurement-layer only. |
| `KR-LISTED-UNIVERSE-COVERAGE-A0` | Start only after official listed-universe / lifecycle source is acquired | Currently DATA BACKLOG. |
| `KR-EXECUTABLE-STATUS-COVERAGE-A0` | Start only after official executable-status source is acquired | Currently DATA BACKLOG. |

## Continuing hard prohibitions

- No return backtest.
- No NAV / CAGR / Sharpe / hit rate / alpha / excess return / MDD.
- No post-event drift / migration return / turnover return / resume return / reversal
  return / flow-return.
- No raw jump alpha.
- No price-only mean reversion.
- No generic value / quality / momentum / RS ranking.
- No DART body alpha test.
- No overhang filter alpha test.
- No flow strategy testing.
- No executable assumption from panel presence.
- No survivorship-safe claim without official listed universe.
- No use of `ALLOW_WITH_GUARD` fields without documented guard.
- No use of invalid OHLCV rows without quarantine.
- No production / paper / P08 / live readiness / shadow connection.
- No card may be described as strategy-ready.

## End condition

Measurement-layer A0 initial pass is **closed**. No active work remains.

The executor will not perform any additional A0, parser, design, strategy, production,
paper, P08, live, or shadow work unless the user explicitly chooses the next
Referee-scoped phase.
