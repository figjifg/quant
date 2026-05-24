# Effective-Date Linkage Rule Design (Design-Only)

Date: 2026-05-25  
Phase: KR-EXECUTABLE-EFFECTIVE-DATE-LINKAGE-A0

**Design only. No execution simulation.** Documents how a future execution
simulator (if/when authorised) would derive effective status date from
OPENDART/KRX status events.

## Empirical context (sample-level)

- Body+title extraction rate observed: **1.8%**
- Most common rcept_vs_effective relation: see `rcept_dt_vs_effective_date_analysis.md`

## Rule precedence (descending priority)

1. **`official_body_date`** (regex-extractable explicit date from DART
   document body): use as effective date. Confidence = high.
2. **`title_date_hint`** (date in report_nm): use only after verifying it
   plausibly aligns with a category-appropriate event. Confidence = medium.
3. **`correction_linkage`**: if a correction supersedes the original
   effective date, use the corrected date. Original is voided.
4. **`requires_manual_review`**: flag for manual audit. DO NOT use rcept_dt.
5. **`unavailable`**: fail-closed. Status MUST be treated as `unknown`. DO
   NOT assume executable.

## Decision matrix

| status category | extracted effective date | conservative downstream treatment |
|---|---|---|
| suspension_related | explicit | block buy / sell on effective date and afterwards until resumption |
| suspension_related | unknown | block buy / sell on rcept_dt-day AND following day; flag for manual review |
| resumption_related | explicit | unblock buy / sell from effective date |
| resumption_related | unknown | unblock requires manual review; do NOT auto-unblock based on rcept_dt |
| delisting | explicit | block all activity from effective date |
| delisting | unknown | block all activity from rcept_dt; flag for manual review |
| liquidation (정리매매) | explicit period | trading-allowed only within explicit period; block before/after |
| liquidation | unknown | block — require manual review |
| managed / investment_alert | explicit | flag in audit log; do NOT block buy/sell automatically |
| managed / investment_alert | unknown | flag in audit log; manual review |

## Forbidden defaults (Referee-lock)

- DO NOT default `effective_date = rcept_dt` for any status event.
- DO NOT use panel-day, OHLCV-day, or 거래대금 as effective-date proxy.
- DO NOT assume same-day execution for resumption events.
- DO NOT silently expand correction-unlinked events.

## Implementation deferred

- Implementation requires a separate Referee verdict opening an
  execution-simulation patch phase.
- Requires the S2 full body parser to be reopened (currently CLOSED AS
  PARTIAL) for higher extraction rate.
- Manual-review queue must be staffed before any production-style use.

## Hard locks (preserved)

- No execution simulation.
- No strategy testing.
- No production / paper / P08 / live readiness.
