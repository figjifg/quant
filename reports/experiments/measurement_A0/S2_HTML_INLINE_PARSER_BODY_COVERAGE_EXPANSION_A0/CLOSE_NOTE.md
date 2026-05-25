# S2-HTML-INLINE-PARSER-BODY-COVERAGE-EXPANSION-A0 — Final Close Note

Date: 2026-05-25  
Verdict source: Referee final close verdict, 2026-05-25.  
Initial pass commit accepted: `1d8a67f` on origin/main.

## Verdict

**CLOSED AS BODY-COVERAGE-EXPANDED AND VALIDATED FOR AVAILABLE ROWS / INCOMPLETE
COVERAGE / EXECUTION STILL CLOSED.**

- Decision: option **A** (close as body coverage expanded).
- No additional coverage pass required inside this same phase now.
- No strategy testing opened.
- No execution simulation opened.
- No performance diagnostics opened.
- No production / paper / P08 / live readiness / shadow-track work touched.
- No card is strategy-ready.

## Accepted scope

- Measurement-layer body-coverage expansion A0 only.
- suspension_related + resumption_related categories only.
- HTML-inline body candidates only.
- body_unavailable rows from prior validation phase.
- Parser version `krx_status_html_inline-1.1.0` used as-is.
- No parser feature expansion.
- No delisting / liquidation / managed / alert parser.
- No DART body alpha / overhang.
- No C2/C3 wiring / all-event event log finalization.
- No strategy testing / performance diagnostics / execution simulation.
- No production / paper / P08 / live / shadow.

## Accepted commit

- `1d8a67f` — S2-HTML-INLINE-PARSER-BODY-COVERAGE-EXPANSION-A0 initial pass.

## Accepted code

- `src/audit/measurement_a0/p_body_coverage_expansion.py`

## Accepted target universe

- body_unavailable target rows: **10,744**.
- Priority buckets assigned to every target row (P0-P5).
- Rows beyond budget logged as `not_attempted_in_this_run` (NOT silently dropped).

## Accepted cache inventory

| metric | value |
|---|---:|
| Cached ZIPs at start | 1,530 |
| Unique rcept_no | 1,530 |
| Valid ZIPs | 1,490 |
| Unparseable ZIPs | 40 |
| Duplicate rcept_no | 0 |
| In-scope cache hits | 1,443 |
| Out-of-scope cache hits | 87 |

Cache remains gitignored and reproducible.

## Accepted acquisition results

| metric | value |
|---|---:|
| Download budget | 5,000 |
| Download attempts | 5,000 |
| **Download successes** | **4,996 (99.92%)** |
| html_inline | 4,996 |
| structured_xml | 0 |
| attachment_only | 0 |
| other_format | 0 |
| zip_unparseable | 4 |
| api_no_document | 0 |
| rate_limited | 0 |
| credential_or_api_error | 0 |
| not_attempted (budget) | 5,744 |

## Accepted coverage delta

| metric | before | after |
|---|---:|---:|
| body_unavailable | 10,744 | 5,744 |
| body_available | 0 | 5,000 |
| extracted | 0 | 4,526 |
| no_label_match | 0 | 296 |
| label_no_value | 0 | 174 |

- **Coverage shift on target rows: 46.54%**.
- Universe-level body availability estimate: ~6,398 / 12,187 ≈ **52.5%** (up
  from ~11.5%; lift ≈ +41 percentage points).

## Accepted parser / validation result

- Parser version: `krx_status_html_inline-1.1.0` (used as-is).
- No parser feature expansion occurred.
- Newly acquired bodies parsed with existing parser only.
- 84-row holdout sample drawn from newly extracted rows.
- **Holdout success rate: 84 / 84 = 100.0%**.
- wrong_date: 0.
- missed_date: 0.
- false_positive: 0.
- correction_not_forced_manual_review: 0.
- Parser behavior preserved.

## Accepted defect ledger (5,748 rows)

- `body_unavailable_remaining`: 5,744 (budget exhausted; preserved)
- `zip_unparseable`: 4
- `body_download_failed`: 0
- `api_no_document`: 0
- `rate_limited`: 0
- `credential_or_api_error`: 0
- `attachment_only`: 0
- `structured_xml_out_of_scope`: 0
- `newly_parsed_wrong_date`: 0
- `newly_parsed_missed_date`: 0
- `correction_policy_violation`: 0
- `duplicate_rcept_no`: 0
- `retry_needed`: 0

## Accepted gate state

**`READY_FOR_NEXT_A0_REVIEW`** (per Referee-permitted enum).

## Referee interpretation (paraphrased)

- Phase achieved body-coverage expansion objective.
- Coverage improved materially.
- Download reliability very high (99.92%).
- New bodies overwhelmingly HTML-inline.
- Parser behavior remained clean on newly acquired bodies.
- Correction policy NOT violated.
- body_unavailable rows preserved and NOT treated as safe.
- The correct close status is NOT "full body coverage complete."
- The correct close status IS body coverage expanded and validated for available
  rows, but incomplete coverage remains.
- Execution simulation remains closed.
- Strategy testing remains closed.
- No card is strategy-ready.

## Important remaining limits

- 5,744 target rows remain body_unavailable.
- These 5,744 are NOT failed documents — most were `not_attempted_in_this_run`
  because the run hit the download budget.
- Remaining body_unavailable rows MUST remain manual_review_required / unavailable.
- body_unavailable rows MUST NOT be treated as parsed / executable / safe.
- This phase did NOT complete S2 globally.
- This phase did NOT create a C2/C3 event log.
- This phase did NOT authorise execution simulation.
- This phase did NOT authorise strategy testing.

## Final status

`S2-HTML-INLINE-PARSER-BODY-COVERAGE-EXPANSION-A0` is **closed as
BODY-COVERAGE-EXPANDED AND VALIDATED FOR AVAILABLE ROWS / INCOMPLETE COVERAGE /
EXECUTION STILL CLOSED**.

## Continuing prior-closed state (unchanged)

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
| `S2-HTML-INLINE-PARSER-BODY-COVERAGE-COMPLETION-A0` | Attempt the remaining 5,744 body_unavailable rows with another controlled budget. **Referee-strongest next candidate.** | NOT approved |
| `KR-STATUS-CORRECTION-LINKAGE-FULL-UNIVERSE-VALIDATION-A0` | Correction linkage beyond sample across all in-scope correction rows. | NOT approved |
| `KR-STATUS-EFFECTIVE-DATE-MANUAL-AUDIT-EXPANSION` | More manual samples (delisting / liquidation / managed / alert). | NOT approved |
| `S2-DELISTING-LIQUIDATION-PARSER-FEASIBILITY-A0` | Separate feasibility for delisting / liquidation (attachment-heavy). | NOT approved |
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

`S2-HTML-INLINE-PARSER-BODY-COVERAGE-EXPANSION-A0` is closed. No active work
remains after housekeeping. Await explicit user / Referee decision for any future
body-coverage completion, correction-linkage full-universe validation, delisting /
liquidation expansion, intraday halt source, official limit-lock source,
lifecycle refinement, ops patch, or strategy phase.
