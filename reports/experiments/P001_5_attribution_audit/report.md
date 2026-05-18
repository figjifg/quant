# P001.5 Attribution Audit

## A. Source Decomposition

- KIS snapshot: cumulative=3.621085, sharpe=0.631187
- KRX current snapshot (2026-05-06): cumulative=4.979884, sharpe=0.699507
- KRX PIT: cumulative=1.468682, sharpe=0.345824
- taxonomy gap, KRX current - KIS: 1.358800
- PIT membership gap, PIT - KRX current: -3.511202
- 해석: KRX current snapshot은 KIS snapshot보다 낮지 않고 오히려 높다. 성과 하락은 taxonomy 교체보다 PIT membership 적용에서 발생한다.

## B. Ticker Attribution

| ticker | name | status | net diff | attribution % |
|---|---|---|---:|---:|
| 000660 |  | snapshot_only | 0.324665 | 5.87% |
| 047040 |  | common | 0.299740 | 5.42% |
| 000720 |  | pit_only | -0.267030 | 4.83% |
| 207940 | 삼성바이오 | snapshot_only | 0.264413 | 4.78% |
| 017670 |  | pit_only | 0.260696 | 4.71% |

## C. Mapping Review

- 명백한 mapping bug 발견: False
- `일반서비스 -> 99 기타`는 YAML의 explicit manual_review에 있는 보수적 선택이며 오타성 버그는 아니다.
- 상세 표: `C_mapping_review.md`, `C_mapping_review_table.csv`.

## D. PIT Score Diagnostics

- Rank IC mean=0.117741, t-stat=2.485017
- Top4-Bottom4 spread=0.066011, t-stat=3.286931
- Selected-Unselected spread=0.058249, t-stat=2.910855
- 해석: PIT 자체의 sector score 진단은 양수이고 t-stat도 양호하다. 포트폴리오 성과 저하는 sector score 전체 실패라기보다 PIT membership이 바꾼 보유 종목/섹터 구성 영향이 크다.

## Verdict

- close: KRX current snapshot is closer to KIS snapshot than PIT, so the main gap is true PIT membership bias.
