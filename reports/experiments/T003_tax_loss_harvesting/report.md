# T003 tax-loss harvesting diagnostic

## 설정

- 대상: P08_IEF30 = SPY 29%, QQQ 21%, H001 20%, IEF 30%.
- Rebalance: quarterly + 0pp, HIFO lot accounting, ongoing NAV.
- 세금/비용: 해외 ETF 양도세 22%, 연 250만원 공제, 매매 수수료 0.25%, 배당 원천징수 15%.
- H001은 한국 주식 비대주주 가정으로 양도세/TLH를 적용하지 않았다.
- 한국 세법 가정: 해외 ETF 손익통산 가능, 동일 ETF 즉시 재매수에 대한 wash sale rule 없음으로 단순화했다.
- Diagnostic only: 실전 적용 전 세무 전문가 확인이 필요하다. Wash sale, 동일/유사 exposure 대체, broker reporting은 별도 검토 대상이다.
- T003-A는 T000-C baseline reproduction이다. 배당 원천징수는 T000과 동일하게 세목 추적만 하고 NAV에서는 차감하지 않아 lot/tax timing 효과를 isolate했다.

## 5 시나리오 net 비교

| scenario | label | net_cagr | net_cagr_delta_vs_t003_a_pp | net_sharpe | net_mdd | realized_loss_krw_16y | tlh_tax_savings_true_up_krw_16y | tlh_commission_krw_16y | tlh_tax_savings_minus_commission_krw | annual_exemption_utilization_ratio | passes_plus_0p1pp_net_cagr |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| T003-A | No TLH | 0.124626 | 0.000000 | 1.149528 | -0.164730 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.787504 | False |
| T003-B | Year-end TLH: all loss lots | 0.124670 | 0.004413 | 1.149852 | -0.164729 | -5916496.745368 | 1070390.969312 | 458117.388470 | 612273.580842 | 0.782765 | False |
| T003-C | Quarter-end TLH: all loss lots | 0.124248 | -0.037738 | 1.146186 | -0.164730 | -8306401.199111 | 1028464.270659 | 1382436.877797 | -353972.607138 | 0.774688 | False |
| T003-D | Year-end TLH: loss <= -5% | 0.124665 | 0.003947 | 1.149797 | -0.164730 | -4038580.661413 | 727585.224342 | 207117.321729 | 520467.902613 | 0.782285 | False |
| T003-E | Year-end TLH: loss <= -10% | 0.124675 | 0.004902 | 1.149914 | -0.164730 | -2009266.507616 | 399225.382487 | 84612.673899 | 314612.708588 | 0.784004 | False |

## TLH 의 net CAGR 개선 효과

- Gross I003.5 참고 CAGR: 0.127384.
- T000-C baseline 참고 CAGR: 0.124626.
- T003-A reproduction net CAGR: 0.124626.
- TLH 최고 시나리오: T003-E Year-end TLH: loss <= -10%, net CAGR 0.124675, T003-A 대비 0.005pp.
- 사전 기준(+0.1pp net CAGR): 미통과.

## 가장 효과적 TLH 시나리오

- Net CAGR 기준 1위는 T003-E Year-end TLH: loss <= -10%이다.
- 16년 누적 TLH tax true-up savings 399225 KRW, TLH 추가 수수료 84613 KRW, 순효과 314613 KRW.

## 250만원 공제 활용 효율

- T003-A annual exemption utilization ratio: 0.787504.
- 최고 TLH annual exemption utilization ratio: 0.784004.
- TLH는 손실을 같은 해 이익과 통산해 과세표준을 낮추는 구조이므로, 공제 활용률 상승 자체보다 과세표준 감소와 true-up savings가 핵심 측정치다.

## 2020/2022 큰 loss 해와 2025 spike exclusion

| scenario | label | 2020_covid_daily_mdd_daily_mdd | 2022_krw_return_calendar_year_return | 2025_spike_exclusion_cagr_excluding_2025_return_days |
| --- | --- | --- | --- | --- |
| T003-A | No TLH | -0.164730 | -0.147537 | 0.116401 |
| T003-B | Year-end TLH: all loss lots | -0.164729 | -0.146986 | 0.116452 |
| T003-C | Quarter-end TLH: all loss lots | -0.164730 | -0.147465 | 0.116019 |
| T003-D | Year-end TLH: loss <= -5% | -0.164730 | -0.147398 | 0.116447 |
| T003-E | Year-end TLH: loss <= -10% | -0.164730 | -0.147630 | 0.116457 |

## TLH 매매 수수료 vs 양도세 절감

| scenario | capital_gains_tax_reduction_vs_t003_a_krw | tlh_true_up_tax_savings_krw |
| --- | --- | --- |
| T003-A | 0.000000 | 0.000000 |
| T003-B | 662040.549089 | 1070390.969312 |
| T003-C | 719823.147020 | 1028464.270659 |
| T003-D | 332286.551586 | 727585.224342 |
| T003-E | 275998.647580 | 399225.382487 |

## Realized loss 발생 상위 연도

| scenario | label | tax_year | realized_loss_krw | tlh_event_count | tlh_commission_krw |
| --- | --- | --- | --- | --- | --- |
| T003-D | Year-end TLH: loss <= -5% | 2020 | -2084858.434536 | 2 | 94573.730776 |
| T003-B | Year-end TLH: all loss lots | 2020 | -2084051.710414 | 2 | 94537.137851 |
| T003-C | Quarter-end TLH: all loss lots | 2020 | -2073018.215380 | 3 | 174593.298931 |
| T003-B | Year-end TLH: all loss lots | 2022 | -2069991.674542 | 7 | 195975.225747 |
| T003-C | Quarter-end TLH: all loss lots | 2022 | -2014667.776411 | 10 | 233156.350975 |
| T003-E | Year-end TLH: loss <= -10% | 2020 | -1743155.883945 | 1 | 74547.480599 |
| T003-C | Quarter-end TLH: all loss lots | 2010 | -1163920.950398 | 4 | 397878.836427 |
| T003-D | Year-end TLH: loss <= -5% | 2013 | -706698.300845 | 5 | 37906.401221 |
| T003-B | Year-end TLH: all loss lots | 2013 | -698939.880991 | 6 | 48097.741293 |
| T003-C | Quarter-end TLH: all loss lots | 2013 | -695406.176193 | 12 | 89353.293437 |

## Verdict

- Verdict: T003-E가 T003-A 대비 net CAGR을 0.005pp 개선했다. 사전 기준은 미통과.
- TLH가 유효한 경우에도 결과는 한국 세법 단순화에 의존한다. 실전 적용 전 세무 전문가 확인이 필요하다.
- T004 권고: account/vehicle study를 진행해 일반계좌, 연금/ISA 가능성, broker reporting, 실제 세금 납부 timing을 비교한다.

## Files

- tlh_scenarios.csv
- realized_loss_by_year.csv
- tax_savings_by_year.csv
- tlh_events.csv
- daily_nav_by_tlh.csv
- stress_net_by_tlh.csv
