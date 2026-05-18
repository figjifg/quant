# Paper Trading Operations

D013 + H001 KR carry paper trading 실거래 framework.
지피티 권장 3 버전 추적.

## 디렉토리

- signals/YYYY-Q.json — 분기별 D013 신호 (사전 등록, 수정 금지)
- executions/YYYY-Q.json — 실제 체결 기록 (사용자 작성)
- evaluations/YYYY-Q.md — 분기말 성과 + IS / slippage 보고

## 3 버전 추적 (지피티 권장)

| 버전 | 실거래 | 추적 |
|---|---|---|
| D013 original (cash) | X | baseline reference (OFF = cash 0%) |
| **H001 primary** | **O** | OFF = KR short-rate carry sleeve |
| H005 shadow | X | OFF = defensive basket (KR 50 / USD 25 / Treasury 25) |

evaluations/YYYY-Q.md 에 3 버전 모두 기록 권장.

## 분기 운영 절차

### 1. 분기말 신호 산출 (분기말 거래일 장 마감 후, T 일)

```bash
.venv/bin/python scripts/quarterly_signal_generator.py --refresh-d013 --quarter YYYY-Q
```

신호 산출:
- regime_on, top 5 tickers (D013)
- regime_off_sleeve = "KR_short_rate_carry" (H001 champion)
- kr_rate_source = "FRED IR3TIB01KRM156N"
- estimated_quarter_carry (분기 carry 추정값)

### 2. 실거래 체결 (T+1 거래일)

**ON 분기 (regime_on = true)**:
- 매수: signals/YYYY-Q.json 의 5 종목 each 20%
- 시가 매수 (시장가 금지)
- 슬리피지 / participation rate ≤ 5% / VWAP/TWAP 권장

**OFF 분기 (regime_on = false)**:
- KR short-rate carry sleeve 매수
- 1순위: MMF / CMA (가장 실전적)
- 2순위: KOFR ETF (예: KODEX KOFR금리 액티브 합성)
- 3순위 reference: 단기채 ETF

### 3. 체결 기록 (executions/YYYY-Q.json)

```json
{
  "quarter": "YYYY-Q",
  "execution_date": "YYYY-MM-DD",
  "regime_state": "on or off",
  "primary_h001": {
    "fills": [...],
    "implementation_shortfall_bps": ?
  },
  "shadow_d013_original": {
    "off_return": 0.0 (cash) or actual cash carry
  },
  "shadow_h005_basket": {
    "off_returns": {"kr_carry": ?, "usdkrw": ?, "treasury": ?}
  }
}
```

### 4. 분기말 평가 (evaluations/YYYY-Q.md)

3 버전 누적 수익 비교:
- D013 original
- H001 primary
- H005 shadow

OFF 시기:
- KR carry MMF/CMA 실제 수익 vs FRED proxy 차이
- KOFR ETF 실제 수익 vs proxy 차이
- 어느 구현이 가장 가까운가

ON 시기:
- 5 종목 IS / slippage
- Cash fallback 이벤트

### 5. 4 분기 누적 후 평가 → Live pilot 결정

docs/live_pilot_criteria.md 의 10 go/no-go criteria.
3 버전 중 H001 이 primary, H005 가 shadow reference.

Pilot 1 진입 시 carrier = H001 (KR carry sleeve), AUM ≤ 10억 원.

## Quarter list

| Quarter | Status |
|---|---|
| 2026-Q1 | D013 ON, 5 종목 매수 (paper trading 시작) |
| 2026-Q2 | 6월말 신호 산출 예정 (OFF 이면 H001 KR carry sleeve) |
| 2026-Q3 | 9월말 |
| 2026-Q4 | 12월말 |
| 2027-Q1 | 3월말 → 4 분기 누적 평가 |

## 주의

- 사후 신호 수정 금지
- 임의 종목 추가/제거 금지
- D013 regime OFF 시 cash 가 아닌 KR carry sleeve 보유 (H001 champion)
- H005 shadow 는 paper 만 (실거래 X)
- AUM 단계 docs/aum_progression.md 준수
