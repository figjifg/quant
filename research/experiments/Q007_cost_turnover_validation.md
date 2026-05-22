# Q007 — Cost / Turnover Validation

Status: REGISTERED

## Purpose

Validate the cost sanity of the Q008 combination framework before any
portfolio-level Q-family promotion decision.

## Decision Input

GPT decision:

- `Q007 = cost/turnover sanity check (production X)`.
- Direct `Q002` / `Q006` sleeves are comparison diagnostics only.
- ETF proxy path uses the T-family cost framework.
- `H001` / `IEF` are not funding sleeves for Q; Q replaces only the registered
  US equity sleeve in Q008.

## Scope

Diagnostic only. This is not a direct-Q production validation and does not
promote any direct Q-family stock sleeve.

### A. Direct Q002/Q006 Cost Validation

Assumption set: Korean resident V1 / T-family Scenario B.

- HIFO lot accounting.
- Annual capital-gain exemption: KRW 2.5m.
- Capital-gains tax: 22%.
- Dividend withholding: 15%.
- FX spread: 10 bps.
- Trading commission: 0.25% each side.
- Report gross CAGR, net CAGR, and cumulative tax / commission / FX impact.

### B. ETF Proxy Cost

Sleeves: `SCHD`, `COWZ`, `MTUM`.

- Buy-and-hold standalone proxy turnover is assumed near zero.
- In Q008 combinations the sleeve trades only through quarterly `P08_IEF30`
  rebalancing.
- Same T-family Scenario B / overseas direct-investment V1 assumptions.

### C. Comparison

Compare:

- Direct `Q002`.
- Direct `Q006`.
- `SCHD`.
- `COWZ`.
- `MTUM`.

Required table:

- Gross.
- Net under T-family.
- Cost impact ranking.

## Outputs

Write only under `reports/experiments/Q007_cost_turnover_validation/`:

- `direct_q_cost.csv`
- `etf_proxy_cost.csv`
- `comparison.csv`
- `report.md` in Korean with verdict.

## Guardrails

- Production X.
- Direct `Q002` / `Q006` remain research diagnostics because of survivorship
  bias.
- No external network.
- Do not modify `D013`, `H001`, `P08_IEF30`, or `engine.py`.
