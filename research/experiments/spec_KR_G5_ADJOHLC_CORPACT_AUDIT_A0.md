# KR-G5-ADJOHLC-CORPACT-AUDIT-001 — A0 Audit Spec (Priority 1A)

## Status
PRE-REGISTERED · **A0 AUDIT only** · 전략 아님
Round 3 Priority: 1A (KR-ID-LIFECYCLE-MASTER-AUDIT-001 과 병렬)
Date: 2026-05-22

## Cycle Lineage

- Round 3 Bull idea #1
- Referee Round 3 lock: **A0 AUDIT (adjusted OHLC / corporate action repair audit only)**
- Trigger: Round 2 Step 5 Gate 5 FAIL + Option D

## Scope

이 카드는 **전략 아님**. Gate 5 adjusted OHLC / corporate action repair
audit. Output = defect ledger + repair feasibility report 만.

## Hard Locks (Round 3 전체)

`docs/round3_no_performance_rule.md` 그대로 적용. 특히:
- Return-based diagnostic 일체 금지
- 147 events 제외 후 strategy test 금지
- Performance language 금지
- P08 / paper / live 연결 금지

## Allowed Audit Actions (Referee 명시)

| Audit | 허용 |
|---|---|
| Adjusted column 존재 여부 확인 | ✅ |
| Adjusted column 이 raw alias 인지 확인 | ✅ |
| `adjust_for_corporate_actions()` logic inspection | ✅ |
| \|daily_return\| > 50% extreme discontinuity full ledger | ✅ |
| Corporate action source 필요 목록 작성 | ✅ |
| Factor chain reproducibility 점검 | ✅ |
| Trusted adjusted OHLC reference 필요 여부 판단 | ✅ |
| Delisted / merged / renamed names 포함 여부 확인 | ✅ |

## Forbidden Actions

| Action | 금지 |
|---|---|
| Repaired 여부 확인 전 return diagnostic | ❌ |
| 147개 extreme event 만 제외하고 테스트 재개 | ❌ |
| Limit incidence 전략 재개 | ❌ |
| Migration / turnover / resume return 재개 | ❌ |
| 성과표 산출 | ❌ |

## Audit Workflow (Allowed only)

### Step 1 — Adjusted Column 존재 / alias 확인

- Panel column list 확인 (`adjusted_*` 존재 여부)
- 존재 시 → values 가 raw column 의 alias 인지 (정확히 같은지)
- 결과: defect entry (`adjusted_column_missing` 또는 `adjusted_column_is_raw_alias`)

### Step 2 — `adjust_for_corporate_actions()` logic inspection

- 함수 소스 코드 inspection (이미 Round 2 Step 5 에서 일부 진행)
- alias-only 동작 / 실제 조정 X 확인
- 결과: defect entry (`metadata_only_no_actual_adjustment` /
  `function_misleading_name`)

### Step 3 — Extreme discontinuity full ledger

- \|daily_return\| > 50% events 전수 추출 (이미 147 건 = Round 2 결과 활용)
- 각 event 별 ticker / date / return / prev_close / 시가 / 거래량 / trading
  value / tradability state 기록
- 단 **return 자체를 outcome 으로 보지 않음** = defect indicator 로만 사용
- 결과: existing `corporate_action_artifact_ledger.csv` 를 schema 에 맞춰
  defect ledger 로 transcribe

### Step 4 — Corporate action source 필요 목록

- 147 events 별 추정 corporate action type (split / 액면병합 / 증자 / 감자 등)
  candidate label (단 confirm 위해 external source 필요)
- 필요한 official source field list (`docs/round3_missing_source_register.md`
  S2 와 연결)

### Step 5 — Factor chain reproducibility

- 만약 vendor adjusted OHLC 가 있다면, factor chain (event 별 누적 factor)
  재계산 가능한지 확인
- 현재 source 없음 = `factor_chain_unreproducible` defect

### Step 6 — Trusted adjusted OHLC reference 필요 여부 판단

- 가능한 source 후보 별 acceptance 가능성 평가
  (`docs/round3_missing_source_register.md` S1 의 후보 list 와 연결)

### Step 7 — Delisted / merged / renamed names 포함 여부

- Panel 의 815 unique ticker 중 disappeared 258 ticker (Round 2 발견)
  분류:
  - 진짜 delisting?
  - merger?
  - rename (= 동일 entity 다른 ticker)?
- 단 이 분류 자체는 KR-ID-LIFECYCLE-MASTER-AUDIT-001 (Priority 1B) 의
  주요 작업과 overlap = 병렬 운영 권장 (Referee 명시)

## Kill Gates (Referee 명시)

