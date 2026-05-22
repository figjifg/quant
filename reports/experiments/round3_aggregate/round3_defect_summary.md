# Round 3 Aggregate Defect Summary

Date: 2026-05-22
Cycle: First Bull/Bear/Referee multi-LLM cycle · Round 3 · Step 5 complete
Status: **5/5 audits complete, infrastructure repair queue ready for sourcing decisions**

## Audit Completion

| Priority | Card | Status |
|---|---|---|
| 1A | KR-G5-ADJOHLC-CORPACT-AUDIT-001 | ✅ Complete (FAIL — Gate 5 confirmed) |
| 1B | KR-ID-LIFECYCLE-MASTER-AUDIT-001 | ✅ Complete (PARTIAL — DART corp_code 94%) |
| 2 | KR-TRADABILITY-SEMANTICS-AUDIT-001 | ✅ Complete (FAIL — 4-cause distinction 불가) |
| 3 | KR-TOP100-PIT-LINEAGE-AUDIT-001 | ✅ Complete (PARTIAL PASS — selection rule reproducible) |
| 4 | KR-FLOW-UNIT-TIMESTAMP-AUDIT-001 | ✅ Complete (PARTIAL FAIL — critical new finding) |

## Defect Aggregate (34 total)

### By Severity

| Severity | Count |
|---|---:|
| **critical** | **6** |
| high | 9 |
| medium | 6 |
| low | 3 |
| informational | 10 |

### By Card × Severity

| Card | critical | high | medium | low | info |
|---|---:|---:|---:|---:|---:|
| G5 ADJOHLC | **4** | 2 | 1 | 0 | 0 |
| TRADABILITY SEMANTICS | **2** | 2 | 1 | 0 | 1 |
| FLOW UNIT/TS | 0 | 2 | 2 | 1 | 3 |
| ID LIFECYCLE | 0 | 2 | 1 | 1 | 3 |
| TOP100 PIT | 0 | 1 | 1 | 1 | 3 |

→ Critical defect 모두 G5 + Tradability (= measurement layer core).

### By Repair Path

| Path | Count |
|---|---:|
| requires_external_source | 16 |
| requires_both | 4 |
| requires_code_fix | 4 |
| not_repairable (informational) | 10 |

→ 외부 source 가 핵심 unblock 경로 (16/24 actionable defects).

## Critical Defects List (6)

| Defect ID | Card | Defect | Severity |
|---|---|---|---|
| G5_000001 | G5 | adjusted_column_missing | critical |
| G5_000002 | G5 | adjusted_column_is_raw_alias | critical |
| G5_000004 | G5 | extreme_return_unexplained (147 events) | critical |
| G5_000005 | G5 | event_source_missing | critical |
| TRAD_000001 | TRAD | tradability_flag_is_panel_presence_proxy | critical |
| TRAD_000002 | TRAD | true_suspension_indistinguishable | critical |

## Major Positive Findings (informational, action 불필요)

| Card | Finding |
|---|---|
| ID Lifecycle | (날짜, 종목코드) uniqueness 100% (0 duplicates) |
| ID Lifecycle | DART corp_code 94% coverage = strong permanent ID base |
| ID Lifecycle | within-DART 1:1 mapping (no code reuse detected) |
| ID Lifecycle | 833 ever-top100 names all preserved (survivor-safe) |
| Top100 | **Selection rule = 거래대금추정 top 100, 100% reproducible** (major positive) |
| Top100 | 0% estimated flag for market cap / trading value |
| Top100 | 833 unique tickers = top100 history 보존 |
| Flow | NaN = 0 across all years (data integrity) |
| Flow | Sign convention: + = buy / - = sell (sample verified) |
| Flow | Unit consistency (KRW, ratio < 1.0) |
| Trad | volume / trade_value missing same source (consistent) |
| Trad | limit_threshold 0.299 = KRX 30% rule align |

## Critical Cross-Card Insights

### 1. Selection Rule Discovery

**Top100 = 거래대금추정 top 100 (100% reproducible)**.

Migration / turnover / liquidity 카드의 universe semantics 가 사실 명확:
"daily liquidity ranked top 100".

함의: 향후 KR-LIQ-MIGRATION 의 "entry event" 는 사실 daily trading value
ranking 변동. 단 daily churn ≈ 19.6 신규 entry per day (out of 100) 이라
signal-to-noise 매우 낮음 가능성.

### 2. Round 2 Finding 정정 (CRITICAL)

Round 2 audit 에서 잘못 reported:
- ✅ `시가총액추정여부` / `거래대금추정여부` = 0% True (정확)
- ❌ `수급금액추정여부` = 0% True (Round 2 누락, 이번 발견 = **100% True**)

즉 **모든 flow value 가 vendor estimated**. 정확한 KRX 공식 X.
KR-FLOW-ABSORPTION-001 의 unblock 조건 추가.

### 3. Gate 5 가 Top100 에도 영향

Top100 selection = 거래대금추정 (= 거래량 × close). Close 가 raw → split day
의 trading value 일부 왜곡. Top100 membership 의 일부 transition 이 corp
action artifact 가능. Migration diagnostic 의 false signal source.

