# Tradability Semantics Audit (W001 v1)

Date: 2026-05-22
Status: **Gate 3 FAIL** confirmed
Origin: Round 2 Step 5 Option D allowed action #5
Referee lock: `docs/round2_gate5_fail_lock.md`

## Issue

Round 2 Global Gate 3 (`docs/round2_global_A0_gates.md`) 의 요구: `tradable=false`
를 4-cause 로 명확히 구분.

| Cause | 처리 |
|---|---|
| 실제 거래정지 / 매매정지 | strategy event 가능 |
| Limit-lock | 별도 locked-position rule |
| Panel absence (universe 밖) | strategy event 아님 |
| Data missing (vendor 누락) | strategy event 아님 |
| Delisting transition | terminal event |

W001 v1 `tradable_mask()` 현재 동작 분석 결과 = **4-cause 구분 불가**.

## Evidence

Panel: `dynamic_top100_2018_2024_panel.csv` (969,208 rows, 2018-2024)

| Metric | Value | 비율 |
|---|---:|---:|
| Total rows | 969,208 | 100% |
| tradable=True | 172,002 | **17.75%** |
| tradable=False | 797,206 | **82.25%** |

### tradable=False 의 component 분해 (mutually inclusive, mask AND 구성)

| Component | Count | 비율 |
|---|---:|---:|
| OHLC missing 또는 ≤ 0 | 7,450 | 0.77% |
| Trading value missing 또는 ≤ 0 | 7,450 | 0.77% |
| Trade value estimated flag = True | 0 | 0.00% |
| NOT in dynamic universe (`동적유니버스포함 = False`) | **797,108** | **82.24%** |
| Limit move at open (\|open/prev_close - 1\| ≥ 29.9%) | 7,772 | 0.80% |
| Status column (`상태`/`종목상태`) | **N/A** | panel 에 컬럼 없음 |

### Priority-based 4-cause classification 시도

`tradable=False` 행을 priority 순으로 단일 cause 에 attribution:

| Classified cause | Count | 비율 |
|---|---:|---:|
| `panel_absence` | 649,090 | 81.42% |
| `unknown` (어느 component 에도 명확히 attribution 안 됨) | **141,693** | 17.78% |
| `data_missing` (OHLC bad) | 6,165 | 0.77% |
| `limit_lock_candidate` (open limit move) | 258 | 0.03% |
| `true_suspension_candidate` (tv ≤ 0 + in universe) | 0 | 0.00% |

## Findings

### 1. Panel absence dominates (82.24%)

대부분의 `tradable=False` 는 단순히 "그 날짜의 dynamic top100 universe 밖"
이라는 의미. 실제 거래정지 / limit lock 과 무관.

### 2. True suspension 별도 분류 불가

`STATUS_COLS = ("status", "상태", "종목상태")` 가 panel 에 존재하지 않음.
즉 KRX 공식 매매정지 status 가 panel 에 없음. trading value = 0 만으로
true_suspension 추정 시도했으나, **0 건**으로 분류됨 (universe 밖이 먼저
필터링됨).

→ 4-cause 중 `true_suspension` 구분 **불가**.

### 3. Limit-lock 만 부분 분리 가능 (단 corporate action artifact 오염)

`open / prev_close - 1` 의 절댓값 ≥ 29.9% 행: 7,772 건.
단 priority classification 후 limit_lock_candidate = 258 건만 남음.

**이 limit_lock_candidate 자체도 오염**: `data_gap_adjusted_ohlc.md` 의
147 corporate action artifact 중 **146 건 (99.3%)** 이 open_limit_move 로
잘못 분류됨 (split / 액면병합 day 가 limit move 처럼 보임).

→ "Limit-lock" 카테고리 신뢰성 매우 낮음.

### 4. Unknown 141,693 건 (17.78%)

어느 named component 에도 명확히 attribution 안 되는 행. 가능한 원인:
- `groupby + shift` 의 첫 row NaN 으로 인한 false (`prev_close` NaN 시 limit
  계산이 False)
- Mask 의 NaN 처리 의도하지 않은 부수 효과
- 또는 `tradable_mask()` 의 다른 implicit 조건

→ `tradable_mask()` 의 의도가 명확히 표현되지 않음. Reverse engineering
필요.

### 5. Panel absence vs in-universe tradability 구분 어려움

`동적유니버스포함 = True` 인 행만 보면 (172,100 rows = 동적 top100 안):
- 그 중 `tradable=True` = 172,002 = 99.94%
- `tradable=False` (동적 universe 안) = 98 rows = 0.06%

→ 동적 universe 안에서는 거의 모든 행이 tradable. 즉 tradability mask 가
사실상 "in_dynamic_universe + 일부 limit / OHLC sanity" 의 합.

진짜 의미 있는 tradability event (true suspension / forced delisting / limit
lock) 가 명시적으로 추적되지 않음.

## Implication for KR-LIQ-FRAGILITY-AVOID-001

