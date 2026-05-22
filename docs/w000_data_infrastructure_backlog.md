# W000 Data Infrastructure Backlog

Status: production/research infrastructure backlog. This is not a paper
candidate list.

## 우선순위 표

| Priority | 항목 | ROI | 이유 |
|---|---|---|---|
| P0 | Korean total return data | 매우 높음 | 배당 포함 수익률 없이는 장기 비교와 세금/배당 해석이 왜곡됨 |
| P0 | PIT sector membership | 매우 높음 | E014 재발 방지. sector 연구 재개 전 필수 |
| P1 | Execution data | 높음 | spread, volume participation, slippage가 production capacity 판단의 핵심 |
| P1 | Survivorship-safe US universe | 높음 | Q-family direct survivor bias를 줄이는 전제 조건 |
| P2 | DART body parser | 중간 | 자사주 금액, 소각 규모, 배당 금액의 본문 추출 품질 개선 |
| P3 | KRX borrow / short-sale data | 낮음 | W001 v2 prerequisite. 현재 long-short Korean research 자체가 backlog. |

## Korean Total Return Data

- 목표: 배당 포함 adjusted return을 종목/지수 단위로 확보.
- 필요성: price return만 쓰면 배당주와 방어 업종의 성과를 과소평가할 수 있음.
- ROI: 높음. backtest, benchmark, 세금 검토 모두에 직접 영향.
- 완료 조건: raw source, adjustment method, ex-date/payment-date timing policy 문서화.

## DART Body Parser

- 목표: 공시 본문에서 자사주 취득 금액, 소각 규모, 배당 금액을 구조화.
- 필요성: title-only event family의 실패를 반복하지 않기 위함.
- ROI: 중간. 이벤트 연구를 다시 열기 위한 필요조건이지만 즉시 production은 아님.
- 완료 조건: 본문 파싱 coverage, false positive 표본, event timestamp policy.

## PIT Sector Membership

- 목표: 특정 날짜 기준 실제 sector membership을 재현.
- 필요성: E014의 PIT sector fail 재발 방지.
- ROI: 매우 높음. sector momentum/breadth 계열 재개 전 hard gate.
- 완료 조건: effective_date, stale mapping policy, delisting 처리, regression test.

## Survivorship-safe US Universe

- 목표: S&P 500/100 historical membership을 PIT로 구성.
- 필요성: Q-family direct stock universe의 survivor bias를 줄임.
- ROI: 높음. 단, Q-family direct 재개는 별도 ticket 필요.
- 완료 조건: membership effective date, identifier mapping, delisted ticker price handling.

## Execution Data

- 목표: spread, volume participation, slippage, partial fill 기록 확보.
- 필요성: paper/live 괴리와 capacity 판단.
- ROI: 높음. production hardening에 직접 사용.
- 완료 조건: broker export schema, timestamp, order type, quote reference, fill discrepancy report.

## KRX Borrow / Short-Sale Data

- 목표: per-date borrowable universe, borrow fee / short rebate, 공매도 제한
  종목 list, 강제 buy-in event 기록.
- 필요성: W001 v2 (Korean long-short residual engine) 의 사전 조건. 현재
  Korean long-short Korean equity research 는 backlog 상태 (X-KR001 closure
  이후).
- ROI: 낮음. 현재 long-short Korean alpha 자체가 backlog 이고, 구조적
  short/borrow 제약 때문에 production 현실성이 낮음.
- 완료 조건: source, 가용 종목/날짜 범위, borrow fee schema, regulatory
  restriction handling.

## Hard Rule

이 backlog 항목은 새 marginal paper candidate가 아니다. 데이터를 확보하더라도
별도 ticket 없이 Q-family direct, sector momentum, event strategy, Korean
long-short residual research 를 재개하지 않는다.
