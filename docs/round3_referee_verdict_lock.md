# Round 3 Referee Verdict Lock

Date: 2026-05-22
Cycle: First Bull/Bear/Referee multi-LLM cycle · **Round 3**
Step: 3 (Referee lock after Bull Round 3 + Bear refutation)
Status: LOCKED

## Scope of Round 3

Round 3 = **새 alpha 탐색 라운드 아님**.

Round 3 = **Gate-5-aware infrastructure A0 audit queue**.

한국 stock-level research stack 이 다시 성과 진단을 해도 되는 상태인지 확인.

## Hard Locks (전체 Round 3 적용)

- No performance tests
- No bounded diagnostic tests
- No deep validation
- No paper candidate language
- No production candidate language
- No P08 / paper tracking / live readiness connection

현재 adjusted OHLC / corporate action layer 가 깨져 있는 상태이므로 다음을
signal 또는 outcome 으로 사용하는 작업 **전부 금지**:
- raw return
- price jump
- turnover spike
- migration return
- resume return
- reversal return
- post-event drift

## Round 3 Decision Table

| Strategy ID | Decision | Priority | 허용 범위 |
|---|---|---|---|
| KR-G5-ADJOHLC-CORPACT-AUDIT-001 | A0 AUDIT | **1A** | adjusted OHLC / corporate action repair audit only |
| KR-ID-LIFECYCLE-MASTER-AUDIT-001 | A0 AUDIT | **1B** | permanent ID / delisting / merge / rename audit only |
| KR-TRADABILITY-SEMANTICS-AUDIT-001 | A0 AUDIT | 2 | tradability flag semantics audit only |
| KR-TOP100-PIT-LINEAGE-AUDIT-001 | A0 AUDIT | 3 | dynamic_top100 universe lineage audit only |
| KR-FLOW-UNIT-TIMESTAMP-AUDIT-001 | A0 AUDIT | 4 / lowest | flow data lineage audit only; no flow strategy test |

**Final Round 3 state**:
- A0 AUDIT: **5**
- BOUNDED DIAGNOSTIC TEST: 0
- DEEP VALIDATION: 0
- BACKLOG: conditional only if required official source missing
- REJECT (original cards): 0
- Performance test authorized: **0**

## Sequencing Lock (Bear 권고 채택)

```
Priority 1A + 1B  병렬 시작
  KR-G5-ADJOHLC-CORPACT-AUDIT-001
  KR-ID-LIFECYCLE-MASTER-AUDIT-001
        ↓
Priority 2
  KR-TRADABILITY-SEMANTICS-AUDIT-001
        ↓
Priority 3
  KR-TOP100-PIT-LINEAGE-AUDIT-001
        ↓
Priority 4
  KR-FLOW-UNIT-TIMESTAMP-AUDIT-001
```

이유 (Referee 명시):
- G5 + ID lifecycle 분리 불가. adjusted OHLC repair 는 issuer identity /
  delisting / merger / split / relisting / ticker rename lifecycle 이 깨져
  있으면 신뢰 X.
- 가격 조정 복구 후 → tradability semantics. 둘 다 통과해야 execution
  simulation 신뢰 가능.
- 그 후 → top100 universe PIT.
- 마지막 → flow. F-family overlap 가장 큼.

## Global Non-Negotiable Rule (Round 3 전체)

> 이 라운드에서는 어떤 카드도 성과 수익률, Sharpe, CAGR, hit rate,
> post-event drift, migration return, turnover return, resume return,
> reversal return, flow-return diagnostic 을 outcome 으로 보지 않는다.
> 모든 output 은 defect ledger, reconciliation rate, pass/fail status,
> missing-source list, repair feasibility report 로 제한한다.

명시적 금지:

| 금지 항목 | 상태 |
|---|---|
| raw return 을 signal 로 사용 | 금지 |
| raw return 을 outcome 으로 사용 | 금지 |
| adjusted OHLC repair 전 return-based diagnostic 재개 | 금지 |
| tradability semantics 확인 전 entry/exit simulation 재개 | 금지 |
| top100 lineage 확인 전 migration/turnover universe strategy 재개 | 금지 |
| flow timestamp 확인 전 t+1 flow signal 사용 | 금지 |
| lifecycle mapping 없이 delisted/merged/suspended names 제거 | 금지 |
| audit 통과 가능성 = strategy edge 가능성 해석 | 금지 |
| P08 / production / paper / live readiness 연결 | 금지 |

