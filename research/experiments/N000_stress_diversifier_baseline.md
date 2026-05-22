# N000 Stress Diversifier Baseline

Status: READY

## Purpose

Measure the stress response of the frozen `P08_IEF30` baseline across major
stress windows:

- GFC proxy: 2008-2009.
- 2022 rate shock: full year.
- COVID: 2020-02 to 2020-03.
- Dot-com proxy: 2002-07 to 2003-12, using the period when IEF + SPY + QQQ
  are available.

## Pre-registration

Use existing `P08_IEF30` exactly as frozen:

- SPY 29%.
- QQQ 21%.
- H001 20%.
- IEF 30%.

No modification is allowed in N000.

H001 is unavailable before 2010. Therefore:

- 2010 onward stress windows use exact `P08_IEF30` with H001.
- Pre-2010 stress windows are US-core proxy only and must be labeled as proxy.

## Comparison Target

Report stress-window metrics only:

- Total return.
- Gross Sharpe.
- Daily max drawdown.
- Peak date.
- Trough date.
- Recovery date.

## Guardrails

- No new best-Sharpe search.
- No weights grid.
- No sleeve addition.
- No direct replacement or promotion of `P08_IEF30`.
- N-family output is backlog candidate library only.

## Expected Output

Write results to:

`reports/experiments/N000_stress_diversifier_baseline/`
