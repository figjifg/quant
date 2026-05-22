# KR-FLOW-ABSORPTION-001 — Lineage-Only Audit Spec (Priority 5)

## Status
PRE-REGISTERED · **BACKLOG** · **lineage-only audit only, NO performance diagnostic**
Round 2 Priority: 5
Date: 2026-05-22

## Cycle Lineage

- Round 2 Bull idea #5
- Referee Round 2 lock: **BACKLOG (lineage-only audit only)**
- Bear / Referee 주의 : flow 데이터 사용 시 F-family overlap 매우 큼

## Scope

이 카드는 **performance diagnostic 자체 금지** (이번 사이클 내내).

이번 사이클 허용 = **lineage-only audit**:
- Flow data 의 sign convention / unit / timestamp / missingness 검증
- F-family flow-following 재포장이 아님을 사전 구조로 입증

## Hypothesis (lineage-first)

> "foreign selling + institution absorption + price resilience" joint
> condition 은 흥미롭지만, 먼저 flow 데이터의 정합성 / PIT 가용성 / F-family
> 와의 구조적 차별성을 입증해야 한다.

## Required Global Gates

`docs/round2_global_A0_gates.md` 10 gate 중 적용 가능 항목:
- Gate 1 Permanent ID
- Gate 2 Survivorship
- Gate 5 Adjusted OHLC sanity
- Gate 9 Performance language

Gate 7 (event ledger), Gate 8 (controls), Gate 10 (metric priority) = N/A
(performance diagnostic 자체 금지).

## Allowed Lineage-Only Audit Items

| Audit Item | Allowed |
|---|---|
| `foreign_net_buy_value` sign convention | ✅ |
| `institution_net_buy_value` sign convention | ✅ |
| Flow value 단위 확인 (KRW, 백만 KRW, 십억 KRW 등) | ✅ |
| `trading_value` 대비 flow sanity check (ratio / sign consistency) | ✅ |
| Flow data 공개 시점 확인 (장 마감 후 / 익일 / 익영업일) | ✅ |
| t+1 진입 가능성 확인 | ✅ |
| Missing flow 처리 방식 확인 (0 vs NaN 구분) | ✅ |
| `dynamic_top100` survivor bias 확인 (Gate 2 적용) | ✅ |
| F-only / I-only / resilience-only baseline 정의 | ✅ |

## NOT Allowed (이번 사이클 내내)

| Task | 판정 |
|---|---|
| Return backtest | 금지 |
| Alpha table | 금지 |
| NAV / CAGR / Sharpe / MDD 산출 | 금지 |
| F+I composite 성과 주장 | 금지 |
| Flow-following 과 다르다는 **성과 기반** 주장 | 금지 |

## Unblock Conditions (TEST 승격 조건)

이 카드가 TEST 로 승격하려면 다음 모두 통과:

| Gate | Requirement |
|---|---|
| Sign convention | foreign / institution 순매수 부호 명확 (+ = 매수 / - = 매도) |
| Unit consistency | flow value 와 trading value 단위 일관 (또는 변환 규칙 명시) |
| Timestamp | t 일 flow 가 t+1 진입에 사용 가능한지 확인 (look-ahead 없음) |
| Missingness | missing flow 가 0 으로 오인되지 않음 (NaN 구분) |
| Baseline | F-only / I-only / resilience-only 가 사전 정의됨 |
| Closed-family | 기존 F-family flow-following 재포장이 아님을 **사전 구조로** 입증 |

마지막 gate (closed-family) = 가장 어려움. F-family 와 본 카드 의 **차별
mechanism** 을 데이터 / 구조 수준에서 명시해야 함 (성과 사용 X).

## Kill Gates (Referee 명시)

| Failure | Decision |
|---|---|
| Flow sign convention 불명확 | KILL |
| Flow value / trading value 단위 불일치 | KILL |
| 공개 시점상 t+1 사용 불가 | KILL |
| Flow-only baseline 과 차별화 안 됨 (구조적, 성과 X) | KILL |
| Sign shuffle 후에도 effect 유지 (만약 진행했다면 lineage 외 작업 = protocol violation) | KILL |
| 특정 연도 / 종목 집중 (lineage 기반 식별) | KILL |

## Forbidden (Round 2 lock)

- Performance diagnostic 자체 (return / NAV / Sharpe / CAGR / MDD / portfolio)
- 성과 기반 주장 (F-family 와 다름을 성과로 증명 시도)
- Production / paper / P08 / live readiness 연결
- Sign shuffle 후 performance 측정
- spec 사후 수정 (Bear 재심의 없이)

## Codex Implementation Task

```
Implement KR-FLOW-ABSORPTION-001 lineage-only audit.

DO NOT:
- Run ANY return backtest
- Generate NAV / CAGR / Sharpe / MDD tables
- Claim performance differentiation from F-family
- Build event ledger with performance fields
- Connect to P08 / paper tracking / production
- Modify research_input_data/ files

Tasks (lineage-only):
1. Verify foreign_net_buy_value / institution_net_buy_value sign convention
   (sample 10-20 종목 × 10-20 거래일, vendor doc 대조).
2. Verify flow value unit (KRW exact unit, 변환 규칙 명시).
3. Verify trading_value vs flow value ratio sanity.
4. Verify flow data publication timing (장 마감 후 / 익일).
5. Verify t+1 진입 가능성 (look-ahead 없음).
6. Verify missing flow handling (0 vs NaN 구분).
7. Verify dynamic_top100 PIT (Gate 2).
8. Define F-only / I-only / resilience-only baselines (정의만, 성과 X).
9. Document F-family overlap structural analysis (성과 X, 구조적 차별성만).
10. Save outputs under reports/experiments/KR_FLOW_ABSORPTION_001/.

Required outputs:
- config.yaml (locked scope, lineage-only)
- lineage_audit.md (1-7 항목 보고)
- sign_convention_sample.csv (10-20 x 10-20 sample)
- unit_consistency_check.md
- timestamp_publication_check.md
- missingness_check.md
- baseline_definitions.md (8 번 결과)
- f_family_overlap_structural.md (9 번 결과)
- gate_check.md (적용 가능 gate)
- report.md (lineage-only, NO performance language, NO alpha claim)

CRITICAL: If you find yourself wanting to compute returns or P&L, STOP.
This card is BACKLOG, lineage-only this cycle.
```

## Result Summary

작성 금지.

## Bull/Bear/Referee Review

작성 금지.
