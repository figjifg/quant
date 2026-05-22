# S001 Audit-First Validation

Status: OPEN. Audit-first kill-test for S-family formal validation.

## Decision Context

S000 is accepted only as `PASS_diagnostic`. S-family formal validation is open,
but S000 numbers are unusually strong, so S001 is an audit-first validation
rather than alpha expansion. No P08 satellite combination is authorized before
standalone validation.

Frozen constraints:

- `P08_IEF30` remains the frozen primary.
- Do not modify D013, H001, P08_IEF30, or `src/backtest/engine.py`.
- S-family must stay standalone until formal validation passes.
- `r1d_lt_m3` is the main candidate.
- `r3d_lt_m7` is a crisis sub-signal only.
- `volume_z` is rejected.

## Hypothesis

S000's strong short-horizon Korean mean-reversion result may be a measurement
artifact rather than a robust tradable standalone effect.

## Sub-Tickets

| Ticket | Name | Purpose | Output |
|---|---|---|---|
| S001-0 | Metric / Implementation Audit | Verify units, timing, costs, random control, duplicate events, and overlap/leverage. | `reports/experiments/S001_0_metric_audit/` |
| S001-A | Distribution / Attribution Audit | Test concentration in top trades, dates, crisis windows, and bootstrap confidence. | `reports/experiments/S001_a_distribution_audit/` |
| S001-B | Real Sleeve Daily NAV Simulation | Recalculate standalone sleeve NAV with no leverage, cash, MTM, caps, and entry limits. | `reports/experiments/S001_b_real_sleeve_simulation/` |
| S001-C | Execution / Capacity Stress | Stress slippage, fill, delay, participation, spread widening, and capital scale. | `reports/experiments/S001_c_execution_capacity/` |
| S001-D | Robustness / Placebo | Test date/drop/stock matched randoms, time shifts, opposite signal, threshold grid, and holding grid. | `reports/experiments/S001_d_robustness_placebo/` |
| S001-E | Tax Model | Compare conservative, ordinary domestic listed, and large-shareholder tax assumptions. | `reports/experiments/S001_e_tax_model/` |
| S001-F | Mechanism Analysis | Attribute candidate behavior by D013 state, market direction, flow, size, sector if possible, gaps, and volatility regime. | `reports/experiments/S001_f_mechanism/` |

## Pass Criteria

S001 can pass only if all of the following hold:

1. S001-0 has no FAIL item that requires S000 recalculation.
2. Return units are confirmed as decimal per-trade returns, not percent or
   annualized returns.
3. Signal date, execution date, and exit date follow KRX trading-day timing with
   no same-day execution.
4. Dynamic-universe membership is point-in-time safe for T+1 execution.
5. Price columns are split/right-adjusted or otherwise proven internally
   consistent for open-to-close trade measurement.
6. Duplicate and consecutive signal handling is explicit and reproducible.
7. Real sleeve NAV remains net positive without leverage.
8. `r1d_lt_m3` remains net positive after top trade/date and crisis exclusions.
9. Random and placebo controls are materially worse than the candidate.
10. Tax and execution stress remain net positive for realistic small-capacity
    deployment assumptions.

## Fail Criteria

S001 fails if any of the following hold:

1. S001-0 finds timing, return-unit, or implementation leakage requiring S000
   recalculation.
2. S000 trade results depend on filtered-row jumps rather than next KRX trading
   day execution.
3. Results are explained by a few top trades, dates, or the 2020 crisis window.
4. Real sleeve NAV is flat or negative after costs and cash drag.
5. Date/drop/stock/time-shift placebo controls match or exceed the candidate.
6. The effect exists only at one tuned threshold/holding point.
7. Capacity is too low even for tactical small-sleeve deployment.
8. Tax/execution assumptions erase the result under ordinary domestic
   implementation.

Fail verdict: S-family returns to backlog or terminates as diagnostic-only.
Pass verdict: S002 experimental execution log may begin. Paper-candidate
promotion requires S001-B/C/D/E PASS, not S001 registration alone.
