# T002 no-trade band / drift tolerance

## 설정

- 대상: P08_IEF30 = SPY 29%, QQQ 21%, H001 20%, IEF 30%.
- 체크 스케줄: monthly, quarterly, annual.
- Band grid: 0pp, 2.5pp, 5pp, 7.5pp, 10pp, 12.5pp, 15pp, 20pp.
- 세금/비용: HIFO lot accounting, 연 250만원 공제, ongoing NAV, 매매 수수료 0.25%, 배당 원천징수 15%, 양도세 22%.
- terminal liquidation tax는 포함하지 않았다.

## Band grid x schedule 24 portfolio net 비교

| label | gross_cagr | net_cagr | net_sharpe | net_mdd | average_tracking_drift_pp | max_component_drift_pp | total_rebalance_events_count_16y | total_tax_paid_krw | total_commission_paid_krw | disqualified_drift_gt_20pp |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Monthly + 20pp | 0.137967 | 0.136640 | 1.052996 | -0.209079 | 24.275369 | 20.385968 | 1 | 21929479.678731 | 616415.229901 | True |
| Annual + 15pp | 0.137987 | 0.135713 | 1.093437 | -0.175593 | 22.511639 | 17.799535 | 1 | 20917540.493689 | 598459.018956 | True |
| Quarterly + 20pp | 0.137967 | 0.135604 | 1.044028 | -0.209079 | 24.562835 | 20.735163 | 1 | 22658389.690572 | 626841.701231 | True |
| Monthly + 15pp | 0.136480 | 0.135331 | 1.087131 | -0.180314 | 19.785857 | 17.168692 | 3 | 43927693.151348 | 1709183.228178 | False |
| Annual + 20pp | 0.136816 | 0.134216 | 1.026747 | -0.209079 | 24.813020 | 23.424504 | 1 | 25362826.208653 | 677939.770609 | True |
| Quarterly + 15pp | 0.135969 | 0.133841 | 1.072195 | -0.179875 | 20.042848 | 16.304873 | 2 | 45493406.283308 | 1178634.104175 | True |
| Annual + 10pp | 0.133579 | 0.130539 | 1.072773 | -0.183558 | 15.078564 | 16.734336 | 3 | 38570312.052873 | 1046125.000468 | False |
| Annual + 12.5pp | 0.134282 | 0.130155 | 1.066953 | -0.184122 | 16.995543 | 14.173441 | 2 | 30499003.138063 | 835737.421292 | False |
| Quarterly + 12.5pp | 0.134282 | 0.129759 | 1.094980 | -0.186413 | 14.577210 | 13.364624 | 2 | 27745685.656868 | 771532.851472 | False |
| Monthly + 12.5pp | 0.134739 | 0.129523 | 1.090510 | -0.178089 | 14.253272 | 12.722304 | 2 | 26254322.715914 | 737790.525237 | False |
| Monthly + 10pp | 0.132790 | 0.127358 | 1.072898 | -0.186119 | 12.952275 | 12.190979 | 4 | 31167616.070328 | 1234938.573674 | False |
| Quarterly + 10pp | 0.131742 | 0.127171 | 1.065320 | -0.183558 | 13.549622 | 12.185728 | 3 | 31417558.348020 | 873901.014783 | False |
| Quarterly + 7.5pp | 0.133704 | 0.124653 | 1.083886 | -0.167230 | 9.728627 | 14.645879 | 5 | 35403494.097742 | 1263617.023240 | False |
| Monthly + 7.5pp | 0.129981 | 0.124420 | 1.096293 | -0.167299 | 9.073076 | 11.308641 | 5 | 33032867.343911 | 1183799.294638 | False |
| Annual + 7.5pp | 0.129526 | 0.124194 | 1.091348 | -0.172636 | 10.840825 | 10.206504 | 4 | 33346881.611402 | 971483.554368 | False |
| Quarterly + 5pp | 0.130246 | 0.123104 | 1.086010 | -0.166772 | 7.806551 | 9.805267 | 9 | 32098206.016386 | 1255940.927445 | False |
| Annual + 5pp | 0.128874 | 0.123012 | 1.092068 | -0.170866 | 8.016040 | 8.661212 | 6 | 31902293.010122 | 1084639.298214 | False |
| Monthly + 5pp | 0.128659 | 0.122899 | 1.110179 | -0.167228 | 6.691771 | 9.702491 | 9 | 26988110.462052 | 1191297.965853 | False |
| Annual + 2.5pp | 0.129234 | 0.122620 | 1.114539 | -0.166949 | 6.222334 | 9.583792 | 11 | 27513822.291977 | 1270485.814840 | False |
| Annual + 0pp | 0.128451 | 0.122598 | 1.121424 | -0.166926 | 5.393897 | 9.553492 | 16 | 26191516.820052 | 1329040.496043 | False |
| Quarterly + 2.5pp | 0.128777 | 0.122593 | 1.121318 | -0.164847 | 4.064206 | 9.259191 | 21 | 26129698.543268 | 1534014.265881 | False |
| Quarterly + 0pp | 0.128502 | 0.121943 | 1.126830 | -0.164749 | 2.834848 | 9.231467 | 65 | 26343845.737517 | 2102061.084695 | False |
| Monthly + 2.5pp | 0.128041 | 0.121616 | 1.121427 | -0.168169 | 3.465000 | 7.490490 | 30 | 25333801.269895 | 1866764.677862 | False |
| Monthly + 0pp | 0.127182 | 0.120461 | 1.120597 | -0.169439 | 1.576707 | 7.142276 | 196 | 25124981.394560 | 3215973.196086 | False |