## Allowed Outputs (Round 3 전체)

| Output | 허용 |
|---|---|
| defect ledger | ✅ |
| reconciliation rate | ✅ |
| pass / fail status | ✅ |
| missing-source list | ✅ |
| repair feasibility report | ✅ |
| source requirement list | ✅ |

## Forbidden Outputs

| Output | 금지 |
|---|---|
| return table | ❌ |
| NAV | ❌ |
| CAGR / Sharpe / hit rate / alpha / excess return | ❌ |
| MDD as strategy performance | ❌ |
| post-event drift / migration return / turnover return | ❌ |
| resume return / reversal return / flow-return | ❌ |

## Required Round 3 Artifacts (9개)

| # | Artifact | 위치 |
|---|---|---|
| 1 | `round3_referee_verdict_lock.md` (이 파일) | `docs/` |
| 2 | `round3_no_performance_rule.md` | `docs/` |
| 3 | `spec_KR_G5_ADJOHLC_CORPACT_AUDIT_A0.md` | `research/experiments/` |
| 4 | `spec_KR_ID_LIFECYCLE_MASTER_AUDIT_A0.md` | `research/experiments/` |
| 5 | `spec_KR_TRADABILITY_SEMANTICS_AUDIT_A0.md` | `research/experiments/` |
| 6 | `spec_KR_TOP100_PIT_LINEAGE_AUDIT_A0.md` | `research/experiments/` |
| 7 | `spec_KR_FLOW_UNIT_TIMESTAMP_AUDIT_A0.md` | `research/experiments/` |
| 8 | `round3_defect_ledger_schema.md` | `docs/` |
| 9 | `round3_missing_source_register.md` | `docs/` |

## Cycle Position

```
Round 1: Step 1-5 종료 (TEST 0 / BACKLOG 6)
Round 2: Step 1-5 종료 (Option D, TEST 0 / BACKLOG 5 + 1 infra)

Round 3:
✅ Step 1 Bull 5 ideas (infrastructure-focused)
✅ Step 2 Bear refutations
✅ Step 3 Referee lock (5 A0 AUDIT, 0 TEST, 0 REJECT)
🔄 Step 4 Claude executor spec drafting (지금)
⏸  Step 5 audit 실행 (사용자 결정 후)
⏸  Step 6-9 not reached this round (no return diagnostic possible)
```

## Final Referee Lock

```
Round 3 = A0 infrastructure repair queue.
KR-G5-ADJOHLC-CORPACT-AUDIT-001      A0 AUDIT
KR-ID-LIFECYCLE-MASTER-AUDIT-001     A0 AUDIT
KR-TRADABILITY-SEMANTICS-AUDIT-001   A0 AUDIT
KR-TOP100-PIT-LINEAGE-AUDIT-001      A0 AUDIT
KR-FLOW-UNIT-TIMESTAMP-AUDIT-001     A0 AUDIT
Performance tests authorized: 0
Strategy promotions authorized: 0
Production/paper/P08 changes authorized: 0
```

측정층이 복구될 때까지 한국 stock-level alpha research 는 닫힌 상태 유지.

## Related Documents

- `docs/round3_no_performance_rule.md`
- `docs/round3_defect_ledger_schema.md`
- `docs/round3_missing_source_register.md`
- `docs/round2_gate5_fail_lock.md` (Round 3 의 trigger 가 된 Round 2 결과)
- `docs/data_gap_adjusted_ohlc.md` (Round 2 finding, Round 3 spec 의 base)
- `docs/tradability_semantics_audit.md` (Round 2 finding, Round 3 spec 의 base)
- `docs/adjustment_engine_requirements.md` (Round 2 finding)
- 5 spec: `research/experiments/spec_KR_*_AUDIT_A0.md`
