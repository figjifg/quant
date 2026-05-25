# KR-STATUS-EFFECTIVE-DATE-MANUAL-AUDIT-PHASE — Final Close Note

Date: 2026-05-25  
Verdict source: Referee final close verdict, 2026-05-25.  
Initial pass commit accepted: `046cf20` on origin/main.

## Verdict

**CLOSED AS MANUAL-AUDIT-COMPLETED / SUPPORTS HTML-INLINE PARSER REOPEN / EXECUTION
STILL CLOSED.**

- Decision: option **A** (close as manual effective-date audit completed).
- No additional manual samples required now.
- No S2 HTML-inline parser opened automatically.
- No execution simulation opened.
- No strategy testing reopened.
- No performance diagnostics reopened.
- No production / paper / P08 / live readiness / shadow-track work touched.
- No card is strategy-ready.

## Accepted scope

- Measurement-layer manual audit only.
- BeautifulSoup-driven Korean-label search over OPENDART document.xml bodies.
- No full parser build.
- No S2 parser reopen.
- No strategy testing.
- No performance diagnostics.
- No execution simulation.
- No production / paper / P08 / live / shadow.
- No credential committed.

## Accepted deliverables (12)

1. `manual_audit_referee_lock.md`
2. `manual_sample_plan.csv` (195 rows)
3. `manual_effective_date_audit.csv` (195 rows)
4. `manual_body_format_summary.md`
5. `manual_rcept_dt_relation_summary.md`
6. `correction_manual_review.md`
7. `effective_date_label_inventory.csv` (30 tuples)
8. `parser_feasibility_assessment.md`
9. `manual_audit_reliability.md`
10. `effective_date_blocker_update.csv`
11. `manual_audit_gate_status.md`
12. `manual_audit_final_summary.md`

Build script: `src/audit/measurement_a0/p_manual_effective_date_audit.py`.  
Data cache (gitignored): `data/acquired/round5_manual_audit_samples/` (195 ZIPs;
reproducible via build script).

## Accepted sample plan (195 total, within 150-200 Referee target)

| bucket | count |
|---|---:|
| managed_bucket | 30 |
| suspension_related_pre | 20 |
| suspension_related_post | 20 |
| resumption_related_pre | 20 |
| resumption_related_post | 20 |
| delisting_pre | 20 |
| delisting_post | 20 |
| correction_flagged | 20 |
| prior_failed_extraction | 20 |
| liquidation_all | 3 |
| prior_successful_control | 2 |

## Accepted headline result

- Effective-date extraction rate: **110 / 195 = 56.4%**.
- Prior simple-regex A0: 2 / 113 = 1.8%.
- **31× lift** accepted as evidence that HTML-inline effective-date extraction is
  feasible for some categories.
- This does NOT mean parser is already implemented.
- This does NOT mean extraction is complete across all categories.

## Accepted body-format finding

| format | count |
|---|---:|
| `html_inline` | 188 |
| `unparseable` | 7 |
| `structured_xml` | 0 |
| `download_failed` | 0 |

Interpretation: KRX status disclosures are overwhelmingly HTML-inline.

## Accepted classification distribution

| classification | count |
|---|---:|
| `explicit_suspension_period` | 63 |
| `no_date_found` | 60 |
| `explicit_resumption_date` | 36 |
| `ambiguous_date` | 18 |
| `explicit_effective_date` | 10 |
| `body_unavailable` | 7 |
| `explicit_liquidation_period` | 1 |

## Accepted rcept_dt relation finding

| relation | count |
|---|---:|
| `unknown` | 139 |
| `equal_to_rcept_dt` | 27 |
| `after_rcept_dt` | 18 |
| `before_rcept_dt` | 11 |

Conclusion: `rcept_dt` frequently differs from `effective_date`. Existing locks
remain **permanent**:

- No `rcept_dt` treated as effective status date.
- No `effective_date` inferred from `rcept_dt` fallback.

## Accepted label inventory

- 30 distinct `(label × category × format)` tuples.
- 12 distinct Korean date labels observed (expanded from 9 prior patterns).

## Accepted parser feasibility by category

| category | n | extraction_rate | verdict |
|---|---:|---:|---|
| `suspension_related` | 67 | 92.5% | `parser_feasible_html_inline` |
| `resumption_related` | 41 | 90.2% | `parser_feasible_html_inline` |
| `delisting` | 52 | 3.8% | `parser_not_feasible_without_attachment` |
| `managed` | 28 | 28.6% | `parser_feasible_with_custom_rules` |
| `liquidation` | 3 | 0.0% | `parser_not_feasible_without_attachment` |
| `investment_alert` | 1 | 0.0% | `parser_not_feasible_without_attachment` |
| `short_term_overheated` | 1 | 0.0% | `parser_not_feasible_without_attachment` |
| `other` | 2 | 50.0% | `parser_feasible_html_inline` |