## Net CAGR 1위

- 전체 1위: Monthly + 20pp net CAGR 0.136640, Sharpe 1.052996, MDD -0.209079.
- Drift 20pp 초과 및 2020/2022 stress hurt 제외 후 1위: Quarterly + 0pp net CAGR 0.121943.
- Quarterly 0pp baseline 대비 전체 1위 차이: 1.470pp.

## Quarterly + 10pp band vs T002 grid 최고

- T002 Quarterly + 10pp: net CAGR 0.127171, max drift 12.186pp.
- T001 Threshold 10pp 참고값: after-tax CAGR 0.126506. T002 grid 1위와 차이 1.013pp.
- T002 Quarterly + 10pp 대비 T002 grid 1위 차이: 0.947pp.

## Drift 의 stress 영향

- Baseline Quarterly 0pp 2020 COVID daily MDD -0.164749, 2022 KRW return -0.149528.
- Grid 1위 Monthly + 20pp 2020 COVID daily MDD -0.209079, 2022 KRW return -0.167896.
- 권장 조합 Quarterly + 0pp 2020 COVID daily MDD -0.164749, 2022 KRW return -0.149528.

## Drift catastrophic 임계값

- Drift > 20pp disqualifier 발생 조합: annual 15.0pp, annual 20.0pp, monthly 20.0pp, quarterly 15.0pp, quarterly 20.0pp.
- 전체 1위 max component drift: 20.386pp.

## 권장 band / schedule 조합

- 권장 조합: Quarterly + 0pp.
- Net CAGR 0.121943, max component drift 9.231pp, rebalance events 65회.
- 사전 stress 기준을 엄격 적용하면 positive band 조합은 2020 또는 2022 중 하나를 baseline보다 악화시켰다.

## Verdict

- Verdict: No-trade band는 net CAGR을 높였지만, 사전 등록된 drift/stress 필터까지 통과한 positive band 조합은 없었다. 현행 Quarterly 0pp를 유지한다.
- 다음 단계 권고: T003 tax-loss harvesting을 우선 진행한다. T002 결과는 no-trade band가 매도 시점과 과세 timing을 바꾸는 문제이므로, 손실 harvesting과 직접 연결된다.

## Files

- band_grid_metrics.csv
- drift_paths.csv
- rebalance_events.csv
- stress_net_by_band.csv
- daily_nav_by_band.csv
