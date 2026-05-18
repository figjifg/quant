# E010 — E007 spike year + 연도별 + D013 overlap 분석

## 상태
계획됨

## 이게 무슨 ticket 인가

E007 carrier (Flow+RS+Breadth) 가 D013 의 92% (+232% vs +254%) 수준.
정직한 분석:
- spike year 의존도 (D013 의 63% 와 비교)
- 연도별 균일성
- D013 보유 종목과의 overlap (Layer 2 의 독립 가치)

## 분석 항목

### A. 연도별 분해
- 매 연도 별 누적, 샤프, 거래 수
- 양의 수익 연도 수 (D013 7 vs E007)
- 2010-2017 / 2018-2026 subperiod

### B. Spike year 영향
- 2020, 2025, 2026 단독 비중
- 합산 비중
- 그 연도들 제외 시 누적

### C. D013 overlap (지피티 핵심 권장)
- 분기별 D013 보유 5종목 vs E007 보유 5종목 overlap
- 매수 분기 수 비교
- 같은 분기에 D013 ON 인데 E007 OFF (또는 반대) 수
- E007 가 D013 와 같은 종목 보유하는데 다른 수익 나오는지

만약 E007 가 D013 와 거의 같은 종목 보유 → Layer 2 의 독립 가치 작음
만약 매우 다른 종목 → 진짜 Layer 2 알파

## 산출물

- reports/experiments/E010_spike_year_d013_overlap/
- per_year_breakdown.csv
- spike_year_contribution.csv
- d013_overlap_quarterly.csv
- report.md

## 엄격 제약

- 새 backtest 없음 (E007 결과 + D013 결과 분석)
- 기존 strategy / D013 / E003-E009 미수정
- 분석 코드: src/audit/e007_vs_d013_attribution.py
