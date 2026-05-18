# Research Phase Summary — Final Report

**Status**: Research phase complete. Production validation pending.
**Date**: 2026-05-18

## 1. Executive Summary

외국인 수급 기반 KOSPI 추격 매수 전략. 4-layer 구조 (macro → sector
→ stock → risk overlay) 로 51 ticket 의 실험 진행.

**최종 결과**:
- Layer 1 champion: **D013** (factor aggregation macro gate, RS+Breadth 10 변수)
- Layer 2 prototype champion: **E014** (D013 + sector RS+Breadth Top 4)
- Layer 3 (stock ranking): **important null result**
- Layer 4 (alpha overlay): **important null result**
- **최종 prototype champion: E014**

## 2. Research Timeline

| Family | Ticket 수 | 결과 |
|---|---:|---|
| D-family (Layer 1 macro) | 19 | D013 champion |
| E-family (Layer 2 sector) | 16 | E014 prototype champion |
| F-family (Layer 3 stock) | 13 | null result |
| G-family (Layer 4 risk) | 3 | null result |
| **총** | **51** | |

## 3. Final Model Specification

### Layer 1: D013 macro gate
- 5 블록 10 변수 (Risk, USD/FX, Rates, Inflation, Growth)
- 변수: VIX, BAA10Y, USDKRW, DXY, US 10y real, US 2-10y curve, Brent, US breakeven, KR CLI, KR exports
- Z-score: 60 months rolling
- 임계값: composite >= -0.2 → ON
- 리밸런싱: 분기

### Layer 2: E014 sector selection (D013 위)
- Score: RS + Breadth (Flow 제거, E012 ablation finding)
- Top-K: 4
- Allocation: 2/1/1/1
- Sector 내 시총 top 종목 선택
- Universe: dynamic top 100

## 4. Performance Summary

| Carrier | 누적 net | Sharpe | MDD | 양의 수익 연도 |
|---|---:|---:|---:|---:|
| D013 (Layer 1 only) | 2.5458 | 0.5334 | -0.3392 | 7 |
| **E014 (Layer 1 + Layer 2)** | **3.6211** | **0.6312** | **-0.3564** | **9** |

E014 vs D013: +108pp 누적, +0.10 샤프, -2pp MDD (E014 slightly worse).

## 5. Robustness

### D013 (D006-D008, D016-D019)
- 윈도우 plateau (48-84mo Sharpe 0.47-0.48)
- 임계값 plateau (0.0 ~ +0.1)
- Subperiod OOS PASS
- 비용 3x +207%
- 데이터 누수 감사 통과
- MDD attribution: COVID 2020-03

### E014 (E015)
- 7 pass 기준 모두 통과
- 비용 3x +299%
- spike 제외 (2020+2025+2026) +129%
- subperiod OOS > IS 모든 schemes
- MDD attribution: 2021-2022 (긴 회복)

## 6. Important Null Results

### Layer 3 (F-family):
- 종목 단위 RS, Flow, Liquidity, alignment, composite 모두 baseline 미달
- **IC strong + portfolio fail** 패턴
- 해석: top 5 집중 long-only 가 IC 의 평균적 순위 관계와 다른 결과
- 한국 시총 top 5 baseline 자체가 강함

### Layer 4 (G-family):
- 변동성 타겟팅, MDD 쿨다운, 스트레스 필터 모두 fail
- Slow indicator (60일, 252일) 가 COVID 못 잡음
- D013 macro gate 와 정보 중복
- 추가 overlay 가 누적 -48 ~ -155pp 감소, MDD 개선 0-5.65pp

## 7. Known Limitations

1. **KIS snapshot sector mapping** (2026-05) — PIT 멤버십 아님
2. **진짜 OOS 없음** — 2010-2026 전체 연구 사용
3. **Execution simulation 부족** — 1일/2일 지연, partial fill 미테스트
4. **MDD -36%** — 실전 감내 큼
5. **Universe = dynamic top 100** — 다른 universe 미테스트

## 8. Production Validation Roadmap

| P-ticket | 내용 |
|---|---|
| P000 (이번) | Research freeze memo |
| P001 | Point-in-time sector membership validation |
| P002 | Execution simulation |
| P003 | 더 강한 cost/slippage/capacity stress |
| P004 | Paper trading / forward OOS |
| P005 | Production risk limits (sector/name cap, liquidity, turnover) |

## 9. Go / No-Go Criteria

E014 production deployment 가능 조건:
1. PIT sector 후 D013 대비 우위 유지
2. Sharpe ≥ 0.55 유지
3. 5x 비용 / 슬리피지 stress 통과
4. 1-2일 체결 지연에서 우위 유지
5. Paper trading 4 분기 이상 관찰 OK
6. MDD 감내 가능 (또는 production risk limit 으로 cap)

---

**Research phase 완료. Production validation 진입.**
