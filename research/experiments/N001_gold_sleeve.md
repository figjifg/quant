# N001 Gold Sleeve

Status: BACKLOG

## Purpose

Measure whether a GLD sleeve improves `P08_IEF30` stress response in GFC and
2022-style stress windows.

## Hypothesis

GLD may act as a hedge during GFC-like stress. Historical reference: GLD was
positive in 2008, approximately +12.5%.

## Pre-registration

Variants:

- N001-A: `P08_IEF30` + GLD 5%, proportional reduction from existing sleeves.
- N001-B: `P08_IEF30` + GLD 10%, proportional reduction from existing sleeves.

## Comparison

Compare against frozen `P08_IEF30`:

- Gross Sharpe.
- Max drawdown.
- GFC proxy.
- 2022 rate shock.
- COVID.
- Dot-com proxy.

## Guardrails

- Run only after N000.
- No new best-Sharpe search.
- No unregistered weights grid.
- Do not directly replace or modify `P08_IEF30`.
- Result enters N-family backlog candidate library only.
