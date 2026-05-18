# Final Project Report — Production Ready

**Status**: Research + Validation complete. Paper-trading ready.
**Date**: 2026-05-18

## 1. Executive Summary

외국인 수급 기반 KOSPI 단기 추격 매수 전략. 4-layer 구조 (macro →
sector → stock → risk overlay) 로 51 ticket 알파 연구 + 6 ticket
production validation 진행.

**최종 결과**:
- **D013 = 유일 검증된 production-ready carrier**
- E014 (Layer 2) PIT validation FAIL → 폐기
- Layer 3 (F), Layer 4 (G) null result
- Paper-trading deployable. Live = 4분기 평가 후

## 2. D013 Final Performance

| 항목 | 값 |
|---|---:|
| 누적 net | +254.58% |
| Sharpe | 0.5334 |
| MDD | -33.92% |
| 양의 수익 연도 | 7 / 16 |
| 비용 3x | +207% |
| 비용 5x | +166% |
| 비용 10x | +84% |
| AUM 1000억 까지 | 누적 +250% |

## 3. Validation Results

| Phase | 결과 |
|---|---|
| P001 PIT sector (E014) | FAIL → E014 demoted |
| P001.5 attribution | E014 close, mapping bug 없음 |
| P002 execution (6 시나리오) | 5 PASS (timing robust), 1 FAIL (worst case) |
| P003 cost/slippage/capacity | PASS |
| P004 paper trading protocol | 완성 |
| P005 production constraints | byte-identical (binding 0) |

## 4. Operational Guidelines

### AUM 권장
- 보수적: ≤ 100억 원
- 확장: 300-500억 원
- 상한 stress: 1000억 (max participation 49%, 실거래 리스크)

### 실행
- 분기말 +1 거래일 시가 매수
- 분기마다 1회 신호 산출 (scripts/quarterly_signal_generator.py)
- 5종목 equal weight 20%
- D013 regime OFF 시 cash 보유

### 제약
- 단일 종목 ≤ 25% (자연 충족)
- 상위 2 종목 ≤ 50% (자연 충족)
- 유동성 ≥ 50억 원 (universe 충족)
- 거래정지/관리 종목 → cash fallback

## 5. Important Null Results (Lessons Learned)

### Layer 2 (E014) PIT 실패
- Snapshot sector mapping 으로 +362% → PIT 으로 +147%
- E014 의 알파가 KIS snapshot bias 에 결정적 의존
- 교훈: sector 전략은 PIT membership 없이 production validation 불가

### Layer 3 (F-family)
- 종목 단위 algorithmic ranking 이 시총 top 5 단순 cap-weight 보다 약함
- IC strong + portfolio fail paradox (단기 reversal effect)

### Layer 4 (G-family)
- Slow exposure overlay (60일 vol, 252일 drawdown, 60일 stress) 가 lag
- COVID 같은 급격 충격 못 잡음
- 누적 -48 ~ -155pp 감소, MDD 개선 0-5.65pp

## 6. Next Steps

### 즉시 가능
1. 다음 분기 (2026-Q3) D013 신호 산출 시작
2. Paper trading 시작 (4 분기 = 1년 추적)
3. signals/, executions/ directory 자동 관리

### 4분기 후
- Paper trading 실제 vs 백테스트 비교
- Live deployment 결정 (소액 시작)

### Backlog (Layer 2 PIT rebuild)
- KRX PIT mapping 기반 새 Layer 2 설계 (시간 소요)
- Layer 3 의 Top10/15 portfolio 확장
- 다른 universe (KOSDAQ, 중형주)

---

**Final Verdict: D013 = Production-deployable single-layer macro strategy.
Paper trading 4 분기 후 live deployment.**
