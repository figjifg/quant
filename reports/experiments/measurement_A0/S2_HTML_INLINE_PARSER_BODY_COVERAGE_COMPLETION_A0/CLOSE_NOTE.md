# S2-HTML-INLINE-PARSER-BODY-COVERAGE-COMPLETION-A0 — Final Close Note

Date: 2026-05-25  
Verdict source: Referee final close verdict, 2026-05-25.  
Initial pass commit accepted: `b3a971d` on origin/main.

## Verdict

**CLOSED AS BODY-COVERAGE COMPLETED FOR TARGET SET / RESIDUAL SOURCE DEFECTS
PRESERVED / EXECUTION STILL CLOSED.**

- Decision: option **A** (close as body coverage completed with residuals).
- No additional coverage pass required now.
- No correction-linkage full-universe validation opened automatically.
- No delisting / liquidation manual expansion opened automatically.
- No execution simulation opened.
- No strategy testing reopened.
- No performance diagnostics reopened.
- No production / paper / P08 / live readiness / shadow-track work touched.
- No card is strategy-ready.

## Accepted scope

- Measurement-layer body-coverage completion A0 only.
- suspension_related + resumption_related categories only.
- HTML-inline body candidates only.
- Remaining body_unavailable rows from prior expansion phase only.
- Parser `krx_status_html_inline-1.1.0` used as-is.
- No parser feature expansion.
- No delisting / liquidation / managed / alert parser.
- No DART body alpha / overhang.
- No C2/C3 wiring / all-event event log finalization.
- No strategy testing / performance diagnostics / execution simulation.
- No production / paper / P08 / live / shadow.

## Accepted commit

- `b3a971d` — initial pass.

## Accepted code

- `src/audit/measurement_a0/p_body_coverage_completion.py`

## Accepted remaining target construction

- Remaining target rows: **5,744** (from prior expansion phase rows where
  `attempt_status = not_attempted_in_this_run`).
- Priority bucket, correction flag, and period info preserved.
- Every target row received a terminal status.

## Accepted cache re-inventory

| metric | value |
|---|---:|
| cached ZIPs at start | 6,692 |
| unique rcept_no | 6,692 |
| valid ZIPs | 6,648 |
| unparseable ZIPs | 44 |
| duplicate rcept_no | 0 |
| remaining target rows already cached | 162 |
| remaining rows still missing before completion attempt | 5,582 |

## Accepted acquisition results

| metric | value |
|---|---:|
| download budget | 6,000 |
| download attempts | 5,582 |
| **download successes** | **5,579 (99.95%)** |
| html_inline | 5,579 |
| structured_xml | 0 |
| attachment_only | 0 |
| other_format | 0 |
| zip_unparseable | 3 |
| api_no_document | 0 |
| rate_limited | 0 |
| credential_or_api_error | 0 |
| retry_needed_after_retries | 0 |
| not_attempted_due_to_budget | 0 |

## Accepted target-set coverage delta

| metric | before | after |
|---|---:|---:|
| body_unavailable on remaining target | 5,744 | **0** |
| body_available on remaining target | 0 | 5,744 |
| extracted | 0 | 5,577 |
| no_label_match | 0 | 164 |
| label_no_value | 0 | 0 |
| out_of_scope_body_format | 0 | 3 |

- **Coverage shift on remaining target: 100.0%**.
- Target body_unavailable: 5,744 → 0.

## Accepted universe-level coverage estimate

| metric | value |
|---|---:|
| In-scope universe | 12,187 |
| Body available before this run | ~6,398 / 12,187 ≈ 52.5% |
| Body acquired this run | 5,579 |
| **Body available now** | **~11,977 / 12,187 ≈ 98.3%** |

Accepted **as an estimate**, NOT a claim of perfect 100% universe coverage.

## Target-set vs universe-level residual distinction (Referee-mandated)

1. **Target-set residual**: body_unavailable on the prior expansion target set is
   **0** after completion. The 5,744 rows that prompted this phase are all
   accounted for as 162 already cached + 5,579 newly acquired + 3 zip_unparseable
   = 5,744. The 3 zip_unparseable rows are residual source defects, not parsed
   bodies.

2. **Universe-level / non-target residual**: ~210 rows in the 12,187-row in-scope
   universe still do NOT have an HTML-inline body available. Breakdown:
   - 3 zip_unparseable from this completion run.
   - Prior `out_of_scope_body_format` rows from FULL-UNIVERSE-VALIDATION
     (non-HTML bodies, e.g. structured_xml / attachment_only / other).
   - Any other rows that never entered this phase's target set.

3. **Treatment of all residual rows (target-set and universe-level)**:
   - MUST remain `manual_review_required` / `unavailable`.
   - MUST NOT be treated as parsed / executable / safe.
   - MUST NOT be silently dropped.

