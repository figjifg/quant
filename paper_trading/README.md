# Paper Trading Operations

D013 paper trading 실거래 framework.

## 디렉토리

- signals/YYYY-Q.json — 분기별 D013 신호 (사전 등록, 수정 금지)
- executions/YYYY-Q.json — 실제 체결 기록
- evaluations/YYYY-Q.md — 분기말 성과 + IS / slippage 보고

## 분기 운영 절차

### 1. 분기말 신호 산출 (분기말 거래일 장 마감 후, T 일)

```bash
.venv/bin/python scripts/quarterly_signal_generator.py \
    --refresh-d013 \
    --quarter YYYY-Q
```

- D013 backtest 재실행 (최신 데이터 반영)
- signals/YYYY-Q.json 자동 생성
- regime_on, composite, top 5 tickers, intended weights

### 2. 다음 거래일 (T+1) 매수 실행

- 매도: 이전 분기 보유 종목 매도 (rollover)
- 매수: signals/YYYY-Q.json 의 5 종목 each 20%
- 체결가 = 시가 (또는 VWAP/TWAP 사전 선택)
- 시장가 금지 (docs/execution_rules.md)

### 3. 체결 기록 (T+1 장 마감 후)

executions/YYYY-Q.json 수동 작성:
```json
{
  "quarter": "YYYY-Q",
  "execution_date": "YYYY-MM-DD",
  "fills": [
    {"ticker": "005930", "intended_weight": 0.2, "actual_weight": 0.2,
     "intended_price": 12345, "actual_price": 12389, "slippage_bps": 35.6},
    ...
  ],
  "cash_fallback_events": [],
  "implementation_shortfall_bps": 28.4
}
```

### 4. 분기 추적 (분기 동안)

- 매 거래일 portfolio value 기록
- 거래정지 / 관리 종목 발생 시 cash fallback
- 분기말 누적 수익 계산

### 5. 분기말 평가 (다음 분기 신호 산출 전)

evaluations/YYYY-Q.md 작성:
- 실제 누적 수익 (1 분기)
- 백테스트 기준 가상 누적 (D013 outputs 참조)
- 차이 (실제 - 백테스트)
- IS 평균
- 평균 slippage
- 사건 (incident) 기록

## 4 분기 누적 평가 → Live pilot 결정

docs/live_pilot_criteria.md 의 10 go/no-go criteria 확인.
통과시 docs/aum_progression.md 의 Pilot 1 단계로 진입.

## Quarter list

| Quarter | Status |
|---|---|
| 2026-Q1 | 신호 산출 완료 (signals/2026-Q1.json) — paper trading 첫 분기 |
| 2026-Q2 | 6월 말 신호 산출 예정 |
| 2026-Q3 | 9월 말 |
| 2026-Q4 | 12월 말 |
| 2027-Q1 | 3월 말 → 4 분기 누적 평가 |

## 주의

- 사후 신호 수정 금지 (사전 등록 신호 그대로)
- 임의 종목 추가/제거 금지
- D013 regime OFF 시 cash 보유 (강제)
- AUM 단계 docs/aum_progression.md 준수
