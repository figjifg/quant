# W001 v2 Re-A0 Gate Spec

Date: 2026-05-22
Status: **DEFINITION-ONLY**. Re-A0 실행 = W001 v2 repair 완료 + 사용자 명시 결정 후
Origin: Referee Round 3 final lock
Phase: Round 4 → Re-A0 → (조건부) Round 5

## Purpose

W001 v2 infrastructure repair 완료 후 **34 defects 의 close / reduce /
잔존 status 를 재평가**하는 gate spec.

Re-A0 = Round 3 의 5 A0 audit 을 W001 v2 결과로 재실행. 새 audit 아님.

## Pass Criteria

Re-A0 의 각 audit 별 pass criteria = Round 3 audit 의 kill gate 가 close
되는지 + 새 issue 가 발견되지 않는지.

### Re-A0 G5 (Adjusted OHLC / Corporate Action) — Pass Criteria

| Kill gate | Pass criteria |
|---|---|
| Official corporate action source 확보 불가 | S2 acquired + event_log loaded |
| Adjusted OHLC 가 raw alias 로 남아 있음 | `adjusted_close != 종가` for at least one corporate action day |
| Extreme discontinuity 상당수가 설명 불가 | abs(adjusted_daily_return) > 50% events < 10 (current 147) + remaining events 모두 event_log 에 매칭 |
| Adjustment factor chain 재현 불가 | Sample 5-10 ticker 의 cumulative factor reconstruct + validation |
| Delisted / merged / renamed names 누락 | 1B audit 결과 + S4 fallback 완료 시 100% mapping |
| Repair 후에도 다수 abs(adjusted daily return) > 50% 잔존 | < 10 events |

→ **All pass = G5 verdict = PASS** (vs Round 3 FAIL)

### Re-A0 ID Lifecycle — Pass Criteria

| Kill gate | Pass criteria |
|---|---|
| Permanent ID 또는 reliable lifecycle mapping 생성 불가 | C4 + S4 = 100% mapping (94% DART + 6% fallback) |
| Disappeared stocks 의 terminal event 설명 불가 | C6 + S3 = 모든 258 disappeared 의 reason 분류 |
| Delisted names 가 panel 에서 cash-like 처리됨 | C6 결과 + tradable_state = `delisting_transition` 분류 |
| Code reuse / reappearance 구분 불가 | C6 결과 = 307 reappeared 의 cause 분류 (resume vs reuse) |
| Dynamic_top100 이 survivor-only universe 에서 생성됨 | (Round 3 이미 NO, 변경 X) |

→ **All pass = ID Lifecycle verdict = PASS** (vs Round 3 PARTIAL)

### Re-A0 Tradability Semantics — Pass Criteria

| Kill gate | Pass criteria |
|---|---|
| Tradability flag 가 exchange status 가 아니라 panel presence proxy | C5 `tradable_state` 9-cause categorical 구현 + 각 state nonzero count |
| Missingness 와 true suspension 구분 불가 | C5 결과 = `data_missing` vs `true_suspension` 분리 |
| Official status source 확보 불가 | S3 acquired + C6 module |
| Limit lock / executable status 판단 불가 | C5 결과 = `limit_lock_up` / `down` 명시 + corporate_action_day 분리 |
| Delisted / suspended names 누락 | (Round 3 이미 NO, 변경 X) |

→ **All pass = Tradability verdict = PASS** (vs Round 3 FAIL)

### Re-A0 Top100 PIT — Pass Criteria

| Kill gate | Pass criteria |
|---|---|
| dynamic_top100 재현 불가 | (Round 3 이미 PASS, 100% reproducible) |
| Generation rule undocumented | (Round 3 이미 reverse-engineered, S5 closed) |
| Universe survivor-only | (Round 3 이미 NO) |
| Delisted / merged historical members absent | (Round 3 이미 보존됨) |
| Market cap / trading value non-PIT | (Round 3 이미 PASS, 0% estimated) |
| Top100 membership 이 깨진 adjusted OHLC 에 의존 | C1 adjusted close 사용 시 trading value 재계산 = 5/100 sample dates re-test 100% match |

