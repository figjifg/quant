# KR-ID-LIFECYCLE-MASTER-AUDIT-001 — Audit Summary

Card: KR-ID-LIFECYCLE-MASTER-AUDIT-001
Round: 3 (Step 5, Priority 1B)
Date: 2026-05-22
Status: **PARTIAL** (DART corp_code 94% coverage = strong base; terminal event source 부재)

## Audit Workflow Results (8 step)

| Step | Audit Item | Status | Defect ID |
|---|---|---|---|
| 1 | (날짜, 종목코드) uniqueness | ✅ PASS | ID_000001 |
| 2 | Disappeared ticker full list | ⚠ PARTIAL (299 tickers, terminal event reason missing) | ID_000002 |
| 3 | Reappeared code (90d+ gap) | ⚠ PARTIAL (307 tickers, reuse vs resume 구분 불가) | ID_000003 |
| 4 | Name change trace | ✅ DOCUMENTED (152 tickers) | ID_000004 |
| 5 | DART corp_code mapping | ⚠ PARTIAL (94% coverage) | ID_000005 |
| 6 | corp_code ↔ stock_code linkage | ✅ PASS (1:1 within DART) | ID_000006 |
| 7 | dynamic_top100 lifecycle coverage | ✅ POSITIVE (833 ever-top100 names preserved) | ID_000007 |
| 8 | Code reuse detection | ✅ NONE within DART (0 multi-corp ticker) | (covered in ID_000006) |

**Total defects**: 7 (2 high / 1 medium / 1 low / 3 informational)

## Key Findings

### Positive
- (날짜, 종목코드) uniqueness 정상 (0 duplicates)
- DART corp_code 가 strong permanent ID candidate (94% coverage, 1:1 mapping)
- Panel 의 모든 833 unique tickers 가 한 번이라도 top100 진입 = survivor-only universe 아님 (강력한 PIT 신호)
- 152 name change cases 모두 panel 안에서 추적 가능 (uniqueness 깨지지 않음)
- Within DART: no ticker reuse / no multi-ticker corp 발견

### Concerns
- 299 disappeared tickers 의 **terminal event reason** 외부 source 부재
  - 101 long_inactive (>1000d before panel end) = likely delisted
  - 194 mid_inactive (>365d) = candidate
  - 4 recent inactive = panel end artifact 가능성
- 307 tickers 가 90d+ gap = reappearance. 12 with name change.
  - Reuse vs suspension+resume 구분 = 외부 status source 필요
- 50 panel tickers (6%) NOT in DART = 외국 ETF / 지주회사 / 합병 후 fallback 필요

## Kill Gates Status (Referee 명시)

| Kill gate | Status |
|---|---|
| Permanent ID 또는 reliable lifecycle mapping 생성 불가 | ⚠ PARTIAL (corp_code 94% 가능, 6% fallback 필요) |
| Disappeared stocks 의 terminal event 설명 불가 | ❌ FAIL (외부 source 필요) |
| Delisted names 가 panel 에서 cash-like 처리됨 | ⚠ unverified (lifecycle source 후 audit) |
| Code reuse / reappearance 구분 불가 | ❌ FAIL (외부 status source 필요) |
| Dynamic_top100 이 survivor-only universe 에서 생성됨 | ✅ NO (833 ever-top100 names 보존됨) |

## Card Verdict

**PARTIAL** with strong positive base.

- DART corp_code 가 즉시 사용 가능한 permanent ID (Round 3 Q2 후속의 부분 unblock)
- 단 terminal event reason / reuse status 는 외부 source 필요 (S3, S4)

## Reconciliation Rate

| Item | Rate |
|---|---|
| stock_code uniqueness | 100% (0 duplicates) |
| DART corp_code 매핑 | 94% |
| within-DART 1:1 linkage | 100% |
| Top100 universe permanent ID coverage | 94% (mapped) |

## Missing Source Update

`docs/round3_missing_source_register.md` 의 S3 (KRX status), S4 (Permanent ID)
entry priority 강화. S4 는 사실 부분적으로 DART corp_code 로 cover 가능.

추가 entry 후보:
- S4-fallback: 50 non-DART tickers 의 별도 ID source (KRX listed companies file
  또는 ISIN)

## Repair Path Summary

| Path | Count |
|---|---|
| requires_external_source | 3 (KRX delisting / KRX listing status / KRX 전체 listed companies) |
| requires_code_fix | 1 (name change history table) |
| not_repairable | 3 (informational, no action needed) |

## Downstream Impact

이 카드의 PARTIAL 결과:
- KR-G5-ADJOHLC-CORPACT-AUDIT-001 (Priority 1A) 의 G5_000007 cross-reference 가능
- KR-TOP100-PIT-LINEAGE-AUDIT-001 (Priority 3) 의 survivor check 에 positive evidence 제공
- KR-TRADABILITY-SEMANTICS-AUDIT-001 (Priority 2) 의 terminal stock treatment audit 에 input
- 향후 strategy 카드의 permanent identifier requirement 일부 충족

## Reproducibility

- 데이터: panel + OPENDART parquet
- 결과: `disappeared_ticker_ledger.csv` (299 rows) + `code_reuse_candidates.csv` (307 rows) + `corp_code_to_ticker_mapping.csv` (833 rows)
- 환경: `.venv/bin/python` + `pyarrow`

## Compliance with Round 3 Hard Locks

- ✅ No return computation
- ✅ No NAV / CAGR / Sharpe / MDD
- ✅ No delisted names dropped from universe analysis
- ✅ No lifecycle outcome as alpha label
- ✅ No P08 / paper / production 연결

## Related

- `docs/round3_referee_verdict_lock.md`
- `docs/round3_defect_ledger_schema.md`
- `docs/round3_missing_source_register.md` (S3, S4)
- `research/experiments/spec_KR_ID_LIFECYCLE_MASTER_AUDIT_A0.md`
- `reports/experiments/KR_G5_ADJOHLC_CORPACT_AUDIT_001/audit_summary.md` (Priority 1A 병렬)
