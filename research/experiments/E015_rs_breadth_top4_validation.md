# E015 — RS+Breadth Top 4 검증 (탐색 금지, 마지막 cycle)

## 상태
계획됨

## 이게 무슨 ticket 인가

E014 carrier 의 pass/fail 검증. 지피티 지시: **검증만, 탐색 금지**.

## 허용된 검증 항목

A. E014 결과 재현 sanity
B. 비용 stress: base / 2x / 3x / extra slippage
C. Top-K 주변 안정성: K=3, 4, 5 (안정 여부만, 새 챔피언 채택 X)
D. 시기 분할: D015 패턴 (학습/검증 3 schemes)
E. spike 제외: 2020 / 2025 / 2026 / 2020+2025+2026
F. 연도별 / sector / 종목 / 리밸런싱 기여도
G. D013 & E011 overlap
H. MDD 원인 분석

## 금지 사항 (지피티 강조)

- ❌ Breadth only 또는 RS only 가 더 좋아도 채택 X
- ❌ lookback grid 탐색 (20/60 고정)
- ❌ RS/Breadth 가중치 최적화
- ❌ Allocation rule 변경
- ❌ Top-K 변경 (K=4 고정)
- ❌ 새 변수 추가
- ❌ 새 chamipon cycle 시작

새 finding 나오면 → finding_log.md 에 기록 + Layer 3 이후 backlog only.

## Pass/fail 기준 (사전 등록)

**Pass 조건 (모두 충족)**:
1. 누적 수익 ≥ D013 (+254%)
2. Sharpe ≥ D013 (0.53)
3. MDD ≥ -45% (-34% D013 보다 약간 나빠도 OK)
4. 비용 3x 에서 누적 ≥ D013 3x (+207%) 또는 Sharpe ≥ D013 3x (0.47)
5. spike 제외 (2020+2025+2026) 후에도 D013 spike 제외 (+95%) 보다 우위 또는 동등
6. 상위 1 sector 기여도 < 50%, 상위 1 종목 기여도 < 40%
7. Top-K (K=3,4,5) 모두 Sharpe ≥ 0.40

**Fail 시 fallback**: E011 (Flow+RS+Breadth Top 4) 또는 D013

## 산출물

- reports/experiments/E015_rs_breadth_top4_validation/
- cost_stress_summary.csv
- topk_stability.csv
- subperiod_table.csv
- spike_exclusion.csv
- year_contribution.csv
- sector_contribution.csv
- d013_overlap.csv, e011_overlap.csv
- mdd_attribution.md
- finding_log.md (탐색 중 발견한 것 기록, 채택 X)
- report.md (종합 pass/fail)

## 엄격 제약

- engine, 기존 strategy 미수정
- D001-D015, E003-E014 byte-identical
- E014 carrier 고정 (K=4, allocation 2/1/1/1, RS+Breadth)
- 새 finding 채택 금지 (backlog only)
