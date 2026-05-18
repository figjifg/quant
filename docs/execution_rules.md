# D013 Execution Rules (Production)

기반: 지피티 권장 + P002 unfavorable fill FAIL mitigation.

## 금지

1. **시장가 (market order) 사용 금지** — 매수 고가 / 매도 저가 위험
2. **장중 급등/급락 추격 체결 금지**
3. **사후 신호 수정 금지** (사전 등록 신호 그대로)
4. **단일 분기 5종목 모두 시장가 동시 체결 금지**

## 권장

1. **체결 timing**: 다음 거래일 시가, 종가, VWAP, TWAP 중 선택 (사전 등록)
2. **참여율 (participation rate) 제한**: 종목당 일평균 거래대금의 ≤ 5%
3. **분할 주문**: AUM 300억 초과 시 의무, 1-3일 분할
4. **체결가 모니터링**: 모델 기준가 vs 실제 체결가 차이 기록
5. **불리한 체결 시 대응**: 차이 > 20 bps → partial fill 또는 다음날 이월

## Implementation shortfall 측정

- IS = (실제 체결 평균가 - 신호 시점 종가) / 신호 시점 종가
- 분기당 평균 IS ≤ 30 bps 목표
- IS > 50 bps 분기 발생 시 운영 review

## 매도 시 (분기 rollover)

- 이전 보유 종목 매도 → 새 종목 매수
- 매도와 매수 same-day 가능 (cash flow neutral)
- 매도 종목이 거래정지 → 다음 거래 가능일 매도

## Cash fallback

- 거래정지 / 관리종목 / 상폐 위험 종목 → 그 종목 매수 X
- 그 비중을 다른 4 종목에 분산 (25% 씩) — 또는 cash 보유
- 사전 등록: cash 보유 (단순)
