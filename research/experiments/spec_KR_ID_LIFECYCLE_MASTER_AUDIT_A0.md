# KR-ID-LIFECYCLE-MASTER-AUDIT-001 — A0 Audit Spec (Priority 1B)

## Status
PRE-REGISTERED · **A0 AUDIT only** · 전략 아님
Round 3 Priority: 1B (KR-G5-ADJOHLC-CORPACT-AUDIT-001 과 병렬)
Date: 2026-05-22

## Cycle Lineage

- Round 3 Bull idea #2
- Referee Round 3 lock: **A0 AUDIT (permanent ID / delisting / merge / rename audit only)**
- Trigger: G5 audit + ID lifecycle 분리 불가 (Referee 명시)

## Scope

종목코드, 회사명, 상장폐지, 합병, 분할, 재상장, ticker 변경을 **permanent
identifier** 기준으로 추적할 수 있는지 검증. Output = defect ledger.

## Hard Locks (Round 3 전체)

`docs/round3_no_performance_rule.md` 그대로 적용.

## Allowed Audit Actions (Referee 명시)

| Audit | 허용 |
|---|---|
| Stock_code uniqueness by date | ✅ |
| Disappeared ticker full list | ✅ |
| Reappeared code full list | ✅ |
| Name-change trace | ✅ |
| Delisting / merger / split / relisting coverage | ✅ |
| Dynamic_top100 members permanent ID mapping | ✅ |
| Corporate action events issuer ID linkage | ✅ |
| Code reuse / reappearance 구분 | ✅ |

## Forbidden Actions

| Action | 금지 |
|---|---|
| Final delisting outcome 을 alpha label 로 사용 | ❌ |
| Delisted names 제거 후 universe 구성 | ❌ |
| Lifecycle 복구 없이 adjusted OHLC repair pass 선언 | ❌ |
| Lifecycle 복구 없이 top100 PIT pass 선언 | ❌ |

## Audit Workflow (Allowed only)

### Step 1 — stock_code uniqueness by date

- Panel 의 `(날짜, 종목코드)` pair 가 unique 한지 확인
- 같은 ticker 가 한 날짜에 2 row 있으면 duplicate / split bug

### Step 2 — Disappeared ticker full list

- 815 unique tickers 중 panel end 이전에 사라진 ticker 전수 (Round 2 = 258)
- 각 ticker 별 last_seen_date / market_cap_at_last_seen / 이유 추정
- 단 이유 confirm = 외부 source (KRX delisting archive / DART) 필요

### Step 3 — Reappeared code full list

- panel 중간에 사라졌다가 다시 나타나는 ticker = code reuse 의심
- (ticker A 가 회사 X 가 사용 후 delisted → KRX 가 ticker A 재배정 → 회사 Y 가
  사용) 케이스 확인
- code reuse 발견 시 = `code_reuse_unrecognized` defect

### Step 4 — Name change trace

- 같은 ticker / 같은 corp_code 에서 종목명 변경 chronology 추적
- DART corp_code 와 ticker 의 1:1 mapping 인지 확인 (1:1 아니면 rename /
  reuse 의 신호)

### Step 5 — Delisting / merger / split / relisting coverage

- Disappeared 258 ticker 중 각 type 별 coverage
- 외부 source (KRX 공시 / DART) 와 reconciliation 필요 (현재 없음 = defect)

### Step 6 — Dynamic_top100 members permanent ID mapping

- 매 시점 top100 의 100 member 가 permanent ID 로 일관 매핑 가능한지 확인
- ticker rotation / rename 시점에 매핑 깨지지 않는지

### Step 7 — Corporate action events issuer ID linkage

- OPENDART parquet 의 corp_code (이미 존재) ↔ panel 의 종목코드 mapping
- 매핑 누락 / 불일치 확인

### Step 8 — Code reuse / reappearance 구분

- "사라졌다 다시 나타난 ticker" 가:
  - 같은 entity 가 거래정지 후 재개 (= 같은 corp_code)
  - 다른 entity 가 ticker 재사용 (= 다른 corp_code)
- 둘 구별 = corp_code 활용

## Data Available in Repo

