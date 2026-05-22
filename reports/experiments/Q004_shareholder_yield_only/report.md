# Q004 Shareholder Yield Only

## Verdict

STRONG. 이 실험은 사전 등록한 단일 score만 사용했다. 현재 survivor universe 한계가 있으므로 production promote 판단에는 쓰지 않는다.

## Hypothesis

Buyback yield와 dividend yield가 높고 dilution이 낮은 대형주는 다음 분기 보유 구간에서 SPY 100%보다 더 나은 성과를 낼 수 있다.

## 사전 등록 구현

- Universe: Q001 99종목(S&P 100 유사 현재 universe, MMC 제외).
- Composite: `SY_Score = z(Buyback_yield) + z(Dividend_yield) - z(Dilution)`.
- Market cap estimate: SEC `filed` 기준으로 사용 가능한 latest shares x rebalance/execution date 종가.
- Portfolio: 매 분기 Top 30 equal weight, 비용 0 gross only, USD NAV.
- Benchmark: SPY 100% buy-hold.
- PIT: SEC `filed` 날짜와 분기말 +35일 lag를 통과한 값만 사용했다. 실행일은 `available_date` 이후 첫 SPY 거래일이다.
- Factor grid: 없음. 사전 등록 factor 정의만 테스트했다.
- Dividend missing zero-fill: 26개 종목이 최소 한 signal row에서 cash dividend concept 결측으로 0 처리됐다.

## 핵심 성과

| Strategy | Total return | CAGR | Sharpe | MDD | SPY excess CAGR | IR vs SPY |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Q004_shareholder_yield_top30 | 898.08% | 17.82% | 1.11 | -30.80% | 3.06% | 0.38 |
| SPY 100% | 589.70% | 14.76% | 0.91 | -33.72% | 0.00% |  |

## Quartile Spread

- Q1-Q4 long-short 평균 분기 수익률: -1.38%
- Q1-Q4 양수 비율: 38.6%

## Turnover / Concentration

- 평균 분기 turnover: 12.63%
- 평균 최대 sector weight: 11.75%
- 최대 sector weight: 16.67% (Pharmaceutical Preparations)
- 보유 구간 수: 57
- signal row 수: 4064

## Subperiod

| Period | CAGR | Sharpe | MDD | Excess CAGR vs SPY |
| --- | ---: | ---: | ---: | ---: |
| 2010_2015 | 14.24% | 1.13 | -14.88% | 0.36% |
| 2016_2020 | 21.02% | 1.09 | -30.80% | 5.56% |
| 2021_2026 | 17.85% | 1.19 | -17.67% | 2.47% |

## 한계

- 현재 universe는 살아남은 99종목이므로 survivorship bias가 있다.
- 비용은 0 gross only이며, 비용/세금 검증은 Q007에서 별도로 해야 한다.
- `P08_IEF30` 직접 promote가 아니라 Q-family 별도 sleeve 검증이다.
