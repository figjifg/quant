# Round 4 Partial Re-A0 — Referee Lock

Date: 2026-05-22
Status: LOCKED · **Option B (Phased partial Re-A0) APPROVED**
Origin: Referee Round 4 verdict on Source Acquisition + W001 v2 Components report

## Scope (Strictly Locked)

**Approved**: Partial Re-A0 Infrastructure Closure Audit
**NOT approved**:
- strategy TEST
- bounded diagnostic test
- performance diagnostic
- Round 2 strategy restart

Purpose: Round 3 의 34 defects 중 어느 것이 실제로 닫혔는지, 어느 것이
S2/C2/C3 의존으로 잔존하는지 **공식 측정**. 성과 재개 아님.

## Naming Lock

> "Partial Re-A0 pass does not automatically reopen any strategy card."

Partial Re-A0 결과가 좋아도 Referee 재판정 전에는 다음 모두 닫힌 상태 유지:
- KR-LIQ-FRAGILITY-AVOID-001
- KR-TRADABILITY-RESUME-RISK-001
- KR-LIQ-MIGRATION-001
- KR-TURNOVER-ATTENTION-001
- KR-FLOW-ABSORPTION-001

## Source Status Clarification (Referee 정정)

이전 executor report 의 "mandatory sources 4/4 acquired" 표현은 다음으로 변경:

> Phase-1 repair sources acquired or verified.
> S2 corporate action body/event-log source is not yet parser-complete.
> C2/C3 remain deferred.

| Source | 정정된 status |
|---|---|
| S1 Adjusted OHLC | COMPLETE |
| S3 Status Events | COMPLETE, **단 source semantics must be re-audited** (OPENDART pblntf=I vs KRX exchange status 동등성 확인) |
| S4 Listed Master | COMPLETE |
| S6 Official Flow | **SAMPLE VERIFIED, not full final pass** |
| S2 OPENDART Body | **FEASIBILITY VERIFIED only, parser 미완** |

→ **Full G5 pass 불가**. S2/C2/C3 미완 동안 G5 = partial pass with deferred.

## Card-by-Card Allowed Verdict Range

### G5 (KR-G5-ADJOHLC-CORPACT-AUDIT-001)

Allowed:
- FAIL / PARTIAL FAIL / **PARTIAL PASS WITH S2/C3 DEFERRED**

NOT allowed:
- **FULL PASS**

Blockers:
- C2 corp action factor chain 미완
- C3 corp action event log 미완
- S2 body parser 미완
- 잔존 35 event 의 공식 event-log linkage 미완

### ID Lifecycle (KR-ID-LIFECYCLE-MASTER-AUDIT-001)

Allowed:
- PARTIAL PASS / FULL PASS

단 50 fallback 이 단순 ticker-based temporary ID 라면 = PARTIAL PASS only.

### Tradability Semantics (KR-TRADABILITY-SEMANTICS-AUDIT-001)

Allowed:
- PARTIAL PASS / PARTIAL FAIL

NOT allowed:
- FULL PASS (S3 가 공식 exchange status 와 충분히 reconciled 안 되면)

특히 panel_absence 를 "거래 불가" 로 해석하면 안 됨. 다음 구분 필요:
- not_in_dynamic_universe
- listed_but_not_selected
- true_suspension
- delisting_transition
- data_missing
- limit_lock_candidate
- executable

### Top100 PIT Lineage (KR-TOP100-PIT-LINEAGE-AUDIT-001)

Allowed:
- PARTIAL PASS

요구:
- Sample 25 dates → **full-period (1,721 dates) reproducibility**
- daily churn 19.6/100 = migration strategy warning 등록 (defect 아니지만 향후 strategy review 시 Bear objection)

해석:
- Top100 audit pass = KR-LIQ-MIGRATION-001 자동 재개 X

### Flow Unit / Timestamp (KR-FLOW-UNIT-TIMESTAMP-AUDIT-001)

Allowed:
- PARTIAL PASS FOR DATA AUDIT / PARTIAL FAIL

NOT allowed:
- FLOW STRATEGY READY

100% estimated flow = residual risk 유지 (vendor doc 또는 full reconciliation 후 close).

## Allowed Audit Actions

