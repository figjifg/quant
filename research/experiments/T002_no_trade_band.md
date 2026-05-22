# T002 no-trade band / drift tolerance

## Hypothesis

P08_IEF30에서 quarterly schedule에 no-trade band를 결합하면, 매 분기마다 목표 비중을 정확히 맞추는 quarterly 단독보다 turnover와 과세를 줄여 net 성과가 개선될 수 있다.

검증 질문은 다음과 같다: 비중 drift를 허용하면 세후 성과가 좋아지는가?

## Fixed Portfolio

- Portfolio: P08_IEF30
- Target weights: SPY 29%, QQQ 21%, H001 20%, IEF 30%
- Target weights are fixed. Only the rebalance check schedule and band change.

## Tax and Cost Model

- Lot accounting: HIFO
- Annual capital-gains exemption: 2,500,000 KRW
- Ongoing NAV: terminal liquidation tax excluded
- Trading commission: 0.25% both buy and sell legs
- Dividend withholding: 15%
- Capital-gains tax: 22%
- FX spread: 0 bps
- Capital gains are measured in KRW.

## Pre-Registered Grid

Band grid:

- 0pp: scheduled rebalance baseline
- 2.5pp
- 5pp
- 7.5pp
- 10pp
- 12.5pp
- 15pp
- 20pp

Schedules:

- Quarterly check: quarter boundary check, rebalance only if band is breached
- Monthly check: month boundary check, rebalance only if band is breached
- Annual check: year boundary check, rebalance only if band is breached

Quarterly check + 0pp band is the T001 quarterly baseline.

## Band Rebalance Logic

At each scheduled check date:

1. Compute each component's current weight.
2. Compute current weight minus target weight for SPY, QQQ, H001, and IEF.
3. If `max(abs(component_drift)) > band`, rebalance the entire portfolio to target weights.
4. Otherwise, do not trade.

At inception, allocate to target weights regardless of band.

## Pre-Registered Criteria

- Winner: highest net CAGR.
- Drift disqualifier: average tracking drift or max component drift above 20pp means portfolio identity is lost.
- Stress criterion: the selected band must not materially hurt 2020 COVID daily MDD or 2022 KRW return versus quarterly 0pp baseline.

## Required Outputs

Write outputs under `reports/experiments/T002_no_trade_band/`:

- `band_grid_metrics.csv`
- `drift_paths.csv`
- `rebalance_events.csv`
- `stress_net_by_band.csv`
- `daily_nav_by_band.csv`
- `report.md`

## Required Report Sections

- Band grid × schedule 24 portfolio net comparison
- Net CAGR rank 1 combination
- Quarterly + 10pp band from T001 versus T002 grid winner
- Drift stress impact in 2020 and 2022
- Catastrophic drift threshold where portfolio identity is lost
- Recommended band / schedule combination
- Verdict and recommendation for T003 tax-loss harvesting or T004 account study

## Guardrails

- Do not modify D013 or H001 strategy code.
- Do not modify `src/backtest/engine.py`.
- Do not modify existing D-H, P, I000-I005, T000, or T001 outputs.
- Add only the T002 audit script and T002 outputs.
- No external network access.
- Do not change P08_IEF30 weights.
