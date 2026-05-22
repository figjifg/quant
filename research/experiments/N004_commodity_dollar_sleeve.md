# N004 Commodity / Dollar Sleeve

Status: BACKLOG

## Purpose

Measure DBC commodity and UUP dollar defensive sleeve behavior versus frozen
`P08_IEF30`.

## Hypothesis

- DBC may act as an inflation hedge.
- UUP may act as a strong-dollar hedge.

## Pre-registration

Variants:

- N004-A: `P08_IEF30` + DBC 5%, proportional reduction from existing sleeves.
- N004-B: `P08_IEF30` + UUP 5%, proportional reduction from existing sleeves.
- N004-C: `P08_IEF30` + DBC 5% + UUP 5%, proportional reduction from existing
  sleeves.

## Guardrails

- No new best-Sharpe search.
- No unregistered weights grid.
- Do not directly replace or modify `P08_IEF30`.
- Result enters N-family backlog candidate library only.