This phase does NOT describe the full 12,187-row in-scope universe as 100%
body-complete. Correct phrasing: **target set completed; universe-level body
coverage approximately 98.3%; residual source defects preserved**.

## Accepted parser / validation result

- Parser version: `krx_status_html_inline-1.1.0` (used as-is).
- No parser feature expansion occurred.
- Newly acquired bodies parsed with existing parser only.
- 88-row holdout sample drawn from newly extracted rows.
- **Holdout success rate: 88 / 88 = 100.0%**.
- wrong_date: 0.
- missed_date: 0.
- false_positive: 0.
- correction_not_forced_manual_review: 0.
- body_unavailable: 0.
- Parser behavior preserved.

## Accepted defect ledger (3 rows)

- `zip_unparseable`: 3 (residual source defects)
- `body_download_failed`: 0
- `api_no_document`: 0
- `rate_limited`: 0
- `attachment_only`: 0
- `structured_xml_out_of_scope`: 0
- `credential_or_api_error`: 0
- `newly_parsed_wrong_date`: 0
- `newly_parsed_missed_date`: 0
- `correction_policy_violation`: 0
- `duplicate_rcept_no`: 0
- `retry_needed`: 0
- `not_attempted_remaining`: 0
- `body_unavailable_remaining (within target set)`: 0

## Accepted gate state

**`READY_FOR_NEXT_A0_REVIEW`** (per Referee-permitted enum).

## Referee interpretation (paraphrased)

- Phase achieved body-coverage completion objective for prior expansion target set.
- All previously not_attempted target rows were already cached, attempted,
  successfully downloaded, or explicitly defected.
- Download reliability remained very high (99.95%).
- Parser behavior remained stable on newly acquired bodies (100% holdout).
- Correction policy NOT violated.
- No body_unavailable target row silently dropped.
- The correct status is NOT "all S2 body coverage complete."
- The correct status IS target-set body coverage completed with residual source
  defects preserved.
- Execution simulation remains closed.
- Strategy testing remains closed.
- No card is strategy-ready.

## Important remaining limits

- Universe-level coverage is approximate, NOT perfect.
- Any residual body issue outside the target set remains unavailable /
  manual-review-only.
- 3 zip_unparseable rows remain as residual source defects.
- This phase did NOT complete S2 globally.
- This phase did NOT create a C2/C3 event log.
- This phase did NOT authorise execution simulation.
- This phase did NOT authorise strategy testing.
- This phase did NOT authorise production / paper / P08 / live / shadow work.

## Final status

`S2-HTML-INLINE-PARSER-BODY-COVERAGE-COMPLETION-A0` is **closed as BODY-COVERAGE
COMPLETED FOR TARGET SET / RESIDUAL SOURCE DEFECTS PRESERVED / EXECUTION STILL
CLOSED**.

## Continuing prior-closed state (unchanged)

- S2-HTML-INLINE-PARSER-BODY-COVERAGE-EXPANSION-A0: CLOSED AS BODY-COVERAGE-EXPANDED AND VALIDATED FOR AVAILABLE ROWS / INCOMPLETE COVERAGE / EXECUTION STILL CLOSED.
- S2-HTML-INLINE-PARSER-FULL-UNIVERSE-VALIDATION-A0: CLOSED AS FULL-UNIVERSE-PARSER-VALIDATED FOR SUSPENSION / RESUMPTION ONLY / AVAILABLE-BODY SCOPE / EXECUTION STILL CLOSED.
- KR-STATUS-CORRECTION-LINKAGE-A0: CLOSED AS CORRECTION-LINKAGE VALIDATED FOR SAMPLE / HIGH_VALIDATED ONLY / EXECUTION STILL CLOSED.
- S2-HTML-INLINE-PARSER-REOPEN-PHASE: CLOSED AS HTML-INLINE-PARSER-VALIDATED FOR SUSPENSION / RESUMPTION ONLY / EXECUTION STILL CLOSED.
- KR-STATUS-EFFECTIVE-DATE-MANUAL-AUDIT-PHASE: CLOSED AS MANUAL-AUDIT-COMPLETED / SUPPORTS HTML-INLINE PARSER REOPEN / EXECUTION STILL CLOSED.
- KR-EXECUTABLE-EFFECTIVE-DATE-LINKAGE-A0: CLOSED AS EFFECTIVE-DATE-LINKAGE-AUDITED / PARTIAL / NOT GENERALIZABLE / EXECUTION STILL CLOSED.
- KR-EXECUTABLE-STATUS-PRE2018-EXTENSION-A0: CLOSED AS PRE2018-STATUS-SOURCE-ACQUIRED / RECONCILED / EXECUTION STILL CLOSED.
- KR-EXECUTABLE-STATUS-LIMIT-LOCK-SOURCE-A0: CLOSED AS LIMIT-LOCK-PROXY-RECONCILED / PARTIAL COVERAGE / EXECUTION STILL CLOSED.
- KR-EXECUTABLE-STATUS-COVERAGE-A0: CLOSED AS EXECUTABLE-STATUS-SOURCE-ACQUIRED / PARTIAL COVERAGE / EXECUTION STILL CLOSED.
- KR-LISTED-UNIVERSE-COVERAGE-A0: CLOSED AS LISTED-UNIVERSE-SOURCE-ACQUIRED / PARTIAL LIFECYCLE / NOT SURVIVORSHIP-SAFE.
- KR-KRX-CALENDAR-SOURCE-ACQUISITION-A0: CLOSED AS CALENDAR-SOURCE-RECONCILED / EXECUTION STILL CLOSED.
- OHLCV quarantine / runtime / residual blocker phases: CLOSED.
- S2 OPENDART Body Parser Phase: CLOSED AS PARTIAL globally.
- C2-C3-DESIGN-FINALIZATION: CLOSED.
- Strategy TEST: CLOSED.
- Performance diagnostics: CLOSED.
- Round 2 strategy restart: CLOSED.
- DART body alpha: CLOSED.
- Overhang filter alpha: CLOSED.
- Flow strategy testing: CLOSED.
- Production / paper / P08 / live readiness / shadow tracks: UNCHANGED.

