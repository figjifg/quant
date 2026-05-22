# X-ETF900 Final Defensive ETF Challenge Report

X-Lab 격리 산출물이다. D013, H001, P08_IEF30 strategy, engine.py, P08 paper tracking은 수정하지 않았다.

## Verdict

- Final verdict: `ALL_VARIANTS_CLOSE_BUT_TRACK_FAIL_GATE_NOT_FULLY_TRIGGERED`
- Verdict distribution: `{"CLOSE": 24}`
- Non-close survivor count: `0`
- All close criteria met by every variant: `False`

## Benchmarks

- Evaluation start: `2011-01-03`
- P08 proxy Sharpe: `1.035643` MDD `-0.154235`
- P08_IEF30 full Sharpe: `1.125290` MDD `-0.234285`
- EW13 after-cost Sharpe: `0.854798`
- N001-B Sharpe: `1.184426`
- N002-B Sharpe: `1.165980`

## Best Variants

- Best after-cost: `XETF900_V10` module `B` Sharpe `1.149424` CAGR `0.139732` MDD `-0.145913` QQQ exposure `0.210000`
- Best after-tax: `XETF900_V10` module `B` Sharpe `1.065802` CAGR `0.129560` MDD `-0.185517`

## P08 Combination Diagnostic

- 90% P08_IEF30 + 10% `XETF900_V10` CAGR `0.155587` MDD `-0.222158` Sharpe `1.157841`
- MDD improvement vs P08_IEF30: `0.012126`
- CAGR drag vs P08_IEF30: `0.001415`
- Deep combo gate candidate: `False`

## Output Files

- `config.yaml`
- `variant_metrics.csv`
- `module_a_dual_momentum.csv`
- `module_b_defensive_rotation.csv`
- `module_c_risk_budget.csv`
- `subperiod_breakdown.csv`
- `stress_windows.csv`
- `random_control.csv`
- `turnover_tax_drag.csv`
- `pass_gate_evaluation.csv`
- `p08_combination_test.csv`
