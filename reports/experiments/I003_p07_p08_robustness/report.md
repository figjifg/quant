# I003 — P07/P08 Robustness

## 방법

- I001.6과 동일한 daily NAV 재구성: quarterly rebalance + daily mark-to-market.
- 외부 network는 사용하지 않았다. D013/H001 strategy와 `engine.py`는 수정하지 않았다.
- 기간: 2010-01-04부터 2026-05-18까지.
- USDKRW latest observation used: 2026-04-24 at 1476.47.
- Grid는 plateau 확인용이며, 새 weight를 final 후보로 승격하지 않는다.

## Grid plateau 확인

### I003-A P07-style IEF grid

| candidate | weights | cagr | sharpe | sortino | max_drawdown | positive_years |
| --- | --- | --- | --- | --- | --- | --- |
| A01_QQQ70_H00130_IEF00 | QQQ70/H00130 | 0.179699 | 1.131242 | 1.505084 | -0.252425 | 16 |
| A02_QQQ60_H00130_IEF10 | QQQ60/H00130/IEF10 | 0.163865 | 1.172466 | 1.579317 | -0.219741 | 16 |
| A03_P07_QQQ50_H00130_IEF20 | QQQ50/H00130/IEF20 | 0.147724 | 1.210984 | 1.654043 | -0.199070 | 16 |
| A04_QQQ40_H00130_IEF30 | QQQ40/H00130/IEF30 | 0.131292 | 1.234846 | 1.713894 | -0.178219 | 16 |

### I003-B P08-style IEF grid

| candidate | weights | cagr | sharpe | sortino | max_drawdown | positive_years |
| --- | --- | --- | --- | --- | --- | --- |
| B01_SPY46_QQQ34_H00120_IEF00 | SPY46/QQQ34/H00120 | 0.167101 | 1.070409 | 1.396504 | -0.272948 | 16 |
| B02_P08_SPY40_QQQ30_H00120_IEF10 | SPY40/QQQ30/H00120/IEF10 | 0.154328 | 1.109627 | 1.468604 | -0.234285 | 16 |
| B03_SPY34_QQQ26_H00120_IEF20 | SPY34/QQQ26/H00120/IEF20 | 0.141254 | 1.146777 | 1.543249 | -0.195824 | 16 |
| B04_SPY29_QQQ21_H00120_IEF30 | SPY29/QQQ21/H00120/IEF30 | 0.127384 | 1.172143 | 1.605149 | -0.164077 | 16 |

### I003-C SPY inclusion test

| candidate | weights | cagr | sharpe | sortino | max_drawdown | positive_years |
| --- | --- | --- | --- | --- | --- | --- |
| C01_P07_QQQ50_SPY00_H00130_IEF20 | QQQ50/H00130/IEF20 | 0.147724 | 1.210984 | 1.654043 | -0.199070 | 16 |
| C02_QQQ40_SPY10_H00130_IEF20 | QQQ40/SPY10/H00130/IEF20 | 0.142728 | 1.209363 | 1.643114 | -0.194827 | 16 |
| C03_QQQ35_SPY15_H00130_IEF20 | QQQ35/SPY15/H00130/IEF20 | 0.140210 | 1.206839 | 1.635222 | -0.196777 | 16 |
| C04_QQQ30_SPY20_H00130_IEF20 | QQQ30/SPY20/H00130/IEF20 | 0.137678 | 1.203035 | 1.625462 | -0.198739 | 16 |
| C05_QQQ25_SPY25_H00130_IEF20 | QQQ25/SPY25/H00130/IEF20 | 0.135132 | 1.197850 | 1.613374 | -0.200797 | 16 |

## 2020 stress 결과

- P07 COVID MDD: -0.190961, recovery 2020-05-20.
- P08 COVID MDD: -0.234285, recovery 2020-06-05.

| candidate | daily_mdd | recovery_date | QQQ_return_contribution | SPY_return_contribution | H001_return_contribution | IEF_return_contribution |
| --- | --- | --- | --- | --- | --- | --- |
| A03_P07_QQQ50_H00130_IEF20 | -0.190961 | 2020-05-20 | -0.109810 | 0.000000 | -0.095786 | 0.014635 |
| B02_P08_SPY40_QQQ30_H00120_IEF10 | -0.234285 | 2020-06-05 | -0.072933 | -0.115994 | -0.058068 | 0.012710 |

## 2022 stress 결과

- P07 2022 KRW return: -0.191375; IEF weight 20%.
- P08 2022 KRW return: -0.170427; IEF weight 10%.
- Local data 기준 QQQ 2022 USD return -0.332199, IEF 2022 USD return -0.143584.

