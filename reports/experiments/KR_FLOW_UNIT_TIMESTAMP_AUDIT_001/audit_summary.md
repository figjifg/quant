# KR-FLOW-UNIT-TIMESTAMP-AUDIT-001 — Audit Summary

Card: KR-FLOW-UNIT-TIMESTAMP-AUDIT-001
Round: 3 (Step 5, Priority 4 / lowest)
Date: 2026-05-22
Status: **PARTIAL FAIL** (1 critical-significant new finding: 100% estimated flow + publication lag unknown)

## Audit Workflow Results (9 step)

| Step | Audit Item | Status | Defect ID |
|---|---|---|---|
| 1 | Flow field definitions | ✅ DOCUMENTED (4 columns clean) | FLOW_000001 |
| 2 | Sign convention | ✅ Sample verified (+ = buy, - = sell) | FLOW_000002 |
| 3 | Unit consistency | ✅ PASS (KRW consistent, ratio < 1.0) | FLOW_000003 |
| 4 | Publication lag | ❌ FAIL (unknown, "장마감 후" 만 표기) | FLOW_000004 |
| 5 | Missingness by year | ✅ Clean (NaN = 0, low zero rates) | FLOW_000005 |
| 6 | Nonzero flow on nontradable | ⚠ PARTIAL (98.7% but dominant cause = panel_absence) | FLOW_000006 |
| 7 | KRX sample reconciliation | ⚠ DEFERRED (S6 source 필요) | (covered in FLOW_000001) |
| 8 | Delisted / suspended names | ✅ Inclusion verified | (covered in FLOW_000005) |
| 9 | F-family warning | ✅ Registered | FLOW_000008 |
| -- | Estimation flag (added) | ❌ CRITICAL NEW FINDING | FLOW_000007 |

**Total defects**: 8 (2 high / 2 medium / 1 low / 3 informational)

## CRITICAL NEW FINDING (FLOW_000007)

**`수급금액추정여부` column = True for ALL 969,208 rows (100%)**.

즉 **모든 flow value 가 vendor (Kiwoom) 의 추정값**. 정확한 KRX 공식 투자자별
거래실적 아님.

이것은 Round 2 audit 에서 잘못 reported 됐던 finding 의 정정:
- Round 2: `시가총액추정여부` / `거래대금추정여부` = 0% True (✅ 정확)
- **Round 2 누락**: `수급금액추정여부` = 100% True (❌ 이전 누락, 이번 발견)

이는 추후 flow strategy 의 PIT 가정에 영향. KR-FLOW-ABSORPTION-001 의
unblock 조건 추가 (vendor 의 추정 방식 doc 확보).

## Key Findings

### Positive
- Flow NaN = 0 across all years (data integrity)
- Sign convention 일관 (+ = buy)
- Unit consistency (KRW, ratio < 1.0)
- F-family warning 사전 등록 완료

### Concerns
- **100% estimated flow** (FLOW_000007, CRITICAL)
- Publication lag 미확정 (FLOW_000004)
- Non-tradable 98.7% nonzero flow (단 universe filter 가 dominant)
- KRX 공식 sample 과 reconciliation 미진행

## Kill Gates Status (Referee 명시)

| Kill gate | Status |
|---|---|
| Positive sign 검증 불가 | ⚠ PARTIAL (sample yes, vendor doc 필요) |
| Unit 불일치 | ✅ PASS (consistent) |
| Timestamp / publication timing unknown | ❌ FAIL |
| Official KRX sample mismatch material | ⚠ UNVERIFIED (reconciliation 미진행) |
| Missingness 가 failed / suspended names 에 집중 | ✅ NO (NaN = 0) |
| 이후 flow strategy 가 flow-only baseline 을 못 이김 | future strategy kill |

## Card Verdict

**PARTIAL FAIL** with critical new finding.

기존 audit 결과:
- 4 audit items PASS / DOCUMENTED
- 1 critical NEW finding (100% estimated)
- 1 high (publication lag)
- 1 medium (nonzero on non-tradable, 단 panel_absence dominant)

미래 flow strategy 진입 전 필수:
- 추정 방식 vendor 문서 확보
- Publication lag 확정 (t+1 safety)
- KRX 공식 sample reconciliation

## Reconciliation Rate

- FLOW_000001 (fields): 100% NaN-free
- FLOW_000003 (unit): 100% sub-1.0 ratio
- FLOW_000007 (estimation): 100% verified True (1.0 reconciliation = 모두 추정)

## Missing Source Update

`docs/round3_missing_source_register.md` S6 (Flow vendor doc) entry 결과:
- Vendor doc 필요 우선순위 상승 (CRITICAL FLOW_000007 finding 후)
- 추가 entry: official KRX 투자자별 거래실적 source (정확한 값 reference)

## Repair Path Summary

| Path | Count |
|---|---|
| requires_external_source | 5 (vendor doc / KRX official) |
| not_repairable | 3 (informational positives) |

## Downstream Impact

이 카드 결과 (CRITICAL FLOW_000007 포함):
- KR-FLOW-ABSORPTION-001 (Round 2 BACKLOG): unblock 조건 추가 (vendor estimation doc)
- 향후 모든 flow-based strategy: 100% estimated 인지 명시 + reconciliation 진행 필요
- F-family 재시도 시: 같은 추정 데이터 사용 = 같은 결과 risk

## Reproducibility

- 데이터: panel + DATA_CATALOG.md + DATA_SOURCES.md
- 결과: `defect_ledger.csv` + `sign_convention_sample.csv` (10x14) + `missingness_breakdown.csv` (year x 5)

## Compliance with Round 3 Hard Locks

- ✅ No flow-return diagnostic
- ✅ No t+1 flow alpha test
- ✅ No F/I absorption performance table
- ✅ No flow strategy resume
- ✅ No NAV / CAGR / Sharpe / MDD
- ✅ No P08 / paper / production 연결

## Related

- `docs/round3_referee_verdict_lock.md`
- `docs/round3_missing_source_register.md` (S6)
- `research/experiments/spec_KR_FLOW_UNIT_TIMESTAMP_AUDIT_A0.md`
- `research/experiments/lineage_only_KR_FLOW_ABSORPTION_A0.md` (Round 2 lineage-only BACKLOG)
- F-family closure register
