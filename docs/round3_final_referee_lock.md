# Round 3 Final Referee Lock

Date: 2026-05-22
Cycle: First Bull/Bear/Referee multi-LLM cycle · Round 3 · Step 5 complete
Status: **ROUND 3 CLOSED · LOCKED**
Next: Round 4 = W001 v2 Infrastructure Repair + Re-A0 (NOT a Bull alpha round)

## Round 3 Accepted Result

| Item | Value |
|---|---|
| A0 audits completed | 5 / 5 |
| Total defects | 34 |
| Critical | 6 |
| High | 9 |
| Medium | 6 |
| Low | 3 |
| Informational | 10 |
| Compliance | ✅ no return / NAV / Sharpe / MDD / alpha / P08 connection / spec post-hoc 수정 |

## Card-by-Card Final Lock

### 1. KR-G5-ADJOHLC-CORPACT-AUDIT-001
- **Verdict**: FAIL / **BACKLOG-INFRA**
- Reason: 4 critical Gate 5 defects (adjusted_column_missing, alias-only, 147 unexplained extreme events, event_source_missing)
- Constraint: **No return-based diagnostic allowed**

### 2. KR-ID-LIFECYCLE-MASTER-AUDIT-001
- **Verdict**: PARTIAL / continue repair
- Positive: DART corp_code 94% permanent ID coverage, 0 duplicate (date, ticker) pairs
- Limitation: 6% fallback + lifecycle terminal events 미해결
- Status: Not full pass until repaired

### 3. KR-TRADABILITY-SEMANTICS-AUDIT-001
- **Verdict**: FAIL / **BACKLOG-INFRA**
- Reason: true_suspension distinction requires S3 (KRX status); 2 critical defects 잔존
- Constraint: **No execution simulation allowed**

### 4. KR-TOP100-PIT-LINEAGE-AUDIT-001
- **Verdict**: **CONDITIONAL PARTIAL PASS**
- Positive: Top100 selection rule = 거래대금추정 top 100 (100% reproducible across sample dates); survivor safety strong
- Limitation: Gate 5 dependency (trading value depends on raw close); daily churn ≈ 19.6 new entries / 100 = signal-to-noise warning

### 5. KR-FLOW-UNIT-TIMESTAMP-AUDIT-001
- **Verdict**: PARTIAL FAIL / **BACKLOG-LINEAGE**
- Critical correction: 수급금액추정여부 = 100% True (모든 flow vendor estimated). Round 2 "0% estimated" 는 시가총액 / 거래대금 한정.
- Constraint: **No flow performance diagnostic allowed**

## Current Authorized Status

```
Active strategy TEST                : 0
Bounded diagnostic tests            : 0
Performance tests                   : 0
Production / paper / P08 / live changes : 0
```

## Round 4 Framework (NEXT)

**Round 4 = W001 v2 Infrastructure Repair + Re-A0** (NOT a Bull alpha round)

Round 4 deliverable = infrastructure repair artifacts only, followed by Re-A0.

### Missing source mandatory tier (Referee 명시)

| Source | Tier | Purpose |
|---|---|---|
| **S1** Adjusted OHLC | mandatory | adjusted return enables G5 unblock |
| **S2** Corporate Action Event Log | mandatory | 147 event classification + factor chain |
| **S3** KRX Suspension / Delisting / Managed Status | mandatory | true_suspension distinction (Tradability unblock) |
| **S4** Permanent ID fallback | needed for full lifecycle pass | 6% non-DART fallback |
| **S5** Top100 Rule | **resolved** (reverse-engineered) | external source 불필요 |
| **S6** Flow Vendor Documentation | mandatory for any flow continuation | 100% estimated finding 해결 필요 |

S5 = ✅ resolved. 단 **Top100 Gate 5 dependency open** (trading value 의 raw close 의존성).

## Allowed Round 4 Actions (7개, Referee 명시)