**Overall parser feasibility verdict: `parser_feasible_html_inline`** — driven by
suspension + resumption parseability from HTML-inline bodies.

Important limitations:

- Delisting / liquidation / investment_alert / short_term_overheated are NOT
  sufficiently solved by this audit.
- Managed category needs custom rules.
- Correction linkage remains unresolved (depends on S2-style corp_code +
  base_form + series_marker linkage).

## Accepted reliability distribution

| reviewer_confidence | count |
|---|---:|
| `high` | 110 |
| `medium` | 18 |
| `low` | 67 |

## Accepted defect / blocker updates (5)

| blocker_id | prior | updated |
|---|---|---|
| `EDL_BLK_01 effective_date_unextracted_majority` | open | partial |
| `EDL_BLK_02 html_inline_unparsed` | open | parser_required |
| `EDL_BLK_03 correction_linkage_partial` | open | still_open |
| `EDL_BLK_04 rcept_dt_default_forbidden` | open | closed (lock permanent) |
| `EDL_BLK_05 body_download_failures` | open | closed (0 / 195) |

## Accepted gate state

**MANUAL_AUDIT_SUPPORTS_PARSER_REOPEN** (per Referee-permitted enum).

## Referee interpretation (paraphrased)

- The manual audit achieved its purpose.
- Effective dates are often present in HTML-inline bodies.
- Simple regex was too weak; BeautifulSoup-style label extraction is materially
  better.
- The result supports a future S2 HTML-inline parser reopen phase.
- Parser reopen is NOT automatic.
- This phase did not implement a parser.
- This phase did not reopen S2.
- This phase did not create execution-simulation readiness.
- This phase did not make any strategy testable.
- The correct close status is NOT PASS-to-backtest.
- The correct close status is: manual audit completed, supports parser reopen,
  execution still closed.

## Important remaining blockers

- Correction linkage remains open (S2-style corp_code + base_form + series_marker
  linkage dependency).
- Delisting effective dates poorly extracted from current manual sample.
- Liquidation / investment_alert / short_term_overheated are attachment- or
  manual-review-heavy.
- Managed events need custom rules.
- `rcept_dt` remains forbidden as `effective_date` fallback.
- Execution simulation remains closed.

## Possible future phases (none active)

| Phase id | Purpose | Status |
|---|---|---|
| `S2-HTML-INLINE-PARSER-REOPEN-PHASE` | Reopen parser work for HTML-inline status disclosures. Initial scope = suspension_related + resumption_related only. | NOT approved |
| `KR-STATUS-EFFECTIVE-DATE-MANUAL-AUDIT-EXPANSION` | Add more manual samples (delisting / liquidation / managed / alert). | NOT approved |
| `KR-STATUS-CORRECTION-LINKAGE-A0` | Resolve correction linkage using corp_code + base_form + series_marker. | NOT approved |
| `KR-INTRADAY-HALT-SOURCE-BACKLOG` | Intraday halt / VI / circuit-breaker source. | NOT approved |
| `KR-EXECUTABLE-STATUS-LIMIT-LOCK-OFFICIAL-SOURCE-A0` | Direct KRX/KOSCOM official limit-lock acquisition. | NOT approved |
| `KR-LIMIT-LOCK-CORPORATE-ACTION-ADJUSTMENT-A0` | CA effects on prev-close limit. | NOT approved |
| `KR-LISTED-UNIVERSE-DAILY-LIFECYCLE-REFINEMENT-A0` | Monthly → daily lifecycle / merger linkage / rename / code reuse. | NOT approved |
| `KR-OPS-NAV-UPDATE-QUARANTINE-PATCH-PHASE` | 4 ops blockers. | NOT approved |

Referee-strongest next candidate: **`S2-HTML-INLINE-PARSER-REOPEN-PHASE`**
(suspension + resumption only, HTML-inline body only, no delisting / liquidation
parser first pass, no strategy testing, no execution simulation).

Alternative: `KR-STATUS-EFFECTIVE-DATE-MANUAL-AUDIT-EXPANSION`.

Auto-start is forbidden.

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
- No parser result described as strategy-ready.
- No production / paper / P08 / live readiness / shadow connection.
- No card may be described as strategy-ready.

## End condition

`KR-STATUS-EFFECTIVE-DATE-MANUAL-AUDIT-PHASE` is **closed as MANUAL-AUDIT-COMPLETED
/ SUPPORTS HTML-INLINE PARSER REOPEN / EXECUTION STILL CLOSED**. No active work
remains after housekeeping. Await explicit user / Referee decision for any future
parser reopen, manual expansion, correction linkage, intraday halt source, official
limit-lock source, lifecycle refinement, ops patch, or strategy phase.
