# Downstream Blockers After Parser Reopen

Date: 2026-05-25
Phase: S2-HTML-INLINE-PARSER-REOPEN-PHASE

## Question

Even if this parser reopen is accepted, what still blocks strategy testing,
execution simulation, and any production-side use?

## Blockers preserved (do NOT count this phase as resolving any of them)

### Category coverage

- Delisting parser: NOT implemented (manual audit extraction was 3.8%).
- Liquidation parser: NOT implemented (manual audit 0.0%).
- Managed / investment_alert / short_term_overheated: NOT implemented.
- Other category: NOT implemented.

### Effective-date linkage

- Correction linkage: NOT implemented. Depends on S2 `corp_code + base_form +
  series_marker + window` join (S2 closed as PARTIAL).
- `rcept_dt` MUST NOT be used as `effective_date` fallback (permanent lock).
- Effective-date for `parser_only_no_gt` rows MUST NOT be auto-promoted to
  authoritative without per-row manual review.

### Universe / data

- KRX intraday-halt source: NOT acquired.
- KRX official limit-lock source: NOT acquired (only rule-derived proxy).
- Listed-universe daily lifecycle: NOT acquired (monthly resolution only).
- Pre-2018 corrections: not back-validated against this parser at full universe scale.

### OHLCV / runtime

- 45 OHLCV residual blockers preserved (40 patched in prior phase; 4 ops
  blockers remain reopen-blocker).
- Closed-strategy entry guards remain mandatory before any strategy reopen.

### Ops / production

- `src/ops/nav_update.py` 4 ops blockers remain in
  `KR-OPS-NAV-UPDATE-QUARANTINE-PATCH-PHASE` (not approved).
- P08 / paper / live / shadow are UNCHANGED.

## Minimum additional work before this parser can be used downstream

- Approve `KR-STATUS-CORRECTION-LINKAGE-A0` (separate Referee).
- Approve a delisting / liquidation manual expansion or attachment-acquisition phase
  (separate Referee).
- Approve full-universe parser validation (not just 195 samples) (separate Referee).
- Resolve `rcept_dt` vs `effective_date` policy for all unknown rows
  (currently fail-closed per permanent lock).

## What this phase does NOT unlock

- Strategy testing remains CLOSED.
- Execution simulation remains CLOSED.
- Performance diagnostics remains CLOSED.
- No card is strategy-ready.
- No production / paper / P08 / live / shadow connection.

## Numerical context (this phase)

- In-scope sample size: 108.
- Negative-control false positives: 0.
- Manual-review-required rate (in-scope): 14 / 108.

Even at this parser quality, the surrounding data + universe + execution-safety
blockers preserved across the prior measurement-layer closes are unchanged.
