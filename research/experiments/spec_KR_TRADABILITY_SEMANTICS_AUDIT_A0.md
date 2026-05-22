# KR-TRADABILITY-SEMANTICS-AUDIT-001 — A0 Audit Spec (Priority 2)

## Status
PRE-REGISTERED · **A0 AUDIT only** · 전략 아님
Round 3 Priority: 2 (Priority 1A + 1B 통과 후)
Date: 2026-05-22

## Cycle Lineage

- Round 3 Bull idea #3
- Referee Round 3 lock: **A0 AUDIT (tradability flag semantics audit only)**
- Trigger: Round 2 Step 5 Gate 3 PARTIAL + Option D
- Round 2 finding 활용: `docs/tradability_semantics_audit.md` 이미 작성

## Scope

W001 tradability flag 가 실제 거래 가능성을 의미하는지, 아니면 단순 panel
presence / missingness proxy 인지 검증. Output = defect ledger.

## Hard Locks (Round 3 전체)

`docs/round3_no_performance_rule.md` 그대로 적용. 특히 **entry / exit
simulation 금지**.

## Allowed Audit Actions (Referee 명시)

| Audit | 허용 |
|---|---|
| `tradability.py` logic inspection | ✅ |
| Panel missingness by stock/date | ✅ |
| Zero-volume vs missing-row 분리 | ✅ |
| Official suspension/resumption source 필요 여부 확인 | ✅ |
| False tradable / false non-tradable count | ✅ |
| Listed universe calendar alignment | ✅ |
| Terminal stock treatment | ✅ |
| Limit / executable status availability 확인 | ✅ |
| 147 extreme return event 와 tradability flag 교차표 | ✅ |

## Forbidden Actions

| Action | 금지 |
|---|---|
| Resume-risk return diagnostic | ❌ |
| 재개 후 5d / 20d / 63d return table | ❌ |
| Entry / exit simulation | ❌ |
| Liquidity fragility filter 성과 테스트 | ❌ |

## Audit Workflow (Allowed only)

### Step 1 — `tradability.py` logic inspection

- `src/utils/tradability.py` 의 `tradable_mask()` AND 조건 inspection
- Round 2 결과 (`docs/tradability_semantics_audit.md`) transcribe
- defect: `tradability_flag_is_panel_presence_proxy` (severity: critical)

### Step 2 — Panel missingness by stock/date

- 각 (stock, date) pair 의 missingness pattern audit
- 일부 stock 이 일부 date 에 missing rows = strategy event 아님 (Round 2
  finding 활용)
- defect: `data_missing_vs_panel_absence_conflation` (이미 unknown 141,693
  rows 결과)

### Step 3 — Zero-volume vs missing-row 분리

- trading_value = 0 vs trading_value = NaN vs row absent 구분
- 각 case 별 의미: 정지 / hold / out of panel
- defect: `zero_volume_vs_missing_row_conflation`

### Step 4 — Official suspension/resumption source 필요 여부

- `docs/round3_missing_source_register.md` S3 와 연결
- 현재 source 없음 = defect: `status_column_missing` (severity: critical)

### Step 5 — False tradable / false non-tradable count

- Sample 검증: 외부 source (만약 있다면) 와 비교
- 현재 외부 source X → reconciliation 불가 = defect

### Step 6 — Listed universe calendar alignment

- KRX 거래일 calendar 와 panel 의 date coverage 일치 확인
- W001 `korean_calendar.py` 사용

### Step 7 — Terminal stock treatment

- Disappeared 258 ticker 가 panel 에서 어떻게 사라지는지 확인
- 마지막 row 가 거래정지일 / 상폐일 / 그 전인지 audit
- KR-ID-LIFECYCLE-MASTER-AUDIT-001 (Priority 1B) 결과와 cross-reference

### Step 8 — Limit / executable status availability

- `tradable_mask()` 의 limit_threshold = 0.299 가 실제 KRX limit (30%) 과
  일치
- corporate action day = false limit positive (Round 2 = 146/147 = 99.3%)
  → defect: `limit_lock_polluted_by_corporate_action` (severity: high)

### Step 9 — 147 extreme return × tradability flag 교차표

- 이미 Round 2 audit 에서 작성:
  `reports/experiments/KR_TRADABILITY_RESUME_RISK_001/extreme_x_tradability_crosstab.csv`
- defect ledger 에 transcribe

## Data Available