| Kill gate | Decision |
|---|---|
| Official corporate action source 확보 불가 | FAIL |
| Adjusted OHLC 가 raw alias 로 남아 있음 | FAIL |
| Extreme discontinuity 상당수가 설명 불가 | FAIL |
| Adjustment factor chain 재현 불가 | FAIL |
| Delisted / merged / renamed names 누락 | FAIL |
| Repair 후에도 다수의 abs(adjusted daily return) > 50% 잔존 | FAIL |

## Required Outputs

| Output | 형식 |
|---|---|
| `defect_ledger.csv` | `docs/round3_defect_ledger_schema.md` schema 그대로 |
| `audit_summary.md` | pass/fail 집계 + reproducibility 방법 + repair feasibility |
| `extreme_discontinuity_ledger.csv` | 147 events transcribed (이미 Round 2 의 `corporate_action_artifact_ledger.csv` 활용) |
| `missing_source_update.md` | `docs/round3_missing_source_register.md` 에 추가할 entry |
| `repair_feasibility_report.md` | source 후보별 acceptance 가능성 + 추정 effort |

출력 위치: `reports/experiments/KR_G5_ADJOHLC_CORPACT_AUDIT_001/`

## Pass / Fail Status

**PASS**: 모든 audit 항목 통과 + repair path 명확 (source acquired or
acquisition plan locked)

**FAIL**: 위 kill gate 중 하나라도 해당. 해당 시 KR-G5 카드 자체는 인정 -
단 strategy diagnostic 차단 상태 유지.

**ACCEPTABLE FINDING** (PARTIAL): defect 있으나 repair feasible (source 후보
명확 + 사용자 host 작업 가능)

## Forbidden Outputs

(Round 3 no-performance rule 그대로)
- Return table / NAV / CAGR / Sharpe / hit rate / alpha / excess return
- MDD as strategy performance
- Post-event drift / migration return / turnover return / resume return /
  reversal return / flow-return

## Codex Implementation Task

```
Implement KR-G5-ADJOHLC-CORPACT-AUDIT-001 A0 AUDIT only.

ABSOLUTE PROHIBITIONS:
- Do not compute any return outcome
- Do not run any strategy backtest
- Do not generate NAV/CAGR/Sharpe/MDD tables
- Do not test with 147 events excluded
- Do not connect to P08/paper/production
- Do not modify research_input_data/ files
- Do not modify specs

Tasks (Allowed actions only, per spec):
1. Inspect panel adjusted column existence (Step 1).
2. Inspect adjust_for_corporate_actions() logic (Step 2).
   - Already partially documented in docs/adjustment_engine_requirements.md
3. Transcribe 147 extreme events from existing artifact ledger to
   defect_ledger format (Step 3).
   - Source: reports/experiments/W001_V1_AUDIT/corporate_action_artifact_ledger.csv
4. Compile corporate action source requirements (Step 4).
5. Evaluate factor chain reproducibility (Step 5).
6. List trusted adjusted OHLC source candidates with acceptance criteria (Step 6).
7. Note delisted/merged/renamed name coverage (Step 7, partial — full work in
   KR-ID-LIFECYCLE-MASTER-AUDIT-001).

Required outputs:
- reports/experiments/KR_G5_ADJOHLC_CORPACT_AUDIT_001/defect_ledger.csv
- reports/experiments/KR_G5_ADJOHLC_CORPACT_AUDIT_001/audit_summary.md
- reports/experiments/KR_G5_ADJOHLC_CORPACT_AUDIT_001/extreme_discontinuity_ledger.csv
- reports/experiments/KR_G5_ADJOHLC_CORPACT_AUDIT_001/missing_source_update.md
- reports/experiments/KR_G5_ADJOHLC_CORPACT_AUDIT_001/repair_feasibility_report.md

If any task would require computing return-based metrics: STOP and report to
user. Round 3 hard lock.
```

## Result Summary

작성 금지 (Round 3 = audit only, performance metric X).

## Bull/Bear/Referee Review

작성 금지 (Round 3 = no Bear-interpretation / Bull-rebuttal step).

## Related

- `docs/round3_referee_verdict_lock.md`
- `docs/round3_no_performance_rule.md`
- `docs/round3_defect_ledger_schema.md`
- `docs/round3_missing_source_register.md` (S1, S2)
- `docs/round2_gate5_fail_lock.md` (origin)
- `docs/data_gap_adjusted_ohlc.md` (Round 2 finding base)
- `docs/adjustment_engine_requirements.md` (Round 2 finding base)
- `reports/experiments/W001_V1_AUDIT/corporate_action_artifact_ledger.csv` (147 events)
