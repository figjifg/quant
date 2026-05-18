# I000 — US/Global ETF Universe Diagnostic

## Verdict

- 판정: PROCEED
- I001 권고: ETF별 buy-and-hold KRW baseline 및 D013/H001 결합 포트폴리오 baseline으로 진행

## Data Availability

- ETF 수: 9
- 공통 요청 구간: 2010-03-31 ~ 2026-03-31
- D013 분기 기준일 수: 61
- ETF KRW return 유효 분기 수: 60
- ETF 가격 기준: Yahoo Finance auto-adjusted Close
- 환산 기준: ETF_KRW_return = (1 + ETF_USD_return) * (1 + USDKRW_quarter_change) - 1
- 분기말 정렬: D013 quarterly_regime_log.signal_date별 가장 가까운 ETF/USDKRW 관측치

## KRW Cumulative Returns

| ticker | n_quarters | cumulative_krw_return |
| --- | --- | --- |
| QQQ | 60 | 17.576497 |
| SPY | 60 | 8.964154 |
| IWM | 60 | 5.120801 |
| GLD | 60 | 4.319087 |
| TLT | 60 | 1.064900 |
| IEF | 60 | 1.046532 |
| DBC | 60 | 0.960798 |
| UUP | 60 | 0.881757 |
| SHY | 60 | 0.670361 |

## Correlation With D013/H001

| ticker | pearson_d013 | spearman_d013 | pearson_h001 | spearman_h001 | max_abs_pearson_vs_d013_h001 | low_correlation_candidate |
| --- | --- | --- | --- | --- | --- | --- |
| TLT | -0.090839 | 0.015544 | -0.091118 | -0.037121 | 0.091118 | True |
| IEF | -0.095890 | -0.097440 | -0.097647 | -0.134871 | 0.097647 | True |
| SHY | -0.099677 | -0.169445 | -0.106620 | -0.193054 | 0.106620 | True |
| UUP | -0.139485 | -0.193252 | -0.146491 | -0.204668 | 0.146491 | True |
| GLD | 0.196408 | 0.052130 | 0.191515 | 0.035288 | 0.196408 | True |
| DBC | 0.212403 | 0.040119 | 0.202394 | 0.043012 | 0.212403 | True |
| QQQ | 0.244491 | 0.297050 | 0.240968 | 0.250181 | 0.244491 | True |
| SPY | 0.262923 | 0.274595 | 0.258630 | 0.221839 | 0.262923 | True |
| IWM | 0.399177 | 0.350839 | 0.398285 | 0.285913 | 0.399177 | False |

## Lowest Correlation Top 3

| ticker | pearson_d013 | pearson_h001 | max_abs_pearson_vs_d013_h001 |
| --- | --- | --- | --- |
| TLT | -0.090839 | -0.091118 | 0.091118 |
| IEF | -0.095890 | -0.097647 | 0.097647 |
| SHY | -0.099677 | -0.106620 | 0.106620 |

## Files

- etf_data_availability.csv
- etf_quarterly_returns.csv
- correlation_matrix.csv
- correlation_with_d013_h001.csv

## Notes

- D013/H001 strategy code and engine code were not modified.
- This is a diagnostic analysis only; no new strategy code was added.
- Correlation matrix shape: 11x11
