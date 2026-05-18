# F001 — Layer 3 neutral baseline (D013 direct + E014, 중립 기준 종목 선택)

## 상태
계획됨

## 이게 무슨 ticket 인가

Layer 3 의 첫 실험 — neutral baseline 재현. 종목 선택을 시총 (또는
거래대금) 기준으로만 함. 이게 다음 ticket (F002+) 의 변수 추가 효과
측정의 baseline.

## Baseline 2 개

### F001-A: D013 direct neutral
- D013 ON 분기에 dynamic top 100 universe 의 시총 top 5
- 기존 D013 와 동일 (즉 D013 자체)
- 결과: +254% / 0.53 / -34% (D013 재현)

### F001-B: E014 neutral
- D013 ON 분기에 RS+Breadth Top 4 sector
- Allocation 2/1/1/1
- 각 sector 내: 시총 top 종목 선택 (중립 기준)
- 기존 E014 와 동일 (즉 E014 자체)
- 결과: +362% / 0.63 / -36% (E014 재현)

## 결정 사항

F001 은 사실 F000 의 재현과 같다 — 새 코드 안 만들고 그냥 D013 / E014
metric 가져와서 Layer 3 baseline 으로 명시. 그러나 명확히:
- F002 부터 Layer 3 score 가 종목 선택을 바꾼다
- F001 baseline 이 변경 측정의 기준

## 산출물

- reports/experiments/F001_layer3_neutral_baseline/
- baseline_summary.csv (D013 direct + E014 metric)
- report.md (baseline 명시)

## 엄격 제약

- 새 strategy code 없음 — D013, E014 metric 가져오기만
- engine, 기존 strategy 미수정
- D001-D015, E003-E015 byte-identical
