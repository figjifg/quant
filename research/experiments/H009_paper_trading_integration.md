# H009 — Paper trading framework H001 통합

## 상태
계획됨

## 이게 무슨 ticket 인가

H001 champion 확정 후 paper trading framework 통합. 매 분기 신호 산출
시 OFF sleeve (KR carry) 도 자동 적용.

## 통합 작업

### A. quarterly_signal_generator.py update
- D013 신호 (regime ON/OFF) 산출
- OFF 시 sleeve = KR 단기금리 carry 사용 명시
- signals/YYYY-Q.json 에 sleeve 정보 추가:
  - regime_off_sleeve: "KR_short_rate_carry"
  - kr_rate_source: "FRED IR3TIB01KRM156N"
  - estimated_quarter_carry: 분기 carry 추정값

### B. paper_trading/README.md update
- 분기 운영 절차에 KR carry sleeve 적용 명시
- D013 OFF 분기 = MMF / 단기채 ETF / 한국 국채 단기 / 정기예금 등 carry asset 보유
- 사용자 가이드: OFF 분기에 KRW cash 대신 carry asset

### C. docs/production_rulebook.md update (또는 새 docs)
- OFF sleeve 운영 룰 명시
- carry asset 선택 옵션 (정기예금 vs MMF vs 단기채 ETF)
- 분기 carry 추정 + 실제 carry 차이 추적

### D. evaluations template update
- 분기 evaluations 에 KR carry contribution 항목 추가

### E. D013 + H001 paper trading parallel (지피티 권장)
- D013 original (cash) paper trading
- D013 + H001 KR carry paper trading
- 4 분기 후 비교

## 사전 등록 (production decision)

- Paper trading 시 H001 carrier 우선 사용 (4 분기 후 평가)
- 동시에 D013 original (cash) 도 가상 추적 (비교 baseline)
- 4 분기 후 H001 paper trading PASS 시 → Pilot 1 (≤ 10억) 진입 carrier = H001

## 산출물

- scripts/quarterly_signal_generator.py update (sleeve 정보 추가)
- paper_trading/README.md update
- docs/production_rulebook.md update (또는 새 docs/h001_operations.md)
- evaluations template update

## 엄격 제약

- 새 backtest 없음 (framework update 만)
- D013 strategy 미수정
- H001 strategy 미수정
- 기존 모든 결과 byte-identical
- 사전 등록 carrier (H001) 명시 후 변경 X