| Allowed | 목적 |
|---|---|
| Round 3 34 defects closure 재분류 (CLOSED/PARTIAL/OPEN/DEFERRED-S2/REGRESSION) | defect status 측정 |
| C1 adjusted OHLC integration 검증 | raw alias 문제 해소 확인 |
| 175→35 extreme event ledger 검증 | 잔존 35 원인 분류 |
| C4 permanent ID coverage 검증 | 833/833 fallback 타당성 |
| C5 tradable_state 검증 | true_suspension / delisting_transition 분리 |
| C6 listing_status 검증 | terminal status linkage |
| C7 flow_safe 검증 | sign/unit/timestamp safety marker |
| Top100 rule full-period 재현 | sample → full panel |
| S6 flow reconciliation 확장 계획 | sample → full audit 조건 |

## Continuously Forbidden

- return backtest / NAV / CAGR / Sharpe / hit rate / alpha / excess return / MDD
- post-event / migration / turnover / resume / reversal / flow-return result
- Round 2 strategy diagnostic restart
- 147/175 events 제외 후 우회 testing
- production / paper / P08 / live readiness / shadow track 연결
- Partial pass = strategy-ready 표현

## Allowed Output Types

| Output | 허용 |
|---|---|
| defect ledger | ✅ |
| closure ledger | ✅ |
| reconciliation rate | ✅ |
| pass / fail / partial status | ✅ |
| residual-risk list | ✅ |
| missing-source list | ✅ |
| repair feasibility report | ✅ |

## Partial Re-A0 Kill / Regression Gates

| Regression | Action |
|---|---|
| Adjusted OHLC merge가 일부 ticker/date에서 raw alias | G5 regression |
| 35 residual event 중 다수가 unexplained price artifact | G5 remains fail |
| Permanent_id fallback이 ticker reuse를 구분 못 함 | ID partial/fail |
| panel_absence가 true non-tradability로 처리됨 | Tradability fail |
| S3가 exchange suspension status가 아니라 disclosure proxy에 불과 | Tradability partial/fail |
| Top100 full-period reproducibility가 sample보다 낮음 | Top100 partial/fail |
| Flow reconciliation 실패가 특정 market/year/ticker에 집중 | Flow partial/fail |
| flow_safe가 unknown timestamp를 safe로 표시 | Flow fail |
| Any performance metric generated | protocol violation |

## Post-Partial-Re-A0 Possible States

가능한 final 상태:
- Infrastructure Gate Closed
- Infrastructure Gate Partial
- Infrastructure Gate Open
- Infrastructure Gate Regression
- S2/C3 Deferred

불가능한 final 상태:
- Strategy TEST reopened
- Alpha diagnostic approved
- Production / Paper / P08 / Live-readiness change

## Required Outputs (9개)

1. ✅ `docs/round4_partial_reA0_referee_lock.md` (이 파일)
2. `reports/experiments/round4_partial_reA0/round4_reA0_defect_closure_ledger.csv`
3. `reports/experiments/round4_partial_reA0/round4_reA0_summary.md`
4. `reports/experiments/round4_partial_reA0/residual_35_extreme_event_ledger.csv`
5. `reports/experiments/round4_partial_reA0/permanent_id_fallback_validation.md`
6. `reports/experiments/round4_partial_reA0/tradable_state_v2_validation.md`
7. `reports/experiments/round4_partial_reA0/top100_full_period_reproducibility.md`
8. `reports/experiments/round4_partial_reA0/flow_s6_reconciliation_validation.md`
9. `reports/experiments/round4_partial_reA0/unresolved_S2_C2_C3_register.md`

## Final Referee Lock

```
Option B selected.
Round 4 Partial Re-A0 Infrastructure Closure Audit is approved.
S1/S3/S4/S6/C1/C4/C5/C6/C7 progress is substantial.
S2/C2/C3 remain unresolved.
Full G5 pass is not allowed yet.
Strategy tests remain closed.
Performance diagnostics remain closed.
Round 2 cards remain closed.
Production / paper / P08 remain untouched.
```

## Related

- `docs/round3_final_referee_lock.md`
- `docs/W001_v2_infrastructure_repair_plan.md`
- `docs/W001_v2_reA0_gate_spec.md`
- `data/acquired/round4/ACQUISITION_SUMMARY.md`
- `reports/experiments/round3_aggregate/round3_defect_summary.md` (34 defects)
