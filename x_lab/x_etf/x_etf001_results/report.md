# X-ETF001 Time-Series Momentum Scan Report

X-Lab 격리 산출물이다. D013, H001, P08_IEF30, engine.py, P08 paper tracking은 수정하지 않았다.

## Verdict

사전 등록 40개 variant를 그대로 실행했다. Verdict 분포: `{"CLOSE": 40}`.

## Benchmark

- Evaluation start: `2011-01-03`
- P08 proxy Sharpe: `1.035643`
- P08_IEF30 full Sharpe: `1.125290`
- Equal-weight 13 ETF after-cost Sharpe: `0.854798`

## Best Variants

- Best after-cost Sharpe: `XETF001_V40` `0.699814` CAGR `0.081531` MDD `-0.182777`
- Best after-tax Sharpe: `XETF001_V40` `0.631154` CAGR `0.072943` MDD `-0.185188`

## Caveats

- Local Yahoo Finance `Close` is treated as adjusted total-return input following X-ETF000 convention.
- Dividend withholding is documented as a taxable-account caveat; cash dividend streams are not separately available in local inputs.
- After-tax NAV uses HIFO realized-gain accounting, 22% tax, and annual KRW 2.5M exemption on a KRW 100M normalized account.
- Random TopK control uses deterministic local RNG seed and 1,000 trials per variant.

## Output Files

- `config.yaml`
- `variant_metrics.csv`
- `top_rankings.csv`
- `subperiod_breakdown.csv`
- `stress_windows.csv`
- `random_control.csv`
- `qqq_exposure_test.csv`
- `equal_weight_comparison.csv`
- `pass_gate_evaluation.csv`
- `secondary_mchi_robustness.csv`
