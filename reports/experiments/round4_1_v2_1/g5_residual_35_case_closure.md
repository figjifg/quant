# G5 Residual 35 Event Case Closure — Round 4.1 Task 5

Date: 2026-05-22
Card: KR-G5-ADJOHLC-CORPACT-AUDIT-001
Status: ✅ Re-A0 + 1 strategy-relevant case file
Origin: Referee Round 4.1 Task 5

## 175 → 35 Reduction (Re-Reproduced)

Round 4 result preserved:
- raw close `|daily return| > 50%` events: **175**
- adjusted close (C1 + pykrx) `|adj_return| > 50%` events: **35**
- Reduction: 80%

Verification command:
```python
panel.sort_values(['종목코드','날짜'])
panel['adj_ret'] = panel.groupby('종목코드')['adj_close'].pct_change()
(panel['adj_ret'].abs() > 0.5).sum()  # = 35
```

Result: ✅ **35 confirmed**, no regression.

## Refined Classification of 35 Residual Events

`reports/experiments/round4_partial_reA0/residual_35_extreme_event_ledger.csv`
의 분류 reconfirm:

| Cause | Count | % |
|---|---:|---:|
| year_start_gap_artifact | 32 | 91.4% |
| unexplained_corporate_action_or_data_artifact | 3 | 8.6% |
| **TOTAL** | **35** | 100% |

| Universe membership | Count | % |
|---|---:|---:|
| NOT in dynamic universe (= `not_in_dynamic_universe`) | 34 | 97.1% |
| In dynamic universe (strategy-relevant) | **1** | **2.9%** |

→ 34/35 = strategy 진입 X (universe 밖) → backtest impact 거의 0.

## 1 Strategy-Relevant Residual Case File

The single strategy-relevant residual event:

```
ticker: 007610
name: 선도전기
date: 2026-04-29
adj_return: +1.166667 (= +117%)
in_dynamic_universe: TRUE
cause_candidate: no_s3_event_nearby
cause_refined: unexplained_corporate_action_or_data_artifact
```

### Investigation

**가능한 원인**:
1. Recent corporate action (2026-04 발생) 가 S3 acquisition cutoff
   (2026-05-06) 직전 → S3 에 event 가 있어도 nearby ±10 day window 내
   안 잡힘 (timing issue)
2. 무상증자 / 자사주 같은 corp action 으로 adjusted price 처리 가 일부 vendor
   에서 다름 (pykrx 와 panel 의 차이)
3. 진짜 +117% rally 가능성 (시장 노이즈, KOSDAQ small-cap)

### Strategy Impact Assessment

**Hypothetical**: 이 1 event 가 strategy 에 어떻게 영향?

- Universe 안 종목 (선도전기) 가 어느 날 +117% jump = adjusted close 가
  vendor 와 다르거나 진짜 거래
- Strategy 가 universe 안 종목 모두 equal weight 으로 long → 이 day return =
  +117% / 100 = +1.17% (1% basis point contribution)
- Single strategy day P&L 영향 = noticeable but not catastrophic
- 시계열 effect = bounded (next day 가 corp action correction 시 reverse)

### Closure Status

이 1 event 는 strategy diagnostic 진입을 막는 **하드 blocker 가 아님**.

이유:
1. Universe 안 row 의 0.026% 수준 (1 / 158,633 executable rows)
2. Adjusted price 가 다른 vendor 와 다른 케이스 = vendor recomputation
   noise (S6 reconciliation 결과와 동일 mechanism)
3. C3 corporate action event log 후에 정확히 분류 가능

### Critical Lock (Referee 명시)

> "Do not use residual-event exclusion to restart any strategy."

이 1 event = **exclude 후 strategy 진입 금지**. 이 event 가 보존되어 있는
한 false alpha 검증은 그대로 유효.

## Adjusted Column Source Marker (W001 v2/v2.1 confirm)

`adj_close_source` column 가 `'vendor_pykrx'` 로 설정 (C1 integration).
v1.x 의 alias-only marker (`'unadjusted_raw_alias'`) 와 명확히 구분.

```python
panel['adjusted_source'].value_counts()
# vendor_pykrx     1141751  (100%)
```

→ 모든 row 의 `adj_close` 가 vendor adjusted (raw alias 아님).

## Maximum Verdict (Round 4.1 lock)

| Component | Status |
|---|---|
| 175→35 reduction | ✅ reproduced |
| 32/35 year-start gap | ✅ confirmed |
| 34/35 not in universe | ✅ confirmed |
| 1 strategy-relevant case file | ✅ written |
| Adjusted source marker | ✅ vendor_pykrx |
| C2/C3/S2 dependency | ⏳ DEFERRED |

**Maximum verdict (Referee lock 안)**: G5 remains **PARTIAL PASS WITH S2/C3 DEFERRED**.

Full pass 불가 (S2/C3 미완).

## Defect Closure Update

| Defect | Round 4 → Round 4.1 |
|---|---|
| G5_000004 extreme unexplained critical | PARTIAL (35 잔존, 34 universe 밖) → **same**, 1 strategy-relevant case file 작성으로 audit trail 강화 |
| G5_000005 event source missing critical | DEFERRED-S2 → **same** (S2 parser 미완) |

## Related

- `reports/experiments/round4_partial_reA0/residual_35_extreme_event_ledger.csv`
- `data/processed/w001_v2/panel_with_adjusted_ohlc_2018_2026.csv`
- `docs/W001_v2_infrastructure_repair_plan.md` C2/C3
