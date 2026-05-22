# KR-G5-ADJOHLC-CORPACT-AUDIT-001 — Audit Summary

Card: KR-G5-ADJOHLC-CORPACT-AUDIT-001
Round: 3 (Step 5, Priority 1A)
Date: 2026-05-22
Status: **FAIL** (multiple kill gates triggered)

## Audit Workflow Results (7 step)

| Step | Audit Item | Status | Defect ID |
|---|---|---|---|
| 1 | Adjusted column existence | ❌ FAIL | G5_000001 |
| 2 | Function alias-only behavior | ❌ FAIL | G5_000002 |
| 3 | Function logic inspection (metadata only) | ❌ FAIL | G5_000003 |
| 4 | Extreme discontinuity full ledger (147 events) | ⚠ PARTIAL (catalogued, unverified) | G5_000004 |
| 5 | Corporate action source requirement | ❌ FAIL | G5_000005 |
| 6 | Factor chain reproducibility | ❌ FAIL | G5_000006 |
| 7 | Delisted / renamed inclusion | ⚠ PARTIAL (1B cross-reference 필요) | G5_000007 |

**Total defects**: 7 (4 critical / 2 high / 1 medium)

## Kill Gates Status (Referee 명시)

| Kill gate | Status |
|---|---|
| Official corporate action source 확보 불가 | ❌ FAIL (current state) |
| Adjusted OHLC가 raw alias로 남아 있음 | ❌ FAIL |
| Extreme discontinuity 상당수가 설명 불가 | ❌ FAIL (147/147 unverified) |
| Adjustment factor chain 재현 불가 | ❌ FAIL |
| Delisted / merged / renamed names 누락 | ⚠ PARTIAL (1B 결과 후 결정) |
| Repair 후에도 다수의 abs(adjusted daily return) > 50% 잔존 | N/A (repair 안 됨) |

## Card Verdict

**FAIL** under current data. KR-LIQ-FRAGILITY-AVOID-001 등 dependent strategy
diagnostic 진입 차단 유지. Round 2 Step 5 Option D lock 그대로 유지.

이번 audit 의 가치 = defect 공식 등록 + missing source 명확화 + repair path
identification.

## Reconciliation Rate

- G5_000002 (alias check): 100% verified internal (adjusted_close == 종가 정확히 일치)
- 나머지 unverified (외부 source 없음)

## Repair Path Summary

| Path | Count |
|---|---|
| requires_external_source | 5 (S1 + S2 acquisition 필요) |
| requires_both | 1 (G5_000002, naming/doc fix + actual source) |
| requires_code_fix | 1 (G5_000003, function 분리 / 새 함수) |

## Missing Source Update

`docs/round3_missing_source_register.md` 에 추가 entry 없음 (S1, S2 이미 등록).
G5 audit 결과로 S1, S2 의 priority 강화 (downstream block 4 strategy 카드 +
1 infrastructure 카드 확정).

## Repair Feasibility

| Component | Feasibility | Effort |
|---|---|---|
| Adjusted OHLC source 확보 (S1) | medium | 1-4 weeks vendor / 2-8 weeks 자체 |
| Corporate action event log (S2) | medium | 2-8 weeks (OPENDART body parser) |
| `adjust_for_corporate_actions()` fix | high | 1-2 weeks W001 v2 함수 |
| Naming / documentation fix | high | 1 day |

## Downstream Block

이 카드의 FAIL 지속 시:
- KR-LIQ-FRAGILITY-AVOID-001 (Round 2 BACKLOG, 이미 차단)
- KR-LIQ-MIGRATION-001 (Round 2 BACKLOG, 이미 차단)
- KR-TURNOVER-ATTENTION-001 (Round 2 BACKLOG, 이미 차단)
- KR-TRADABILITY-RESUME-RISK-001 (Round 2 infrastructure only, 이미 차단)
- 향후 한국 stock-level return-based diagnostic 일체

## Reproducibility

- 데이터: `research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv`
- 코드: `src/utils/corporate_action.py` (inspection)
- 환경: `.venv/bin/python` + `pyarrow`
- 결과 파일: 이 디렉토리 `defect_ledger.csv` + `extreme_discontinuity_ledger.csv`

## Compliance with Round 3 Hard Locks

- ✅ No return computation (defect indicators only)
- ✅ No NAV / CAGR / Sharpe / MDD
- ✅ No 147 events 제외 후 strategy test
- ✅ No P08 / paper / production 연결
- ✅ No spec 사후 수정

## Related

- `docs/round3_referee_verdict_lock.md`
- `docs/round3_no_performance_rule.md`
- `docs/round3_defect_ledger_schema.md`
- `docs/round3_missing_source_register.md` (S1, S2)
- `research/experiments/spec_KR_G5_ADJOHLC_CORPACT_AUDIT_A0.md`
- `docs/data_gap_adjusted_ohlc.md` (Round 2 base finding)
- `docs/adjustment_engine_requirements.md` (Round 2 base finding)
