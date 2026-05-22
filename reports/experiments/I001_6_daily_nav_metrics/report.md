# I001.6 — Daily NAV Metric Standardization

## 방법

- 기간: 2010-01-04부터 2026-05-18까지.
- Calendar: 9 ETF, D013, H001 source date의 union calendar. 휴일 차이는 component NAV forward-fill.
- Portfolio: 분기 첫 관측일에 사전 등록 weight로 reset, 분기 내 daily mark-to-market으로 weight drift 허용.
- Metric: Sharpe/volatility/Sortino는 daily return 기준 annualized, MDD는 daily NAV peak-to-trough.
- D013/H001 strategy와 `engine.py`는 수정하지 않았다.
- USDKRW latest observation used: 2026-04-24 at 1476.47.

## QC 결과

- QQQ Sharpe: quarterly 1.211435 vs daily 1.003577. Production 기준은 daily 1.003577이다.
- P08 MDD: I001.5 quarterly -0.165629 (-16.56%) vs daily -0.234285 (-23.43%). Daily가 -6.87pp 더 낮다.
- 결론: quarterly metric은 portfolio ranking 참고용으로만 남기고, production risk metric은 daily NAV 재계산값으로 고정한다.

## Sharpe 차이 상위

| carrier | quarterly_sharpe | daily_sharpe | sharpe_delta | large_sharpe_delta |
| --- | --- | --- | --- | --- |
| P03_QQQ50_SPY50 | 1.231085 | 0.979359 | -0.251726 | True |
| SPY | 1.161971 | 0.913187 | -0.248785 | True |
| P02_SPY_100 | 1.161971 | 0.913187 | -0.248785 | True |
| P01_QQQ_100 | 1.211435 | 1.003577 | -0.207857 | True |
| QQQ | 1.211435 | 1.003577 | -0.207857 | True |
| P08_SPY40_QQQ30_H00120_IEF10 | 1.301124 | 1.109627 | -0.191496 | True |
| UUP | 0.230549 | 0.350390 | 0.119841 | True |
| P06_SPY35_QQQ35_H00130 | 1.233358 | 1.116405 | -0.116953 | True |

## MDD 차이 상위

| carrier | quarterly_max_drawdown | daily_max_drawdown | mdd_delta | large_mdd_delta |
| --- | --- | --- | --- | --- |
| P05_SPY50_H00150 | -0.126688 | -0.297983 | -0.171295 | True |
| P02_SPY_100 | -0.150236 | -0.296166 | -0.145930 | True |
| SPY | -0.150236 | -0.296166 | -0.145930 | True |
| H001 | -0.207547 | -0.339235 | -0.131687 | True |
| D013 | -0.210512 | -0.339235 | -0.128723 | True |
| IWM | -0.268345 | -0.384643 | -0.116298 | True |
| P06_SPY35_QQQ35_H00130 | -0.172034 | -0.272298 | -0.100264 | True |
| P04_QQQ50_H00150 | -0.185346 | -0.268630 | -0.083284 | True |

## 최종 Daily Metric 표

| carrier | asset_type | cumulative_net_total_return | cagr | daily_annualized_volatility | sharpe | sortino | max_drawdown | positive_years |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SPY | ETF buy-hold | 10.210326 | 0.159126 | 0.174105 | 0.913187 | 1.182458 | -0.296166 | 15 |
| QQQ | ETF buy-hold | 21.568635 | 0.209756 | 0.205955 | 1.003577 | 1.338888 | -0.306440 | 16 |
| IWM | ETF buy-hold | 5.940840 | 0.125666 | 0.220155 | 0.634011 | 0.863117 | -0.384643 | 14 |
| SHY | ETF buy-hold | 0.603097 | 0.029255 | 0.088915 | 0.360228 | 0.509915 | -0.169777 | 13 |
| IEF | ETF buy-hold | 0.953742 | 0.041770 | 0.111517 | 0.413021 | 0.617309 | -0.181936 | 13 |
| TLT | ETF buy-hold | 0.921582 | 0.040714 | 0.177492 | 0.307503 | 0.474129 | -0.426555 | 12 |
| GLD | ETF buy-hold | 3.901859 | 0.101997 | 0.174321 | 0.629953 | 0.852731 | -0.422463 | 14 |
| UUP | ETF buy-hold | 0.859149 | 0.038616 | 0.129044 | 0.350390 | 0.519632 | -0.328058 | 11 |
| DBC | ETF buy-hold | 0.891479 | 0.039710 | 0.176753 | 0.303151 | 0.419577 | -0.616960 | 8 |
| D013 | Korea strategy | 2.545770 | 0.080405 | 0.156275 | 0.559856 | 0.454181 | -0.339235 | 7 |
| H001 | Korea strategy | 3.571886 | 0.097315 | 0.156243 | 0.656752 | 0.532666 | -0.339235 | 13 |
| P01_QQQ_100 | Quarterly rebalanced portfolio | 21.568635 | 0.209756 | 0.205955 | 1.003577 | 1.338888 | -0.306440 | 16 |
| P02_SPY_100 | Quarterly rebalanced portfolio | 10.210326 | 0.159126 | 0.174105 | 0.913187 | 1.182458 | -0.296166 | 15 |
| P03_QQQ50_SPY50 | Quarterly rebalanced portfolio | 15.126010 | 0.185165 | 0.186772 | 0.979359 | 1.285315 | -0.267811 | 16 |
| P04_QQQ50_H00150 | Quarterly rebalanced portfolio | 10.004968 | 0.157817 | 0.131035 | 1.154710 | 1.512209 | -0.268630 | 16 |
| P05_SPY50_H00150 | Quarterly rebalanced portfolio | 6.625211 | 0.132152 | 0.118880 | 1.076314 | 1.361607 | -0.297983 | 15 |
| P06_SPY35_QQQ35_H00130 | Quarterly rebalanced portfolio | 10.700099 | 0.162158 | 0.139874 | 1.116405 | 1.460125 | -0.272298 | 16 |
| P07_QQQ50_H00130_IEF20 | Quarterly rebalanced portfolio | 8.535666 | 0.147724 | 0.116404 | 1.210984 | 1.654043 | -0.199070 | 16 |
| P08_SPY40_QQQ30_H00120_IEF10 | Quarterly rebalanced portfolio | 9.474559 | 0.154328 | 0.134073 | 1.109627 | 1.468604 | -0.234285 | 16 |

