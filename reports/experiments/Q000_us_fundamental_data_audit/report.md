# Q000 US Fundamental Data Audit

## Verdict

PASS. SEC EDGAR `companyfacts`는 filing date 기준 PIT 게이트를 걸 수 있고, Q-family 품질/가치/주주환원 기초 팩터의 원천 데이터로 사용 가능하다.

## 핵심 결과

- 표본 10종목: AAPL, MSFT, GOOGL, AMZN, META, NVDA, BRK-B, JPM, V, JNJ
- 종목별 `us-gaap` concept 수: 437-917
- 최초 filing date: 2009-07-22
- Tag alias 확장 후 non-dividend 14개 concept coverage: 134/140 (95.7%)
- Dividends 포함 전체 15개 concept coverage: 142/150 (94.7%)
- 15개 concept 중 평균 95% 이상 coverage를 보인 concept: 9/15
- Quarterly filing PIT lag median 범위: 24-38일

## Coverage Matrix

| Concept | Covered | Coverage |
| --- | ---: | ---: |
| Revenue | 10/10 | 100.0% |
| NetIncome | 10/10 | 100.0% |
| OperatingIncome | 10/10 | 100.0% |
| StockholdersEquity | 10/10 | 100.0% |
| Assets | 10/10 | 100.0% |
| CFO | 10/10 | 100.0% |
| Buybacks | 10/10 | 100.0% |
| Cash | 10/10 | 100.0% |
| LongTermDebt | 9/10 | 90.0% |
| TotalLiabilities | 10/10 | 100.0% |
| EPS_Basic | 9/10 | 90.0% |
| EPS_Diluted | 8/10 | 80.0% |
| CapEx | 9/10 | 90.0% |
| Shares | 9/10 | 90.0% |
| Dividends | 8/10 | 80.0% |

## PIT 해석

`companyfacts` 각 fact row의 `filed` 날짜를 사용하면 회계기간 종료일 이후 실제 제출 시점부터만 데이터를 사용할 수 있다. 따라서 Q-family feature builder는 `period_end`가 아니라 `filed`를 availability timestamp로 삼아야 하며, filing date 이전에는 해당 값을 절대 노출하면 안 된다.

## 남은 보강

- JPM 같은 은행, BRK-B 같은 보험/복합 지주, V/MA 같은 결제 네트워크는 일반 제조/기술 기업과 다른 tag가 섞인다. Q001 이후 sector별 alias 보강이 필요하다.
- 현재 10종목 audit은 PIT 가능성 검증이며 survivorship-free universe가 아니다. Survivorship-free universe 구성은 Q001 이후 별도 한계로 명시해야 한다.
- 개별주 universe가 막히면 ETF proxy(`QUAL`, `VLUE`, `MTUM`, `USMV`, `SCHD`, `COWZ`) 대안은 가능하다.

## 산출물

- `coverage_matrix.csv`
- `pit_lag_distribution.csv`
- `concept_aliases_used.csv`
