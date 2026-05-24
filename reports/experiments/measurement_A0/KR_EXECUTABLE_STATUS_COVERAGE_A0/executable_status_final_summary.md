# KR-EXECUTABLE-STATUS-COVERAGE-A0 — Final Summary

Date: 2026-05-24  
Predecessor: KR-LISTED-UNIVERSE-COVERAGE-A0 CLOSED.

## Scope respected

- Measurement-layer executable-status source acquisition + coverage audit only.
- No strategy testing.
- No performance diagnostics.
- No execution simulation.
- No production / paper / P08 / live / shadow.

## What was delivered

Code artifacts:
- `src/audit/measurement_a0/p_executable_status_coverage.py`

Data artifacts:
- (none new — S3 KRX status events already acquired in Round 4)

Reports (this dir, 12 outputs):
1. `executable_status_referee_lock.md`
2. `source_inventory.md` (7 sources)
3. `official_executable_status_source_report.md`
4. `executable_status_taxonomy.md` (15+ canonical labels)
5. `executable_status_coverage_table.csv`
6. `w001_tradable_state_reconciliation.md`
7. `w001_tradable_state_reconciliation_ledger.csv`
8. `listed_lifecycle_executable_reconciliation.md`
9. `ohlcv_status_overlap_audit.md`
10. `executable_status_defect_ledger.csv`
11. `executable_status_gate_status.md`
12. `executable_status_final_summary.md` (this file)

## Source acquisition

- Primary: S3 KRX status events `data/acquired/round4/s3_krx_status/krx_status_events_2018_2026.csv`
  - Date range: 2018-01-01 → 2026-05-06
  - Events: **10774**
  - Unique tickers: **1855**
- Status category breakdown:
  - `suspension_related`: 4978
  - `delisting`: 2790
  - `resumption_related`: 1940
  - `other`: 762
  - `managed`: 290
  - `investment_alert`: 13
  - `liquidation`: 1

## Reconciliation headline (S3 vs W001 v2 tradable_state)

| class | count |
|---|---:|
| `official_status_but_panel_absent` | 9551 |
| `requires_manual_review` | 762 |
| `proxy_only` | 304 |
| `official_resumption_but_repo_other` | 94 |
| `matched_status` | 63 |

## Lifecycle cross-check

| class | count |
|---|---:|
| `s3_event_with_lifecycle_and_terminal` | 1723 |
| `s3_event_not_in_lifecycle` | 132 |

## Defect ledger

- Total defects: **4**
- Classes: official-vs-repo disagreement, proxy-only (managed/alert/liquidation),
  W001 v2 terminal without S3 event, limit-lock proxy-only, intraday-halt-source-missing,
  pre-2018 status coverage gap.

## Executable-status gate state: **PARTIAL**

## Pass criteria evaluation

| criterion | status |
|---|---|
| Executable-status source candidates identified + documented | YES (7 sources surveyed) |
| Best-available source acquired or failure documented | YES (S3 KRX status events; intraday-halt + limit-lock gaps documented) |
| Taxonomy separates official / proxy / unknown / panel-absence | YES (15+ labels with confidence column) |
| W001 tradable_state reconciled where possible | YES |
| Listed-lifecycle cross-checked | YES |
| OHLCV invalid rows not used as sole executable-status proof | YES (cross-check rule documented) |
| Defect ledger produced | YES |
| Gate status explicitly stated | YES |
| No strategy test / execution sim / performance metric produced | YES |

## Hard locks (preserved)

- No return / NAV / Sharpe / CAGR / MDD / alpha / strategy / execution sim
  / production / paper / P08 / live / shadow.
- No survivorship-safe claim.
- No executable claim from panel presence.
- No card is strategy-ready.

## Awaiting Referee

Per Referee-defined exit conditions, Referee will decide whether to:
- A. close as executable-status source acquired and reconciled,
- B. require another reconciliation pass,
- C. open listed-universe daily lifecycle refinement,
- D. open ops NAV blocker patch,
- E. keep all strategy research closed.