1. ✅ `docs/round3_final_referee_lock.md` (이 파일)
2. ✅ Update `docs/round3_missing_source_register.md` with S1/S2/S3/S4/S6 priority + S5 resolved
3. ✅ Create `docs/W001_v2_infrastructure_repair_plan.md`
4. ✅ Create `docs/W001_v2_reA0_gate_spec.md`
5. ✅ Define requirements for 7 components:
   - real adjusted OHLC / adjusted return
   - corporate action factor chain
   - corporate action event log
   - permanent identifier fallback
   - tradable_state categorical field
   - KRX suspension/resumption reconciliation
   - flow vendor documentation
6. ✅ Preserve all 34 defects in the defect register
7. ✅ Mark S5 Top100 Rule as resolved by reverse-engineered reproducible rule; keep Top100 Gate 5 dependency open

## Hard Prohibitions (Round 3 closed + Round 4 lock)

- ❌ Performance tests
- ❌ NAV / CAGR / Sharpe / hit rate / alpha / excess return / MDD as strategy performance
- ❌ Post-event drift / migration return / turnover return / resume return / reversal return / flow-return results
- ❌ Raw return as signal or outcome
- ❌ Round 2 strategy diagnostic 재시작
- ❌ 147 extreme-return events 제외 후 testing 계속
- ❌ 100% estimated + S6 missing 상태에서 flow data 사용한 strategy testing
- ❌ Production / paper tracking / P08 / live readiness / shadow track 연결

## Cycle 1 Final State

| Round | Active TEST | A0 AUDIT | BACKLOG | REJECT |
|---|---:|---:|---:|---:|
| Round 1 | 0 | 0 | 6 | 0 |
| Round 2 | 0 | 0 | 5 + 1 infra | 0 |
| Round 3 | 0 | 5 (complete) | 0 | 0 |
| **Cycle 1 total** | **0** | **5 complete** | **12** | **0** |

False alpha 차단 framework: **9/9 catches** (Round 2 종료 시점) + 34 data
layer defects 공식 등록 (Round 3).

## Cycle Position

```
Round 1: Step 1-5 종료
Round 2: Step 1-5 종료 Option D
Round 3:
  ✅ Step 1-5 모두 종료 (5 audits complete, 34 defects)
  ✅ Final Referee Lock (이 파일)
Round 4:
  🔄 Infrastructure Repair + Re-A0 (Bull alpha round 아님)
```

## Round 4 → Round 5 Transition (future)

Round 4 의 W001 v2 repair + Re-A0 통과 후:
1. Re-A0 결과 = 34 defects 의 close / reduce / 잔존 status
2. Referee 재승인
3. (조건부) 새 strategy round 또는 기존 BACKLOG 카드 unblock 가능
4. 단 사용자 host 작업 (S1/S2/S3/S6 acquire) 가 prerequisite

## Related Documents

### Round 3 framework
- `docs/round3_referee_verdict_lock.md` (Round 3 verdict)
- `docs/round3_no_performance_rule.md` (forbidden metrics)
- `docs/round3_defect_ledger_schema.md`
- `docs/round3_missing_source_register.md` (updated for Round 4)

### Round 3 audit results
- `reports/experiments/round3_aggregate/round3_defect_summary.md` (34 defects aggregate)
- `reports/experiments/KR_G5_ADJOHLC_CORPACT_AUDIT_001/`
- `reports/experiments/KR_ID_LIFECYCLE_MASTER_AUDIT_001/`
- `reports/experiments/KR_TRADABILITY_SEMANTICS_AUDIT_001/`
- `reports/experiments/KR_TOP100_PIT_LINEAGE_AUDIT_001/`
- `reports/experiments/KR_FLOW_UNIT_TIMESTAMP_AUDIT_001/`

### Round 4 framework
- `docs/W001_v2_infrastructure_repair_plan.md`
- `docs/W001_v2_reA0_gate_spec.md`

### Production track (unaffected)
- `docs/MISSION.md`
- `docs/p08_ief30_frozen_spec.md`
- `x_lab/closed_register.md`
