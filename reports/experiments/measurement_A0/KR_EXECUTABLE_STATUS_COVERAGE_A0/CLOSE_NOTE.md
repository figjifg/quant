# KR-EXECUTABLE-STATUS-COVERAGE-A0 — Final Close Note

Date: 2026-05-24  
Verdict source: Referee final close verdict, 2026-05-24.  
Initial pass commit accepted: `712d45b` on origin/main.

## Verdict

**CLOSED AS EXECUTABLE-STATUS-SOURCE-ACQUIRED / PARTIAL COVERAGE / EXECUTION STILL CLOSED.**

- Decision: option **A** (close as executable-status source acquired and reconciled).
- More precisely: semi-official S3 source accepted; coverage remains PARTIAL;
  execution simulation stays CLOSED.
- No additional reconciliation pass required now.
- No execution simulation opened.
- No strategy testing reopened.
- No performance diagnostics reopened.
- No production / paper / P08 / live readiness / shadow-track work touched.

## Accepted deliverables (12)

1. `executable_status_referee_lock.md`
2. `source_inventory.md` (7 sources surveyed)
3. `official_executable_status_source_report.md`
4. `executable_status_taxonomy.md` (15+ canonical labels)
5. `executable_status_coverage_table.csv` (10,774 rows)
6. `w001_tradable_state_reconciliation.md`
7. `w001_tradable_state_reconciliation_ledger.csv` (10,774 rows)
8. `listed_lifecycle_executable_reconciliation.md`
9. `ohlcv_status_overlap_audit.md`
10. `executable_status_defect_ledger.csv` (4 entries)
11. `executable_status_gate_status.md`
12. `executable_status_final_summary.md`

## Accepted source

- Primary semi-official: **S3 KRX status events** (OPENDART pblntfty=I 거래소공시
  filtered) — `data/acquired/round4/s3_krx_status/krx_status_events_2018_2026.csv`.
- 10,774 events / 1,855 unique tickers / 2018-01-01 → 2026-05-06.
- Categories: suspension / resumption / delisting / managed / investment_alert /
  liquidation / other.

## Accepted reconciliation (S3 vs W001 v2 tradable_state)

| class | count |
|---|---:|
| official_status_but_panel_absent | 9,551 |
| requires_manual_review | 762 |
| proxy_only | 304 |
| official_resumption_but_repo_other | 94 |
| matched_status | 63 |

The dominant `official_status_but_panel_absent` is a **dynamic_top100 panel-selection
artefact**, not a true status disagreement.

## Accepted lifecycle cross-check

- `s3_event_with_lifecycle_and_terminal`: 1,723
- `s3_event_not_in_lifecycle`: 132

## Accepted OHLCV overlap

- 41 `limit_lock_candidate` rows in W001 v2 tradable_state — accepted as
  **candidate-only**, NOT official limit-lock evidence.

## Accepted defects (4)

1. **intraday_halt_source_missing** (high) — KOSCOM/KRX real-time feed not in repo.
2. **pre_2018_status_coverage_gap** (high) — S3 covers 2018+ only.
3. **no_tradable_state_label_for_managed_alert_liquidation** (medium) — 304 S3 events
   have no W001 v2 equivalent label.
4. **limit_lock_proxy_only** (medium) — KRX official limit log not in repo.

## Accepted gate state

**PARTIAL** (per Referee-permitted enum).

## Accepted limitations

- S3 is semi-official OPENDART exchange disclosure data, not direct KRX feed.
- Coverage starts 2018; pre-2018 missing.
- Intraday halt windows NOT covered.
- Official upper-limit / lower-limit lock log NOT covered.
- Managed / investment-alert / liquidation labels lack W001 tradable_state equivalents.
- Effective status dates may differ from rcept_date (DART body parsing PARTIAL).
- Unknown status MUST NOT be treated as executable.
- Panel absence MUST NOT be treated as non-tradable.
- Volume > 0 MUST NOT be treated as full executable-status proof.
- OHL=0 / `close>0` MUST NOT be treated as suspension proof.

## Possible future phases (none active)

| Phase id | Purpose | Status |
|---|---|---|
| `KR-EXECUTABLE-STATUS-PRE2018-EXTENSION-A0` | Extend executable-status coverage pre-2018 | NOT approved |
| `KR-EXECUTABLE-STATUS-LIMIT-LOCK-SOURCE-A0` | Acquire official upper/lower-limit lock source | NOT approved |
| `KR-INTRADAY-HALT-SOURCE-BACKLOG` | KRX/KOSCOM intraday halt source (likely commercial) | NOT approved |
| `KR-LISTED-UNIVERSE-DAILY-LIFECYCLE-REFINEMENT-A0` | Monthly → daily lifecycle; merger linkage; rename; code reuse | NOT approved |
| `KR-OPS-NAV-UPDATE-QUARANTINE-PATCH-PHASE` | Patch the 4 remaining ops blockers | NOT approved |

Referee-recommended directions:

- If priority = historical completeness → `KR-EXECUTABLE-STATUS-PRE2018-EXTENSION-A0`.
- If priority = order/execution feasibility under limit-lock conditions →
  `KR-EXECUTABLE-STATUS-LIMIT-LOCK-SOURCE-A0`.
- If priority = survivorship quality before execution detail →
  `KR-LISTED-UNIVERSE-DAILY-LIFECYCLE-REFINEMENT-A0`.

Strategy testing remains **premature**. Backtesting remains premature.

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
- No production / paper / P08 / live readiness / shadow connection.
- No card may be described as strategy-ready.

## End condition

`KR-EXECUTABLE-STATUS-COVERAGE-A0` is **closed as EXECUTABLE-STATUS-SOURCE-ACQUIRED /
PARTIAL COVERAGE / EXECUTION STILL CLOSED**. No active work remains. Await explicit
user / Referee decision for any future executable-status extension, limit-lock source,
intraday halt source, lifecycle refinement, ops patch, parser, or strategy phase.