→ **All pass = Top100 verdict = FULL PASS** (vs Round 3 CONDITIONAL PARTIAL)

### Re-A0 Flow Lineage — Pass Criteria

| Kill gate | Pass criteria |
|---|---|
| Positive sign 검증 불가 | C7 + S6 = vendor doc + KRX reconciliation > 95% |
| Unit 불일치 | (Round 3 이미 PASS) |
| Timestamp / publication timing unknown | C7 + S6 = publication lag 명시 (예: T 종가 후 18:00 KST 사용 가능) |
| Official KRX sample mismatch material | C7 + S6 = 100 sample reconciliation > 95% |
| Missingness 가 failed / suspended names 에 집중 | (Round 3 이미 NaN = 0) |
| 100% estimated 처리 | Estimation method vendor doc + KRX reconciliation 결과 |

→ **All pass = Flow verdict = PASS** (vs Round 3 PARTIAL FAIL)

## Defect Closure Status Table (Re-A0 후 예상)

| Round 3 Defect | Pass criteria | Re-A0 후 status |
|---|---|---|
| G5_000001 (adjusted missing) | C1 acquired | CLOSED |
| G5_000002 (alias only) | C1 + C2 implemented | CLOSED |
| G5_000003 (metadata only) | C2 implemented | CLOSED |
| G5_000004 (147 unexplained) | C3 event log matching | CLOSED if all 147 matched |
| G5_000005 (event source missing) | S2 + C3 acquired | CLOSED |
| G5_000006 (factor chain unreproducible) | C2 + C3 | CLOSED |
| G5_000007 (delisted excluded — 1B overlap) | C6 cross-reference | CLOSED |
| ID_000001 (uniqueness) | (Round 3 PASS) | CLOSED (no change) |
| ID_000002 (disappeared terminal) | C6 + S3 | CLOSED |
| ID_000003 (code reuse) | C6 + S3 | CLOSED |
| ID_000004 (name change) | C4 history table | CLOSED |
| ID_000005 (permanent ID 6% miss) | C4 + S4 | CLOSED |
| ID_000006 (within-DART linkage) | (Round 3 PASS) | CLOSED (no change) |
| ID_000007 (top100 lifecycle coverage) | (Round 3 PASS) | CLOSED (no change) |
| TRAD_000001 (panel proxy) | C5 implemented | CLOSED |
| TRAD_000002 (true suspension) | C5 + C6 + S3 | CLOSED |
| TRAD_000003 (limit pollution) | C5 corporate_action_day 분리 | CLOSED |
| TRAD_000004 (zero-volume conflation) | C5 4-cause categorical | CLOSED |
| TRAD_000005 (delisting transition) | C5 + C6 | CLOSED |
| TRAD_000006 (limit threshold) | (Round 3 PASS) | CLOSED (no change) |
| TOP_000001 (script missing) | Documentation 추가 | CLOSED |
| TOP_000002-005 (positive findings) | (Round 3 PASS) | CLOSED (no change) |
| TOP_000006 (Gate 5 dependency) | C1 → Top100 재계산 | CLOSED |
| FLOW_000001 (field doc) | C7 + S6 | CLOSED |
| FLOW_000002 (sign) | C7 reconciliation | CLOSED |
| FLOW_000003 (unit) | (Round 3 PASS) | CLOSED (no change) |
| FLOW_000004 (publication lag) | C7 + S6 | CLOSED |
| FLOW_000005 (missingness) | (Round 3 PASS) | CLOSED (no change) |
| FLOW_000006 (nontradable nonzero) | C5 + C7 cross-reference | CLOSED |
| FLOW_000007 (100% estimated CRITICAL) | C7 + S6 | CLOSED if reconciliation > 95% |
| FLOW_000008 (F-family warning) | (Round 3 PASS) | CLOSED (no change) |

→ **All 34 defects can close** if 7 components 모두 implemented + 4
mandatory sources (S1/S2/S3/S6) acquired + S4 fallback completed.

## Partial Pass Scenarios

만약 일부 source 만 acquired:

