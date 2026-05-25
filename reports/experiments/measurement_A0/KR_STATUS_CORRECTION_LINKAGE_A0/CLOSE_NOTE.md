# KR-STATUS-CORRECTION-LINKAGE-A0 — Final Close Note

Date: 2026-05-25  
Verdict source: Referee final close verdict, 2026-05-25.  
Commits accepted as evidence: Pass 1 `3d09033`, Pass 2 `565f0d3`, Pass 3 `2f890d7`
(all on origin/main).

## Verdict

**CLOSED AS CORRECTION-LINKAGE VALIDATED FOR SAMPLE / HIGH_VALIDATED ONLY /
EXECUTION STILL CLOSED.**

- Decision: option **A** (close as correction linkage validated for sample).
- No additional correction-linkage pass required now.
- No full-universe parser validation opened automatically.
- No delisting / liquidation manual expansion opened automatically.
- No execution simulation opened.
- No strategy testing reopened.
- No performance diagnostics reopened.
- No production / paper / P08 / live readiness / shadow-track work touched.
- No card is strategy-ready.

## Accepted scope

- Measurement-layer correction-linkage A0 only.
- suspension_related + resumption_related only.
- HTML-inline status disclosures only.
- correction-flagged rows + candidate originals only.
- No delisting / liquidation / managed / alert parser.
- No DART body alpha. No overhang. No all-event event log.
- No C2/C3 wiring. No strategy testing. No execution simulation.
- No performance diagnostics. No production / paper / P08 / live / shadow.

## Accepted commits (3 passes)

| commit | role |
|---|---|
| `3d09033` | Pass 1 (accepted as evidence) — 53.3% sample / 123 no_link |
| `565f0d3` | Pass 2 (accepted as evidence) — raw pool + cross-cat + rcept_dt parser fix; 70 no_link; 55.1% sample |
| `2f890d7` | Pass 3 (close-ready) — body-confirmation gate + 5-tier confidence; 78.1% sample; gate READY_FOR_NEXT_A0_REVIEW |

## Accepted code artifacts

- `src/audit/measurement_a0/p_status_correction_linkage.py` (Pass 1)
- `src/audit/measurement_a0/p_status_correction_linkage_pass2.py` (Pass 2)
- `src/audit/measurement_a0/p_status_correction_linkage_pass3.py` (Pass 3)

## Accepted Pass-3 deliverables (12 + 1 detail CSV)

1. `pass3_referee_lock.md`
2. `pass3_wrong_candidate_root_cause.md` + `pass3_wrong_candidate_root_cause_detail.csv`
3. `pass3_scoring_variants.csv`
4. `pass3_body_confirmation_rules.md`
5. `pass3_candidate_links_recalibrated.csv` (with `supersession_ready` field)
6. `pass3_remaining_no_link_ledger.csv`
7. `pass3_manual_validation_sample.csv` (72 rows)
8. `pass3_manual_validation_summary.md`
9. `pass3_supersession_readiness.md`
10. `pass3_defect_delta.csv`
11. `pass3_gate_status.md`
12. `pass3_final_summary.md`

Pass-1 (12) and Pass-2 (12) artifacts preserved untouched.

## Accepted body-confirmation gate

- `high_validated` requires:
  - `body_format = html_inline`,
  - `body_refs_candidate_title` OR `body_refs_candidate_date`,
  - same-corp ∨ same-stock, event_type_compat, same_base_form,
    `margin ≥ 1.5`, `title_similarity ≥ 0.60`,
  - NOT cross-category.
- Body unavailable → cap at `medium_needs_manual`.
- Body cross-check fails AND score was high → `rejected_wrong_candidate`.

## Accepted 5-tier confidence enum

- `high_validated`
- `medium_needs_manual`
- `low_needs_manual`
- `no_link`
- `rejected_wrong_candidate`

## Accepted Pass-3 universe-level status (166 in-scope corrections)

- `high_validated`: 35
- `medium_needs_manual`: 42
- `low_needs_manual`: 18
- `no_link`: 71
- `rejected_wrong_candidate`: 0 at universe level (body-confirmation run on sample only).

## Accepted Pass-3 manual validation

- Sample size: 72.
- `linked_unambiguous`: 9.
- `linked_likely`: 16.
- `rejected_wrong_candidate`: 10 (Pass-2 wrong cases caught by Pass-3 body gate).
- `manual_review_required`: 7.
- `no_original_found`: 30.
- Eligible: 32.
- Linked total: 25.
- **Sample link rate: 25 / 32 = 78.1%**.
- Residual FP in linked pool: 0 (by construction — every linked row has body cross-check support).
- Date-change markers in sample: 59 / 72 = 82%.

## Accepted remaining no_link classification

- `original_not_in_raw_pool`: 44
- `insufficient_evidence`: 25
- `original_likely_cross_category_not_allowed`: 1
- `original_possible_but_title_too_generic`: 1

## Accepted supersession readiness (design-only)