| candidate | calendar_year_return_krw | QQQ_weighted_krw_impact | IEF_weighted_krw_impact | QQQ_return_contribution | IEF_return_contribution |
| --- | --- | --- | --- | --- | --- |
| A03_P07_QQQ50_H00130_IEF20 | -0.191375 | -0.146820 | -0.018827 | -0.149948 | -0.016700 |
| B02_P08_SPY40_QQQ30_H00120_IEF10 | -0.170427 | -0.088092 | -0.009413 | -0.090945 | -0.008394 |

## Long-history stress

- local ETF files do not contain 2000-2002 history; network fetch is forbidden
- 2000-2002 dot-com 구간은 local QQQ/SPY/IEF 파일이 2010부터 시작하므로 산출하지 않았다. H001은 ticket대로 2010 이전 재현하지 않는다.

## Subperiod 결과

| candidate | period | cagr | sharpe | max_drawdown | mdd_peak_date | mdd_trough_date | mdd_length_days |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A03_P07_QQQ50_H00130_IEF20 | 2010_2017 | 0.101045 | 1.098869 | -0.075050 | 2012-09-06 | 2012-11-15 | 70 |
| A03_P07_QQQ50_H00130_IEF20 | 2018_2026 | 0.193880 | 1.324199 | -0.199070 | 2021-12-28 | 2022-12-28 | 365 |
| A03_P07_QQQ50_H00130_IEF20 | 2021_2022_drawdown | 0.079796 | 0.609202 | -0.199070 | 2021-12-28 | 2022-12-28 | 365 |
| B02_P08_SPY40_QQQ30_H00120_IEF10 | 2010_2017 | 0.111335 | 0.987301 | -0.114783 | 2011-02-14 | 2011-08-08 | 175 |
| B02_P08_SPY40_QQQ30_H00120_IEF10 | 2018_2026 | 0.196841 | 1.217889 | -0.234285 | 2020-02-19 | 2020-03-23 | 33 |
| B02_P08_SPY40_QQQ30_H00120_IEF10 | 2021_2022_drawdown | 0.115920 | 0.758851 | -0.176765 | 2021-12-28 | 2022-12-28 | 365 |

## Contribution attribution

### P07

| component | target_weight | return_contribution | component_total_return_krw | component_total_return_usd | fx_contribution_estimate |
| --- | --- | --- | --- | --- | --- |
| QQQ | 0.500000 | 5.354972 | 21.568635 | 16.563081 | 2.502777 |
| SPY | 0.000000 | 0.000000 | 10.210326 | 7.723960 | 0.000000 |
| H001 | 0.300000 | 2.771762 | 3.571886 |  | 0.000000 |
| IEF | 0.200000 | 0.408932 | 0.953742 | 0.520417 | 0.086665 |
| rebalance_effect |  | -3.510966 |  |  |  |
| total | 1.000000 | 8.535666 | 8.535666 |  | 2.589442 |

### P08

| component | target_weight | return_contribution | component_total_return_krw | component_total_return_usd | fx_contribution_estimate |
| --- | --- | --- | --- | --- | --- |
| QQQ | 0.300000 | 3.509701 | 21.568635 | 16.563081 | 1.501666 |
| SPY | 0.400000 | 3.649517 | 10.210326 | 7.723960 | 0.994547 |
| H001 | 0.200000 | 2.085400 | 3.571886 |  | 0.000000 |
| IEF | 0.100000 | 0.229941 | 0.953742 | 0.520417 | 0.043333 |
| rebalance_effect |  | -1.889913 |  |  |  |
| total | 1.000000 | 9.474559 | 9.474559 |  | 2.539545 |

## 최종 verdict

- Verdict: P08 prefer.
- P07: Sharpe 1.210984, CAGR 0.147724, MDD -0.199070.
- P08: Sharpe 1.109627, CAGR 0.154328, MDD -0.234285.
- 사전 등록 rule에 따라 grid의 새 best weight는 final 승격하지 않는다.
- 진행 권고: I004 final candidate registration으로 넘어가되, grid best가 아니라 사전 등록 후보만 등록한다.

## Files

- grid_a_p07_style.csv
- grid_b_p08_style.csv
- grid_c_spy_inclusion.csv
- covid_stress_2020.csv
- rate_shock_stress_2022.csv
- subperiod_split.csv
- us_long_history_stress.csv
- contribution_attribution_p07.csv
- contribution_attribution_p08.csv
- daily_metrics_all_candidates.csv
