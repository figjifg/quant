# Production Candidate Manual

## Candidate

Production candidate:

`P08_IEF30 = SPY 29 / QQQ 21 / H001 20 / IEF 30`

Status: frozen primary. This manual is for paper and deployment preparation only; it does not authorize live trading by itself.

## Quarterly Rebalance Procedure

Frequency: quarterly.

User operating time: target 30 minutes per quarter after data is available.

Procedure:

1. Run NAV update and dashboard commands.
2. Review drift and alerts.
3. Generate the rebalance report.
4. Apply HIFO lot accounting for any sells.
5. Use the KRW 2.5M annual overseas ETF capital-gains exemption before taxable realization where applicable.
6. Record the paper decision and actual fill assumptions.

Sample commands:

```bash
.venv/bin/python -m src.ops.nav_update
.venv/bin/python -m src.ops.gross_tax_nav
.venv/bin/python -m src.ops.tax_ledger
.venv/bin/python -m src.ops.rebalance_report
.venv/bin/python -m src.ops.drift_alert
.venv/bin/python -m src.ops.dashboard
.venv/bin/python -m src.ops.quarterly_evaluation
```

## HIFO Lot Accounting

Default taxable-lot rule: HIFO.

For SPY, QQQ, IEF, and GLD sells in taxable V1-style accounts:

- Sort lots by KRW tax basis from highest to lowest.
- Sell highest-basis lots first.
- Track realized gains in KRW, including FX tax basis treatment used by the broker.
- Confirm broker lot-selection support before live use.

## KRW 2.5M Exemption

Default assumption:

- Overseas ETF direct holdings use KRW 2.5M annual capital-gains exemption.
- Remaining taxable overseas ETF gains are modeled at 22%.
- The exemption is not an alpha source; it is an implementation assumption for after-tax NAV tracking.

## MIX1 Vehicle Composition

MIX1 practical vehicle shadow:

| Vehicle | Weight | Role |
|---|---:|---|
| V1 taxable overseas ETF direct | 50% | Flexible taxable implementation with HIFO and KRW 2.5M exemption |
| ISA brokerage account | 30% | Tax-advantaged sleeve under ISA rules |
| Pension account | 20% | Long-horizon tax-advantaged sleeve |

Pension assumption:

- Pension capital is locked until eligible retirement withdrawal age.
- Do not size the pension sleeve with capital needed before lock-up ends.

## Operations Command List

| Module | Purpose |
|---|---|
| `src.ops.nav_update` | Computes paper NAV for tracked global allocation portfolios. |
| `src.ops.gross_tax_nav` | Computes gross, taxable, MIX1, pension, and defensive shadow NAV views. |
| `src.ops.tax_ledger` | Produces paper tax ledger artifacts. |
| `src.ops.rebalance_report` | Produces quarterly rebalance report. |
| `src.ops.drift_alert` | Produces drift and stress alert file. |
| `src.ops.dashboard` | Produces six-portfolio dashboard. |
| `src.ops.quarterly_evaluation` | Produces quarterly evaluation template. |

Live implementation requires tax-professional and broker-operation confirmation before orders.
