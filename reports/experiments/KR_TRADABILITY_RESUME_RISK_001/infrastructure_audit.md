# KR-TRADABILITY-RESUME-RISK-001 — Infrastructure Audit (Allowed Scope Only)

Date: 2026-05-22
Cycle: Round 2 Step 5 Option D
Scope: **Infrastructure audit only** (strategy diagnostic 중단)
Spec: `research/experiments/spec_KR_TRADABILITY_RESUME_RISK_A0.md`
Referee lock: `docs/round2_gate5_fail_lock.md`

## Allowed vs Forbidden (Referee 명시)

| Allowed (이 audit 에서 수행) | Forbidden (수행 X) |
|---|---|
| Tradability flag lineage | 재개 후 5d/20d/63d return diagnostic |
| `tradable=false` 원인 분해 | Long-only exclusion filter 성과 |
| 4-cause 구분 가능 여부 | Event-driven return table |
| `next_executable_date()` 동작 검증 | NAV / CAGR / Sharpe / MDD |
| 147 extreme return × tradability flag 교차 | Performance language |
| Corporate action artifact ledger 작성 | Tail / alpha 개선 주장 |
| Adjusted OHLC missing issue 문서화 | Production / paper / P08 연결 |

## Step 1 — Tradability Flag Lineage

W001 v1 `src/utils/tradability.py` 의 `tradable_mask()` 구성:

| Component | Logic |
|---|---|
| OHLC sanity | open / high / low / close numeric + > 0 |
| Trading value sanity | `거래대금추정` numeric + > 0 |
| Trade value estimation flag | `거래대금추정여부 = False` 만 통과 |
| Dynamic universe | `동적유니버스포함 = True` 만 통과 (default policy) |
| Status (suspension) | `STATUS_COLS` 가 panel 에 없음 → 적용 X |
| Limit move | `(open / prev_close - 1).abs() < 0.299` 만 통과 |

결과 (`docs/tradability_semantics_audit.md` 와 일치):
- tradable=True 비율 = 17.75%
- tradable=False 비율 = 82.25%
- 82.24% 가 단순 `not in_dynamic_universe`

→ 현재 `tradable_mask()` 의 의미 ≈ "in_dynamic_universe + 가격/거래량 sanity + limit move 차단".
진짜 KRX suspension status / forced delisting 별도 추적 X.

## Step 2 — 4-Cause Distinction

Referee Gate 3 요구의 4 cause:

| Cause | 현재 detection 가능? | 비고 |
|---|---|---|
| `true_suspension` | ❌ NO | STATUS column 없음 |
| `limit_lock` | ⚠ PARTIAL | open limit move 만, 단 99.3% 가 corporate action artifact |
| `panel_absence` | ✅ YES | `동적유니버스포함 = False` 명확 (dominant cause, 82%) |
| `data_missing` | ⚠ PARTIAL | OHLC / trading value missing 으로 추정 가능 |
| `delisting_transition` | ❌ NO | listing status column 없음 |

**Step 2 verdict**: 4-cause distinction **현재 데이터로 불가**. true_suspension /
delisting_transition source 별도 필요. limit_lock 도 corporate action 과
오염 분리 필요.

## Step 3 — Resumption Event Count (현재 데이터)

진짜 resumption event = `tradable_state` 가 `true_suspension` → `executable`
로 전환되는 시점. 그러나 Step 2 에서 `true_suspension` detection 불가.

대안 측정 (panel_absence → executable 전환):

```
tradable=False (any cause) → tradable=True 전환: 매우 많음
  단 이건 단순 "동적 universe 진입" event 가 dominant
  진짜 KRX suspension 후 resumption 과 다름
```

→ Step 3 의 "resumption event count" = **현재 데이터로 정확히 카운트
불가**. Step 3 fail.

## Step 4 — 147 Extreme Return × Tradability Flag Cross-tab

147 |daily return| > 50% 이벤트 의 tradability flag 분석:

| Day | tradable | 비율 |
|---|---:|---:|
| Extreme event day (T) | False | **146 / 147 (99.3%)** |
| Extreme event day (T) | True | 1 / 147 (0.7%) |
| Prior day (T-1) | False | **144 / 147 (98.0%)** |
| Prior day (T-1) | True | 3 / 147 (2.0%) |

Cross-tab:
```
prev_day_tradable   False   True
tradable=False        143      3
tradable=True           1      0
```

해석:
- **146/147 corporate action artifact day 가 tradability flag = False 로
  이미 차단** = 단순 backtest 에서는 자동 회피됨 (false alpha 방어 효과)
- 단 prior day (T-1) 에는 144 건이 이미 False → 즉 panel 의 universe 밖
  이었던 종목이 corporate action day 에도 universe 밖
- T-1 에 True / T 에 False (1 건) = 의도된 회피
- T-1 에 True / T 에 True (0 건) = 모든 corporate action day 가 차단됨
- T-1 에 False / T 에 True (3 건) = panel 진입과 corporate action 동시 발생

