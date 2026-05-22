# I005 production cost validation

## Hypothesis

P08_IEF30가 실제 비용(수수료 + 양도소득세 + 환전 spread + 배당 원천징수)을 반영한 뒤에도 multi-metric framework를 통과하는가.

## Registered portfolio

- Candidate: P08_IEF30
- Weights: SPY 29% / QQQ 21% / H001 20% / IEF 30%
- Rebalance: quarterly only
- Gross reference: I003.5 B04_SPY29_QQQ21_H00120_IEF30
- Gross reference metrics: Sharpe 1.172, CAGR 12.7%, MDD -16.4%

## Cost assumptions

- 매매 수수료: 0.25%, 매수 + 매도 양방향, 사용자 명시.
- 양도소득세: 22%, 매도 시 US ETF net realized gain에 적용. H001에는 적용하지 않는다.
- 양도소득세 공제 단순화: 초기자본 100,000,000 KRW 기준 연 2,500,000 KRW 공제, 즉 normalized NAV 0.025까지 annual realized gain 비과세.
- 보수 시나리오: 위 2,500,000 KRW 공제를 무시하고 realized gain 전액에 22%를 적용한다.
- 환전 spread: USD <-> KRW 편도 spread 0 / 10 / 20 bps sensitivity. US ETF 매수/매도 금액에만 적용한다.
- 배당 원천징수: US ETF withholding 15%. SPY annual yield 1.3%, QQQ 0.5%, IEF 3.5%를 사용하고 quarterly dividend = annual yield / 4 * current weight로 단순화한다.
- H001은 한국 strategy sleeve지만 production-style validation 단순화를 위해 수수료는 동일하게 0.25%를 적용하고, 양도세/환전/US 배당 원천징수는 적용하지 않는다.

## Pre-registered scenarios

- Scenario A (사용자 명시): 0.25% 수수료 + 양도세 22%, 환전 0 bps, 배당 무시, 2,500,000 KRW 공제 미적용.
- Scenario B (full cost): 0.25% 수수료 + 양도세 22% + 환전 10 bps + 배당 원천징수 15%, 2,500,000 KRW 공제 미적용.
- Scenario C (worst): 0.25% 수수료 + 양도세 22% + 환전 20 bps + 배당 원천징수 15%, 2,500,000 KRW 공제 무시.
- Scenario D (best): 0.25% 수수료 + 양도세 22% + 환전 0 bps + 배당 무시, 2,500,000 KRW 공제 적용.

## Pre-registered pass criteria

- Net Sharpe >= 1.00 (gross 1.172의 85% 보존)
- Net CAGR >= 10% (gross 12.7%의 80% 보존)
- Net MDD 악화 <= +3pp
- 모든 stress(2020 COVID, 2022)가 여전히 P07/P08보다 우수

## Pre-registered kill criteria

- Net Sharpe < 0.90
- Net CAGR < 8%
- 양도세가 누적 수익을 50% 이상 잠식

## Required outputs

Write all outputs under `reports/experiments/I005_production_cost_validation/`:

- `cost_scenarios.csv`: gross and Scenario A/B/C/D net metrics.
- `quarterly_turnover.csv`: each quarterly rebalance turnover and costs.
- `cost_attribution.csv`: commission / capital gains tax / FX spread / dividend withholding by quarter and scenario.
- `daily_nav_gross_vs_net.csv`: gross NAV and four net NAV series.
- `stress_net.csv`: net stress diagnostics for COVID, 2022, 2025 spike exclusion, and 2010-17 vs 2018-26.
- `report.md`: Korean report with verdict.

## Constraints

- Do not modify D013, H001 strategy, or `engine.py`.
- Do not change existing D-H, P, or I000-I004 results.
- Add only a new audit script for computation.
- Do not use external network.
- Do not test alternate rebalance frequencies.
- All cost assumptions must be explicit; no TBD items.