| Source acquired | Re-A0 result |
|---|---|
| S1 + S2 only | G5 PASS, Top100 FULL PASS. Others 영향 X. |
| S3 only | Tradability PASS. G5 / Top100 / Flow 영향 X. |
| S6 only | Flow PASS. Others 영향 X. |
| S4 only | ID Lifecycle FULL PASS. Others 영향 X. |
| S1 + S2 + S3 | G5, Top100, Tradability PASS. Flow 잔존. |
| S1 + S2 + S6 | G5, Top100, Flow PASS. Tradability 잔존. |
| ALL S1/S2/S3/S6 (mandatory) | 4 audits PASS, ID Lifecycle PARTIAL (S4 미완) |
| ALL S1/S2/S3/S4/S6 | 5 audits FULL PASS |

## Re-A0 Trigger Threshold

Referee 가 Re-A0 진행 승인하는 minimum threshold (제안, Referee 최종 결정
필요):

**Option A — Strict (recommended)**: ALL S1+S2+S3+S6 mandatory sources
acquired + W001 v2 7 components 모두 implemented. → 5 audits 모두 PASS or
PARTIAL.

**Option B — Phased**: S1+S2 만 acquired + C1+C2+C3 implemented → G5 / Top100
re-A0 만 실행. 나머지 audits 는 별도 phase.

**Option C — Permissive**: 어느 single component 라도 complete 시 partial
re-A0 가능. (Referee 권장 X — 부분 진행이 false sense of progress 만들 수
있음)

→ Round 4 → Round 5 transition 전 Referee 가 Option 선택.

## Re-A0 Execution Sequence

Re-A0 진행 시 (Round 3 audit 와 동일 sequence):

```
Re-A0 1A: KR-G5-ADJOHLC-CORPACT-AUDIT-001 (재실행)
Re-A0 1B: KR-ID-LIFECYCLE-MASTER-AUDIT-001 (재실행)
Re-A0 2:  KR-TRADABILITY-SEMANTICS-AUDIT-001 (재실행)
Re-A0 3:  KR-TOP100-PIT-LINEAGE-AUDIT-001 (재실행)
Re-A0 4:  KR-FLOW-UNIT-TIMESTAMP-AUDIT-001 (재실행)

Each re-audit:
- Round 3 의 같은 audit workflow 적용
- W001 v2 의 새 column / module 사용
- 새 defect ledger 생성 (Round 3 defect 와 separate)
- Pass/fail determination per kill gate
- Referee 보고용 summary
```

## Required Round 4 → Re-A0 Artifacts (future, when triggered)

Re-A0 실행 시 (Round 4 종료 후):
- `reports/experiments/round4_reA0/KR_*_AUDIT_002/defect_ledger.csv` (5 카드 재audit)
- `reports/experiments/round4_reA0/round4_reA0_summary.md`
- `reports/experiments/round4_reA0/defect_closure_register.csv` (Round 3 34 defects 의 close / reduce / 잔존 status)
- Referee Re-A0 verdict lock document

## Round 4 본 phase 의 scope (이번)

Round 4 본 phase = **Definition only**.

작성 완료:
- ✅ `docs/round3_final_referee_lock.md`
- ✅ `docs/round3_missing_source_register.md` (priority 갱신)
- ✅ `docs/W001_v2_infrastructure_repair_plan.md` (7 components requirements)
- ✅ `docs/W001_v2_reA0_gate_spec.md` (이 파일, re-A0 gate criteria)

추가 작업 (사용자 host + code work) = **사용자 명시 결정 후만**.

## Forbidden (Re-A0 lock)

- Re-A0 진행 전 또는 도중 performance test 시도
- Re-A0 결과를 alpha edge 로 해석
- Partial repair 로 strategy round 진입 (Round 5 도 Referee 재승인 후)
- 34 defects 일부만 "closed" 마크 후 strategy 진행
- Production / paper / P08 / live readiness / shadow 연결

## Related

- `docs/round3_final_referee_lock.md`
- `docs/W001_v2_infrastructure_repair_plan.md`
- `docs/round3_missing_source_register.md`
- `docs/round3_defect_ledger_schema.md`
- `reports/experiments/round3_aggregate/round3_defect_summary.md`
- Per-card Round 3 defect ledgers