### 4. Tradability 의 4-Cause Distinction 가능

- volume / trade_value missing = same source (data_missing 분류 가능)
- limit_threshold = KRX 30% 정확 (limit_lock 분류 가능, 단 corp action 분리 필요)
- panel absence = `동적유니버스포함 = False` 명확 (분류 가능)
- **true_suspension = 별도 source 필요 (KRX status)**

W001 v2 의 4-cause categorical column 구현 가능 (source 확보 후).

### 5. Survivor Safety 확인

3 카드 (ID, Top100, Tradability) 가 cross-reference:
- 833 unique tickers 모두 ever-top100
- 299 disappeared 모두 panel 에 보존 (제거 X)
- terminal row 모두 tradable=False (자동 차단)

→ **Panel 은 survivor-only universe 아님**. Strong PIT 신호.

## Missing Source Priority (refined)

`docs/round3_missing_source_register.md` priority 갱신:

| Source | Round 3 Priority | Updated Note |
|---|---|---|
| **S1 Adjusted OHLC** | 🔴 critical (4 G5 critical defects + Top100 dependency) | acquisition 즉시 가치 큼 |
| **S2 Corporate Action Event Log** | 🔴 critical (G5 unblock + 147 events 분류) | S1 와 같이 필요 |
| S3 KRX Suspension Status | 🟠 high (Tradability 4-cause 완성 + Resume Risk unblock) | Tradability defect 차단 |
| S4 Permanent ID | 🟡 medium (DART 이미 94%, fallback 6% 보완) | partial OK, marginal value |
| S5 Top100 Rule | 🟢 documented (rule reverse-engineered, 추가 source 불필요) | finding 으로 충분 |
| S6 Flow Vendor Doc | 🔴 critical NEW (100% estimated finding) | doc + KRX reconciliation 필요 |

## Round 3 → Round 4 Transition Conditions

Round 3 audit 5 카드 모두 PASS or ACCEPTABLE FINDING 이 되려면:

1. **S1 + S2 acquire** → G5 critical 4건 + Top100 Gate 5 dependency unblock
2. **S3 acquire** → Tradability 4-cause distinction 완성 → Trad critical 2건 unblock
3. **S6 vendor doc** → Flow critical new finding unblock
4. (Optional) S4 fallback (6% 잔여 ticker mapping)
5. Code fix:
   - W001 v1.1 `adjust_for_corporate_actions()` naming/doc
   - W001 v2 `apply_corporate_action_adjustment(event_log, panel)`
   - `tradable_state` categorical column 추가
   - Generation script documentation

위 7 항목 통과 → 측정층 sanity check → Referee 재승인 → 새 strategy round
(Round 4) 또는 기존 BACKLOG 카드 unblock.

## Cycle 1 Final State

| Category | Count |
|---|---:|
| Active strategy TEST | 0 |
| A0 AUDIT complete (Round 3) | 5 |
| BACKLOG (strategy + infra) | 12 |
| REJECT | 0 |
| Critical defects (need source) | 6 |
| High defects | 9 |

False alpha 차단 framework **9/9 catches** (Round 2 종료 시점) + Round 3 의
data layer 무결성 공식 등록.

## Round 3 핵심 의미

**Round 3 는 새 alpha 발굴이 아니라 한국 stock-level research stack 의
measurement layer 의 정직한 상태 audit 였다.**

긍정적 finding (panel PIT 보호, 33 ticker 보존, top100 rule reproducible,
flow data integrity 등) 과 critical defect (adjusted OHLC 부재, suspension
source 부재, flow 100% estimated 등) 가 명확히 분리됨.

미래 strategy diagnostic 진입 = 사용자 host 작업 (S1, S2, S3, S6 acquire) +
W001 v2 code fix 후 가능. 그 전까지 한국 stock-level alpha research 닫힌
상태 유지.

## Compliance with Round 3 Hard Locks

5 audit 모두:
- ✅ No return computation
- ✅ No NAV / CAGR / Sharpe / MDD / alpha
- ✅ No strategy edge claim
- ✅ No P08 / paper / production / live readiness / shadow 연결
- ✅ No spec 사후 수정
- ✅ Only allowed output: defect ledger / reconciliation / pass-fail / missing source / repair feasibility

## Related Files

### Per-card outputs (5 directories)
- `reports/experiments/KR_G5_ADJOHLC_CORPACT_AUDIT_001/`
- `reports/experiments/KR_ID_LIFECYCLE_MASTER_AUDIT_001/`
- `reports/experiments/KR_TRADABILITY_SEMANTICS_AUDIT_001/`
- `reports/experiments/KR_TOP100_PIT_LINEAGE_AUDIT_001/`
- `reports/experiments/KR_FLOW_UNIT_TIMESTAMP_AUDIT_001/`

### Aggregate
- `reports/experiments/round3_aggregate/all_defects.csv` (34 defects unified)
- `reports/experiments/round3_aggregate/round3_defect_summary.md` (이 파일)

### Round 3 framework
- `docs/round3_referee_verdict_lock.md`
- `docs/round3_no_performance_rule.md`
- `docs/round3_defect_ledger_schema.md`
- `docs/round3_missing_source_register.md`
