# T001 rebalance frequency vs tax

## Hypothesis

P08_IEF30의 현행 quarterly rebalance가 HIFO lot accounting, 연 250만원 양도소득 기본공제, ongoing NAV 기준 after-tax 성과에서 최적일 수 있다.

대안 가설은 annual rebalance 또는 threshold rebalance가 turnover와 세금을 줄여 gross 성과는 낮아도 after-tax 성과를 개선한다는 것이다.

## Fixed Portfolio

- Portfolio: P08_IEF30
- Weights: SPY 29%, QQQ 21%, H001 20%, IEF 30%
- Only rebalance frequency changes. Weights are fixed.

## Frequencies

- Monthly: 월말/월초 경계 리밸런싱
- Quarterly: 분기말/분기초 경계 리밸런싱, current P08_IEF30
- Semiannual: 반기 경계 리밸런싱
- Annual: 연말/연초 경계 리밸런싱
- No-rebalance: initial allocation 후 16.4년 buy-and-hold drift
- Threshold 5pp: target weight 대비 5%p 이상 이탈 시 리밸런싱
- Threshold 10pp: target weight 대비 10%p 이상 이탈 시 리밸런싱

## Tax and Cost Model

- Lot accounting: HIFO
- Annual capital-gains exemption: 2,500,000 KRW
- Ongoing NAV: terminal liquidation tax excluded
- Trading commission: 0.25% both buy and sell legs
- Dividend withholding: 15%, deducted separately
- Capital-gains tax: 22% for Korean resident taxable account
- FX spread: 0 bps
- Capital gains are measured in KRW, so USD price movement and USDKRW movement are both included in taxable base.

## Pre-Registered Criteria

- Winner: highest after-tax CAGR.
- If the winner's after-tax CAGR differs from another frequency by less than 0.5 percentage points, treat them as equivalent and keep the current quarterly rebalance.
- Evaluate after-tax Sharpe and after-tax max drawdown together with CAGR.

## Required Outputs

Write outputs under `reports/experiments/T001_rebalance_frequency_vs_tax/`:

- `frequency_metrics.csv`
- `tax_paid_by_frequency.csv`
- `turnover_by_frequency.csv`
- `tracking_drift_by_frequency.csv`
- `stress_net_by_frequency.csv`
- `daily_nav_by_frequency.csv`
- `report.md`

## Required Report Sections

- Gross vs after-tax comparison table for all seven frequencies
- Net CAGR winner
- Quarterly vs annual comparison
- Threshold rebalance net effect
- No-rebalance buy-and-hold drift net effect
- Stress retest on after-tax NAV
- Verdict: recommended rebalance frequency for P08_IEF30
- T002 no-trade band recommendation

## Guardrails

- Do not modify D013, H001 strategy, or `src/backtest/engine.py`.
- Do not modify existing D-H, P, I000-I005, or T000 outputs.
- Add only the T001 audit script and T001 outputs.
- No external network access.
- Do not change P08_IEF30 weights.
