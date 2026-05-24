# KR-STATUS-EFFECTIVE-DATE-MANUAL-AUDIT-PHASE — Final Summary

Date: 2026-05-25  
Predecessor: KR-EXECUTABLE-EFFECTIVE-DATE-LINKAGE-A0 CLOSED.

## Scope respected

- Measurement-layer manual audit only.
- bs4-driven Korean-label search (broader than prior simple regex).
- No parser implementation. No S2 parser reopen.
- No strategy testing. No execution simulation. No performance.
- No production / paper / P08 / live / shadow.

## What was delivered

Code artifacts:
- `src/audit/measurement_a0/p_manual_effective_date_audit.py`

Data artifacts (gitignored):
- `data/acquired/round5_manual_audit_samples/` (per-sample document.xml cache)

Reports (this dir, 12 outputs):
1. `manual_audit_referee_lock.md`
2. `manual_sample_plan.csv`
3. `manual_effective_date_audit.csv`
4. `manual_body_format_summary.md`
5. `manual_rcept_dt_relation_summary.md`
6. `correction_manual_review.md`
7. `effective_date_label_inventory.csv`
8. `parser_feasibility_assessment.md`
9. `manual_audit_reliability.md`
10. `effective_date_blocker_update.csv`
11. `manual_audit_gate_status.md`
12. `manual_audit_final_summary.md` (this file)

## Sample plan (executed)

- Total samples reviewed: **195**

| bucket | count |
|---|---:|
| `managed_bucket` | 30 |
| `suspension_related_pre` | 20 |
| `suspension_related_post` | 20 |
| `resumption_related_pre` | 20 |
| `resumption_related_post` | 20 |
| `delisting_pre` | 20 |
| `delisting_post` | 20 |
| `correction_flagged` | 20 |
| `prior_failed_extraction` | 20 |
| `liquidation_all` | 3 |
| `prior_successful_control` | 2 |

## Body format breakdown

| format | count |
|---|---:|
| `html_inline` | 188 |
| `unparseable` | 7 |

## Classification distribution

| classification | count |
|---|---:|
| `explicit_suspension_period` | 63 |
| `no_date_found` | 60 |
| `explicit_resumption_date` | 36 |
| `ambiguous_date` | 18 |
| `explicit_effective_date` | 10 |
| `body_unavailable` | 7 |
| `explicit_liquidation_period` | 1 |

## Effective-date extraction rate: **56.4%**

## Label inventory: **30** distinct (label × category × format) tuples

## Parser feasibility verdict: **parser_feasible_html_inline**

## Manual-audit gate state: **MANUAL_AUDIT_SUPPORTS_PARSER_REOPEN**

## Comparison with prior simple-regex A0

| metric | prior A0 | this phase |
|---|---:|---:|
| samples | 113 | 195 |
| extraction rate | 1.8% | 56.4% |
| label coverage | 9 patterns | 12 distinct labels found |

## Pass criteria evaluation

| criterion | status |
|---|---|
| Manual sample plan documented | YES |
| Major event categories covered | YES |
| Pre-2018 + post-2018 both represented | YES |
| Effective-date evidence classified | YES |
| rcept_dt relation measured manually | YES |
| Correction / cancellation samples reviewed | YES |
| Label inventory produced | YES |
| Parser feasibility assessed | YES |
| Defect / blocker update produced | YES |
| Gate status explicitly stated | YES |
| No strategy test / execution sim / performance metric produced | YES |

## Hard locks (preserved)

- No return / NAV / Sharpe / CAGR / MDD / alpha / strategy / execution sim /
  production / paper / P08 / live / shadow.
- No rcept_dt defaulted to effective date.
- No panel / OHLCV used as effective-date proof.
- No card is strategy-ready.
- No parser implementation in this phase.
- No credential committed.

## Awaiting Referee

Per Referee-defined exit conditions, Referee will decide whether to:
- A. close as manual audit completed,
- B. require more samples,
- C. open S2 HTML-inline parser reopen phase,
- D. keep manual-only effective-date path,
- E. keep all strategy research closed.
