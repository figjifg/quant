# D013 Project — Final Summary (Production Ready)

**Status**: Research + Validation 완료. Paper trading 시작 가능.
**Date**: 2026-05-18

## 1. 프로젝트 전체

총 63 ticket (D 19 + E 16 + F 13 + G 3 + P 12).

| Family | Layer | 결과 |
|---|---|---|
| D | 1 macro | **D013 champion** |
| E | 2 sector | E014 prototype → **PIT FAIL → demoted backlog** |
| F | 3 stock | important null result |
| G | 4 risk | important null result |
| P | validation | **D013 paper-trading ready** |

## 2. D013 Final Specification

- 변수: VIX, BAA10Y, USDKRW, DXY, US 10y real, US 2-10y curve, Brent, US breakeven, KR CLI, KR exports
- 5 블록, 60mo z-score, threshold -0.2
- Universe: dynamic top 100
- Selection: 시총 top 5 equal weight 20%
- Rebalance: 분기말 +1 거래일 시가
- D013 OFF 시 cash

## 3. Final Performance

| 항목 | 값 |
|---|---:|
| 누적 net | +254.58% |
| Sharpe | 0.5334 |
| MDD | -33.92% |
| 양의 수익 연도 | 7 / 16 |
| 비용 3x | +207% |
| 비용 5x | +166% |
| 비용 10x | +84% |
| 1000억 capacity | 누적 +250% |

## 4. Validation 결과

| 검증 | 결과 |
|---|---|
| 데이터 누수 (D016) | PASS |
| 임계값 안정 (D017) | -0.25~-0.15 안정 구간 |
| 비용 stress (D018, P003) | 5x 까지 PASS |
| MDD attribution (D019) | COVID 2020-03 23일 급락 |
| Execution timing (P002) | 5/6 PASS (worst case 만 fail) |
| Capacity (P003) | 1000억 stress 통과 |
| Constraints (P005) | byte-identical (binding 0) |
| PIT sector (P001) | E014 fail (D013 영향 없음) |

## 5. 등급

- Research Champion: A
- Production Candidate: A-
- Paper-trading Deployable: **YES**
- Live Deployment: **4 분기 paper trading 후 결정**

## 6. Important Null Results

### Layer 2 E014 PIT FAIL (P001)
- Snapshot +362% → PIT +147%
- KIS snapshot bias 결정적
- Sector 전략 = PIT membership 필수

### Layer 3 F-family
- IC strong + portfolio fail paradox
- 종목 단위 algorithmic ranking < 시총 top 5 단순

### Layer 4 G-family
- Slow overlay (60일/252일/60일) lag
- COVID 같은 급격 충격 못 잡음

## 7. Next Steps (Action Items)

### 즉시
1. **다음 분기 (2026-Q3) D013 신호 산출** — scripts/quarterly_signal_generator.py
2. Paper trading 시작
3. 분기마다 신호 + 체결 기록 (signals/, executions/)

### 4 분기 후
- docs/live_pilot_criteria.md 의 10 criteria 평가
- 통과 시 Pilot 1 시작 (≤ 10억)

### Backlog (후순위)
- E014 PIT-based rebuild (시간 소요)
- Layer 3 Top 10/15 portfolio 확장
- KOSDAQ/중형주 universe
- Intraday execution model

## 8. 운영 가이드

### AUM 단계 (docs/aum_progression.md)
- Paper: 0 / Pilot 1: 10억 / Pilot 2: 30억 / Pilot 3: 100억 / Full: 500억 / Stress: 1000억

### Execution rules (docs/execution_rules.md)
- 시장가 금지
- VWAP/TWAP 또는 분할 주문
- 종목당 participation ≤ 5%
- IS > 50 bps 분기 발생 시 review

### Constraints (production_rulebook.md)
- 단일 종목 ≤ 25%, top 2 ≤ 50%, 유동성 ≥ 50억, 회전율 ≤ 100%, 거래정지 제외

---

**Final**: D013 = production-deployable single-layer macro strategy.
Paper trading 시작 → 4 분기 후 live 결정.
