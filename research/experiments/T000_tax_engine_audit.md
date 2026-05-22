# T000 tax engine audit

## Hypothesis

I005의 양도세 30.5pp 차감 모델이 한국 거주자 해외 ETF 세법을 정확히 반영하는가.

## Scope

- Candidate: P08_IEF30 = SPY 29% / QQQ 21% / H001 20% / IEF 30%
- Rebalance: quarterly
- Base comparison: I003.5 gross and I005 production cost validation
- Account assumption: 한국 거주자, 일반 계좌, 대주주 아님, H001 한국 주식 양도세 비과세 가정
- This is audit only. 새 alpha family X, P08_IEF30 production validation extension.

## Audit items

1. 해외 ETF 양도세 22% (소득세 20% + 지방세 2%) 정확 적용.
2. 연 2,500,000 KRW 기본공제: (a) 적용, (b) 미적용, (c) 시나리오별 비교.
3. 손익통산: SPY + QQQ + IEF realized gain/loss 통산.
4. 양도세 timing: 매도 시점 즉시 차감 vs 다음 해 5월 납부.
5. Terminal liquidation tax: 16년 후 청산 시 미실현 이익 과세.
6. Realized gain vs unrealized gain 분리 추적.
7. FX taxable gain: 원화 환산 차익 기준 계산.
8. 배당 원천징수 15%와 양도세 base 중복 처리 여부.
9. Lot accounting: FIFO vs HIFO vs I005 average-cost reproduction.
10. H001: 한국 strategy sleeve는 대주주 X 가정 시 한국 주식 양도세 비과세 적용.

## Pre-registered scenarios

- T000-A: I005 reproduction, 2,500,000 KRW 공제 미적용, I005 average-cost model, immediate tax, ongoing NAV.
- T000-B: FIFO + 2,500,000 KRW 공제, immediate tax, ongoing NAV.
- T000-C: HIFO + 2,500,000 KRW 공제, immediate tax, ongoing NAV.
- T000-D: FIFO + 2,500,000 KRW 공제, terminal liquidation tax included.
- T000-E: FIFO + 2,500,000 KRW 공제, annual tax timing, next-year May payment.

## Pre-registered audit criteria

- 2,500,000 KRW 공제 적용 시 NAV가 개선되어야 한다.
- Terminal liquidation 포함 시 ongoing NAV보다 낮아져야 한다.
- HIFO vs FIFO 차이를 측정한다. HIFO는 FIFO보다 세금 절감 방향이어야 한다.
- T000-A는 I005 Scenario A와 cross-check하고 차이를 보고한다.

## Comparison anchors

- Gross (I003.5): Sharpe 1.172 / CAGR 12.7% / MDD -16.4%
- I005 Scenario A: Sharpe 1.113 / CAGR 12.0%
- T000-A: I005 reproduction sanity check
- T000-B: 2,500,000 KRW 공제 효과
- T000-C: HIFO lot selection 효과
- T000-D: terminal liquidation tax 효과
- T000-E: annual tax timing 효과

## Required outputs

Write all outputs under `reports/experiments/T000_tax_engine_audit/`:

- `tax_scenarios.csv`
- `lot_ledger.csv`
- `realized_gain_by_year.csv`
- `unrealized_gain_by_year.csv`
- `tax_paid_by_year.csv`
- `i005_cross_check.csv`
- `report.md`

## Report sections

- I005 세금 모델 audit 결과: 정확 / 부정확 / 누락 항목.
- 2,500,000 KRW 공제 효과: A vs B 차이.
- Lot accounting 효과: FIFO vs HIFO.
- Terminal liquidation 효과: ongoing vs liquidation.
- Tax timing 효과: immediate vs annual.
- Verdict: I005 모델 정확 / 수정 필요 / 보완 필요.
- T001 rebalance frequency vs tax 진행 권고.

## Constraints

- Do not modify D013, H001 strategy, or `engine.py`.
- Do not modify existing D-H, P, or I000-I005 results.
- Add only the new audit script and report outputs.
- Do not use external network.
- Audit only: no new backtest engine change, no strategy change.
- If blocked, write `research/experiments/T000_codex_questions.md`.
