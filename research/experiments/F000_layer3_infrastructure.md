# F000 — Layer 3 인프라 + carrier 재현

## 상태
계획됨

## 이게 무슨 ticket 인가

Layer 3 진입. 지피티 권장: **D013 direct + E014 두 carrier 동시 비교**.

F000 = 인프라 확인. 새 변수 코드 만들기 전:
1. 두 carrier 재현 sanity check
2. 종목 단위 데이터 정합성 검증
3. Layer 3 위에서 portfolio 구조 명확화

## 검증 항목

### A. Carrier 재현
- D013 direct (시총 top 5) — D013 정확 재현
- E014 (RS+Breadth Top 4) — E014 정확 재현
- 새 코드 만들지 말고 기존 strategy 호출만

### B. 종목 단위 데이터 정합성
- 종목별 외국인/기관 매매 결측 비율 (분기말 기준)
- 종목별 가격 결측 (거래정지/관리종목)
- 종목별 거래대금 분포 (Layer 3 의 liquidity 변수 기반)
- 종목별 시가총액
- 상장/상폐 처리

### C. 리밸런싱 시점별 후보 종목 수
- D013 ON 분기 별 universe 종목 수 (dynamic top 100)
- 각 sector 별 종목 수 (E014 carrier)
- thin sector 분기 별 처리

### D. Layer 3 portfolio 구조
- D013 direct: top 5 from universe (Layer 3 score 위)
- E014: Top 4 sector × allocation 2/1/1/1 (Layer 3 score within sector)

## 사전 등록 판정

| 결과 | 판정 |
|---|---|
| D013, E014 재현 + 데이터 정합성 OK | PROCEED → F001 baseline |
| 재현 실패 | STOP, 원인 분석 |
| 데이터 결측 큼 | 결측 처리 방식 사전 등록 후 PROCEED |

## 산출물

- reports/experiments/F000_layer3_infrastructure/
- carrier_reproduction.csv (D013, E014 재현 확인)
- stock_data_quality.csv (결측, 분포)
- universe_size_by_quarter.csv
- report.md

## 엄격 제약

- 새 strategy 코드 만들지 말 것 (재현 + 분석만)
- engine, 기존 strategy 미수정
- D001-D015, E003-E015 byte-identical
- research_input_data/ 읽기만
