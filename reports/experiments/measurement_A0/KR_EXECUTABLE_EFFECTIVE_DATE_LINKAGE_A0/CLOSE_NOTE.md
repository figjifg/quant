# KR-EXECUTABLE-EFFECTIVE-DATE-LINKAGE-A0 — Final Close Note

Date: 2026-05-25  
Verdict source: Referee final close verdict, 2026-05-25.  
Initial pass commit accepted: `7ff7d0a` on origin/main.

## Verdict

**CLOSED AS EFFECTIVE-DATE-LINKAGE-AUDITED / PARTIAL / NOT GENERALIZABLE / EXECUTION
STILL CLOSED.**

- Decision: option **A** (close as effective-date linkage audited).
- No additional simple-regex sample/body audit required now.
- No execution simulation opened.
- No strategy testing reopened.
- No performance diagnostics reopened.
- No production / paper / P08 / live readiness / shadow-track work touched.

## Accepted deliverables (12)

1. `effective_date_referee_lock.md`
2. `status_event_universe_summary.md`
3. `effective_date_source_inventory.md`
4. `effective_date_sample_plan.csv`
5. `effective_date_sample_audit.csv`
6. `dart_body_sample_check.md`
7. `rcept_dt_vs_effective_date_analysis.md`
8. `correction_cancellation_effective_date_check.md`
9. `effective_date_linkage_rule_design.md`
10. `effective_date_defect_ledger.csv`
11. `effective_date_gate_status.md`
12. `effective_date_final_summary.md`

## Accepted universe

- pre-2018 events: 7,150
- post-2018 events: 10,774
- **total: 17,924**

## Accepted sample plan (stratified)

- 113 samples
- suspension_related: 30
- resumption_related: 30
- delisting: 30
- managed / investment_alert / short_term_overheated (combined bucket): 20
- liquidation: 3
- pre-2018 and post-2018 balanced

## Accepted sample finding (extraction-method breakdown — canonical per repo artifact)

| extraction_method | count |
|---|---:|
| `unavailable` | 109 |
| `official_body_date` | 2 |
| `body_unavailable` | 2 |

Effective-date extraction rate: **1.8% (2 / 113)**.

Most status disclosures are HTML-inline. Simple regex is not viable for bulk
effective-date extraction. 111 / 113 samples remain `effective_date_unknown` or
unavailable. At least one extracted sample showed `effective_date_after_rcept_dt` —
confirming `rcept_dt` is not a safe default effective status date.

## Accepted rcept_dt conclusion

- `rcept_dt` is filing date.
- `rcept_dt` MUST NOT be treated as effective status date.
- No default fallback from `rcept_dt` to `effective_date` is allowed.
- Unknown effective_date MUST remain unknown or fail-closed.
- Execution simulation cannot safely use status events until effective-date handling
  is separately resolved.

## Accepted correction / cancellation finding

- Correction-flagged samples exist.
- Full correction linkage remains PARTIAL.
- Linkage depends on the S2 design contract: `corp_code + base_form + series_marker +
  window` linkage.
- S2 OPENDART Body Parser Phase remains CLOSED AS PARTIAL.
- Unlinked corrections MUST go to manual review and MUST NOT be used as authoritative
  status events.

## Accepted conservative rule design (design-only)

- Use explicit body/title date only when extractable.
- Unknown effective date = fail-closed.
- Do not auto-unblock resumption events based on `rcept_dt`.
- Delisting / liquidation require explicit date or period.
- Corrections supersede prior events only when linked.
- Cancellation / withdrawal MUST invalidate prior event when linked.
- Design only; no execution simulation.

## Accepted defect ledger (5)

1. `effective_date_unextracted_majority`
2. `rcept_dt_default_forbidden`
3. `body_download_failures` / unparseable documents
4. `correction_linkage_partial`
5. `html_inline_unparsed`

## Accepted gate state

**PARTIAL** (per Referee-permitted enum).

## New hard prohibitions added (Referee 2026-05-25)

- No `effective_date` inferred from `rcept_dt` fallback.
- Reinforces existing 2026-05-24 lock that `rcept_dt` MUST NOT be treated as effective
  status date without audit.

## Possible future phases (none active)

| Phase id | Purpose | Status |
|---|---|---|
| `S2-HTML-INLINE-PARSER-REOPEN-PHASE` | Reopen parser work for HTML-inline status disclosures | NOT approved |
| `KR-STATUS-EFFECTIVE-DATE-MANUAL-AUDIT-PHASE` | Manual review of larger status-event sample | NOT approved |
| `KR-INTRADAY-HALT-SOURCE-BACKLOG` | Intraday halt / VI / circuit-breaker source | NOT approved |
| `KR-EXECUTABLE-STATUS-LIMIT-LOCK-OFFICIAL-SOURCE-A0` | Direct KRX/KOSCOM official limit-lock acquisition | NOT approved |
| `KR-LIMIT-LOCK-CORPORATE-ACTION-ADJUSTMENT-A0` | CA effects on prev-close limit | NOT approved |
| `KR-LISTED-UNIVERSE-DAILY-LIFECYCLE-REFINEMENT-A0` | Monthly → daily lifecycle | NOT approved |
| `KR-OPS-NAV-UPDATE-QUARANTINE-PATCH-PHASE` | 4 ops blockers | NOT approved |

Referee-recommended next candidates (if user chooses to continue): either
**`S2-HTML-INLINE-PARSER-REOPEN-PHASE`** (parser automation) or
**`KR-STATUS-EFFECTIVE-DATE-MANUAL-AUDIT-PHASE`** (manual evidence). Must NOT
auto-start.

Strategy testing + backtesting remain **premature**.

## Continuing hard locks

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
- No execution simulation.
- No executable assumption from panel presence.
- No survivorship-safe claim unless explicitly supported.
- No unknown status treated as executable.
- No panel absence treated as non-tradable.
- No OHLCV signature treated as suspension proof.
- No rule-derived limit candidate treated as official lock evidence.
- No `rcept_dt` treated as effective status date.
- No `effective_date` inferred from `rcept_dt` fallback.
- No production / paper / P08 / live readiness / shadow connection.
- No card may be described as strategy-ready.

## End condition

`KR-EXECUTABLE-EFFECTIVE-DATE-LINKAGE-A0` is **closed as EFFECTIVE-DATE-LINKAGE-AUDITED
/ PARTIAL / NOT GENERALIZABLE / EXECUTION STILL CLOSED**. No active work remains.
Await explicit user / Referee decision for any future parser reopen, manual audit,
intraday halt source, official limit-lock source, lifecycle refinement, ops patch, or
strategy phase.
