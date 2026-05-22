# KR-TRADABILITY-RESUME-RISK-001 — A0 Diagnostic Spec (Priority 2)

## Status
PRE-REGISTERED · TEST · **infrastructure A0 first, strategy diagnostic second**
Round 2 Priority: 2
Date: 2026-05-22

## Cycle Lineage

- Round 2 Bull idea #2
- Referee Round 2 lock: **TEST (infrastructure A0 first)**
- Bear 권고 : alpha mining 보다 infrastructure audit 가치가 큼

## Scope

이 카드는 **alpha 카드 아님**. 먼저 W001 tradability infrastructure 감사
카드. Strategy diagnostic 은 infrastructure A0 통과 후 second-stage only.

## Hypothesis (infrastructure-first)

거래정지 후 재개되는 종목에서 5d / 20d / 63d window 에 tail loss, gap risk,
재정지 incidence 가 통계적으로 의미 있게 높다. 따라서:

1. (Infrastructure) W001 tradability flag 가 정확히 4 cause 를 구분 가능한가?
2. (Strategy) 재개 직후 종목을 long-only basket 에서 limited 기간 제외하면
   tail risk 가 줄어드는가?

## Required Test Order (LOCKED, sequential only)

| Step | 내용 | 다음 단계 진입 조건 |
|---|---|---|
| 1 | Tradability flag lineage audit | flag 의미 확인 (4 cause 구분 가능) |
| 2 | Panel absence vs true suspension vs limit-lock 구분 | 구분 가능해야 함 |
| 3 | Resumption event count 확인 | 충분한 event count (≥ 50) |
| 4 | 재개 후 5d / 20d / 63d diagnostic | tail / gap / 재정지 확인 |
| 5 | Long-only basket exclusion filter 효과 확인 | A0 (Step 1-4) 통과 후만 |

**Step 1-4 통과 전 Step 5 진입 금지.** Step 1 fail 시 카드 자체 kill.

## Required Global Gates

`docs/round2_global_A0_gates.md` 10 gate 모두 적용. 특히:
- **Gate 3 Tradability semantics (핵심, 이 카드의 raison d'être)**
- Gate 1 Permanent ID
- Gate 4 Locked limit handling
- Gate 5 Adjusted OHLC sanity (재개 후 price gap)
- Gate 7 Event ledger

## Required Tradability Cause Distinction (Step 2 핵심)

`tradable=false` 의 4 cause 명확 구분:

| Cause | 처리 | Event 가능? |
|---|---|---|
| 실제 거래정지 / 매매정지 | KRX 공식 suspension | ✅ Yes |
| Limit-lock (상한가 / 하한가 종가 고정) | locked-position rule | ⚠ 별도 처리 |
| Panel absence (당시 universe 밖) | strategy event 아님 | ❌ No |
| Data missing (vendor 누락) | strategy event 아님 | ❌ No |
| Delisting transition | terminal event | ⚠ 별도 처리 |

**구분 불가 시 → KILL** (Step 2 통과 X).

## Step 3-4 Resume Event Diagnostic

- Resumption event = 실제 거래정지 (cause = `true_suspension`) 후 재개되는
  종목의 첫 거래일
- Event count 가 50 미만 = statistical power 부족 = kill
- 각 event 별 forward 5d / 20d / 63d 측정:
  - Return distribution
  - Gap (재개일 첫 거래 price vs 정지 직전 price)
  - 재정지 incidence (window 내 다시 suspension 발생)
  - Delisting incidence

## Step 5 Long-Only Filter Effect (A0 통과 후만)

연구용 long-only basket (W001 universe 또는 dynamic_top100) 에서:
- 재개 후 N 일 (N = 5 / 20 / 63 별도 측정) 동안 해당 종목 제외
- Filtered vs original basket 비교 (Round 2 priority metric)

## Required Controls

| Control | 목적 |
|---|---|
| Random exclusion (같은 비율) | random control |
| 모든 suspension cause 동시 처리 (4 cause 합산) | semantic check |
| Limit-lock-only exclusion | locked-limit 효과 분리 |
| Panel-absence-only exclusion (placebo) | 진짜 suspension 효과 분리 |
| Event-date shift placebo (±20d) | calendar / event timing placebo |

## Required Event Ledger

`docs/round2_event_ledger_schema.md` 그대로. 각 resumption = 1 event.

추가 ledger column (이 카드 specific):
- `suspension_cause` (vendor 코드 + 4 cause 분류)
- `suspension_start_date`
- `resumption_date`
- `pre_suspension_close`
- `resumption_open`
- `gap_pct` (resumption_open / pre_suspension_close - 1)
- `re_suspension_within_5d` (bool)
- `re_suspension_within_20d` (bool)
- `re_suspension_within_63d` (bool)
- `delisting_within_63d` (bool)

출력: `reports/experiments/KR_TRADABILITY_RESUME_RISK_001/event_ledger.csv`

## A0 Diagnostic Metrics

Round 2 우선순위 (Gate 10) 그대로:

1. **Locked-position incidence** (재개 직후 locked-limit 비율)
2. **Exit infeasibility ratio** (재개 후 N일 exit 시도 시 실패 비율)
3. **Left-tail loss** (재개 후 5/20/63d return 의 5% / 10% VaR)
4. **MDD** (filtered vs original)
5. **After-cost return** (filtered vs original)

## Kill Gates (Referee 명시)

| Failure | Decision |
|---|---|
| Tradability flag 가 실제 suspension 이 아니라 data missing | KILL (Step 2 fail) |
| Resumption event count 부족 (< 50) | KILL (Step 3 fail) |
| 재정지 / 상폐 / merged ticker 처리 없음 | KILL (Step 4 fail) |
| Random exclusion 과 차이 없음 | KILL (Step 5 fail) |
| Locked-limit execution rule 없음 | KILL (Gate 4 fail) |

## Forbidden (Round 2 lock)

- Standalone alpha 측정 시도
- Step 1-4 통과 전 Step 5 진입
- Production / paper / P08 / live readiness / shadow track 연결
- 사후 corporate action 결과 사용
- spec 사후 수정 (Bear 재심의 없이)

## Codex Implementation Task

```
Implement KR-TRADABILITY-RESUME-RISK-001 A0 diagnostic.

DO NOT:
- Skip Step 1-4 order
- Implement as standalone alpha
- Run return backtest before Step 1-4 pass
- Connect to P08 / paper tracking / production
- Modify research_input_data/ files

Tasks (sequential, 순서 변경 X):
1. Step 1: tradability flag lineage audit (W001 tradability.py + vendor source).
   If flag 의미 불분명: KILL, stop. Report Step 1 only.
2. Step 2: 4-cause distinction (true_suspension / limit_lock / panel_absence
   / data_missing / delisting_transition). If 구분 불가: KILL, stop.
3. Step 3: resumption event count (cause = true_suspension only). If < 50:
   KILL, stop.
4. Step 4: forward 5d / 20d / 63d diagnostic (return distribution, gap,
   re-suspension, delisting incidence).
5. Step 5: filter effect on long-only basket (A0 ONLY, Round 2 priority
   metrics).

Required outputs:
- config.yaml (locked scope, infrastructure-first)
- event_ledger.csv (per round2 schema + 추가 column)
- ledger_audit.md
- step1_lineage_audit.md
- step2_cause_distinction.md
- step3_event_count.md
- step4_forward_diagnostic.csv
- step5_filter_effect.csv (A0 통과 시만)
- gate_check.md
- report.md (A0 diagnostic only, NO production language)
```

## Result Summary

작성 금지.

## Bull/Bear/Referee Review

작성 금지.
