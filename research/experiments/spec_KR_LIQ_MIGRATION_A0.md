# KR-LIQ-MIGRATION-001 — A0 Diagnostic Spec (Priority 3)

## Status
PRE-REGISTERED · TEST · **strict hidden-momentum controls required**
Round 2 Priority: 3
Date: 2026-05-22

## Cycle Lineage

- Round 2 Bull idea #3
- Referee Round 2 lock: **TEST (hidden momentum controls required)**
- Bear / Referee 주의 : hidden momentum, market-cap jump, theme-following
  proxy 위험 큼

## Scope

dynamic_top100 신규 진입을 investability / liquidity regime migration 으로
해석하는 **A0 diagnostic 허용**. 단 trailing-return matched control **없이는
결과 해석 금지**.

### Allowed question

> "dynamic_top100 신규 진입이 단순한 hidden momentum / size jump / theme
> spike 가 아닌, investability state transition 으로서 incremental
> evidence 를 가지는가?"

### Not allowed

> 신규 진입을 alpha signal 로 production 연결

## Hypothesis (with strict controls)

매 분기 dynamic_top100 에 신규 진입하는 종목은 liquidity regime transition
(저 ADV → 고 ADV) 을 겪고 있다. 이 transition 자체가 forward 5d / 20d /
63d 의 (locked-position incidence / exit infeasibility / left-tail) 에 영향
을 주는지 진단.

**살아남으려면**: trailing 20d / 60d return matched control 후에도 효과 잔존.

## Required Global Gates

`docs/round2_global_A0_gates.md` 10 gate 모두 적용. 특히:
- **Gate 2 Survivorship (핵심: top100 entry 가 진짜 PIT 인지)**
- **Gate 6 Market cap PIT (핵심: size jump 통제)**
- Gate 1 Permanent ID
- Gate 5 Adjusted OHLC sanity (split / 증자 시 size jump 가짜 일 수 있음)
- Gate 7 Event ledger

## Required Controls (Referee 명시, 모두 필수)

| Control | 목적 |
|---|---|
| Same-date top100 incumbent matched basket | 신규 진입 효과 분리 |
| Market cap matched control | size jump 통제 |
| Trading value matched control | liquidity level 통제 |
| **Trailing 20d / 60d return matched control** | **hidden momentum 통제 (핵심)** |
| top100 유지 종목 subgroup | migration vs incumbent 비교 |
| 재진입 종목 subgroup | one-off entry 와 re-entry 분리 |
| Entry date ±60d shift placebo | calendar / event timing placebo |

## Signal Definition

각 분기 (또는 monthly snapshot) 의 dynamic_top100 entry:

- `entry_event` = 시점 t-1 에 top100 밖이었으나 t 에 top100 진입
- `entry_type` ∈ {first_entry, re_entry}
- `entry_market_cap_jump` = market_cap(t) / market_cap(t-1)
- `entry_trading_value_jump` = trading_value(t) / trading_value(t-1)
- `entry_trailing_return_20d` = return(t-20, t)
- `entry_trailing_return_60d` = return(t-60, t)

**Tuning 금지**: 위 변수의 threshold / weight 사후 조정 X.

## Required Event Ledger

`docs/round2_event_ledger_schema.md` 그대로. 각 entry_event = 1 main event,
각 matched control = 별도 row.

추가 ledger column (이 카드 specific):
- `entry_type` (first_entry / re_entry)
- `entry_market_cap_jump`
- `entry_trading_value_jump`
- `entry_trailing_return_20d`
- `entry_trailing_return_60d`
- `prior_top100_dates` (re_entry 시 이전 진입 history)
- `theme_cluster_id` (있다면; 특정 sector / theme 군집)

출력: `reports/experiments/KR_LIQ_MIGRATION_001/event_ledger.csv`

## A0 Diagnostic Metrics

Round 2 우선순위 (Gate 10) 그대로:

1. **Locked-position incidence** (entry 후 5/20/63d 내)
2. **Exit infeasibility ratio**
3. **Left-tail loss** (entry 후 5/20/63d 의 5% / 10% VaR)
4. **MDD** (entry 직후 N일 cumulative MDD)
5. **After-cost return** (control 대비)

각 metric = 신규 entry vs incumbent vs 4 matched control 비교.

## Kill Gates (Referee 명시)

| Failure | Decision |
|---|---|
| dynamic_top100 membership 이 survivor-biased | KILL (Gate 2 fail) |
| top100 entry date 가 미래 데이터로 재계산 (look-ahead) | KILL (Gate 6 fail) |
| Trailing-return matched control 후 효과 소멸 | KILL (= hidden momentum) |
| Market cap jump 만 설명 | KILL (= size effect) |
| Trading value spike 만 설명 | KILL (= liquidity level effect) |
| 특정 테마 / 연도 / 종목군 집중 | KILL |

## Forbidden (Round 2 lock)

- Standalone alpha 측정 시도
- top100 entry 를 production basket 연결
- 사후 entry result 사용
- spec 사후 수정 (Bear 재심의 없이)
- "최근 많이 오른 종목이 top100 에 들어왔다" 로 판명되면 즉시 폐기

## Codex Implementation Task

```
Implement KR-LIQ-MIGRATION-001 A0 diagnostic.

DO NOT:
- Skip Gate 2 (survivorship verification)
- Skip Gate 6 (market cap PIT)
- Skip trailing-return matched control
- Implement as standalone alpha
- Run return backtest before event ledger + gate check pass
- Connect to P08 / paper tracking / production

Tasks:
1. Verify Gate 2: dynamic_top100 PIT (t-1 시점 정보만으로 t 시점 panel 재현 가능).
2. Verify Gate 6: market_cap is PIT (restated 사용 X).
3. Build entry_event ledger (per spec definition).
4. Generate matched controls (7 control types).
5. Compute Round 2 priority metrics per control comparison.
6. Verify trailing-return matched control 후 효과 잔존 여부.
7. Verify theme / year / size concentration check.
8. Save outputs under reports/experiments/KR_LIQ_MIGRATION_001/.

Required outputs:
- config.yaml (locked scope)
- event_ledger.csv (per round2 schema + 추가 column)
- ledger_audit.md
- gate_check.md (Gate 1-10)
- entry_vs_controls.csv (5 metric x 8 group)
- hidden_momentum_check.md (trailing return matched 결과)
- concentration_check.csv (theme / year / size)
- report.md (A0 diagnostic only, NO production language, NO alpha claim)
```

## Result Summary

작성 금지.

## Bull/Bear/Referee Review

작성 금지.
