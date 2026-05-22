# Round 4.1 W001 v2.1 Residual Closure Sprint + Mini Re-A0 — Referee Lock

Date: 2026-05-22
Status: LOCKED · **APPROVED**
Origin: Referee Round 4 Partial Re-A0 Final Result verdict

## Scope (Strictly Locked)

**Approved**:
- W001 v2.1 residual closure
- Mini Re-A0

**NOT approved**:
- No performance
- No strategy restart
- No S2 full parser build (S2 planning 만 허용, build = Round 4.1 mini Re-A0 후 재판정)

## Round 4 Accepted Result (Locked)

| Card | Verdict |
|---|---|
| KR-G5-ADJOHLC-CORPACT-AUDIT-001 | PARTIAL PASS WITH S2/C3 DEFERRED |
| KR-ID-LIFECYCLE-MASTER-AUDIT-001 | PARTIAL PASS |
| KR-TRADABILITY-SEMANTICS-AUDIT-001 | PARTIAL PASS WITH S3 SEMANTICS RESIDUAL |
| KR-TOP100-PIT-LINEAGE-AUDIT-001 | PARTIAL PASS 99.78/100 |
| KR-FLOW-UNIT-TIMESTAMP-AUDIT-001 | PARTIAL PASS FOR DATA AUDIT |

34 defects: CLOSED 23 / PARTIAL 10 / DEFERRED-S2 1 / OPEN 0 / REGRESSION 0.

Lock principles:
- No FAIL, No REGRESSION → W001 v2 repair direction = valid
- No FULL PASS → strategy research cannot reopen yet

## Current State (Unchanged)

- Infrastructure Gate: PARTIAL CLOSED
- Strategy TEST: CLOSED
- Performance diagnostics: CLOSED
- Round 2 cards: CLOSED
- Production / paper / P08 / live readiness / shadow tracks: UNCHANGED

## Why Small Patches First (Referee 이유)

| 종류 | 예시 | 처리 |
|---|---|---|
| 짧게 닫을 수 있는 residual | naming / KRX direct reconciliation / flow full-year / Top100 tie-break / fallback 검증 | Round 4.1 즉시 |
| 장기 의존 residual | S2 body parser / C2 factor chain / C3 corp action event log | Round 4.1 후 재판정 |

Reason: S2 (5-9주) 진입 전에 작은 불확실성을 닫아 두면 다음 판단이 선명해짐.

## 6 Allowed Tasks

### Task 1 — Tradability naming patch
- Rename `panel_absence` → `not_in_dynamic_universe`
- Backward compatibility marker / deprecated alias (필요 시)
- Ensure `not_in_dynamic_universe` ≠ non-tradable exchange status

### Task 2 — KRX suspension direct reconciliation
- pykrx 또는 KRX API direct suspension/resumption status (가능한 경우)
- vs S3 OPENDART pblntf=I events
- Advisory 12% 별도 분류

### Task 3 — Flow full-year stratified reconciliation
- 1 month × 20 ticker sample 한계 보완
- Stratify by: year / market (KOSPI/KOSDAQ) / liquidity bucket / flow-size bucket / investor type
- All >±5% mismatch 분류
- `flow_safe` fail-closed verify

### Task 4 — Top100 exact-rule residual audit
- 99.78/100 full-period mismatch (392 dates) full ledger
- Tie-break candidates:
  - trading value ties
  - market ordering
  - ticker ordering
  - missing values
  - suspension/delisting treatment
- trade_value source: official field vs reconstructed close × volume

### Task 5 — G5 residual 35 event follow-up
- 175→35 result preserve
- 32/35 year-start gap artifact confirm
- 34/35 not in dynamic universe confirm
- **1 strategy-relevant residual** case file
- Residual exclusion → strategy restart 금지 (Referee 명시)

### Task 6 — Permanent ID fallback hardening
- 50 KRX fallback IDs case ledger
- Ticker reuse / relisting / delisting / rename stability test
- Terminal status records linkage
- 815 vs 833 universe count explanation 보존

## 10 Required Outputs

1. `docs/round4_1_v2_1_referee_lock.md` (이 파일)
2. `reports/experiments/round4_1_v2_1/round4_1_closure_delta.csv`
3. `reports/experiments/round4_1_v2_1/round4_1_mini_reA0_summary.md`
4. `reports/experiments/round4_1_v2_1/tradable_state_v2_1_patch.md`
5. `reports/experiments/round4_1_v2_1/krx_suspension_direct_reconciliation.md`
6. `reports/experiments/round4_1_v2_1/flow_full_year_stratified_reconciliation.md`
7. `reports/experiments/round4_1_v2_1/top100_tiebreak_residual_ledger.csv`
8. `reports/experiments/round4_1_v2_1/g5_residual_35_case_closure.md`
9. `reports/experiments/round4_1_v2_1/permanent_id_fallback_hardening.md`
10. `reports/experiments/round4_1_v2_1/S2_phase_decision_brief.md`

## Hard Prohibitions (continued)

- No return backtest
- No NAV / CAGR / Sharpe / hit rate / alpha / excess return / MDD as strategy performance
- No post-event / migration / turnover / resume / reversal / flow-return
- No raw return as signal/outcome
- No Round 2 strategy restart
- No residual-event exclusion followed by testing
- No flow strategy testing
- No production / paper / P08 / live readiness / shadow connection
- No partial pass = strategy-ready

## End Condition (Referee 명시)

- Return only residual closure status
- Do not recommend strategy testing
- Referee 가 mini Re-A0 후 결정:
  - A. start S2 full parser phase
  - B. keep strategy research closed
  - C. reopen narrowly bounded non-flow diagnostic
  - D. continue infrastructure repair

## S2 Phase Decision Criteria

Round 4.1 mini Re-A0 후 S2 phase 진입 조건 (Referee 명시):
- Only remaining hard blocker = S2/C2/C3
- AND G5 residual 35 ledger is stable
- AND tradability direct reconciliation is closed or well-scoped
- AND flow residual is no longer blocking non-flow research

## Card별 Maximum Verdict (Lock)

| Card | Max possible verdict at Round 4.1 |
|---|---|
| G5 | PARTIAL PASS (C2/C3/S2 전까지 full 불가) |
| ID | PARTIAL PASS (fallback ticker-based) |
| Tradability | PARTIAL PASS (full pass = direct KRX reconciliation 필요) |
| Top100 | PARTIAL PASS (exact tie-break 후) |
| Flow | PARTIAL PASS FOR DATA AUDIT (FLOW STRATEGY READY 불허) |

## Related

- `docs/round3_final_referee_lock.md`
- `docs/round4_partial_reA0_referee_lock.md`
- `docs/W001_v2_infrastructure_repair_plan.md`
- `docs/W001_v2_reA0_gate_spec.md`
- `reports/experiments/round4_partial_reA0/` (5 validation md + delta CSV + summary)
- `reports/experiments/round3_aggregate/round3_defect_summary.md` (34 defects base)
