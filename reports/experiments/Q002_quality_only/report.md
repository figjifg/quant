# Q002 Quality Only

## Verdict

STRONG. Q002는 사전 등록한 단일 Quality composite만 사용했다. 현재 survivor universe 한계가 있으므로 production promote 판단에는 쓰지 않는다.

## Hypothesis

ROIC가 높고 FCF margin이 높으며 leverage가 낮은 대형주는 다음 분기 보유 구간에서 SPY 100%보다 더 나은 위험조정 성과를 낼 수 있다.

## 사전 등록 구현

- Universe: Q001 99종목(S&P 100 유사 현재 universe, MMC 제외).
- Composite: `Quality_Score = z(ROIC) + z(FCF_margin) - z(Leverage)`.
- ROIC: `trailing_4Q_operating_income / (latest_equity + latest_long_term_debt)`.
- FCF margin: `(trailing_4Q_CFO - trailing_4Q_CapEx) / trailing_4Q_revenue`.
- Leverage: `latest_long_term_debt / latest_equity`.
- Portfolio: 매 분기 Top 30 equal weight, 비용 0 gross only.
- Benchmark: SPY 100% buy-hold, USD NAV.
- PIT: SEC `filed` 날짜와 분기말 +35일 lag를 통과한 값만 사용했다. 실행일은 `available_date` 이후 첫 SPY 거래일이며, 해당일 가격이 없는 종목은 제외했다.
- Factor grid: 없음. Q002는 단일 composite만 테스트했다.

## 핵심 성과

| Strategy | Total return | CAGR | Sharpe | MDD | SPY excess CAGR | IR vs SPY |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Q002 Top30 | 1125.34% | 19.56% | 1.08 | -27.77% | 4.80% | 0.84 |
| SPY 100% | 589.70% | 14.76% | 0.91 | -33.72% | 0.00% |  |

Top 30 ranking은 각 분기 단면에서 높은 ROIC, 높은 FCF margin, 낮은 leverage가 동시에 강한 종목을 고른다는 의미다. 순위 자체는 예측 점수이며, SPY 대비 alpha는 다음 분기 실제 보유 수익으로만 검증했다.

## Quartile Spread

- Q1-Q4 long-short 평균 분기 수익률: -0.94%
- Q1-Q4 양수 비율: 43.9%
- Long-short가 양수이면 Quality score가 단순 long-only 구성 효과를 넘어 진짜 factor premium을 가진다는 보조 증거로 본다. 이번 결과는 SPY 대비 long-only alpha는 강하지만 Q1-Q4 spread가 음수라서 순수 factor premium 증거는 약하다.

## Turnover / Concentration

- 평균 분기 turnover: 14.85%
- 평균 최대 sector weight: 12.87%
- 최대 sector weight: 20.00% (Pharmaceutical Preparations)
- 보유 구간 수: 57
- signal row 수: 4131

## Subperiod

| Period | CAGR | Sharpe | MDD | Excess CAGR vs SPY |
| --- | ---: | ---: | ---: | ---: |
| 2010_2015 | 19.26% | 1.40 | -11.86% | 5.38% |
| 2016_2020 | 24.08% | 1.15 | -27.45% | 8.63% |
| 2021_2026 | 16.31% | 0.91 | -27.77% | 0.94% |

## Pass Criteria

- SPY 대비 CAGR 우수 + Sharpe 우수 = STRONG
- SPY 대비 CAGR 비슷 + Sharpe 우수(MDD 작음) = OK
- SPY 대비 CAGR 낮음 + Sharpe 비슷 = WEAK
- SPY 대비 CAGR + Sharpe 모두 낮음 = FAIL
- Long-short(Q1-Q4) 양수 = factor의 진짜 premium 보조 확인

## 한계

- 현재 universe는 살아남은 99종목이므로 survivorship bias가 있다.
- 비용은 Q002 사전 등록대로 0 gross only이며, 비용/세금 검증은 T-family 또는 Q007에서 별도로 해야 한다.
- `P08_IEF30` 직접 promote는 Q008 전까지 하지 않는다.

## 다음 단계

Q003 Value only 진행을 권고한다.
