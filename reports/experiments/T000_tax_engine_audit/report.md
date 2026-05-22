# T000 tax engine audit

## I005 세금 모델 audit 결과

- 판정: 보완 필요.
- I005 Scenario A는 22% 해외 ETF 양도세를 적용하고, H001에는 양도세를 적용하지 않는다.
- T000-A sanity check CAGR diff 0.000000000000, Sharpe diff 0.000000000000.
- I005 누락/단순화 항목: FIFO/HIFO lot accounting 명시 없음, 연간 손익통산 사후 정산 없음, terminal liquidation tax 없음, Scenario A 배당 원천징수 제외.
- FX taxable gain은 원화 매수가/매도가 기준으로 계산되어 USD 가격 변동과 USDKRW 환차익이 과세 base에 함께 포함된다.

## Scenario 비교

| scenario | cagr | sharpe | max_drawdown | cagr_delta_vs_gross | sharpe_delta_vs_gross | mdd_delta_vs_gross_pp |
| --- | --- | --- | --- | --- | --- | --- |
| Gross_I003_5 | 0.127384 | 1.172143 | -0.164077 | 0.000000 | 0.000000 | 0.000000 |
| I005_Scenario_A | 0.120137 | 1.112978 | -0.164553 | -0.007247 | -0.059165 | -0.047582 |
| T000-A | 0.120137 | 1.112978 | -0.164553 | -0.007247 | -0.059165 | -0.047582 |
| T000-B | 0.121540 | 1.122555 | -0.164844 | -0.005844 | -0.049587 | -0.076661 |
| T000-C | 0.124626 | 1.149528 | -0.164730 | -0.002758 | -0.022614 | -0.065223 |
| T000-D | 0.115197 | 1.049510 | -0.164844 | -0.012187 | -0.122632 | -0.076661 |
| T000-E | 0.122334 | 1.129818 | -0.164573 | -0.005050 | -0.042324 | -0.049573 |

## 250만원 공제 효과

- T000-A CAGR 0.120137 vs T000-B CAGR 0.121540; delta 0.001402.
- T000-A final NAV 6.403479 vs T000-B final NAV 6.535958.

## Lot accounting 효과

- FIFO T000-B CAGR 0.121540, HIFO T000-C CAGR 0.124626, delta 0.003086.
- HIFO capital gains tax delta vs FIFO: -13,664,481 KRW.

## Terminal liquidation 효과

- Ongoing FIFO T000-B final NAV 6.535958.
- Liquidation T000-D final NAV 5.956560; delta -0.579398.

## Tax timing 효과

- Immediate T000-B CAGR 0.121540, annual May T000-E CAGR 0.122334, delta 0.000794.

## 세금/손익 추적

| scenario | capital_gains_tax_krw | dividend_withholding_krw | total_tax_paid_krw |
| --- | --- | --- | --- |
| T000-B | 30683128.511040 | 9348708.662748 | 40031837.173788 |
| T000-C | 17018647.921280 | 9546330.859675 | 26564978.780955 |
| T000-D | 88478066.234633 | 9348708.662748 | 97826774.897382 |
| T000-E | 30794953.541661 | 9446030.081158 | 40240983.622819 |

## Audit 발견 사항

- I005의 250만원 공제: Scenario A는 미적용, Scenario D_best는 적용.
- 손익통산: T000은 SPY/QQQ/IEF 연도별 net realized gain을 별도 산출한다.
- Terminal tax: I005에는 없음. T000-D에서 별도 측정.
- Lot accounting: I005는 average-cost 단순 모델이며 FIFO/HIFO 선택이 명시되어 있지 않다.
- 배당: T000은 배당 원천징수를 별도 세목으로 추적하고 양도세 base에는 포함하지 않는다. A/B/C/D/E NAV 비교는 250만원 공제, lot accounting, terminal tax, tax timing 효과를 isolate하기 위해 배당세를 NAV에서 차감하지 않았다.

## Verdict

- Verdict: I005 모델 보완 필요.
- I005의 30.5pp 양도세 차감은 Scenario A 정의 안에서는 재현되지만, 한국 거주자 일반계좌 세무 모델로는 lot accounting, 연간 손익통산, terminal liquidation, 납부시점 구분이 보완되어야 한다.
- T001 진행 권고: rebalance frequency vs tax.

## Files

- tax_scenarios.csv
- lot_ledger.csv
- realized_gain_by_year.csv
- unrealized_gain_by_year.csv
- tax_paid_by_year.csv
- i005_cross_check.csv
