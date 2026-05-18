# H008 — H001 (D013 + KR carry) robustness validation

## 상태
계획됨

## 이게 무슨 ticket 인가

H007 champion 확정 후 robustness 검증 (지피티 framework). D-family/E-family
패턴 (P-family 같은 production validation) 그대로 적용.

## 검증 항목 (사전 등록)

### A. Cost stress
- base, 2x, 3x, 5x

### B. Slippage stress
- +5, +10, +20 bps

### C. Subperiod / time split
- 2010-2017 vs 2018-2026
- Spike year (2020, 2025) 제외 누적
- 매 연도 별 누적

### D. KR rate carry sensitivity
- 우리 KR rate = FRED IR3TIB01KRM156N (monthly)
- 만약 weekly / daily 데이터로 바꾸면 결과 변화?
- 또는 KR rate 시기별 변화 (저금리 시기 vs 고금리 시기)
- carry contribution 시기별 분해

### E. Asset / year contribution
- 누적 +103pp (H001 vs D013) 중 분기 별 / 연도 별 분해
- 한 연도 / 한 분기 에 집중 의존 여부

## 사전 등록 pass 기준

- 3x cost 누적 ≥ +250%
- 5x cost 누적 ≥ +180%
- +20 bps slippage 누적 ≥ +280%
- Spike 제외 누적 ≥ +130%
- 한 연도 기여 < 50% (분산)
- 한 분기 기여 < 20%

## 산출물

- reports/experiments/H008_h001_robustness/
- cost_stress.csv, slippage_stress.csv, subperiod_breakdown.csv
- carry_contribution_by_year.csv, sleeve_year_decomposition.csv
- report.md (verdict)

## 엄격 제약

- H001 carrier 정의 변경 X
- engine.py 미수정
- 기존 D-G, P, H000-H007 byte-identical
