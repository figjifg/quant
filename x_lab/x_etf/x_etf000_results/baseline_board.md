# X-ETF000 Baseline Board

X-Lab quarantine applies. This board is diagnostic only and does not affect `P08_IEF30`.

Verdict: `PASS_WITH_SCOPE`

Scope:
- Primary universe: 13 ETFs excluding MCHI, 2010-01 full coverage.
- Secondary robustness: 14 ETFs including MCHI, common-start after MCHI lookback.
- MCHI is excluded from the primary X-ETF001 universe and included only in secondary robustness checks.

## Data Availability

| ticker | source_file | start_date | end_date | row_count | duplicate_date_rows | missing_close_rows | missing_business_days_between_start_end | adjusted_price_assumption | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SPY | research_input_data/inputs/global_etf/yf_SPY_long.csv | 1993-01-29 | 2026-05-18 | 8382 | 0 | 0 | 305 | Yahoo Finance local Close treated as adjusted (auto_adjust=True assumption) | available |
| QQQ | research_input_data/inputs/global_etf/yf_QQQ_long.csv | 1999-03-10 | 2026-05-18 | 6840 | 0 | 0 | 254 | Yahoo Finance local Close treated as adjusted (auto_adjust=True assumption) | available |
| IWM | research_input_data/inputs/global_etf/yf_IWM.csv | 2010-01-04 | 2026-05-18 | 4118 | 0 | 0 | 153 | Yahoo Finance local Close treated as adjusted (auto_adjust=True assumption) | available |
| IEF | research_input_data/inputs/global_etf/yf_IEF_long.csv | 2002-07-30 | 2026-05-18 | 5989 | 0 | 0 | 221 | Yahoo Finance local Close treated as adjusted (auto_adjust=True assumption) | available |
| TLT | research_input_data/inputs/global_etf/yf_TLT_long.csv | 2002-07-30 | 2026-05-18 | 5989 | 0 | 0 | 221 | Yahoo Finance local Close treated as adjusted (auto_adjust=True assumption) | available |
| SHY | research_input_data/inputs/global_etf/yf_SHY.csv | 2010-01-04 | 2026-05-18 | 4118 | 0 | 0 | 153 | Yahoo Finance local Close treated as adjusted (auto_adjust=True assumption) | available |
| GLD | research_input_data/inputs/global_etf/yf_GLD_long.csv | 2004-11-18 | 2026-05-18 | 5407 | 0 | 0 | 201 | Yahoo Finance local Close treated as adjusted (auto_adjust=True assumption) | available |
| UUP | research_input_data/inputs/global_etf/yf_UUP.csv | 2010-01-04 | 2026-05-18 | 4118 | 0 | 0 | 153 | Yahoo Finance local Close treated as adjusted (auto_adjust=True assumption) | available |
| DBC | research_input_data/inputs/global_etf/yf_DBC.csv | 2010-01-04 | 2026-05-18 | 4118 | 0 | 0 | 153 | Yahoo Finance local Close treated as adjusted (auto_adjust=True assumption) | available |
| VWO | research_input_data/inputs/global_etf/yf_em_VWO.csv | 2005-03-10 | 2026-05-18 | 5331 | 0 | 0 | 197 | Yahoo Finance local Close treated as adjusted (auto_adjust=True assumption) | available |
| EWY | research_input_data/inputs/global_etf/yf_em_EWY.csv | 2000-05-12 | 2026-05-18 | 6542 | 0 | 0 | 245 | Yahoo Finance local Close treated as adjusted (auto_adjust=True assumption) | available |
| EWJ | research_input_data/inputs/global_etf/yf_em_EWJ.csv | 1996-03-18 | 2026-05-18 | 7591 | 0 | 0 | 280 | Yahoo Finance local Close treated as adjusted (auto_adjust=True assumption) | available |
| EWZ | research_input_data/inputs/global_etf/yf_em_EWZ.csv | 2000-07-14 | 2026-05-18 | 6499 | 0 | 0 | 243 | Yahoo Finance local Close treated as adjusted (auto_adjust=True assumption) | available |
| MCHI | research_input_data/inputs/global_etf/yf_em_MCHI.csv | 2011-03-31 | 2026-05-18 | 3805 | 0 | 0 | 143 | Yahoo Finance local Close treated as adjusted (auto_adjust=True assumption) | available |