| Source | 가용성 | 한계 |
|---|---|---|
| `src/utils/tradability.py` | ✅ 코드 inspection 가능 | docstring vs 실제 동작 gap 있음 |
| dynamic_top100 panel (`동적유니버스포함`) | ✅ 있음 | universe membership only |
| trading_value / 거래량 | ✅ 있음 | suspension 별도 source X |
| KRX 공식 status column | ❌ 없음 | S3 source 필요 |

## Kill Gates (Referee 명시)

| Kill gate | Decision |
|---|---|
| Tradability flag 가 exchange status 가 아니라 panel presence proxy | FAIL |
| Missingness 와 true suspension 구분 불가 | FAIL |
| Official status source 확보 불가 | FAIL |
| Limit lock / executable status 판단 불가 | FAIL |
| Delisted / suspended names 누락 | FAIL |

**현재 상태 (Round 2 finding 기준)**: 위 모든 kill gate 가 사실상 hit
상태. 따라서 이 audit 의 PASS 가능성 = 낮음. Audit 의 가치 = defect 의
공식 등록 + missing source 명확화.

## Required Outputs

| Output | 형식 |
|---|---|
| `defect_ledger.csv` | Round 3 schema |
| `audit_summary.md` | pass/fail + Round 2 finding 재확인 |
| `logic_inspection.md` | tradable_mask() AND chain audit |
| `missingness_breakdown.csv` | (stock × date) missingness type breakdown |
| `extreme_x_tradability_crosstab.csv` | (Round 2 에서 이미 작성된 것 reuse) |
| `missing_source_update.md` | S3 register 업데이트 |

출력 위치: `reports/experiments/KR_TRADABILITY_SEMANTICS_AUDIT_001/`

## Pass / Fail Status

**Expected: FAIL** (Round 2 finding 기준).

Audit 자체는 FAIL 결과를 공식 등록 + missing source + repair path 명확화로
의미 있음.

## Forbidden Outputs

(Round 3 no-performance rule 그대로)

## Codex Implementation Task

```
Implement KR-TRADABILITY-SEMANTICS-AUDIT-001 A0 AUDIT only.

ABSOLUTE PROHIBITIONS:
- No return computation
- No entry/exit simulation
- No resume-risk return diagnostic
- No liquidity fragility filter performance test
- No NAV/CAGR/Sharpe/MDD
- No P08/paper/production
- Do not modify research_input_data/

Tasks (Allowed actions only):
1. Inspect src/utils/tradability.py tradable_mask() logic.
   - Already documented in docs/tradability_semantics_audit.md
2. Compute panel missingness by stock/date (count + pattern).
3. Separate zero-volume vs missing-row vs row-absent cases.
4. Document need for official suspension/resumption source.
5. Compute false tradable / false non-tradable counts (sample, no external
   source available so report as unverified).
6. Verify listed universe calendar alignment with W001 korean_calendar.
7. Audit terminal stock treatment (disappeared 258 ticker last-row pattern).
8. Verify limit_threshold=0.299 alignment with KRX 30% rule.
9. Cross-tabulate 147 extreme returns × tradability flag (reuse from Round 2).

Outputs:
- reports/experiments/KR_TRADABILITY_SEMANTICS_AUDIT_001/defect_ledger.csv
- reports/experiments/KR_TRADABILITY_SEMANTICS_AUDIT_001/audit_summary.md
- reports/experiments/KR_TRADABILITY_SEMANTICS_AUDIT_001/logic_inspection.md
- reports/experiments/KR_TRADABILITY_SEMANTICS_AUDIT_001/missingness_breakdown.csv
- reports/experiments/KR_TRADABILITY_SEMANTICS_AUDIT_001/extreme_x_tradability_crosstab.csv (copy from Round 2)
- reports/experiments/KR_TRADABILITY_SEMANTICS_AUDIT_001/missing_source_update.md

If any task requires entry/exit simulation or return outcome: STOP.
```

## Result Summary / Bull-Bear-Referee Review

작성 금지.

## Related

- `docs/round3_referee_verdict_lock.md`
- `docs/round3_no_performance_rule.md`
- `docs/round3_defect_ledger_schema.md`
- `docs/round3_missing_source_register.md` (S3)
- `docs/tradability_semantics_audit.md` (Round 2 finding base)
- `reports/experiments/KR_TRADABILITY_RESUME_RISK_001/` (Round 2 infrastructure audit)
