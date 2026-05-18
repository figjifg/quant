# Paper Trading Operations

D013 / H001 paper trading 실거래 framework.

## 디렉토리

- signals/YYYY-Q.json — 분기별 D013 신호 + H001 OFF sleeve 정보 (사전 등록, 수정 금지)
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
- regime_off_sleeve, kr_rate_source, estimated_quarter_carry 기록

### 2. 다음 거래일 (T+1) 실행

- regime_on = true: 이전 분기 보유 종목 매도 후 signals/YYYY-Q.json 의 5 종목 each 20% 매수
- regime_on = false: 주식 신규 매수 없이 H001 OFF sleeve 보유
- OFF sleeve carry asset: MMF / 단기채 ETF / 정기예금 / 한국 국채 단기물 중 사전 선택
- 체결가 = 시가 (또는 VWAP/TWAP 사전 선택); OFF sleeve는 해당 상품의 실행 가능 가격/금리 사용
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
- H001 KR carry contribution: estimated_quarter_carry vs 실제 carry
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
- D013 regime OFF 시 H001 KR short-rate carry sleeve 보유
- D013 original cash baseline도 가상 추적하여 4 분기 후 H001 carrier와 비교
- AUM 단계 docs/aum_progression.md 준수
