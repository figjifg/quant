# Q001 Universe Construction

## Verdict

OK. 현재 large-cap 후보 universe 기준으로 SEC `companyfacts` 다운로드를 시도했고, 확보된 파일에 대해서만 coverage audit을 완료했다. 이 universe는 현재 ticker 목록 기반이므로 survivorship-free universe가 아니며 historical backtest universe로 직접 사용하면 안 된다.

## 핵심 결과

- 요청 ticker 수: 100
- companyfacts 확보 ticker 수: 99
- companyfacts 확보율: 99.0%
- audit 성공 ticker 수: 99
- non-dividend 14개 concept coverage: 1370/1386 (98.8%)
- Dividends 포함 전체 15개 concept coverage: 1459/1485 (98.2%)
- 95% 이상 coverage concept 수: 13/15
- filing date 범위: 2009-04-30 ~ 2026-05-19
- sector 분포는 SEC submissions `sicDescription` 기준이며, 시가총액 분포는 가격/주식수 PIT 원천이 없어 이번 산출물에서 제외했다.

## Coverage

| Concept | Covered | Coverage |
| --- | ---: | ---: |
| Revenue | 99/99 | 100.0% |
| NetIncome | 99/99 | 100.0% |
| OperatingIncome | 99/99 | 100.0% |
| StockholdersEquity | 99/99 | 100.0% |
| Assets | 99/99 | 100.0% |
| CFO | 99/99 | 100.0% |
| Buybacks | 96/99 | 97.0% |
| Cash | 99/99 | 100.0% |
| LongTermDebt | 94/99 | 94.9% |
| TotalLiabilities | 99/99 | 100.0% |
| EPS_Basic | 98/99 | 99.0% |
| EPS_Diluted | 97/99 | 98.0% |
| CapEx | 95/99 | 96.0% |
| Shares | 98/99 | 99.0% |
| Dividends | 89/99 | 89.9% |

## 실패 및 제외

- MMC: missing_cik

## 한계

- 현재 S&P 100 유사 ticker list 기반이므로 survivorship bias가 있다. Q-family historical backtest에는 별도 survivorship-free membership, delisting, ticker-change 처리가 필요하다.
- Financial statement fact는 반드시 SEC `filed` 날짜 이후에만 feature로 노출해야 한다. `period_end` 기준 사용은 look-ahead다.
- 이 작업은 universe/data feasibility audit이며 factor grid search나 성과 해석을 수행하지 않았다.

## 다음 단계

Q002 Quality only로 진행 가능하다. 단, Q002도 현재 universe 한계를 report metadata에 명시하고, historical survivorship-free universe가 완성되기 전에는 production/promotion 판단에 쓰지 않는다.

## 산출물

- `universe_list.csv`
- `coverage_matrix.csv`
- `sector_distribution.csv`
- `pit_lag_distribution.csv`
- `concept_aliases_used.csv`