→ **결과적으로 W001 v1 의 tradability flag 가 strategy 진입 차단에는 효과
있음** (false signal 방어 측면). 단 진짜 mechanism distinction 은 여전히 X.

CSV: `reports/experiments/KR_TRADABILITY_RESUME_RISK_001/extreme_x_tradability_crosstab.csv`

## Step 5 — `next_executable_date()` 동작 검증

Sample test (5 not-tradable + 5 tradable rows):

| Type | ticker | signal_date | next_executable | gap |
|---|---|---|---|---:|
| Not tradable | 241590 | 2023-02-23 | 2023-06-27 | +124d |
| Not tradable | 120030 | 2020-02-13 | 2020-06-03 | +111d |
| Not tradable | 015020 | 2022-07-27 | 2022-08-08 | +12d |
| Not tradable | 013000 | 2021-05-21 | 2021-09-28 | +130d |
| Not tradable | 058430 | 2021-06-15 | 2021-06-22 | +7d |
| Tradable | 010060 | 2021-10-27 | 2021-10-28 | +1d |
| Tradable | 023530 | 2018-06-15 | 2018-06-18 | +3d |
| Tradable | 000150 | 2021-07-06 | 2021-07-07 | +1d |
| Tradable | 032350 | 2023-10-10 | 2023-11-03 | +24d |
| Tradable | 030200 | 2022-11-03 | 2022-11-04 | +1d |

Coverage (1000 random not-tradable sample):
- Success (next_executable 찾음): **920 / 1000 = 92%**
- Error (찾지 못함, ticker 가 panel 끝까지 안 돌아옴): 80 / 1000 = 8%

→ `next_executable_date()` 함수 자체는 동작 OK. 단:
- 매우 큰 gap (+100d 이상) 발견 = panel_absence 가 dominant 이라 단순
  "다음 universe 진입일" 을 찾는 효과
- 진짜 KRX suspension 후 resumption 과 다름
- 8% (80/1000) 가 ticker 가 panel 끝까지 안 돌아옴 = delisting / merge 추정
  (별도 source 로 confirm 필요)

## Summary (Step 1-5 결과)

| Step | Status | 결과 |
|---|---|---|
| 1. Tradability flag lineage | ✅ Documented | 사실상 "in_dynamic_universe + sanity" |
| 2. 4-cause distinction | ❌ FAIL | true_suspension / delisting source 없음 |
| 3. Resumption event count | ❌ FAIL | Step 2 fail 로 인한 cascade |
| 4. Extreme × tradability crosstab | ✅ Documented | 99.3% 이미 차단 (false alpha 방어 효과 확인) |
| 5. `next_executable_date()` 검증 | ✅ Documented | 동작 OK, 단 panel_absence 가 dominant cause |

### Spec 의 Step 4-5 (forward diagnostic + filter effect)

Referee Option D lock 으로 인해 진입 금지. Step 2-3 fail 로 진입 조건도
충족 X.

## Key Findings (감사 가치)

1. **W001 v1 의 tradability flag 가 사실상 universe membership filter**:
   진짜 KRX suspension / delisting tracking 별도 source 필요.
2. **Corporate action artifact 99.3% 가 tradability flag 에 의해 이미 차단**:
   기존 backtest 들의 false alpha 방어에는 도움 됐을 가능성. 단 측정
   layer 의 의도된 design 인지 우연 인지 명확히 X.
3. **next_executable_date() 의 매우 큰 gap (100d+)** 은 "다음 universe
   진입일" 을 찾는 효과 → strategy 의도와 다를 수 있음.
4. **8% ticker 가 panel 끝까지 안 돌아옴** = delisting / merge / managed
   transition. 별도 status source 로 audit 가능한 영역.

## Verdict (Infrastructure-only)

Strategy diagnostic (Step 5) 진입 = 불가. Gate 5 (adjusted OHLC) 와 Gate 3
(4-cause distinction) 모두 unblock 필요.

이 infrastructure audit 자체는 의도된 산출물:
- `W001-V1-ADJUSTED-OHLC-CORPORATE-ACTION-AUDIT-001` backlog task 의 핵심
  artifacts (`docs/backlog_register.md`)
- Round 2 strategy diagnostic 재개 전 prerequisite 명확화

## Forbidden (이 audit 에서 지킨 것)

- 재개 후 forward return 계산 X
- Filter effect 성과 측정 X
- NAV / CAGR / Sharpe / MDD 산출 X
- Performance language 사용 X
- Production / paper / P08 / shadow 연결 X
- Spec 사후 수정 X

## Related

- `docs/round2_gate5_fail_lock.md`
- `docs/tradability_semantics_audit.md`
- `docs/data_gap_adjusted_ohlc.md`
- `docs/adjustment_engine_requirements.md`
- `reports/experiments/W001_V1_AUDIT/corporate_action_artifact_ledger.csv`
- `reports/experiments/KR_TRADABILITY_RESUME_RISK_001/extreme_x_tradability_crosstab.csv`
