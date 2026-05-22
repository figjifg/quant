# N002 Cash / SHY Sleeve

Status: BACKLOG

## Purpose

Measure whether cash or SHY 1-3y short Treasury exposure improves stress
response relative to the frozen `P08_IEF30` baseline.

## Hypothesis

SHY may have lower duration risk than IEF and may therefore provide better
2022 rate-shock defense.

## Pre-registration

Variants:

- N002-A: replace `P08_IEF30` IEF 30% with SHY 30%.
- N002-B: add cash 10%, proportional reduction from existing sleeves.
- N002-C: split duration sleeve as IEF 15% + SHY 15%.

## Guardrails

- No new best-Sharpe search.
- No unregistered weights grid.
- Do not directly replace or modify `P08_IEF30`.
- Result enters N-family backlog candidate library only.