| Source | 가용성 | 한계 |
|---|---|---|
| dynamic_top100 panel (`종목코드`, `종목명`) | ✅ 있음 | ticker = KRX 재배정 가능, 영구 X |
| OPENDART parquet (`corp_code`, `stock_code`, `corp_name`) | ✅ 있음 | 매핑 별도 audit 필요 |
| KRX 공식 delisting / managed status | ❌ 없음 | 외부 source 필요 (S3, S4 of register) |

## Kill Gates (Referee 명시)

| Kill gate | Decision |
|---|---|
| Permanent ID 또는 reliable lifecycle mapping 생성 불가 | FAIL |
| Disappeared stocks 의 terminal event 설명 불가 | FAIL |
| Delisted names 가 panel 에서 cash-like 처리됨 | FAIL |
| Code reuse / reappearance 구분 불가 | FAIL |
| Dynamic_top100 이 survivor-only universe 에서 생성됨 | FAIL |

## Required Outputs

| Output | 형식 |
|---|---|
| `defect_ledger.csv` | Round 3 schema |
| `audit_summary.md` | pass/fail + lifecycle mapping coverage |
| `disappeared_ticker_ledger.csv` | 258 disappeared ticker 분류 시도 (single source = panel + DART corp_code) |
| `code_reuse_candidates.csv` | reappearance 의심 ticker list |
| `corp_code_to_ticker_mapping.csv` | DART corp_code ↔ ticker linkage matrix |
| `missing_source_update.md` | S3 / S4 register 업데이트 |

출력 위치: `reports/experiments/KR_ID_LIFECYCLE_MASTER_AUDIT_001/`

## Pass / Fail Status

**PASS**: 모든 audit 항목 통과 + permanent ID source acquired or path
locked.

**FAIL**: 위 kill gate 중 하나라도 해당.

**ACCEPTABLE FINDING (PARTIAL)**: 일부 mapping 가능 (DART corp_code) + 외부
source 로 보완 필요.

## Forbidden Outputs

(Round 3 no-performance rule 그대로)

## Codex Implementation Task

```
Implement KR-ID-LIFECYCLE-MASTER-AUDIT-001 A0 AUDIT only.

ABSOLUTE PROHIBITIONS:
- No return computation
- No strategy backtest
- No NAV/CAGR/Sharpe/MDD
- No delisted names dropped from universe analysis
- No lifecycle outcome used as alpha label
- No P08/paper/production connection
- Do not modify research_input_data/

Tasks (Allowed actions only):
1. Verify (날짜, 종목코드) uniqueness in panel.
2. Build disappeared ticker ledger (258 from Round 2; classify by panel
   evidence alone).
3. Identify code-reuse candidates (ticker present → absent → present).
4. Trace name changes per ticker.
5. Cross-reference panel 종목코드 with DART corp_code (OPENDART parquet).
6. Verify dynamic_top100 members map to permanent IDs without gap.
7. Test corp_code ↔ ticker linkage for corporate action events.
8. Mark survivor-only universe candidates (kill gate).

Outputs:
- reports/experiments/KR_ID_LIFECYCLE_MASTER_AUDIT_001/defect_ledger.csv
- reports/experiments/KR_ID_LIFECYCLE_MASTER_AUDIT_001/audit_summary.md
- reports/experiments/KR_ID_LIFECYCLE_MASTER_AUDIT_001/disappeared_ticker_ledger.csv
- reports/experiments/KR_ID_LIFECYCLE_MASTER_AUDIT_001/code_reuse_candidates.csv
- reports/experiments/KR_ID_LIFECYCLE_MASTER_AUDIT_001/corp_code_to_ticker_mapping.csv
- reports/experiments/KR_ID_LIFECYCLE_MASTER_AUDIT_001/missing_source_update.md

If any task would require return computation: STOP. Round 3 hard lock.
```

## Result Summary / Bull-Bear-Referee Review

작성 금지.

## Related

- `docs/round3_referee_verdict_lock.md`
- `docs/round3_no_performance_rule.md`
- `docs/round3_defect_ledger_schema.md`
- `docs/round3_missing_source_register.md` (S4)
- `spec_KR_G5_ADJOHLC_CORPACT_AUDIT_A0.md` (병렬 1A)
