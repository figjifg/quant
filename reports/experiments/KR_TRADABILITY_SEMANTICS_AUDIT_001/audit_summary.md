# KR-TRADABILITY-SEMANTICS-AUDIT-001 — Audit Summary

Card: KR-TRADABILITY-SEMANTICS-AUDIT-001
Round: 3 (Step 5, Priority 2)
Date: 2026-05-22
Status: **FAIL** (3 critical kill gates triggered, expected per Round 2 finding)

## Audit Workflow Results (9 step)

| Step | Audit Item | Status | Defect ID |
|---|---|---|---|
| 1 | tradability.py logic inspection | ❌ FAIL (panel presence proxy) | TRAD_000001 |
| 2 | Panel missingness by stock/date | ✅ DOCUMENTED | (in TRAD_000004) |
| 3 | Zero-volume vs missing-row 분리 | ⚠ PARTIAL (가능하나 현재 conflated) | TRAD_000004 |
| 4 | Suspension source 필요 | ❌ FAIL (S3 missing) | TRAD_000002 |
| 5 | False tradable / non-tradable count | ⚠ UNVERIFIED (외부 source 없음) | (in TRAD_000001) |
| 6 | Listed universe calendar alignment | ✅ DOCUMENTED | TRAD_000006 |
| 7 | Terminal stock treatment | ❌ FAIL (delisting/merger 구분 불가) | TRAD_000005 |
| 8 | Limit / executable status | ❌ FAIL (corp action 오염) | TRAD_000003 |
| 9 | 147 extreme × tradability crosstab | ✅ DOCUMENTED (Round 2 reuse) | (covered) |

**Total defects**: 6 (3 critical / 2 high / 1 medium / 1 informational)

## Kill Gates Status (Referee 명시)

| Kill gate | Status |
|---|---|
| Tradability flag 가 exchange status 가 아니라 panel presence proxy | ❌ FAIL |
| Missingness 와 true suspension 구분 불가 | ❌ FAIL |
| Official status source 확보 불가 | ❌ FAIL |
| Limit lock / executable status 판단 불가 | ❌ FAIL (corp action pollution) |
| Delisted / suspended names 누락 | ✅ NO (panel 에 보존됨, ID_000007 evidence) |

## Card Verdict

**FAIL** under current data. **Expected**: Round 2 Step 5 finding 재확인 +
공식 등록 + missing source priority 강화.

이번 audit 의 가치:
- 4-cause distinction 가능성 확정 (zero-volume vs missing row 분리 가능)
- limit threshold (0.299) KRX 30% rule 과 일치 확인
- terminal stock 분석 (258 disappeared 중 25 = volume=0 terminal, 233 = normal volume 사라짐)
- W001 v2 의 categorical state column 추가 path 명확

## Key Findings

### Positive
- close 가격 결손 0건 (전체 panel 무결)
- volume = trade_value missing 동일 count (same source)
- limit threshold 0.299 = KRX 30% rule 과 align
- 0.45% ~ 1.03% per-year missingness (낮음, 2022 dip 흥미)

### Concerns
- tradability flag 가 사실상 universe filter + sanity
- STATUS 컬럼 없음 = true suspension 분리 불가
- 233 disappeared tickers 가 정상 volume 으로 종료 → reason 불명
- 147 corp action artifact 99.3% 가 false limit-lock 분류

## Reconciliation Rate

- TRAD_000001: 100% verified (Round 2 결과 재확인)
- TRAD_000003: 99.3% verified (146/147 false limit)
- TRAD_000004: 100% verified (volume vs trade_value same source 확정)
- TRAD_000006: 100% verified (0.299 ≈ KRX 30%)

## Missing Source Update

`docs/round3_missing_source_register.md` S3 (KRX suspension status) priority
강화. Cross-card dependency 확정:
- TRAD_000005 (terminal) ↔ ID_000002 (disappeared)
- TRAD_000003 (limit pollution) ↔ G5_000004 (corp action artifact)

## Repair Path Summary

| Path | Count |
|---|---|
| requires_external_source | 2 (S3) |
| requires_both | 2 (S3 + code) |
| requires_code_fix | 1 (categorical column) |
| not_repairable | 1 (informational) |

## Downstream Impact

- KR-LIQ-FRAGILITY-AVOID-001: 변화 없음 (이미 차단)
- KR-TRADABILITY-RESUME-RISK-001: 변화 없음 (Round 2 infrastructure only)
- 향후 strategy 카드: tradability flag 사용 시 W001 v2 categorical 필요

## Reproducibility

- 데이터: panel
- 결과: `defect_ledger.csv` (6 rows) + `missingness_breakdown.csv` (year × 5 metric)
  + `extreme_x_tradability_crosstab.csv` (Round 2 copy)

## Compliance with Round 3 Hard Locks

- ✅ No return computation
- ✅ No entry / exit simulation
- ✅ No resume-risk return diagnostic
- ✅ No liquidity fragility filter performance test
- ✅ No NAV / CAGR / Sharpe / MDD
- ✅ No P08 / paper / production 연결

## Related

- `docs/round3_referee_verdict_lock.md`
- `docs/round3_missing_source_register.md` (S3)
- `research/experiments/spec_KR_TRADABILITY_SEMANTICS_AUDIT_A0.md`
- `docs/tradability_semantics_audit.md` (Round 2 base finding)
- `reports/experiments/KR_TRADABILITY_RESUME_RISK_001/` (Round 2 infrastructure audit)
