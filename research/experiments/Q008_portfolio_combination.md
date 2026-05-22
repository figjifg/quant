# Q008 — P08_IEF30 + ETF Proxy Portfolio Combination

Status: REGISTERED

## Purpose

Evaluate whether adding a factor ETF proxy sleeve to `P08_IEF30` improves
portfolio-level Sharpe and maximum drawdown.

## Primary Question

Does `P08_IEF30 + factor ETF sleeve` improve net behavior enough to justify a
new production candidate?

## Replacement Methods

### Method A — SPY Replacement (Primary)

Baseline: `SPY 29 / QQQ 21 / H001 20 / IEF 30`.

For Q weights 10% and 20%:

- `SPY = 29 - Q`.
- `Q sleeve = Q`.
- `QQQ = 21`.
- `H001 = 20`.
- `IEF = 30`.

### Method B — US Equity Pro-rata (Secondary)

Reduce `SPY:QQQ = 29:21` together.

For Q weights 10% and 20%:

- `SPY = 29 * (50 - Q) / 50`.
- `QQQ = 21 * (50 - Q) / 50`.
- `H001 = 20`.
- `IEF = 30`.

### Method C — QQQ Replacement (Optional Diagnostic)

For Q weights 10% and 15%:

- `QQQ = 21 - Q`.
- `SPY = 29`.
- `H001 = 20`.
- `IEF = 30`.

## Sleeves

ETF proxy sleeves:

- `SCHD` dividend proxy, inception 2011-10.
- `COWZ` free-cash-flow proxy, inception 2016-12.
- `MTUM` momentum proxy, inception 2013-04.

Direct diagnostic sleeves:

- `Q002` direct quality, diagnostic only.
- `Q006` direct Q+V+SY, diagnostic only.

Direct Q-family sleeves are not production candidates because of survivorship
bias.

## Candidate Registration

- Method A: 3 ETF x 2 weights + 2 direct x 2 weights = 10 candidates.
- Method B: 3 ETF x 2 weights + 2 direct x 2 weights = 10 candidates.
- Method C: 3 ETF x 2 weights + 2 direct x 2 weights = 10 candidates.
- Total = 30 candidates.
- No grid optimization. Use this pre-registered list exactly.

## Common Settings

- 2010-2026 daily NAV.
- Quarterly rebalance.
- T-family cost framework.
- HIFO lot accounting.
- Annual capital-gain exemption: KRW 2.5m.
- Capital-gains tax: 22% for US ETF/direct overseas sleeve.
- Dividend withholding: 15%.
- FX spread: 10 bps.
- Missing sleeve history before inception/start is proxied by `SPY`.
- `H001` / `IEF` are not reduced to fund the Q sleeve.

## Outputs

Write only under `reports/experiments/Q008_portfolio_combination/`:

- `config.yaml`
- `combination_metrics.csv`
- `stress_windows.csv`
- `delta_vs_p08_ief30.csv`
- `top_ranked_candidates.csv`
- `report.md` in Korean with verdict.

## Report Requirements

- `P08_IEF30` baseline net CAGR / Sharpe / MDD.
- Net differences for each combination.
- Method A vs B vs C comparison.
- ETF proxy vs direct `Q002` / `Q006`.
- Best candidate ranking, Sharpe first.
- Ranking comparison versus `N002-B` cash 10% and `N001-B` GLD 10%.
- Verdict: whether ETF sleeve improves enough, whether N-family defensive
  shadow is superior, and whether a production candidate should be added.

## Guardrails

- Do not modify `D013`, `H001`, `P08_IEF30`, or `engine.py`.
- Do not alter existing D-H, P, I, T, O, N, K, J, or Q000-Q006.6 outputs.
- Add new audit scripts and new reports only.
- No external network.
- Direct `Q002` / `Q006` are diagnostic only.