## 주요 비교 대상

| carrier | cagr | daily_annualized_volatility | sharpe | sortino | max_drawdown | mdd_peak_date | mdd_trough_date | positive_years |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D013 | 0.080405 | 0.156275 | 0.559856 | 0.454181 | -0.339235 | 2020-02-17 | 2020-03-19 | 7 |
| H001 | 0.097315 | 0.156243 | 0.656752 | 0.532666 | -0.339235 | 2020-02-17 | 2020-03-19 | 13 |
| P01_QQQ_100 | 0.209756 | 0.205955 | 1.003577 | 1.338888 | -0.306440 | 2021-12-27 | 2022-12-28 | 16 |
| P02_SPY_100 | 0.159126 | 0.174105 | 0.913187 | 1.182458 | -0.296166 | 2020-02-20 | 2020-03-23 | 15 |
| P03_QQQ50_SPY50 | 0.185165 | 0.186772 | 0.979359 | 1.285315 | -0.267811 | 2020-02-19 | 2020-03-16 | 16 |
| P06_SPY35_QQQ35_H00130 | 0.162158 | 0.139874 | 1.116405 | 1.460125 | -0.272298 | 2020-02-19 | 2020-03-23 | 16 |
| P07_QQQ50_H00130_IEF20 | 0.147724 | 0.116404 | 1.210984 | 1.654043 | -0.199070 | 2021-12-28 | 2022-12-28 | 16 |
| P08_SPY40_QQQ30_H00120_IEF10 | 0.154328 | 0.134073 | 1.109627 | 1.468604 | -0.234285 | 2020-02-19 | 2020-03-23 | 16 |

## P08 일별 NAV drawdown

- P08 daily MDD 구간: peak 2020-02-19에서 trough 2020-03-23까지.
- 일별 NAV 그래프는 장기 우상향이지만 2020년 3월 코로나 급락 구간에서 가장 깊게 꺾인다. 2022년 금리/성장주 drawdown도 길게 나타나지만, P08의 최저 peak-to-trough 손실은 2020년 3월 구간이다.
- P08 worst drawdown dates:

| date | net_value | running_peak | drawdown |
| --- | --- | --- | --- |
| 2020-03-23 | 2.572004 | 3.358956 | -0.234285 |
| 2020-03-20 | 2.584530 | 3.358956 | -0.230556 |
| 2020-03-16 | 2.606317 | 3.358956 | -0.224069 |
| 2020-03-19 | 2.608534 | 3.358956 | -0.223409 |
| 2020-03-18 | 2.620322 | 3.358956 | -0.219900 |

## Verdict

- Best daily Sharpe carrier: P07_QQQ50_H00130_IEF20 (Sharpe 1.210984, MDD -0.199070, CAGR 0.147724).
- I003 진행 권고: P08은 daily 기준에서도 비교 대상 중 Sharpe 최상위권이며, daily MDD가 분기 MDD보다 더 깊지만 demote 기준으로 볼 정도의 순위 붕괴는 확인되지 않았다.
- I003 robustness는 quarterly metric이 아니라 이 I001.6 daily metric 기준으로 진행한다.

## Files

- daily_nav_by_portfolio.csv
- daily_metrics.csv
- quarterly_vs_daily_metrics.csv
- mdd_drawdown_paths.csv
