# T003 tax-loss harvesting diagnostic

## Status

- Type: diagnostic only
- Registered: 2026-05-19
- Prior finding: T001/T002 both keep P08_IEF30 quarterly rebalance + 0pp band as the practical winner after drift/stress filters.

## Hypothesis

Tax-loss harvesting on overseas ETF lots improves after-tax net CAGR by realizing loss lots and using those losses against realized gains in other overseas ETF sleeves.

## Pre-registered tax assumptions

- Investor: Korean resident, taxable general account.
- Overseas ETFs: SPY, QQQ, IEF.
- Korean H001 sleeve: Korean equity assumption, non-large-shareholder case, no capital gains tax and no TLH.
- Overseas ETF realized gains and losses can be netted for Korean capital gains tax purposes.
- Annual capital gains exemption: KRW 2,500,000.
- Capital gains tax rate: 22%.
- Trading commission: 0.25% per trade. A TLH sell and immediate repurchase therefore costs 0.50% of harvested notional.
- Dividend withholding tax: 15%, tracked separately from capital gains tax.
- Simplifying legal assumption: no Korean wash-sale rule is modeled for identical overseas ETF immediate repurchase.
- Diagnostic only: practical use requires confirmation with a qualified tax professional before implementation. Wash-sale, similar exposure substitution, broker reporting, and account-specific constraints need separate legal/tax review.

## Pre-registered scenarios

- T003-A: No TLH. Reproduces T000-C baseline: HIFO + KRW 2.5m annual exemption + ongoing NAV.
- T003-B: Year-end TLH. Review on the final trading day of December; sell all SPY/QQQ/IEF lots with unrealized loss and immediately repurchase the same ETF.
- T003-C: Quarter-end TLH. Review on every quarter-end trading day; sell all SPY/QQQ/IEF lots with unrealized loss and immediately repurchase the same ETF.
- T003-D: Year-end threshold TLH, only lots with return <= -5%.
- T003-E: Year-end threshold TLH, only lots with return <= -10%.

## Common portfolio settings

- Portfolio: P08_IEF30 = SPY 29%, QQQ 21%, H001 20%, IEF 30%.
- Rebalance: quarterly, 0pp band.
- Lot selection for ordinary rebalance sales: HIFO.
- NAV basis: ongoing NAV; no terminal liquidation tax.
- Initial capital: KRW 100,000,000.
- Sample: 2010-01-04 through 2026-05-18.
- Price/FX inputs: existing local research inputs only; no external downloads.

## Pre-registered criteria

- TLH passes only if net CAGR improves by at least +0.1pp versus T003-A.
- Compare 250만원 annual exemption utilization efficiency between no-TLH and TLH scenarios.
- HIFO + TLH must improve net results versus HIFO alone.
- Compare tax savings against additional TLH commissions.
- Stress windows: 2020 COVID, 2022 drawdown, and 2025 spike exclusion.

## Required outputs

Write all outputs under `reports/experiments/T003_tax_loss_harvesting/`:

- `tlh_scenarios.csv`
- `realized_loss_by_year.csv`
- `tax_savings_by_year.csv`
- `tlh_events.csv`
- `daily_nav_by_tlh.csv`
- `stress_net_by_tlh.csv`
- `report.md`

