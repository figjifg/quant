# Adjustment Engine Requirements (W001 v1 → v2)

Date: 2026-05-22
Status: Documentation of current behavior + required changes
Origin: Round 2 Step 5 Option D allowed action #6 (`adjust_for_corporate_actions()` 검증)
Referee lock: `docs/round2_gate5_fail_lock.md`

## Current Behavior — `src/utils/corporate_action.py`

### Function: `adjust_for_corporate_actions(panel, policy)`

코드 분석 결과 (line-by-line audit):

```python
for field, source in price_cols.items():
    out[source] = pd.to_numeric(out[source], errors="coerce")
    out[f"adjusted_{field}"] = out[source]           # ← alias only
    out[f"adjusted_{field}_source"] = source
```

즉 `adjusted_close = 종가` (단순 copy). 가격 값 조정 X.

이어서:

```python
close = out["adjusted_close"]
ret = close.groupby(out[ticker_col], sort=False).pct_change()
out["corporate_action_candidate"] = ret.abs().gt(policy.split_gap_threshold).fillna(False)
split_like = ret.abs().gt(policy.max_abs_single_period_return).fillna(False)
out["impossible_return_flag"] = split_like
out["adjustment_factor"] = 1.0
if split_like.any():
    out.loc[split_like, "adjustment_factor"] = 1.0 / (1.0 + ret.loc[split_like])
```

→ `adjustment_factor` column 생성, split_like row 에서 reverse factor 만
계산. **단 실제 price 값에 적용 X**.

Docstring (line 80-83):
> "If adjusted columns are already present, they are used. Otherwise the local
> panel close is treated as adjusted when available. A conservative backward
> factor is computed only for split-like gaps over 50%; 5% gaps are retained
> as candidates in metadata rather than force-adjusted."

→ "Fail-soft adjustment metadata: **leave prices intact for auditability**"
(line 104-105 주석).

## Design Intent vs Risk

### 의도 (Design)
- Adjusted columns 없는 panel 에서도 함수 호출 가능하게 함 (fail-soft)
- Audit 용 metadata (`corporate_action_candidate`, `impossible_return_flag`,
  `adjustment_factor`) 만 생성
- 진짜 가격 조정은 별도 source 가 있을 때만

### Risk (현재 사용 시)
- 함수 이름 `adjust_for_corporate_actions` 가 **misleading**
- 사용자 / downstream code 가 "adjusted price 를 받았다" 고 가정 가능
- 실제로는 raw price 그대로
- 147 corporate action artifact (Gate 5 fail 의 원인) 가 그대로 잔존

## Required Changes (W001 v1.1 or v2)

### 1. Naming / Documentation Fix (낮은 우선순위, 즉시 가능)

- 함수 이름 변경 후보:
  - `add_adjustment_metadata()` (실제 동작 반영)
  - `prepare_adjustment_aliases()` (alias 동작 반영)
- 기존 이름 deprecated 표시 + 새 이름으로 redirect
- Docstring 의 "leave prices intact" 를 함수 정의 부분에 명시
- `adjusted_*_source` column 의 value 에 `"unadjusted_raw_alias"` 등 명시

### 2. Adjusted OHLC Source Acquisition (높은 우선순위, 사용자 host)

`docs/data_gap_adjusted_ohlc.md` 의 Acceptable Source Requirements 참조:

- Adjusted OHLCV 모두 (open / high / low / close / volume)
- PIT (사후 정정 X)
- Corporate action event log + effective date linkage
- Cancellation / withdrawal handling
- Splits / merges / reductions / rights issues 구별

### 3. New Function: Actual Price Adjustment (W001 v2)

```python
def apply_corporate_action_adjustment(
    panel: pd.DataFrame,
    event_log: pd.DataFrame,
    policy: CorporateActionPolicy | None = None,
) -> pd.DataFrame:
    """
    Apply actual corporate action adjustment using an event log.
    
    Required event_log schema:
    - ticker, event_date, effective_date, event_type (split/merge/rights/reduction),
      factor (adjustment factor), shares_before, shares_after
    
    Returns panel with:
    - adjusted_open, adjusted_high, adjusted_low, adjusted_close (real adjusted)
    - adjustment_factor_cumulative (chronological cumulative)
    - source = 'event_log_applied'
    """
    ...
```

### 4. Tradability Mask Integration (W001 v2)

`src/utils/tradability.py` 의 `tradable_mask()` 에서 corporate action day
는 limit_lock 으로 분류하지 않도록:

```python
# 현재 (false positive 발생):
limit_open = (open_px / prev_close - 1.0).abs().ge(policy.limit_threshold).fillna(False)
mask &= ~limit_open

# 권장 (corporate action 분리 후):
limit_open = (adjusted_open_px / adjusted_prev_close - 1.0).abs().ge(policy.limit_threshold).fillna(False)
corporate_action_day = panel.get("corporate_action_candidate", False)
limit_lock_true = limit_open & ~corporate_action_day
mask &= ~limit_lock_true
```

### 5. 4-Cause Attribution Column (W001 v2)

`tradable_mask()` 가 binary 가 아니라 4-cause categorical column 생성:

```python
def tradable_state(panel) -> pd.Series:
    """
    Returns categorical: 
    'executable' / 'true_suspension' / 'limit_lock' / 'panel_absence' /
    'data_missing' / 'delisting_transition'
    """
    ...
```

이 column 으로 Round 2 Gate 3 (4-cause distinction) 충족 가능.

## Block Impact

| 의존 카드 | Block 사유 |
|---|---|
| KR-LIQ-FRAGILITY-AVOID-001 | adjusted price 없으면 fragility signal 오염 |
| KR-LIQ-MIGRATION-001 | market cap jump 계산 시 split 효과 잘못 측정 |
| KR-TURNOVER-ATTENTION-001 | turnover spike 가 split artifact 인지 구분 X |
| KR-TRADABILITY-RESUME-RISK-001 | 4-cause distinction 불가 → Step 3-5 진입 X |

## Backlog Linkage

이 requirements 는 새 backlog task **`W001-V1-ADJUSTED-OHLC-CORPORATE-ACTION-AUDIT-001`**
(`docs/backlog_register.md` 참조) 의 minimum artifact 중 하나 (artifact #4).

다음 우선순위 (사용자 host 결정 필요):

| 우선 | 작업 | Effort |
|---|---|---|
| P0 | Adjusted OHLC source acquisition (data_gap_adjusted_ohlc.md 참조) | High |
| P0 | KRX suspension/delisting status source | Medium |
| P1 | `tradable_mask()` 의 4-cause attribution column 추가 | Low (코드만, source 필요) |
| P1 | `adjust_for_corporate_actions()` naming/doc fix | Low |
| P2 | W001 v2 = `apply_corporate_action_adjustment()` 구현 | Medium (event log 가 있을 때) |
| P2 | tradable_mask 의 corporate action 분리 logic | Low |

## Related

- `src/utils/corporate_action.py` — 현재 함수 코드
- `src/utils/tradability.py` — 현재 mask 코드
- `docs/round2_gate5_fail_lock.md` — Round 2 Step 5 Option D lock
- `docs/data_gap_adjusted_ohlc.md` — adjusted OHLC 부재 상세
- `docs/tradability_semantics_audit.md` — 4-cause distinction audit
- `reports/experiments/W001_V1_AUDIT/corporate_action_artifact_ledger.csv` — 147 events
