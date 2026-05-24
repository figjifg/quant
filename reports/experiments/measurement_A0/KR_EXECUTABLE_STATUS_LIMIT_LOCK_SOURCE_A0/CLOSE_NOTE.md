# KR-EXECUTABLE-STATUS-LIMIT-LOCK-SOURCE-A0 — Final Close Note

Date: 2026-05-24  
Verdict source: Referee final close verdict, 2026-05-24.  
Initial pass commit accepted: `8d0003b` on origin/main.

## Verdict

**CLOSED AS LIMIT-LOCK-PROXY-RECONCILED / PARTIAL COVERAGE / EXECUTION STILL CLOSED.**

- Decision: option **A variant** (close as limit-lock source/proxy reconciled).
- No additional reconciliation pass required now.
- No execution simulation opened.
- No strategy testing reopened.
- No performance diagnostics reopened.
- No production / paper / P08 / live readiness / shadow-track work touched.

## Accepted deliverables (12)

1. `limit_lock_referee_lock.md`
2. `source_inventory.md` (5 sources)
3. `official_limit_lock_source_report.md`
4. `limit_lock_taxonomy.md` (10 canonical labels + 4-level confidence)
5. `limit_lock_coverage_table.csv` (375 rows)
6. `w001_limit_candidate_reconciliation.md`
7. `w001_limit_candidate_reconciliation_ledger.csv` (375 rows)
8. `conservative_execution_rule_design.md` (asymmetric upper/lower, design-only)
9. `ohlcv_limit_overlap_audit.md`
10. `limit_lock_defect_ledger.csv` (9 entries)
11. `limit_lock_gate_status.md`
12. `limit_lock_final_summary.md`

## Source status (accepted)

- Official daily KRX limit-lock log: **NOT IN REPO**.
- pykrx exposes no relevant limit-lock endpoint.
- KRX 정보데이터시스템 단일가매매 endpoint NOT acquired in this phase.
- Best-available: **rule-derived proxy** from KRX historical price-limit rule.

## Rule basis (accepted)

- KOSPI / KOSDAQ price limit:
  - until 2015-06-14: **±15%**
  - from 2015-06-15: **±30%**
- Candidate detection: `|close − prev_close × (1 ± lim_pct)| / limit_price ≤ 0.001`.
- Semi-official rule-derived proxy, NOT official lock evidence.

## Accepted candidate result

- Panel rows scanned: **1,141,751**.
- `close_at_upper_limit_candidate`: **325**.
- `close_at_lower_limit_candidate`: **11**.
- Total rule-derived candidates: **336**.

## Accepted reconciliation vs W001 v2 limit_lock_candidate

| class | count |
|---|---:|
| matched_limit_candidate | 2 |
| rule_candidate_but_no_repo_flag | 334 |
| repo_candidate_but_no_official_support | 39 |

→ Conclusion accepted: **W001 v2 `limit_lock_candidate` is materially under-counted and
lacks direction.** Rule-derived set is the preferred proxy going forward (still not
official).

## Accepted OHLCV / tradable_state overlap

| tradable_state | rows also rule-derived candidates |
|---|---:|
| panel_absence | 123 |
| true_suspension | 63 |
| delisting_transition | 19 |
| data_missing | 1 |
| limit_lock_candidate | 2 |

Precedence accepted: **OHLCV quarantine + executable-status OUTRANK limit candidate
label.**

## Accepted conservative execution rule design (design-only)

- upper-limit candidate + buy intent → **fail-closed**.
- lower-limit candidate + sell intent → **fail-closed**.
- unknown → **fail-closed**.
- W001 v2 proxy with no direction → **fail-closed for both directions**.
- OHLCV quarantine and executable-status rules **OUTRANK** limit candidate.
- Does **NOT** run execution simulation.

## Accepted defects (9)

1. `official_limit_lock_source_unavailable`
2. `w001_v2_candidate_set_under_counted`
3. `candidate_lacks_direction_in_w001`
4. `close_at_limit_vs_locked_indistinguishable`
5. `corporate_action_prev_close_adjustment`
6. `first_day_listing_no_limit_rule`
7. `vi_circuit_breaker_not_captured`
8. `w001_candidate_no_rule_support`
9. `panel_absence_overlap_with_rule_candidate`

## Accepted gate state

**PARTIAL** (per Referee-permitted enum).

## Accepted limitations

- Official KRX daily limit-lock log still missing.
- KRX 단일가매매 / limit-lock endpoint NOT acquired.
- Rule-derived close-at-limit ≠ locked / unexecutable.
- Close at upper or lower limit does NOT prove order book availability.
- Corporate actions can distort previous-close limit calculations.
- First listing day / relisting day may lack a valid previous close rule.
- VI / intraday circuit breaker status NOT captured.
- W001 v2 proxy lacks upper/lower direction.
- Unknown MUST remain unknown.
- Candidate MUST NOT be promoted to official executable-status evidence.

## Possible future phases (none active)

| Phase id | Purpose | Status |
|---|---|---|
| `KR-EXECUTABLE-STATUS-PRE2018-EXTENSION-A0` | Extend S3 executable-status coverage pre-2018 | NOT approved (**Referee-recommended next** for practical backtest-readiness) |
| `KR-EXECUTABLE-STATUS-LIMIT-LOCK-OFFICIAL-SOURCE-A0` | Direct KRX/KOSCOM official limit-lock source acquisition | NOT approved |
| `KR-LIMIT-LOCK-CORPORATE-ACTION-ADJUSTMENT-A0` | Audit CA effects on prev-close limit calculations | NOT approved |
| `KR-INTRADAY-HALT-SOURCE-BACKLOG` | Intraday halt / VI / circuit-breaker source | NOT approved |
| `KR-LISTED-UNIVERSE-DAILY-LIFECYCLE-REFINEMENT-A0` | Monthly → daily lifecycle | NOT approved |
| `KR-OPS-NAV-UPDATE-QUARANTINE-PATCH-PHASE` | Patch the 4 remaining ops blockers | NOT approved |

Referee-recommended next candidate (if user chooses to continue):
**`KR-EXECUTABLE-STATUS-PRE2018-EXTENSION-A0`** — calendar, OHLCV guard,
listed-universe, 2018+ executable-status, limit-lock proxy now partially covered.
Pre-2018 executable-status gap is one of the largest historical coverage blockers.
Must NOT auto-start.

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
- No OHLCV signature treated as official limit-lock proof.
- No rule-derived candidate treated as official lock evidence.
- No close-at-limit treated as locked / unexecutable without conservative rule.
- No production / paper / P08 / live readiness / shadow connection.
- No card may be described as strategy-ready.

## End condition

`KR-EXECUTABLE-STATUS-LIMIT-LOCK-SOURCE-A0` is **closed as LIMIT-LOCK-PROXY-RECONCILED
/ PARTIAL COVERAGE / EXECUTION STILL CLOSED**. No active work remains. Await explicit
user / Referee decision for any future pre-2018 extension, official limit-lock source,
intraday halt source, lifecycle refinement, ops patch, parser, or strategy phase.
