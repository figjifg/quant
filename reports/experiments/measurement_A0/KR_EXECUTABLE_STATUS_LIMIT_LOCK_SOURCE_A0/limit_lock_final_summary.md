# KR-EXECUTABLE-STATUS-LIMIT-LOCK-SOURCE-A0 — Final Summary

Date: 2026-05-24  
Predecessor: KR-EXECUTABLE-STATUS-COVERAGE-A0 CLOSED.

## Scope respected

- Measurement-layer limit-lock source acquisition + reconciliation audit only.
- No strategy testing.
- No performance diagnostics.
- No execution simulation.
- No production / paper / P08 / live / shadow.

## What was delivered

Code artifacts:
- `src/audit/measurement_a0/p_limit_lock_source_coverage.py`

Reports (this dir, 12 outputs):
1. `limit_lock_referee_lock.md`
2. `source_inventory.md` (5 sources)
3. `official_limit_lock_source_report.md`
4. `limit_lock_taxonomy.md`
5. `limit_lock_coverage_table.csv`
6. `w001_limit_candidate_reconciliation.md`
7. `w001_limit_candidate_reconciliation_ledger.csv`
8. `conservative_execution_rule_design.md`
9. `ohlcv_limit_overlap_audit.md`
10. `limit_lock_defect_ledger.csv`
11. `limit_lock_gate_status.md`
12. `limit_lock_final_summary.md` (this file)

## Headline source status

- **Official daily KRX limit-lock log: NOT IN REPO.** pykrx has no relevant
  endpoint; KRX 정보데이터시스템 단일가매매 requires separate scraping.
- **Best-available proxy**: KRX historical price-limit rule (±15% pre-
  2015-06-15, ±30% post-2015-06-15) applied to W001 v2 panel.

## Rule-derived candidates

- Panel rows scanned: **1141751**
- Total rule-derived candidates (upper or lower): **336**
- Matched with W001 v2 `limit_lock_candidate` flag: **2**
- Rule-only (W001 v2 missed): **334**
- W001 v2 only (no rule support): **39**
- W001 v2 `limit_lock_candidate` total: **41** (UNDER-COUNTED)

## OHLCV overlap audit

| tradable_state | rows also rule-derived candidates |
|---|---:|
| `panel_absence` | 123 |
| `true_suspension` | 63 |
| `delisting_transition` | 19 |
| `limit_lock_candidate` | 2 |
| `data_missing` | 1 |

## Defect ledger

- Total defects: **9**
- Classes: official source unavailable / W001 v2 under-counted / candidate
  lacks direction / close-at-limit vs locked indistinguishable / CA prev_close
  adjustment missing / IPO first-day rule missing / VI not captured / W001
  candidate without rule support / panel_absence overlap.

## Conservative execution rule design

Documented in `conservative_execution_rule_design.md`. Asymmetric: upper-lock
candidate → buy fail-closed; lower-lock candidate → sell fail-closed.
Implementation deferred to a future execution-simulation patch phase.

## Limit-lock gate state: **PARTIAL**

## Pass criteria evaluation

| criterion | status |
|---|---|
| Limit-lock source candidates identified + documented | YES (5 sources, including rule + W001 v2) |
| Official or best-available source acquired or failure documented | YES (no official log; rule applied as best-available; failure documented) |
| Taxonomy separates official / proxy / candidate / unknown | YES (10 labels with confidence column) |
| W001 v2 candidate rows reconciled or classified | YES |
| OHLCV invalid rows not used as sole limit-lock proof | YES (rule precedence documented) |
| Conservative future execution rule design documented | YES |
| Defect ledger produced | YES |
| Gate status explicitly stated | YES (PARTIAL) |
| No strategy test / execution sim / performance metric produced | YES |

## Hard locks (preserved)

- No return / NAV / Sharpe / CAGR / MDD / alpha / strategy / execution sim
  / production / paper / P08 / live / shadow.
- No survivorship-safe claim.
- No executable claim from panel presence.
- No OHLCV signature treated as official limit-lock proof.
- No card is strategy-ready.

## Awaiting Referee

Per Referee-defined exit conditions, Referee will decide whether to:
- A. close as limit-lock source acquired and reconciled,
- B. require another reconciliation pass,
- C. open executable-status pre-2018 extension,
- D. open listed-universe daily lifecycle refinement,
- E. keep all strategy research closed.
