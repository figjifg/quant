# P004 — Paper trading / Forward OOS protocol

## 상태
계획됨

## 이게 무슨 ticket 인가

실거래 forward OOS 는 시간 (분기) 이 필요. P004 = **protocol document
만 작성** + 자동화 script. 실거래 시작 시 사용.

## Protocol 정의

### A. 신호 산출 (분기말 + 1 거래일 전 또는 분기말 당일 장 마감 후)

- D013 strategy 실행
- regime ON/OFF 확인
- ON 이면 universe top 5 종목 추출 + 종목코드 list
- 산출물: `signals/YYYY-Q.json`
  - signal_date, regime_on, composite, 5 tickers, intended weights

### B. 체결 가격 기록

- 매수: 분기말 +1 거래일 시가 (또는 사용자 정한 timing)
- 매도: 이전 분기 보유 종목 매도 (rollover 시점)
- 산출물: `executions/YYYY-Q.json`
  - intended price (이론), actual price (체결), slippage

### C. 분기말 성과 기록

- 보유 기간 동안 portfolio value
- 분기 수익률 (net, cost-after)
- 비교: 이론 (백테스트) vs 실제

### D. 4 분기 누적 후 평가

- 최소 4 분기 (1 년) 관찰
- 실제 Sharpe vs 백테스트 Sharpe
- 실제 MDD vs 백테스트 MDD
- 백테스트 수정 금지 (forward OOS 의 진짜 목적)

### Pass 기준 (실거래 후 평가)
- 4 분기 실제 누적 ≥ 0% (전체 negative 아니어야)
- 실제 vs 백테스트 누적 차이 ≤ 20pp (예: 백테스트 +10% 면 실제 ≥ -10%)
- 실제 vs 백테스트 Sharpe 차이 ≤ 0.20

## 산출물

- src/audit/paper_trading_protocol.py (NEW) — 분기말 신호 산출 + 기록 helper
- scripts/quarterly_signal_generator.py (NEW) — 분기말 1 회 실행
- docs/paper_trading_protocol.md (NEW) — 절차 + checklist
- 향후 signals/, executions/ directory 자동 생성

## 엄격 제약

- 실거래 backtest 없음 (시간 필요)
- D013 strategy 그대로 사용
- engine 미수정
- 기존 모든 결과 byte-identical
- protocol 만 정의 + 자동화 도구 만들기
