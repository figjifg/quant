# KR-TOP100-PIT-LINEAGE-AUDIT-001 — Audit Summary

Card: KR-TOP100-PIT-LINEAGE-AUDIT-001
Round: 3 (Step 5, Priority 3)
Date: 2026-05-22
Status: **PARTIAL PASS** (selection rule reproducible 100%, Gate 5 dependency 남음)

## Audit Workflow Results (8 step)

| Step | Audit Item | Status | Defect ID |
|---|---|---|---|
| 1 | Generation script existence | ⚠ MISSING in repo (vendor 적용) | TOP_000001 |
| 2 | Selection rule documentation | ✅ Reverse-engineered: **거래대금추정 top 100** (100% reproducible) | TOP_000002 |
| 3 | All-listed candidate universe | ⚠ PARTIAL (~563 per date, 전 KRX 별도 source 필요) | TOP_000004 |
| 4 | Membership reproducibility | ✅ 100% across 25+ sample dates | TOP_000003 |
| 5 | Delisted / merged member retention | ✅ POSITIVE (833 ever-top100 names 보존) | TOP_000005 |
| 6 | Market cap / trading value timestamp lineage | ⚠ PIT 0% estimated (good), 단 Gate 5 dependency | TOP_000006 |
| 7 | Missing membership days | ✅ Stable (~100 per date) | (covered in TOP_000002/003) |
| 8 | Membership transition outliers | ⚠ DOCUMENTED (avg 19.6 daily churn, max 34) | (covered in TOP_000003) |

**Total defects**: 6 (1 high / 1 medium / 1 low / 3 informational)

## Major Finding (POSITIVE)

**Dynamic Top100 selection rule = 거래대금추정 (trading value) 상위 100 종목**.

Reproducibility verification (25+ sample dates from 2018-06 to 2024-12):
- Trading value top 100 match: **100/100** (avg) — perfect
- Market cap top 100 match: 60.8/100 (avg) — wrong rule
- Rank composite (mc+tv): 76/100 — wrong rule

→ Selection rule **reproducible from panel data alone**. Repo 안 generation
script 가 없는 것은 documentation gap 일 뿐, rule 자체는 명확.

## Kill Gates Status (Referee 명시)

| Kill gate | Status |
|---|---|
| dynamic_top100 재현 불가 | ✅ PASS (100% reproducible) |
| Generation rule undocumented | ⚠ PARTIAL (rule clear, script missing) |
| Universe survivor-only | ✅ NO (833 names preserved, ID_000007 cross-evidence) |
| Delisted / merged historical members absent | ✅ NO (panel preserves disappeared names) |
| Market cap / trading value non-PIT | ✅ PIT (0% estimated) |
| Top100 membership 이 깨진 adjusted OHLC 에 의존 | ❌ PARTIAL FAIL (Gate 5 dependency: split day 의 trading value 왜곡 가능) |

## Card Verdict

**PARTIAL PASS**:
- Selection rule + reproducibility = strong positive
- Survivorship safety = strong positive (1B + 3 cross-evidence)
- Gate 5 dependency 만 fix 되면 거의 PASS

## Additional Findings

### Transition Churn (KR-LIQ-MIGRATION-001 의 정보)

Membership transition stats:
- Mean **19.6 new entries per day** (out of 100)
- Max 34 new entries on single day
- 1720/1721 days have >5 new entries
- 1706/1721 days have >10 new entries

→ Top100 membership 이 매일 약 19% 교체. KR-LIQ-MIGRATION-001 의 "신규 진입"
event 는 사실상 daily noise. Migration return diagnostic 의 signal-to-noise
ratio 가 spec 예상보다 낮을 가능성 큼.

(단 Round 3 = no return diagnostic, 이 noise level 자체가 informational
finding)

### Gate 5 Dependency (TOP_000006)

거래대금추정 = 거래량 × close (PIT). Close 가 raw (adjusted X) 라서:
- Split day: close 가 1/N 로 떨어짐, 거래량 N 배 → trading value 보존
  (양호)
- 액면병합: 반대로 보존
- **유상증자 (capital raise)**: close 단순 dilution, trading value 의 의미
  변동 가능
- 합병 직후: trading value spike 가능

따라서 Top100 membership 이 corporate action day 에 일시 변동 = false
transition 가능성. KR-LIQ-MIGRATION-001 의 entry event 일부가 artifact.

## Reconciliation Rate

| Item | Rate |
|---|---|
| Selection rule (TV top 100) | 100% |
| Membership reproducibility per date | 100% |
| Survivor universe safety | ✅ verified internally |
| Estimated flag check | 100% (0% estimated) |

## Missing Source Update

`docs/round3_missing_source_register.md` S5 entry 결과:
- Generation rule = 거래대금추정 top 100 (이미 reverse-engineered)
- 추가 acquire 불필요 (단 KRX 전체 listed companies file 은 S5-extension 으로
  유용)

## Repair Path Summary

| Path | Count |
|---|---|
| requires_external_source | 1 (전 KRX listed companies) |
| requires_both | 1 (Gate 5 fix + reuse) |
| requires_code_fix | 1 (script documentation) |
| not_repairable | 3 (informational positives) |

## Downstream Impact

이 카드의 PARTIAL PASS 결과:
- KR-LIQ-MIGRATION-001 (Round 2 BACKLOG): high churn finding (19/day) +
  Gate 5 dependency 명시. Migration return diagnostic 의 signal-to-noise
  매우 낮음 가능성 정보 추가.
- KR-TURNOVER-ATTENTION-001 (Round 2 BACKLOG): turnover 의 trading value
  계산 = same Gate 5 dependency.
- Migration / turnover diagnostic 재개 시 = adjusted OHLC + Bear 재심의
  필요.

## Reproducibility

- 데이터: `dynamic_top100_2018_2024_panel.csv`
- 코드: panel data 자체에서 `거래대금추정 > sort > top 100` 단순 logic
- 결과: `defect_ledger.csv` + `membership_reproducibility.csv` (25+ dates)

## Compliance with Round 3 Hard Locks

- ✅ No migration return / turnover return / strategy edge claim
- ✅ No NAV / CAGR / Sharpe / MDD
- ✅ No P08 / paper / production 연결

## Related

- `docs/round3_referee_verdict_lock.md`
- `docs/round3_missing_source_register.md` (S5)
- `research/experiments/spec_KR_TOP100_PIT_LINEAGE_AUDIT_A0.md`
- `reports/experiments/KR_ID_LIFECYCLE_MASTER_AUDIT_001/audit_summary.md` (ID_000007 cross-evidence)
- `reports/experiments/KR_G5_ADJOHLC_CORPACT_AUDIT_001/audit_summary.md` (Gate 5 dependency)
