# E013 — E011 Top 4 시기 분할 + spike + 기여도

## 상태
계획됨

## 이게 무슨 ticket 인가

E011 Top 4 의 시간 견고성 + spike 의존도. D-family 의 D015 패턴 적용.

## 시기 분할 (D015 와 동일 schemes)

| 시기 | 기간 |
|---|---|
| 전체 | 2010-2026 |
| A 학습 | 2015-2020 |
| A 검증 | 2021-2026 |
| B 학습 | 2015-2019 |
| B 검증 | 2020-2026 |
| C 학습 | 2015-2021 |
| C 검증 | 2022-2026 |

## Spike 분석

- 2020 단독 비중
- 2025 단독 비중
- 2026 단독 비중
- 2020+2025+2026 합산
- 그 연도 제외 시 누적

## 기여도 분석

- 상위 1개 연도 기여도
- 상위 1개 sector 기여도
- 상위 3개 리밸런싱 기여도
- D013 와 종목 overlap (Jaccard 분기별)
- D013 ON 인데 E011 다른 종목 보유 분기 수

## 사전 등록 판정

| 결과 | 판정 |
|---|---|
| 3 시기 분할 모두 검증 샤프 ≥ 0.40 | 시기 견고 |
| spike 제외 누적 ≥ D013 spike 제외 (+95%) | spike 의존 낮음 |
| 상위 1개 연도 기여도 < 50% | 균일 |
| 상위 1개 sector 기여도 < 50% | 분산 |
| D013 overlap Jaccard 평균 < 0.5 | 독립 알파 |

## 산출물

- reports/experiments/E013_top4_subperiod_spike/
- subperiod_table.csv
- per_year_breakdown.csv
- spike_year_contribution.csv
- contribution_top1_top3.csv
- d013_overlap_quarterly.csv
- report.md

## 엄격 제약

- engine, 기존 strategy 미수정
- D001-D015, E003-E012 byte-identical
- E011 carrier 재사용, trading window 만 변경 (z-score lookback 은 historical 유지)