Spec 의 fragility signal 구성 변수 중 2 가지가 직접 오염:

1. **"직전 60d 내 tradability 변동 (suspension / resumption) 1회 이상"**:
   현재 panel 의 tradability flag 는 사실상 universe membership flag.
   진짜 suspension 별도 source 없이는 measurement layer 가 spec 의도와
   일치 X.

2. **"직전 20d locked-limit incidence"**: corporate action day 가 limit
   move 로 잘못 잡힘 (99.3% 오염). 진짜 limit-lock 과 corporate action
   분리 불가.

→ Gate 3 + Gate 5 의 결합 효과로 spec 의 fragility signal 의 핵심 변수
대부분이 false signal 로 오염.

## Implication for KR-TRADABILITY-RESUME-RISK-001

Referee Allowed scope (Round 2 Option D, 이 카드만 infrastructure audit
허용):

이 audit 자체가 이 카드의 Step 1 + Step 2 (tradability flag lineage +
4-cause distinction) 의 핵심 결과. Step 1-2 결과 = **명확한 FAIL**:

- Tradability flag 의미 = "in_dynamic_universe + 일부 sanity" 가 dominant
- 4-cause 구분 = 현재 데이터로 불가
- True suspension status source 별도 필요

따라서 KR-TRADABILITY-RESUME-RISK-001 의 다음 step (3-5) 진입 = 데이터
인프라 unblock 전 불가. Spec 의 Step 3 (resumption event count 확인) 자체
가 진짜 suspension/resumption event 식별 source 없이 수행 불가.

## Required Data / Source Additions

| Field | 의미 | 현재 |
|---|---|---|
| `suspension_start_date` | KRX 공식 매매정지 시작일 | 없음 |
| `suspension_end_date` | 재개일 | 없음 |
| `suspension_reason` | 정지 사유 (관리종목 / 거래소요청 / 감리위 등) | 없음 |
| `delisting_date` | 상폐일 | 없음 |
| `delisting_reason` | 상폐 사유 | 없음 |
| `listing_status` | active / suspended / delisted / managed | 없음 |
| `corporate_action_event_log` | adjusted OHLC 와 함께 (data_gap_adjusted_ohlc.md 참조) | 없음 |

Source 후보: KRX 공시 / DART / vendor (FnGuide / KIS / Bloomberg)

## Function Documentation Recommendation

`src/utils/tradability.py` 의 `tradable_mask()`:

```python
# 현재 동작 (실제 측정 결과):
# - 82.24% 가 단순 in_dynamic_universe = False (panel_absence)
# - 0.77% 가 OHLC / trading_value missing (data_missing 의 일부)
# - 0.03% 가 limit_lock_candidate (단 corporate action artifact 99.3% 오염)
# - 0% 가 명확한 true_suspension (status column 없음)
# - 17.78% 가 unknown attribution

# 즉 사실상 `is_in_dynamic_universe_and_executable` 와 가까움.
# True suspension / forced delisting / 진짜 limit-lock 의 분리는 별도 source 필요.
```

### 권장 수정 방향 (W001 v1.1 또는 v2)

- `tradable_mask()` 의 의도된 의미 명시 (docstring 보강)
- Component 별 mask 분리 함수 추가: `panel_absence_mask()` /
  `data_missing_mask()` / `limit_lock_mask()` / `true_suspension_mask()`
- 4-cause 별 attribution 가능한 categorical column 추가 (예: `tradable_state`)
- Status / suspension source 추가 시 wiring point 명시

## Block Impact (재확인)

| Card | Block 사유 |
|---|---|
| KR-LIQ-FRAGILITY-AVOID-001 | Gate 3 + Gate 5 결합 오염 → A0 KILL (Option D) |
| KR-TRADABILITY-RESUME-RISK-001 | Step 3-5 진입 불가 (현재 audit 가 Step 1-2 결과) |
| KR-LIQ-MIGRATION-001 | Gate 3 영향 (universe membership 변동 ≠ liquidity migration), Gate 5 영향 |
| KR-TURNOVER-ATTENTION-001 | Gate 3 영향 (universe 진입 → turnover spike 가짜 신호), Gate 5 영향 |

## Unblock Path

`docs/round2_gate5_fail_lock.md` Unblock Conditions + 다음 추가:

1. KRX suspension / delisting / managed status source 확보
2. Corporate action event log + adjusted OHLC (별도 data_gap)
3. `tradable_mask()` repair + 4-cause attribution column 추가
4. Gate 3 재실행 (sample audit + true 4-cause distinction)
5. Referee 재승인

## Related

- `docs/round2_gate5_fail_lock.md` — Round 2 Step 5 Option D lock
- `docs/data_gap_adjusted_ohlc.md` — Gate 5 fail 상세 (147 events)
- `reports/experiments/W001_V1_AUDIT/corporate_action_artifact_ledger.csv` —
  147 corporate action events
- `docs/backlog_register.md` — W001-V1 audit task
