# Data Gap — Adjusted OHLC (W001 v1)

Date: 2026-05-22
Status: **CRITICAL** infrastructure defect (Round 2 Step 5 finding)
Block: Round 2 strategy diagnostic 전체 (4 카드)
Origin: KR-LIQ-FRAGILITY-AVOID-001 A0 Gate 5 FAIL
Referee lock: `docs/round2_gate5_fail_lock.md` (Option D)

## Issue Summary

W001 v1 의 dynamic_top100 panel 은 raw OHLC 만 제공. Adjusted OHLC (split /
증자 / 감자 등 corporate action 으로 인한 가격 discontinuity 제거) 컬럼 부재.
`adjust_for_corporate_actions()` 함수 호출 시 raw 컬럼 alias 만 생성 (실제
조정 X).

## Evidence

| 항목 | 값 |
|---|---|
| Panel | `research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv` |
| Adjusted columns 존재 | `[]` (none) |
| Raw price columns | `['시가', '고가', '저가', '종가']` |
| \|daily return\| > 50% events | **147 건** |
| \|daily return\| > 30% events | 472 건 |
| `adjust_for_corporate_actions()` 호출 전 impossible events | 147 |
| `adjust_for_corporate_actions()` 호출 후 impossible events | **147 (unchanged)** |
| Top artifact 예 | `미래산업 2020-07-02`: 79 → 3700 (=+4583%) = 1:46 split |
| Top artifact 예 | `다이나믹디자인 2022-05-04`: 238 → 6690 (=+2711%) = 액면병합/병합 |

## Cross-Impact with Tradability

W001 `tradability.py` 의 limit_threshold = 0.299 (29.9%) 가 corporate action
day 를 limit-lock 으로 잘못 분류:

- 147 events 중 **146 건 (99.3%)** 이 `open / prev_close - 1` > 29.9% 로
  계산되어 tradable_mask 에서 limit move 로 분류
- 즉 **fragility signal 의 "locked-limit incidence" 변수가 false signal 로
  오염**
- 이것이 KR-LIQ-FRAGILITY-AVOID-001 의 핵심 signal 침투 위험의 직접 증거

## Required Source / Fields

| Field | 의미 | 현재 |
|---|---|---|
| `adjusted_open` | split / 증자 / 감자 / 병합 조정된 open | 없음 |
| `adjusted_high` | 조정 high | 없음 |
| `adjusted_low` | 조정 low | 없음 |
| `adjusted_close` | 조정 close | 없음 |
| `adjustment_factor` | event 별 factor (1.0, 0.5, 46.0 등) | 없음 |
| `corporate_action_event_log` | split / reverse / capital reduction / rights issue / merger / suspension / resumption event chain | 없음 |
| `event_effective_date` | 각 event 의 실제 효력 발생일 | 없음 |
| `pre_event_shares` / `post_event_shares` | event 전 / 후 발행주식수 | 일부 (상장주식수 시점별, 단 event linkage X) |

## Forbidden Substitutes

| 시도 | 왜 금지 |
|---|---|
| 147건 명시적 제외 후 raw price 사용 | Round 2 lock (Option C 거부됨); raw return / limit / suspension / panel absence 가 섞임 |
| `시가총액추정 / 상장주식수` 변화 만으로 split 역추정 | 충분치 않음 (감자 / 액면병합 / 증자 구별 X) |
| `pykrx` / vendor 의 사후 보정 데이터 | Gate 6 PIT 위반 (restated) |
| 다른 vendor 의 adjusted return 만 가져오기 (가격 X) | OHLCV 모두 일관되게 조정 필요 |

## Acceptable Source Requirements

1. **OHLCV 모두 adjusted**: open / high / low / close / (volume?) 일관 조정
2. **PIT**: 발표 시점 기준 (사후 정정 X)
3. **Event log linkage**: 각 corporate action 의 type / date / factor / effective date
4. **Cancellation handling**: 취소된 corporate action 처리
5. **Splits vs merges 구별**: 단순 factor 만이 아닌 mechanism 명시
6. **Listing transitions**: 신규상장 / 재상장 / 이전상장 / 상폐 처리

## Source Candidates (사용자 host 평가)

| Source | Cost | 시간 | 난이도 |
|---|---|---|---|
| KRX 공식 수정주가 (krx.co.kr) | 무료 / 일부 유료 | 1-2 주 | 중 (수작업 download + parsing) |
| pykrx with strict PIT verification | 무료 | 1 주 | 중 단 vendor restate 위험 |
| Bloomberg / Refinitiv adjusted OHLC | 유료 (구독) | 1 일 (구독 시) | 낮음 |
| 자체 corporate_action event ledger 구축 + 가격 재계산 | 무료 (DART API) | 4-8 주 | 높음 |
| Vendor parsed (FnGuide / KIS / 매경) | 유료 | 1-4 주 | 중 |

## Function Bug Documentation

`src/utils/corporate_action.py` 의 `adjust_for_corporate_actions()`:

```python
# 현재 동작:
# 1. adjusted_* 컬럼이 panel 에 이미 있으면 → 그대로 사용
# 2. 없으면 → raw 컬럼을 adjusted_* 로 alias 만 생성
# 3. 실제 corporate action 조정 X
```

→ `corporate_action.py` 의 docstring + 함수 이름이 **misleading**. 실제로는
"raw column alias generator" 에 가까움.

### 권장 수정 방향 (W001 v2 또는 v1.1)

- `adjust_for_corporate_actions()` 의 alias-only 동작 명시 (docstring 수정)
- 실제 조정 기능은 별도 함수 `apply_corporate_action_adjustment(event_log, panel)` 로 분리
- Event log 없이 호출 시 명시적 warning / error
- 또는 alias-only 동작 시 `*_source = 'unadjusted_raw'` 로 명확히 표시

## Block Impact

| Card | Block 이유 |
|---|---|
| KR-LIQ-FRAGILITY-AVOID-001 | locked-limit incidence false signal 오염 |
| KR-LIQ-MIGRATION-001 | market cap jump 계산 시 split jump 가짜 신호 |
| KR-TURNOVER-ATTENTION-001 | trading_value / market_cap 계산 시 split artifact |
| KR-TRADABILITY-RESUME-RISK-001 | strategy diagnostic 차단 (단 infrastructure audit 허용) |

## Unblock Path

`docs/round2_gate5_fail_lock.md` Unblock Conditions 섹션 + 위 Acceptable
Source Requirements 통과 후:

1. Panel 에 adjusted OHLC 컬럼 추가 (vendor acquire 또는 자체 구축)
2. `adjust_for_corporate_actions()` repair (or new function)
3. 147 events 의 root cause 분류 ledger (split / 병합 / 증자 / 감자 각각)
4. tradable_mask 의 limit_threshold 처리 = corporate action day 명시 제외
5. Gate 1-6 재실행
6. Referee 재승인
7. Round 2 strategy diagnostic 재개 가능

## Related

- `docs/round2_gate5_fail_lock.md` — Round 2 Step 5 Option D lock
- `docs/tradability_semantics_audit.md` — 4-cause distinction audit
- `reports/experiments/W001_V1_AUDIT/corporate_action_artifact_ledger.csv` — 147 건 ledger
- `docs/backlog_register.md` — W001-V1 audit task 등록
