# Live Pilot Go/No-Go Criteria

Paper trading 4 분기 완료 후 live pilot 진입 결정. **사전 등록 (paper
trading 시작 전 동결)** — 결과 보고 기준 변경 금지.

## Hard criteria (모두 충족)

1. **4 분기 paper trading 완료** (1년)
2. **신호 사전 기록 100%** — 사후 수정 0
3. **체결가 차이**: 실제 vs 모델 기준 차이 평균 ≤ 20 bps
4. **Data pipeline 오류 0** — D013 신호 산출 자동화 정상
5. **Cash fallback 모두 logged + 정상 처리**

## Performance criteria

6. **실제 vs 백테스트 누적 차이 ≤ 20pp**
7. **Implementation shortfall 분기 평균 ≤ 30 bps**
8. **Slippage 평균 ≤ 20 bps** (P003 가정 범위)

## Process criteria

9. **ON 분기 최소 2회** — 성과 판단 표본 충분
10. **OFF 분기 cash 유지 + 다음 신호 대기 정상**

## 통과 처리

10 criteria 모두 통과 → **Pilot 1 시작 (AUM ≤ 10억)**

## Partial 또는 미통과

- 미통과 항목 별 원인 분석
- 4 분기 더 paper trading 연장
- 또는 D013 strategy 점검
- live deployment 보류

## ON 분기 부족 (criterion 9 미충족)

- 4 분기 다 OFF 이면 운영 framework 만 검증, 성과 미평가
- 추가 4 분기 연장 (ON 분기 2회 발생 시까지)
