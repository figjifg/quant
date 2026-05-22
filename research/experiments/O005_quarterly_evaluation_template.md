# O005 quarterly evaluation template

## Purpose

Generate a reusable quarterly evaluation markdown template.

## Output

Write `paper_trading/operations/evaluations_template_<quarter>.md` with sections for:

- performance, quarterly and YTD
- taxes, quarterly and YTD
- rebalancing, including trade list and slippage
- tracking error, model versus actual
- actual versus paper
- major events
- next-quarter actions

## Implementation

Primary function: `src.ops.quarterly_evaluation.generate_quarterly_evaluation(quarter)`.

## Tax note

The template must preserve the statement that tax-professional confirmation is required before live implementation.
