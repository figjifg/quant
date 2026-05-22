# Paper Tracking Manual

## Purpose

Paper tracking is an operations check, not proof of alpha.

Four quarters of forward evidence means:

- The operational process is repeatable.
- NAV, drift, tax, and rebalance files can be updated without manual research intervention.
- The primary and shadows can be compared under real forward market conditions.

It does not prove the strategy has live alpha.

## Six-Portfolio Dashboard

Final paper dashboard portfolios:

| # | Portfolio | Role |
|---:|---|---|
| 1 | P08_IEF30 | Primary |
| 2 | N002-B cash 10% | Defensive shadow |
| 3 | N001-B GLD 10% | Defensive shadow |
| 4 | QQQ 100% | Benchmark |
| 5 | SPY 100% | Benchmark |
| 6 | H001 | Korean sleeve only |

Dashboard output:

`paper_trading/operations/dashboard.md`

## Quarter-End Plus One Trading Day Procedure

Run after quarter-end data is available and before recording the next quarter's paper decision:

```bash
.venv/bin/python -m src.ops.nav_update
.venv/bin/python -m src.ops.gross_tax_nav
.venv/bin/python -m src.ops.tax_ledger
.venv/bin/python -m src.ops.rebalance_report
.venv/bin/python -m src.ops.drift_alert
.venv/bin/python -m src.ops.dashboard
.venv/bin/python -m src.ops.quarterly_evaluation
```

Record:

- As-of date.
- Six-portfolio NAV table.
- P08_IEF30 drift and alerts.
- Tax ledger status.
- Rebalance actions, if any.
- Any data or broker exception.

## Evaluation Writing Guide

Each quarterly evaluation should separate:

- Operations result: did commands run and outputs reconcile?
- Portfolio result: how did the six NAVs move?
- Tax result: what realized gains/losses would have occurred?
- Execution result: what fills would have been needed?
- Decision result: continue paper tracking, pause, or escalate for review.

Avoid claims that a strategy works unless the claim is supported by generated report files and reviewed separately.

## Four-Quarter Go/No-Go Criteria

At the end of four quarters, evaluate:

- All six portfolio NAVs are reproducible from local commands.
- Dashboard and operation files exist for each quarter.
- P08_IEF30 paper drift stays operationally manageable.
- Tax ledger assumptions are confirmed against broker export format.
- HIFO lot selection is operationally feasible.
- The KRW 2.5M exemption workflow is documented.
- ISA and pension constraints are confirmed.
- Defensive shadows are understood as risk references, not automatic replacements.
- Any live pilot uses conservative sizing.
- Tax-professional review is complete before live deployment.
