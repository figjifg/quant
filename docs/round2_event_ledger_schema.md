# Round 2 Event Ledger Schema

Date: 2026-05-22
Status: REQUIRED for all Round 2 TEST cards before any performance diagnostic
Applies to: KR-LIQ-FRAGILITY-AVOID / KR-TRADABILITY-RESUME-RISK /
KR-LIQ-MIGRATION / KR-TURNOVER-ATTENTION

KR-FLOW-ABSORPTION-001 = lineage-only audit only. Event ledger 필요 X (단
유사한 lineage record table 별도 필요).

## Purpose

Event ledger = 각 카드의 모든 signal / event 를 사전 등록하고, 성과 diagnostic
전에 누가 / 언제 / 왜 / 어떤 상태에서 trigger 됐는지 audit 가능하게 함.
ledger 없이 성과 표 만들면 = TEST 중단 (Gate 7).

## Required Schema

| Field | Type | Description |
|---|---|---|
| `event_id` | string | 사이클 내 unique. 카드 prefix + 일련번호 (예: `FRAGILITY_000123`) |
| `card_id` | string | KR-LIQ-FRAGILITY-AVOID-001 등 |
| `signal_date` | date (YYYY-MM-DD) | signal 발생 일자 (T) |
| `entry_date` | date | strategy 진입 일자 (T+1 또는 spec 명시) |
| `exit_date` | date | strategy 청산 일자 (rule 또는 max holding) |
| `stock_id` | string | **permanent identifier** (delisting / merge / rename 안전한 ID) |
| `stock_id_at_signal` | string | signal 시점 종목코드 (ticker) |
| `stock_id_at_exit` | string | exit 시점 종목코드 (변경 시 다름) |
| `market` | enum | KOSPI / KOSDAQ / KONEX |
| `tradability_state_signal` | enum | active / true_suspension / limit_lock / panel_absence / data_missing / delisting_transition |
| `tradability_state_entry` | enum | (entry 시점) 같은 enum |
| `tradability_state_exit` | enum | (exit 시점) 같은 enum |
| `trading_value_signal` | float | PIT trading value (KRW, T 일) |
| `market_cap_signal` | float | PIT market cap (KRW, T 일, restated 사용 X) |
| `shares_outstanding_signal` | int | PIT 발행주식수 |
| `matched_control_id` | string | 동일 사이클 내 matched control event_id (없으면 null) |
| `matched_control_type` | enum | random / size_matched / liquidity_matched / vol_matched / trailing_return_matched / simple_baseline / null |
| `cost_bucket` | string | 비용 layer 식별 (예: "commission_15bps_spread_50bps_tax_20bps") |
| `entry_feasibility` | enum | executable / locked_limit_up / locked_limit_down / suspended / data_missing |
| `exit_feasibility` | enum | executable / locked_limit_up / locked_limit_down / suspended / forced_carry |
| `exit_cause` | enum | rule_match / max_holding / locked_carry / stop_loss / delisting / merge / suspension_terminal |
| `is_matched_control` | bool | True = control event (자체 signal 아님), False = main signal |
| `corporate_action_proximity` | enum | none / split_within_5d / merge_within_5d / rights_within_5d / reduction_within_5d / resumption_within_5d |
| `notes` | string | free text (audit 참고) |

## Field Constraints

### `stock_id` (permanent identifier)
- delisting, merge, rename 후에도 동일 entity 추적 가능한 stable ID
- Ticker (종목코드) 가 아님 (ticker = rotation 됨)
- 후보: corp_code (DART) / ISIN / KRX permanent ID

### `tradability_state_*`
- 4 cause 명확 구분 필수 (Gate 3)
- `active` = 정상 거래 가능
- `true_suspension` = KRX 공식 매매정지 (사유 별도)
- `limit_lock` = 상한가 / 하한가 종가 고정 (locked-limit)
- `panel_absence` = 당시 dynamic_top100 등 universe 밖
- `data_missing` = vendor 데이터 누락 (strategy event 아님)
- `delisting_transition` = 상폐 진행 중 (terminal event)

### `entry_feasibility` / `exit_feasibility`
- `executable` = 실제 거래 가능
- `locked_limit_up` = 상한가, 매수 진입 X / 매도 청산 X (forced carry)
- `locked_limit_down` = 하한가, 매도 청산 X (forced carry)
- `suspended` = 거래정지 중
- `forced_carry` = exit 의도했으나 실제 청산 못함 (다음 가능 시점까지 carry)
- `data_missing` = vendor 누락 (strategy event 아님)

### `matched_control_id` / `is_matched_control`
- 모든 main signal 이벤트에 대해 최소 1 matched control event 필요
- Control event 도 같은 ledger 에 row 로 기록 (`is_matched_control = True`)
- Control 종류 = `matched_control_type` 명시

### `corporate_action_proximity`
- signal_date 기준 ±5 거래일 내 corporate action 발생 시 명시
- artifact 위험 evaluation 에 사용

## Aggregation Rules

성과 metric 계산 (Round 2 metric 우선순위 = `round2_global_A0_gates.md` Gate 10):

1. **Locked-position incidence**: `entry_feasibility != executable` 또는 `exit_feasibility != executable` 비율
2. **Exit infeasibility**: `exit_cause = locked_carry` 비율
3. **Left-tail loss**: bottom 5% / 10% return events (event-level VaR)
4. **MDD**: 누적 NAV 의 max drawdown
5. **After-cost return**: `cost_bucket` 적용 후 return
6. **Turnover-adjusted return**: return / turnover

후순위: CAGR / Sharpe / gross return (보고 가능하나 secondary)

## Output File Convention

각 카드의 event ledger 파일:
- 위치: `reports/experiments/<CARD_ID>/event_ledger.csv`
- 파일명: `event_ledger.csv` (다른 이름 X)
- 인코딩: UTF-8
- Schema: 위 field 그대로
- 정렬: signal_date asc, event_id asc

추가 audit summary:
- `reports/experiments/<CARD_ID>/ledger_audit.md` = ledger 자체의 sanity 보고
  (event count, tradability_state 분포, locked incidence, control coverage 등)

## Pre-Diagnostic Checklist

ledger 생성 후 성과 diagnostic 진입 **전** 다음 모두 확인:

- [ ] `stock_id` 가 permanent identifier 인지 (ticker 아님)
- [ ] `tradability_state_*` 의 4 cause 명확히 구분되어 있는지
- [ ] `entry_feasibility` / `exit_feasibility` 의 locked / forced 처리 명시되어 있는지
- [ ] 모든 main signal 에 matched control 1+ 있는지
- [ ] `market_cap_signal` 이 PIT 인지 (restated 아닌지)
- [ ] `corporate_action_proximity` 가 signal ±5d 내 정확히 채워졌는지
- [ ] `cost_bucket` 이 명시되어 있는지

체크리스트 미충족 시 = TEST 중단, Bear 재심의 trigger.

## Related

- `docs/round2_referee_verdict_lock.md` — Round 2 verdict
- `docs/round2_global_A0_gates.md` — 10 non-negotiable gates
- 각 카드 spec: `research/experiments/spec_KR_*_A0.md`