## Buy-and-Hold Metrics, USD 2010-2026

| name | currency | start_date | end_date | cagr | sharpe | max_drawdown | calmar | annualized_volatility |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SPY | USD | 2010-01-04 | 2026-05-18 | 0.141397 | 0.859102 | -0.337173 | 0.419362 | 0.171356 |
| QQQ | USD | 2010-01-04 | 2026-05-18 | 0.191182 | 0.954362 | -0.351187 | 0.544388 | 0.205912 |
| IWM | USD | 2010-01-04 | 2026-05-18 | 0.108551 | 0.575680 | -0.411333 | 0.263900 | 0.222493 |
| IEF | USD | 2010-01-04 | 2026-05-18 | 0.025856 | 0.420505 | -0.239247 | 0.108074 | 0.065979 |
| TLT | USD | 2010-01-04 | 2026-05-18 | 0.024834 | 0.238807 | -0.483511 | 0.051362 | 0.149937 |
| SHY | USD | 2010-01-04 | 2026-05-18 | 0.013605 | 1.018472 | -0.057071 | 0.238392 | 0.013377 |
| GLD | USD | 2010-01-04 | 2026-05-18 | 0.085175 | 0.578047 | -0.455550 | 0.186972 | 0.165410 |
| UUP | USD | 2010-01-04 | 2026-05-18 | 0.022824 | 0.344113 | -0.189702 | 0.120314 | 0.073543 |
| DBC | USD | 2010-01-04 | 2026-05-18 | 0.023902 | 0.223569 | -0.661442 | 0.036136 | 0.173082 |
| VWO | USD | 2010-01-04 | 2026-05-18 | 0.047758 | 0.330809 | -0.363924 | 0.131230 | 0.205046 |
| EWY | USD | 2010-01-04 | 2026-05-18 | 0.098543 | 0.493694 | -0.497342 | 0.198139 | 0.258702 |
| EWJ | USD | 2010-01-04 | 2026-05-18 | 0.070528 | 0.470792 | -0.331441 | 0.212793 | 0.179191 |
| EWZ | USD | 2010-01-04 | 2026-05-18 | -0.002763 | 0.157339 | -0.748621 | -0.003691 | 0.328282 |
| MCHI | USD | 2011-03-31 | 2026-05-18 | 0.025869 | 0.228635 | -0.628363 | 0.041169 | 0.265709 |

## Buy-and-Hold Metrics, KRW 2010-2026

| name | currency | start_date | end_date | cagr | sharpe | max_drawdown | calmar | annualized_volatility |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SPY | KRW | 2010-01-04 | 2026-05-18 | 0.159020 | 0.925696 | -0.296166 | 0.536928 | 0.176574 |
| QQQ | KRW | 2010-01-04 | 2026-05-18 | 0.209573 | 1.017172 | -0.306440 | 0.683896 | 0.208877 |
| IWM | KRW | 2010-01-04 | 2026-05-18 | 0.125666 | 0.643043 | -0.384643 | 0.326707 | 0.223282 |
| IEF | KRW | 2010-01-04 | 2026-05-18 | 0.041695 | 0.418262 | -0.181937 | 0.229172 | 0.113103 |
| TLT | KRW | 2010-01-04 | 2026-05-18 | 0.040657 | 0.311572 | -0.426555 | 0.095314 | 0.180017 |
| SHY | KRW | 2010-01-04 | 2026-05-18 | 0.029255 | 0.365354 | -0.169777 | 0.172312 | 0.090179 |
| GLD | KRW | 2010-01-04 | 2026-05-18 | 0.101929 | 0.638582 | -0.422463 | 0.241274 | 0.176797 |
| UUP | KRW | 2010-01-04 | 2026-05-18 | 0.038616 | 0.355376 | -0.328058 | 0.117709 | 0.130879 |
| DBC | KRW | 2010-01-04 | 2026-05-18 | 0.039710 | 0.307464 | -0.616960 | 0.064364 | 0.179267 |
| VWO | KRW | 2010-01-04 | 2026-05-18 | 0.063934 | 0.420605 | -0.284592 | 0.224653 | 0.191175 |
| EWY | KRW | 2010-01-04 | 2026-05-18 | 0.115503 | 0.592878 | -0.400093 | 0.288691 | 0.229064 |
| EWJ | KRW | 2010-01-04 | 2026-05-18 | 0.087056 | 0.554159 | -0.257511 | 0.338069 | 0.180262 |
| EWZ | KRW | 2010-01-04 | 2026-05-18 | 0.012634 | 0.199586 | -0.726212 | 0.017397 | 0.316992 |
| MCHI | KRW | 2011-03-31 | 2026-05-18 | 0.046193 | 0.304966 | -0.528305 | 0.087435 | 0.252621 |

