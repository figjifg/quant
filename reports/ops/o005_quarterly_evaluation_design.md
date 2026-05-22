# O005 quarterly evaluation design

Status: design plus local sample runner.

## Scope

`src.ops.quarterly_evaluation.generate_quarterly_evaluation(quarter)` writes a markdown template for quarterly paper evaluation.

## Sections

- performance, quarterly and YTD
- taxes, quarterly and YTD
- rebalancing, trade list, and slippage
- tracking error, model versus actual
- actual versus paper
- major events
- next-quarter actions

## Output

Markdown under `paper_trading/operations/`.

Tax-professional confirmation is required before any live use.