- 9 rows tagged `supersession_ready = yes`.
- Conditions: `high_validated` AND body-confirmed AND body has date-change marker
  AND NOT cross-category.
- No downstream wiring. No C2/C3. No execution simulation. No strategy use.

## Accepted parser interaction

- Parser still detects `correction_flag`.
- Parser still forces `manual_review_required = True` on correction rows.
- No `parser_extracts_correction_without_manual_review` defect.
- Correction row parser output remains non-authoritative.

## Accepted gate state

**`READY_FOR_NEXT_A0_REVIEW`** (per Referee-permitted enum). Used to support
sample-level close; does NOT authorise execution / strategy / production
downstream.

## Referee interpretation (paraphrased)

- Pass 3 achieved the correction-linkage A0 objective at sample level.
- Pass 1 and Pass 2 showed the problem.
- Pass 3 introduced a body-confirmation gate that materially reduced wrong-
  candidate risk.
- The Pass-3 linked pool has zero observed residual false positives in the
  manual sample.
- The `high_validated` tier is useful as a design-level validated link class.
- This does NOT validate all 166 in-scope corrections.
- This does NOT validate the full 17,924-row status-event universe.
- This does NOT make medium / low / no_link rows usable.
- This does NOT make correction rows authoritative by default.
- This does NOT open execution simulation, strategy testing, or any production-
  side path.
- No card is strategy-ready.

## Important remaining limits

- 71 / 166 in-scope corrections remain `no_link`.
- 42 `medium_needs_manual` rows remain manual review only.
- 18 `low_needs_manual` rows remain manual review only.
- Cross-category links remain capped at medium and are NOT supersession-ready.
- Supersession is design-only; no wiring authorised.
- Full-universe correction-linkage validation has NOT run.
- Parser output remains limited to suspension / resumption HTML-inline scope.
- Delisting / liquidation / managed / alert parser remain out of scope.
- C2/C3 event-log finalization remains forbidden.
- Execution simulation remains closed.
- Strategy testing remains closed.

## Possible future phases (none active)

| Phase candidate | Purpose | Status |
|---|---|---|
| `S2-HTML-INLINE-PARSER-FULL-UNIVERSE-VALIDATION-A0` | Validate parser + correction-linkage against broader status-event universe. **Referee-strongest next candidate.** | NOT approved |
| `KR-STATUS-CORRECTION-LINKAGE-FULL-UNIVERSE-VALIDATION-A0` | Isolate correction-linkage validation across all 166 in-scope corrections + beyond sample. | NOT approved |
| `KR-STATUS-EFFECTIVE-DATE-MANUAL-AUDIT-EXPANSION` | More manual samples for delisting / liquidation / managed / alert. | NOT approved |
| `S2-DELISTING-LIQUIDATION-PARSER-FEASIBILITY-A0` | Separate feasibility for delisting / liquidation (attachment-heavy). | NOT approved |
| `KR-INTRADAY-HALT-SOURCE-BACKLOG` | Intraday halt / VI / circuit-breaker source. | NOT approved |
| `KR-EXECUTABLE-STATUS-LIMIT-LOCK-OFFICIAL-SOURCE-A0` | Direct KRX/KOSCOM official limit-lock acquisition. | NOT approved |
| `KR-LIMIT-LOCK-CORPORATE-ACTION-ADJUSTMENT-A0` | CA effects on prev-close limit. | NOT approved |
| `KR-LISTED-UNIVERSE-DAILY-LIFECYCLE-REFINEMENT-A0` | Monthly → daily lifecycle / merger linkage / rename / code reuse. | NOT approved |
| `KR-OPS-NAV-UPDATE-QUARANTINE-PATCH-PHASE` | 4 ops blockers. | NOT approved |

Strategy testing remains **premature**. Backtesting remains premature. Auto-start
forbidden.

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
- No executable assumption from panel presence.
- No survivorship-safe claim unless explicitly supported.
- No unknown status treated as executable.
- No panel absence treated as non-tradable.
- No OHLCV signature treated as suspension proof.
- No rule-derived limit candidate treated as official lock evidence.
- No `rcept_dt` treated as effective status date.
- No `effective_date` inferred from `rcept_dt` fallback.
- No parser result described as strategy-ready.
- No correction row treated as authoritative unless linked AND validated.
- No medium / low / no_link correction row treated as authoritative.
- No supersession rule wired downstream.
- No production / paper / P08 / live readiness / shadow connection.
- No card may be described as strategy-ready.

## End condition

`KR-STATUS-CORRECTION-LINKAGE-A0` is **closed as CORRECTION-LINKAGE VALIDATED FOR
SAMPLE / HIGH_VALIDATED ONLY / EXECUTION STILL CLOSED**. No active work remains
after housekeeping. Await explicit user / Referee decision for any future
full-universe parser validation, correction-linkage full-universe validation,
delisting / liquidation expansion, intraday halt source, official limit-lock
source, lifecycle refinement, ops patch, or strategy phase.