## Benchmark Portfolios

| name | currency | start_date | end_date | cagr | sharpe | max_drawdown | calmar | annualized_volatility |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 60_40_SPY_IEF | USD | 2010-01-04 | 2026-05-18 | 0.098911 | 1.000506 | -0.210175 | 0.470611 | 0.099375 |
| P08_PROXY_SPY29_QQQ21_IEF50 | USD | 2010-01-04 | 2026-05-18 | 0.098182 | 1.092189 | -0.226831 | 0.432840 | 0.089574 |
| 60_40_SPY_IEF | KRW | 2010-01-04 | 2026-05-18 | 0.115877 | 0.977589 | -0.148817 | 0.778657 | 0.119677 |
| P08_PROXY_SPY29_QQQ21_IEF50 | KRW | 2010-01-04 | 2026-05-18 | 0.115137 | 1.014189 | -0.150371 | 0.765688 | 0.114054 |
| P08_IEF30_AVAILABLE | KRW | 2010-01-04 | 2026-05-18 | 0.154328 | 1.109627 | -0.234285 | 0.658721 | 0.134073 |

## COVID Stress Window, USD

| name | asset_type | total_return | max_drawdown | sharpe | status |
| --- | --- | --- | --- | --- | --- |
| SPY | ETF_BUYHOLD | -0.200094 | -0.337173 | -1.711793 | measured |
| QQQ | ETF_BUYHOLD | -0.141984 | -0.285594 | -1.065398 | measured |
| IWM | ETF_BUYHOLD | -0.292123 | -0.408210 | -2.629629 | measured |
| IEF | ETF_BUYHOLD | 0.068857 | -0.046757 | 2.812931 | measured |
| TLT | ETF_BUYHOLD | 0.135176 | -0.157276 | 1.973400 | measured |
| SHY | ETF_BUYHOLD | 0.021617 | -0.006461 | 4.980822 | measured |
| GLD | ETF_BUYHOLD | -0.002089 | -0.125277 | 0.101124 | measured |
| UUP | ETF_BUYHOLD | 0.015903 | -0.048416 | 0.638179 | measured |
| DBC | ETF_BUYHOLD | -0.213836 | -0.273154 | -4.175436 | measured |
| VWO | ETF_BUYHOLD | -0.205563 | -0.311598 | -1.897200 | measured |
| EWY | ETF_BUYHOLD | -0.199044 | -0.380445 | -1.335243 | measured |
| EWJ | ETF_BUYHOLD | -0.151229 | -0.280266 | -1.943060 | measured |
| EWZ | ETF_BUYHOLD | -0.469728 | -0.537230 | -2.530277 | measured |
| MCHI | ETF_BUYHOLD | -0.061014 | -0.204013 | -0.517298 | measured |
| 60_40_SPY_IEF | BENCHMARK_PORTFOLIO | -0.091364 | -0.191325 | -1.396520 | measured |
| P08_PROXY_SPY29_QQQ21_IEF50 | BENCHMARK_PORTFOLIO | -0.050167 | -0.136547 | -0.918653 | measured |

## Tax / Cost Note

This baseline is gross only. Future taxable strategy tests should use the T-family default assumptions: HIFO, KRW 2.5M annual exemption, 22% capital-gains tax, 0.25% round-trip trading cost, 10 bps FX cost, and 15% dividend withholding.

## Proceed Decision

X-ETF001-004 may proceed only if the research director accepts this data audit and keeps all results inside X-Lab quarantine.
