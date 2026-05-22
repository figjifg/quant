# Gate Check — KR-LIQ-FRAGILITY-AVOID-001

Date: 2026-05-22
Cycle: Round 2 Step 5 (Claude executor A0 audit)
Priority: 1 (start)
Strategy ID: KR-LIQ-FRAGILITY-AVOID-001
Spec: `research/experiments/spec_KR_LIQ_FRAGILITY_AVOID_A0.md`
Global gates: `docs/round2_global_A0_gates.md`

## Data Source

- Panel: `research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv`
- Rows: 969,208 / Dates: 1,721 / Unique tickers: 815
- Date range: 2018-01-02 ~ 2024-12-30
- Per-date universe: ~563 종목 (top100 = 100 정확히, 나머지 ~463 은 top100 밖 동일 panel)
- W001 modules: `src/utils/tradability.py`, `corporate_action.py`, `korean_calendar.py`

## Gate Check Results

| Gate | Status | Detail |
|---|---|---|
| 1. Permanent ID | ⚠ PARTIAL | KRX ticker only (6 자리). Permanent identifier (DART corp_code 등) 별도 mapping 필요. Rename / merge 시 ticker rotation 추적 X. |
| 2. Survivorship | ⚠ PARTIAL | 815 unique tickers, 258 disappeared (last seen > 30d before panel end). Panel 에 사라진 종목들 포함 (PIT 가능성 큼) 단 disappear 끝 일자 대부분 2023-12-28 = panel end artifact 의심. 진짜 상폐 / merge 별도 confirm 필요. |
| 3. Tradability semantics | ⚠ PARTIAL | `tradable_mask()` 가 limit-lock (29.9% threshold) + trading value missing 분리 가능. 단 **true_suspension / data_missing / panel_absence / delisting_transition 4-cause 명확 구분 X** (단일 binary `tradable=false`). STATUS_COLS (`상태`/`종목상태`) panel 에 없음. |
| 4. Locked limit handling | ✅ PASS | `tradability.py` 의 `limit_threshold=0.299` + `next_executable_date()` 함수 존재. Open / prev_close 차이 ≥ 29.9% 시 limit move 검출. |
| 5. **Adjusted OHLC sanity** | ❌ **FAIL** | **Panel 에 adjusted 컬럼 없음.** Raw 종가만 사용. `corporate_action.adjust_for_corporate_actions()` 호출해도 raw 컬럼 alias 만 만듦 (실제 adjustment X). **Impossible return events (\|daily return\| > 50%): 147 건** (adjust 전 / 후 변화 X). 30% 이상 daily |return|: 472 건. → split / 증자 / 감자 artifact 잔존. |
| 6. Market cap PIT | ✅ PASS | `시가총액추정여부` = True 비율: **0.00%** (969,208 rows 모두 False). `거래대금추정여부` = True 비율: **0.00%**. 모두 실제 값. |
| 7. Event ledger | ⏸ Not yet | Gate 1-6 통과 전 ledger 생성 시도 X (spec lock). |
| 8. Controls | ⏸ Not yet | Gate 1-6 통과 전 simulation X. |
| 9. Performance language | ✅ PASS | 이 audit 에서 production / paper / P08 / shadow / live readiness 어휘 사용 X. |
| 10. Metric priority | ⏸ Not yet | Performance diagnostic 진입 전. |

## Critical Issue

**Gate 5 FAIL → Round 2 Global Gate (`round2_global_A0_gates.md` Gate 5) KILL trigger:**

> "Failure → KILL: adjusted OHLC artifact 시 KR-LIQ-MIGRATION / KR-TURNOVER-ATTENTION 즉시 kill (시총 / turnover 계산 왜곡)."

Spec 의 fragility signal 구성 요소:
- 직전 60d ADV bottom decile: **거래대금추정** 기반 (현재 PASS, Gate 6)
- 직전 60d 내 tradability 변동: **tradability.py mask** 기반 (PARTIAL, Gate 3)
- 직전 20d locked-limit incidence: **open/prev_close diff** 기반 → **raw price 사용 시 corporate action day 가 거짓 limit move 로 잡힐 위험 (147 건 artifact 중 일부)**

→ Spec 의 fragility signal 자체에 Gate 5 artifact 가 침투 가능. Bear 사전 등록 kill gate "fragile signal 이 missing data artifact" 영역.

## Downstream Impact

같은 panel (dynamic_top100_2018_2024_panel.csv) 을 사용하는 다른 Round 2 카드도 같은 Gate 5 issue:

- **KR-TRADABILITY-RESUME-RISK-001**: Step 5 (filter effect) 도 같은 panel 의존 → Gate 5 fail 영향
- **KR-LIQ-MIGRATION-001**: market cap jump 계산에 raw price 사용 시 split jump 가짜 신호 → Gate 5 fail 영향 (Gate 6 만으로 부족)
- **KR-TURNOVER-ATTENTION-001**: trading_value / market_cap 계산 시 split day artifact → Gate 5 fail 영향

즉 Round 2 의 4 TEST 카드 **모두** Gate 5 fail 영향 받음.

## Remediation Options (Referee 결정 필요)

### Option A — KR-LIQ-FRAGILITY-AVOID-001 즉시 KILL
- Gate 5 fail 그대로 적용 (Global Gate KILL trigger)
- Priority 2-4 카드도 같은 issue 로 단계적 KILL 가능성 큼
- Round 2 effective 결과 = 모든 TEST 카드 KILL
- Cycle 1 final = TEST 0 / BACKLOG 7+ / REJECT 0

### Option B — Panel 의 adjusted price source 별도 acquire 후 재시작
- 사용자 host 작업 (vendor adjusted OHLC 추가 acquire)
- 또는 split / 증자 event chain 별도 source 로 W001 corporate_action.py 재구현
- 새 backlog task Q3 (Adjusted OHLC PIT acquisition)
- Round 2 카드 모두 unblock 까지 대기

### Option C — Raw price impact 분석 후 fragility signal 재정의
- 147 건 corporate action day 명시적 제외 후 ADV / limit 계산
- 단 spec 변경 = Bear 재심의 필요 (Round 2 lock 위반 위험)
- 사전 등록 spec 의 fixed scope 변경 = 글로벌 제약과 모호

### Option D — Gate 5 fail 인정 + 결과를 "infrastructure audit finding" 으로 보고
- KR-LIQ-FRAGILITY-AVOID-001 = KILL (Option A 동일)
- 단 Gate 5 fail 자체가 **W001 v1 infrastructure 의 한계** 노출 = 의미 있는 finding
- 새 backlog task: W001 v1 의 adjusted OHLC source missing audit 명문화
- KR-TRADABILITY-RESUME-RISK-001 (Priority 2) 의 Step 1 (infrastructure audit) 결과로 통합

## Forbidden (이 보고에서 지킨 것)

- Return backtest 실행 X
- NAV / CAGR / Sharpe / MDD 산출 X
- Performance language 사용 X
- Production / paper / P08 / shadow 연결 X
- Spec 사후 수정 X
- Reduced / proxy 변형 X

## Next Step

Referee 결정 필요. Option A / B / C / D 또는 다른 방향.

Claude executor 는 Referee lock 받기 전 다음 action 진행 X:
- 다른 카드 (Priority 2-4) audit 진입 X (같은 panel, 같은 Gate 5 issue 영향)
- Event ledger 구축 X (Gate 5 fail 상태)
- Performance diagnostic X
- Spec / 메모리 / status 문서의 "결정됨" 추정 X
