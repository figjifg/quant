# S2 Phase Decision Brief — Round 4.1 Required Output

Date: 2026-05-22
Origin: Referee Round 4.1 lock — Round 4.1 mini Re-A0 후 S2 phase 결정

## Round 4.1 Achievement (Brief)

| Item | Result |
|---|---|
| Tradability naming (v2.1) | ✅ `panel_absence` → `not_in_dynamic_universe` + deprecated alias |
| KRX suspension cross-reference | ✅ S3 vs pykrx volume=0 = **99.4% match** (= S3 ≈ direct exchange equivalent) |
| Flow full-year stratified | ✅ 90.7% / 94.4% within ±5%, sign 100% |
| Top100 tie-break audit | ✅ 894 mismatch records ledger; 54% boundary, 46% off-boundary |
| G5 residual 35 case file | ✅ 1 strategy-relevant case + 34 universe 밖 |
| Permanent ID hardening | ✅ 50 fallback case ledger + 4 stability tests |
| Defect closure delta | 2 PARTIAL → CLOSED (TRAD_000001 + FLOW_000007-equivalent) |

## Current Hard Blocker Analysis

Round 4 → Round 4.1 후 **only remaining hard blocker = S2/C2/C3** 인지 확인:

### G5 residual

| Item | Status |
|---|---|
| G5_000004 critical (35 잔존) | Strategy-relevant = 1 event 만 (0.026% executable rows) |
| G5_000005 critical DEFERRED-S2 | S2 parser 의존 |
| C3 dependency | reserved enum 0 rows (= corp_action_day reclassification, S2 후) |

→ **Stable**. 1 strategy-relevant case 가 strategy 진입 hard block 아님 (audit trail 보존된 상태).

### Tradability direct reconciliation

| Item | Status |
|---|---|
| TRAD_000001 panel proxy | CLOSED (rename + S3 99.4% direct equivalence) |
| TRAD_000002 true_suspension | CLOSED (99.4% direct equivalence) |
| TRAD_000003 limit pollution | PARTIAL (41 rows; C3 후 corp_action_day 분리) |
| Direct KRX API | Not accessible via standard tooling (별도 priority 낮음) |

→ **Closed or well-scoped**. Direct KRX API = incremental confidence 만 (현재 99.4% 이미 충분).

### Flow residual

| Item | Status |
|---|---|
| FLOW_000007 100% estimated | CLOSED-equivalent (full year 90-96% match) |
| FLOW_000004 publication lag | PARTIAL (conservative t+1 rule, vendor exact lag 미확보) |
| Flow strategy | REMAINS CLOSED (separate Round + Referee 재승인 필요) |

→ **No longer blocking non-flow research**. Flow 가 다른 strategy 의 universe / execution 영향 X.

## S2 Phase Decision Criteria (Referee Round 4 lock)

> Only remaining hard blocker = S2/C2/C3
> AND G5 residual 35 ledger is stable
> AND tradability direct reconciliation is closed or well-scoped
> AND flow residual is no longer blocking non-flow research

| Condition | Status |
|---|---|
| Only remaining hard blocker = S2/C2/C3 | ✅ confirmed |
| G5 residual 35 ledger is stable | ✅ 1 strategy-relevant case + 34 universe 밖 |
| Tradability direct reconciliation closed or well-scoped | ✅ 99.4% direct equivalence |
| Flow residual no longer blocking non-flow research | ✅ confirmed |

→ **모든 condition 충족**. S2 phase 진입 가능 영역.

## S2 Phase Scope Recommendation

| Approach | Effort | Cost | Trade-off |
|---|---|---|---|
| A) 자체 OPENDART body parser 구축 (Codex 위임 가능) | 5-9주 | 무료 | 통제 +, 시간 큼 |
| B) Vendor parsed (FnGuide / KIS / 매경) | 1-4주 | 구독료 | 빠름, vendor field coverage 검증 필요 |
| C) Hybrid (vendor + 자체 sample 검증) | 3-6주 | 일부 구독 | 균형 |
| D) Defer S2 indefinitely | 0 | 0 | G5_000005 잔존 + 7 BACKLOG cards 영구 차단 |

## Open Items After S2 (Future)

S2 + C2 + C3 완성 후 expected:
- G5_000005 DEFERRED-S2 → CLOSED
- G5_000004 → 35 events 의 정확한 corp_action 분류 → CLOSED
- TRAD_000003 limit pollution → 41 rows corp_action_day 분리 → CLOSED
- Round 1 BACKLOG: KR-DART-BODY-RETURN-001 + KR-OVERHANG-AVOID-001 + KR-QUALITY-VALUE-RETURN-001 일부 unblock 가능

단 Strategy diagnostic 진입 = 별도 Referee 재승인 필요 (audit-first 12 항목 재확인).

## Executor Recommendation

Round 4.1 mini Re-A0 결과 = S2 phase entry **prerequisites all met**.

Recommendation:
- **Referee 결정 영역**: S2 phase entry 또는 다른 path (A/B/C/D per Referee Round 4.1 end condition)
- 사용자 host 영역: S2 acquisition approach 선택 (자체 / vendor / hybrid)

Referee Round 4.1 end condition options:
- **A. start S2 full parser phase** ← 모든 prerequisites 충족 시 추천
- B. keep strategy research closed
- C. reopen a narrowly bounded non-flow diagnostic
- D. continue infrastructure repair

→ Executor 의견 (informational): **A** = 가장 자연스러운 next step.
S2 parser 가 마지막 큰 blocker.

## Compliance with Round 4.1 Lock

- ✅ No strategy testing recommendation (only infrastructure status)
- ✅ Referee 가 결정 (S2 / strategy reopen)
- ✅ S2 planning only (build = Referee 재승인 후)
- ✅ No production / paper / P08 / live connection

## Related

- `docs/round4_1_v2_1_referee_lock.md`
- `docs/W001_v2_infrastructure_repair_plan.md` (C2/C3 spec)
- `docs/s2_opendart_body_parser_plan.md` (Round 4 S2 plan)
- `reports/experiments/round4_1_v2_1/round4_1_closure_delta.csv`
- Five Round 4.1 validation md files
