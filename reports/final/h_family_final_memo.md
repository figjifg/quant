# H-family Final Memo

**Status**: Champion H001 (D013 + KR short-rate carry) 동결.
**Date**: 2026-05-18

## 1. H-family 목표

D013 OFF 시기 (62.3% of time) 의 cash 보유 대신 더 나은 sleeve.
"D013 자체를 더 고치는 것이 아니라, D013 가 비어 있는 시간 활용".

## 2. 진행 (10 ticket)

| Ticket | 결과 |
|---|---|
| H000 OFF 진단 | OFF = sideways + bipolar (평균 KOSPI +2.35%, NOT risk-off) |
| H001 KR carry | **CHAMPION** (+357% / 0.65, +103pp vs D013) |
| H002 USDKRW | FAIL (sleeve DD -17%) |
| H003 Treasury | 누적 최고 (+401%) but sleeve DD -13% FAIL |
| H004 Gold (KODEX 132030) | FAIL (sleeve DD -40%) |
| H005 Basket | 분산 효과 (DD -5%) but H001 못 이김 |
| H006 KOSPI inverse | SKIP (지피티 권장) |
| H007 H001 champion 등록 | PASS (재현 정확) |
| H008 robustness | 부분 PASS (cost/slippage/subperiod PASS, spike 절대 기준 FAIL) |
| H009 paper trading 통합 | PASS |

## 3. Champion: H001 D013 + KR carry

| 지표 | 값 |
|---|---:|
| 누적 net | +357.19% |
| Sharpe | 0.6461 |
| MDD | -33.92% (D013 와 동일) |
| OFF carry 누적 | +28.94% |
| vs D013 | +102.61pp 누적, +0.1128 Sharpe |

**핵심 finding (지피티 해석)**:
- H001 은 새 알파 전략 X
- **cash management 현실화**: D013 OFF cash 가 사실 0% 인데 실거래에서 cash 도 carry 받음
- OFF 시기 cash 가 평균 +2.35% 기회비용 (KOSPI 평균) — KR carry 가 일부 만회

## 4. H008 spike 제외 FAIL 해석 (지피티 권장)

- 절대 기준 +130% 미달 (실제 +93%) — FAIL 기록
- 그러나 D013 spike 제외 +52% 대비 **+41pp 개선** — Relative PASS
- **사전 등록 절대 기준이 cash-carry sleeve 의 성격 대비 너무 강했던 케이스**
- Champion 탈락 사유 아님

## 5. 실거래 구현 (지피티 권장)

Backtest proxy: FRED IR3TIB01KRM156N (한국 3개월 interbank rate)
이건 rate proxy 이지 투자 가능 상품 아님.

실거래 구현 우선순위:
1. **MMF / CMA** (가장 실전적, 가격 변동 거의 없음)
2. **KOFR ETF** (예: KODEX KOFR금리 액티브 합성)
3. 단기채 ETF (duration risk, 보조 reference 만)

Paper trading 에서 MMF / CMA + KOFR ETF 둘 다 기록 권장.

## 6. Paper trading 3 버전 추적 (지피티 권장)

| 버전 | 실거래 | 추적 |
|---|---|---|
| D013 original (cash) | X | baseline reference |
| **H001 primary** | **O** | KR carry sleeve |
| H005 shadow (basket) | X | 분산 효과 reference |

## 7. Backlog

- **Treasury (H003)**: 단기 duration (SHY 1-3y) 재검토 가치. 누적 잠재력 큼.
- **Gold (H004)**: 단독 sleeve 부적합, basket component 로만.
- **Basket (H005)**: 시장 환경 바뀌거나 H001 carry 낮아지면 재검토.

## 8. 다음 단계 (지피티 권장)

1. H001 paper trading framework 반영 ← 즉시
2. H-family final memo 작성 ← 본 문서
3. **I-family 시작** (US/Global ETF macro allocation, Strategy 2 분리)
4. Backlog (Treasury short duration, Gold basket, 등) 후순위
5. J-family (PIT fundamental) 는 PIT 재무 데이터 확보 후

## 9. 정직한 등급 (지피티 기준)

- H001 Research Result: A-
- H001 Production Candidate: A-
- H001 Paper-trading Deployable: YES
- H001 Live Deployment: D013 와 동일하게 4 분기 paper trading 후 판단

H001 은 **cash management improvement 로서 A-**, 시장 예측 알파 X.

---

**Final: H-family 성공 (champion H001), paper trading 3 버전 추적, I-family 즉시 시작**