## Possible future phases (none active)

| Phase candidate | Purpose | Status |
|---|---|---|
| `S2-HTML-INLINE-PARSER-UNIVERSE-RESIDUAL-RECONCILIATION-A0` | Reconcile the approximate universe-level residual body coverage gap. **Referee-strongest next candidate.** | NOT approved |
| `KR-STATUS-CORRECTION-LINKAGE-FULL-UNIVERSE-VALIDATION-A0` | Correction linkage beyond sample across all in-scope correction rows. | NOT approved |
| `KR-STATUS-EFFECTIVE-DATE-MANUAL-AUDIT-EXPANSION` | More manual samples (delisting / liquidation / managed / alert). | NOT approved |
| `S2-DELISTING-LIQUIDATION-PARSER-FEASIBILITY-A0` | Separate feasibility for delisting / liquidation. | NOT approved |
| `KR-INTRADAY-HALT-SOURCE-BACKLOG` | Intraday halt / VI / circuit-breaker. | NOT approved |
| `KR-EXECUTABLE-STATUS-LIMIT-LOCK-OFFICIAL-SOURCE-A0` | Direct KRX/KOSCOM official limit-lock. | NOT approved |
| `KR-LIMIT-LOCK-CORPORATE-ACTION-ADJUSTMENT-A0` | CA effects on prev-close limit. | NOT approved |
| `KR-LISTED-UNIVERSE-DAILY-LIFECYCLE-REFINEMENT-A0` | Monthly → daily lifecycle / merger linkage / rename / code reuse. | NOT approved |
| `KR-OPS-NAV-UPDATE-QUARANTINE-PATCH-PHASE` | 4 ops blockers. | NOT approved |

Strategy testing remains **premature**. Backtesting remains **premature**.
Execution simulation remains **closed**. Auto-start forbidden.

## Continuing hard locks

- No return backtest.
- No NAV / CAGR / Sharpe / hit rate / alpha / excess return / MDD.
- No post-event drift / migration / turnover / resume / reversal / flow-return.
- No raw jump alpha.
- No price-only mean reversion.
- No generic value / quality / momentum / RS ranking.
- No DART body alpha.
- No overhang filter alpha.
- No flow strategy testing.
- No execution simulation.
- No C2/C3 integration.
- No all-event event log finalization.
- No delisting parser.
- No liquidation parser.
- No managed / alert parser.
- No parser feature expansion.
- No executable assumption from panel presence.
- No survivorship-safe claim unless explicitly supported.
- No unknown status treated as executable.
- No panel absence treated as non-tradable.
- No OHLCV signature treated as suspension proof.
- No rule-derived limit candidate treated as official lock evidence.
- No `rcept_dt` treated as effective status date.
- No `effective_date` inferred from `rcept_dt` fallback.
- No parser result described as strategy-ready.
- No correction row treated as authoritative unless high_validated AND validated.
- No medium / low / no_link correction row treated as authoritative.
- No supersession rule wired downstream.
- No `body_unavailable` row treated as parsed or safe.
- No production / paper / P08 / live readiness / shadow connection.
- No card may be described as strategy-ready.

## End condition

`S2-HTML-INLINE-PARSER-BODY-COVERAGE-COMPLETION-A0` is closed. No active work
remains after housekeeping. Await explicit user / Referee decision for any future
universe-residual reconciliation, correction-linkage full-universe validation,
delisting / liquidation expansion, intraday halt source, official limit-lock
source, lifecycle refinement, ops patch, or strategy phase.
