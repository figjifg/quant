# KR-TURNOVER-ATTENTION-001 — A0 Diagnostic Spec (Priority 4)

## Status
PRE-REGISTERED · TEST · **lower priority A0 diagnostic**, KR-LIQ-MIGRATION 중복 감시
Round 2 Priority: 4
Date: 2026-05-22

## Cycle Lineage

- Round 2 Bull idea #4
- Referee Round 2 lock: **TEST (lower priority, market cap PIT + corporate
  action checks 강화)**
- KR-LIQ-MIGRATION-001 과 liquidity / attention 계열 **overlap 있음**. A0
  후 더 단순하고 견고한 쪽을 남기는 방식.

## Scope

Trading value / market cap 기반 turnover regime shift A0 diagnostic 허용.
**Lower priority** = 다른 카드들 결과 후 의미 있게 남아야 진행 가치 있음.

## Hypothesis

Turnover regime shift (trading_value / market_cap 의 급격한 증가) 가
hidden momentum / corporate action artifact 가 아닌 진짜 attention regime
변화일 때, 종목 forward window 의 (locked-position incidence / left-tail /
exit infeasibility) 에 영향을 주는지 진단.

**살아남으려면**: high raw trading value baseline + 20d momentum baseline +
matched control 모두 이긴 후.

## Required Global Gates

`docs/round2_global_A0_gates.md` 10 gate 모두 적용. 특히:
- **Gate 5 Adjusted OHLC sanity (핵심: split / 증자 시 share count artifact)**
- **Gate 6 Market cap PIT (핵심: turnover 계산의 분모)**
- Gate 1 Permanent ID
- Gate 2 Survivorship
- Gate 7 Event ledger

## Required A0 Checks (Referee 명시)

| Check | 이유 |
|---|---|
| Market cap PIT lineage | turnover = trading_value / market_cap 계산의 핵심 |
| Adjusted OHLC / share count sanity | split / reduction / rights issue artifact 방지 |
| Corporate action proximity filter | 감자 / 증자 / 합병 주변 spike 제거 (±5d) |
| ret20-neutral condition 검증 | hidden momentum 방지 |
| Trading value missingness check | liquidity artifact 방지 |

## Signal Definition

각 종목 × 날짜:

- `turnover_t` = trading_value(t) / market_cap(t) (PIT)
- `turnover_zscore` = (turnover_t - rolling_mean(60d)) / rolling_std(60d)
- `turnover_regime_shift` = turnover_zscore 가 상위 decile 진입
- `ret20_neutral` = trailing 20d return 이 절대값 1 표준편차 이내 (= 가격이 크게 안 움직임)
- `event_flag` = (turnover_regime_shift = true) AND (ret20_neutral = true)
  AND (corporate_action_proximity = none)

**Tuning 금지**: decile threshold / window size 사후 조정 X.

## Required Baselines (모두 필수)

| Baseline | 필수 | 목적 |
|---|---|---|
| High raw trading value basket | ✅ | turnover 가 단순 trading value 효과 아닌지 |
| High turnover-level basket (turnover_t 만, regime shift X) | ✅ | regime shift 가 level 과 다른지 |
| High 20d return momentum basket | ✅ | hidden momentum 분리 |
| Market cap / trading value / 20d return matched non-signal | ✅ | matched non-signal |
| ret20-neutral condition 제거 버전 | ✅ | ret20 condition 의 incremental value |
| Market cap permutation placebo | ✅ | market cap PIT artifact 확인 |

## Required Event Ledger

`docs/round2_event_ledger_schema.md` 그대로. 각 `event_flag = true` = 1 event.

추가 column:
- `turnover_t`
- `turnover_zscore`
- `trailing_return_20d`
- `corporate_action_proximity` (none / split_within_5d 등)
- `market_cap_jump_5d` (split / 증자 시 jump 감지)

출력: `reports/experiments/KR_TURNOVER_ATTENTION_001/event_ledger.csv`

## A0 Diagnostic Metrics

Round 2 우선순위 (Gate 10) 그대로:

1. Locked-position incidence
2. Exit infeasibility ratio
3. Left-tail loss
4. MDD
5. After-cost return

비교: event_flag = true vs 6 baseline.

## Overlap Watch with KR-LIQ-MIGRATION-001

| Sub-check | 처리 |
|---|---|
| KR-LIQ-MIGRATION 의 entry_event 와 본 카드의 event_flag 의 overlap 비율 | 명시 |
| Overlap 비율 ≥ 80% | 사실상 동일 signal, 하나만 유지 (Referee 결정 trigger) |
| 두 카드 간 unique event 비교 | unique event 의 incremental metric 측정 |

## Kill Gates (Referee 명시)

| Failure | Decision |
|---|---|
| Market cap 이 non-PIT 또는 restated vendor field | KILL (Gate 6) |
| Turnover spike 가 corporate action artifact | KILL (Gate 5) |
| High raw trading value baseline 과 차이 없음 | KILL |
| High 20d momentum baseline 과 차이 없음 | KILL (= hidden momentum) |
| KR-LIQ-MIGRATION 과 사실상 동일 signal (overlap ≥ 80%) | 하나만 유지 (Referee 재심의) |
| After-cost diagnostic 에서 의미 없음 | KILL |

## Forbidden (Round 2 lock)

- Standalone alpha 측정 시도
- Production / paper / P08 / live readiness / shadow track 연결
- Decile / window 사후 tuning
- ret20-neutral condition 사후 변경
- spec 사후 수정 (Bear 재심의 없이)

## Codex Implementation Task

```
Implement KR-TURNOVER-ATTENTION-001 A0 diagnostic.

DO NOT:
- Use restated market cap
- Skip corporate action proximity filter
- Skip ret20-neutral condition
- Run return backtest before event ledger + gate check pass
- Connect to P08 / paper tracking / production
- Modify research_input_data/ files

Tasks:
1. Verify Gate 5 (adjusted OHLC + share count sanity).
2. Verify Gate 6 (market_cap is PIT, no vendor restatement).
3. Apply corporate action proximity filter (±5d split/merge/reduction/rights/resumption).
4. Build event_flag (turnover regime shift + ret20-neutral + corp action none).
5. Generate event ledger.
6. Compute Round 2 priority metrics across 6 baselines.
7. KR-LIQ-MIGRATION-001 overlap check (event ID intersection).
8. If overlap ≥ 80%: stop, escalate to Referee.
9. Save outputs under reports/experiments/KR_TURNOVER_ATTENTION_001/.

Required outputs:
- config.yaml (locked scope, lower priority)
- event_ledger.csv (per round2 schema + 추가 column)
- ledger_audit.md
- gate_check.md
- baselines_comparison.csv (5 metric x 7 group, event vs 6 baseline)
- migration_overlap.md (KR-LIQ-MIGRATION 와 event ID 비교)
- report.md (A0 diagnostic only, NO production language)
```

## Result Summary

작성 금지.

## Bull/Bear/Referee Review

작성 금지.
