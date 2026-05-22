# KR-LIQ-FRAGILITY-AVOID-001 — A0 Diagnostic Spec (Priority 1)

## Status
PRE-REGISTERED · TEST · **A0 diagnostic only** · exclusion filter only
Round 2 Priority: 1
Date: 2026-05-22

## Cycle Lineage

- Round 2 Bull idea #1
- Referee Round 2 lock: **TEST (A0 diagnostic only, exclusion filter only)**
- A0 통과 전 NAV / CAGR / Sharpe / alpha / excess return 표 작성 금지

## Scope

이 카드는 **standalone alpha 아님**. long-only basket 의 liquidity
deterioration / exit fragility **exclusion filter** 로만 허용.

### Allowed question

> "fragile 종목을 제외하면 noisy long-only basket 의 tail risk, exit
> infeasibility, slippage exposure 가 줄어드는가?"

### Not allowed question

> "fragile avoidance 가 독립 alpha 인가?"

## Hypothesis (filter only)

ADV 감소 + tradability flag 변동 + locked-limit incidence 증가가 동시에
나타나는 종목 (fragile signal) 을 long-only basket 에서 제외하면, basket
의 left-tail / MDD / locked-position incidence / exit infeasibility 가
의미 있게 줄어든다.

## Required Global Gates

`docs/round2_global_A0_gates.md` 10 gate 모두 적용. 특히:
- Gate 1 Permanent ID (필수)
- Gate 2 Survivorship (dynamic_top100 PIT 확인)
- Gate 3 Tradability semantics (fragile signal = artifact 위험 핵심)
- Gate 4 Locked limit (보수적 처리 필수)
- Gate 5 Adjusted OHLC sanity
- Gate 7 Event ledger (`docs/round2_event_ledger_schema.md`)
- Gate 8 Controls (random / matched / simple baseline 필수)

## Fragile Signal Definition (binary, A0 단계)

각 종목 × 날짜 에 대해 다음 모두 만족 = fragile flag:

- ADV (20d) 가 직전 60d 의 bottom decile
- 직전 60d 내 tradability 변동 (suspension / resumption) 1회 이상
- 직전 20d 내 locked-limit incidence 비율 상위 decile

**중요**: 이 정의는 A0 단계 binary 만. intensity / score weight tuning 금지.

## Filter Application

- Universe: dynamic_top100 (PIT 확인 후) 또는 다른 검증된 long-only research basket
- 매 rebalance 일에 fragile flag = true 종목 **제외**
- Production basket 연결 X (filter 효과는 연구용 basket 안에서만 평가)

## Required Baselines (모두 필수)

| Baseline | 필수 | 목적 |
|---|---|---|
| Original dynamic_top100 equal-weight | ✅ | reference (filter 적용 X) |
| Fragile-excluded dynamic_top100 | ✅ | 본 signal |
| Random exclusion (같은 비율) | ✅ | random control |
| Low-ADV exclusion (단순) | ✅ | fragile = ADV artifact 분리 |
| High-volatility matched exclusion | ✅ | fragile = vol artifact 분리 |
| Market cap / ADV / volatility matched non-fragile control | ✅ | matched non-signal |

## Required Event Ledger

`docs/round2_event_ledger_schema.md` 그대로. 각 fragile flag = 1 event,
각 matched control = 별도 event row (`is_matched_control = True`).

출력: `reports/experiments/KR_LIQ_FRAGILITY_AVOID_001/event_ledger.csv`

## A0 Diagnostic Metrics (Round 2 우선순위)

성과 표 작성 **금지**. A0 단계 = ledger 기반 다음 metric 만:

1. **Locked-position incidence** (filtered vs original)
2. **Exit infeasibility ratio** (filtered vs original)
3. **Left-tail loss** (5% / 10% VaR, filtered vs original)
4. **MDD** (filtered vs original)
5. **After-cost return** (filtered vs original, 비교용만)

CAGR / Sharpe / gross return = 후순위, 보고 시 secondary 로만 표기.

## Kill Gates (Referee 명시)

다음 중 하나라도 발생 → **KILL**:

| Failure | Decision |
|---|---|
| Fragile signal 이 missing data artifact | KILL |
| 단순 low-ADV exclusion 과 구분 안 됨 | KILL |
| Delisted / suspended 종목 누락 (survivorship) | KILL |
| Limit-down exit 처리 불가능 | KILL |
| After-cost tail 개선 없음 | KILL |
| Random exclusion 과 차이 없음 | KILL |

## Forbidden (Round 2 lock)

- Standalone alpha 측정 시도 (long signal score 등)
- Long-short 변형
- Production / paper / P08 / live readiness / shadow track 연결
- 사후 corporate action 결과 사용
- spec 사후 수정 (Bear 재심의 없이)

## Codex Implementation Task

```
Implement KR-LIQ-FRAGILITY-AVOID-001 A0 diagnostic only.

DO NOT:
- Run return backtest before A0 + event ledger gates pass
- Implement as standalone alpha
- Implement long-short variant
- Connect filtered basket to P08 / paper tracking / production
- Modify research_input_data/ files
- Use future data
- Aggregate metrics before event ledger sanity check

Tasks:
1. Verify Gate 1 (permanent identifier) on dynamic_top100 panel.
2. Verify Gate 2 (dynamic_top100 PIT, survivorship safe).
3. Verify Gate 3 (tradability_state 4-cause distinction).
4. Verify Gate 4 (locked-limit handling rule).
5. Verify Gate 5 (adjusted OHLC sanity).
6. Build fragile flag (binary, per spec definition).
7. Generate event ledger (round2_event_ledger_schema.md).
8. Run pre-diagnostic checklist (ledger sanity).
9. Compute A0 metrics: locked-position incidence / exit infeasibility /
   left-tail / MDD / after-cost (priority order).
10. Save outputs under reports/experiments/KR_LIQ_FRAGILITY_AVOID_001/.

Required outputs:
- config.yaml (locked scope, filter-only)
- event_ledger.csv (per round2 schema)
- ledger_audit.md (event count, tradability distribution, locked incidence,
  control coverage)
- A0_diagnostic.csv (6 baseline x 5 priority metric)
- gate_check.md (Gate 1-10 PASS/FAIL/PARTIAL)
- report.md (A0 diagnostic only, kill gate evaluation, NO production language,
  NO CAGR/Sharpe headline)
```

## Result Summary

작성 금지. Bear interpretation step (Step 6) 후 채워짐.

## Bull/Bear/Referee Review

작성 금지. 사이클 Step 7-9 후 채워짐.
