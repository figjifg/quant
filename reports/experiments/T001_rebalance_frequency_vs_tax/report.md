# T001 rebalance frequency vs tax

## 설정

- 대상: P08_IEF30 = SPY 29%, QQQ 21%, H001 20%, IEF 30%.
- 세금/비용: HIFO lot accounting, 연 250만원 공제, ongoing NAV, 매매 수수료 0.25% 양방향, 배당 원천징수 15%, 양도세 22%, FX spread 0bps.
- terminal liquidation tax는 포함하지 않았다.

## 7 frequency gross vs after-tax 비교

| label | gross_cagr | after_tax_cagr | after_tax_sharpe | after_tax_mdd | realized_gains_krw_16y | total_tax_paid_krw_16y | average_annual_turnover | average_tracking_drift_pp |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| No-rebalance | 0.147394 | 0.146900 | 1.024985 | -0.213305 | 0.000000 | 8775994.921036 | 0.000000 | 38.557463 |
| Threshold 10pp | 0.131842 | 0.126506 | 1.066402 | -0.186119 | 101837690.497891 | 30030740.639205 | 0.124085 | 12.881941 |
| Threshold 5pp | 0.127836 | 0.122726 | 1.106845 | -0.176212 | 100432283.311033 | 27102211.384746 | 0.088314 | 6.357290 |
| Annual | 0.128451 | 0.122598 | 1.121424 | -0.166926 | 104440997.497704 | 26191516.820052 | 0.046889 | 5.393897 |
| Quarterly | 0.128502 | 0.121943 | 1.126830 | -0.164749 | 110484548.559882 | 26343845.737517 | 0.083303 | 2.834848 |
| Semiannual | 0.127373 | 0.121393 | 1.120912 | -0.164893 | 103187986.895817 | 24736050.762252 | 0.055456 | 3.649644 |
| Monthly | 0.127182 | 0.120461 | 1.120597 | -0.169439 | 107821585.293750 | 25124981.394560 | 0.133427 | 1.576707 |

## Net CAGR 1위

- 1위: No-rebalance after-tax CAGR 0.146900, Sharpe 1.024985, MDD -0.213305.
- Quarterly와 1위 차이: 2.496pp.
- 사전 기준상 차이가 0.5pp 미만이면 equivalent로 보고 현행 quarterly를 유지한다.

## Quarterly vs annual

- Quarterly after-tax CAGR 0.121943, Annual 0.122598, delta -0.066pp.
- Quarterly 총 세금 26,343,846 KRW, Annual 총 세금 26,191,517 KRW.
- Quarterly 평균 연 turnover 0.083303, Annual 평균 연 turnover 0.046889.

## Threshold rebalance 효과

- Threshold 5pp: after-tax CAGR 0.122726, 총 세금 27,102,211 KRW, 평균 drift 6.357pp.
- Threshold 10pp: after-tax CAGR 0.126506, 총 세금 30,030,741 KRW, 평균 drift 12.882pp.

## No-rebalance 효과

- No-rebalance after-tax CAGR 0.146900, Sharpe 1.024985, MDD -0.213305.
- 총 세금 8,775,995 KRW, 평균 tracking drift 38.557pp, 최대 component drift 30.112pp.

## Stress 재검증

| label | 2020_covid_daily_mdd_daily_mdd | 2022_krw_return_calendar_year_return | 2025_spike_exclusion_cagr_excluding_2025_return_days |
| --- | --- | --- | --- |
| Annual | -0.165886 | -0.151049 | 0.114544 |
| Monthly | -0.169439 | -0.148348 | 0.112045 |
| No-rebalance | -0.209079 | -0.205504 | 0.140655 |
| Quarterly | -0.164749 | -0.149528 | 0.113814 |
| Semiannual | -0.164893 | -0.149651 | 0.113095 |
| Threshold 10pp | -0.186119 | -0.164666 | 0.117739 |
| Threshold 5pp | -0.176212 | -0.151620 | 0.114332 |

## Verdict

- 권장 rebalance frequency: No-rebalance.
- 사전 기준 적용 결과: 1위 frequency가 quarterly 대비 0.5pp 이상 우위.
- T002 no-trade band 진행 권고: threshold 결과가 세금 절감과 drift 비용의 trade-off를 직접 보여주므로, quarterly schedule 위에 no-trade band를 얹는 후속 실험이 필요하다.

## Files

- frequency_metrics.csv
- tax_paid_by_frequency.csv
- turnover_by_frequency.csv
- tracking_drift_by_frequency.csv
- stress_net_by_frequency.csv
- daily_nav_by_frequency.csv
