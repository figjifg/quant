# KR-TOP100-PIT-LINEAGE-AUDIT-001 — A0 Audit Spec (Priority 3)

## Status
PRE-REGISTERED · **A0 AUDIT only** · 전략 아님
Round 3 Priority: 3 (Priority 1A + 1B + 2 통과 후)
Date: 2026-05-22

## Cycle Lineage

- Round 3 Bull idea #4
- Referee Round 3 lock: **A0 AUDIT (dynamic_top100 universe lineage audit only)**
- Trigger: Round 2 Step 5 결과 + 모든 카드의 dependency

## Scope

dynamic_top100 universe 가 point-in-time 으로 생성됐는지, survivor universe
또는 사후 market cap / trading value 정보로 오염됐는지 검증.

## Hard Locks (Round 3 전체)

`docs/round3_no_performance_rule.md` 그대로 적용. 특히 **migration / turnover
return 금지**.

## Allowed Audit Actions (Referee 명시)

| Audit | 허용 |
|---|---|
| Dynamic_top100 generation script 존재 여부 확인 | ✅ |
| Selection rule documentation 확인 | ✅ |
| All-listed candidate universe by date 확인 | ✅ |
| Membership reproducibility | ✅ |
| Delisted / merged / renamed member retention | ✅ |
| Market cap / trading value timestamp lineage | ✅ |
| Missing membership days | ✅ |
| Membership transition outliers | ✅ |

## Forbidden Actions

| Action | 금지 |
|---|---|
| Top100 migration return diagnostic | ❌ |
| Turnover return diagnostic | ❌ |
| Top100 신규 진입 alpha 주장 | ❌ |
| Universe audit 결과 = strategy evidence 해석 | ❌ |

## Audit Workflow (Allowed only)

### Step 1 — Generation script 존재 여부

- Repo 에 dynamic_top100 panel 생성 코드 / pipeline 존재 확인
- 위치: `src/` 또는 `scripts/` 또는 다른 곳
- 없음 = `generation_script_missing` defect

### Step 2 — Selection rule documentation

- Generation script 의 selection rule 명문화 확인:
  - Universe (전 KOSPI? KOSPI+KOSDAQ?)
  - Ranking 기준 (market cap? trading value? composite?)
  - Top N (정확히 100?)
  - Rebalance 주기 (daily? weekly? monthly?)
  - Tie-breaking rule
- 없음 = `selection_rule_undocumented`

### Step 3 — All-listed candidate universe by date

- 각 date 별 KRX 전체 상장 종목 list (top100 외 포함) PIT 구성 가능?
- Panel 의 ~563 종목 per date = 일부 전체 universe 의 subset
- 전체 universe source 필요 (KRX 상장 list / FnGuide / vendor)

### Step 4 — Membership reproducibility

- Generation script 실행 시 panel 의 `동적유니버스포함 = True` 결과 재현
  가능?
- Panel 의 100 종목 set 이 생성 rule 로 재현되는지 sample audit
- 불가 = `membership_not_reproducible` defect

### Step 5 — Delisted / merged / renamed member retention

- Top100 진입했던 종목이 그 후 상폐 / 합병 / rename 시 panel 에 보존?
- 사라진 disappeared 258 ticker 중 한 번이라도 top100 진입한 종목 list
- Survivor universe vs PIT 검증

### Step 6 — Market cap / trading value timestamp lineage

- `시가총액` / `거래대금` 의 timestamp = 발표 시점 vs 사후 보정?
- Round 2 finding: `시가총액추정여부` / `거래대금추정여부` 모두 0% True
  = 추정 없음 ✅
- 단 그 외 사후 보정 (vendor 가 별도 정정) 가능성 별도 audit

### Step 7 — Missing membership days

- 특정 종목이 top100 에 들어왔다 / 나갔다 transition 의 frequency 분석
- 미친듯이 빠른 churn = generation rule artifact 의심
- 매 거래일 100 종목 ± 변화량 stable 한지

### Step 8 — Membership transition outliers

- 단일 날짜에 다수 종목이 동시에 진입 / 이탈 = rebalance event 또는 rule
  변경
- 이상 transition 패턴 detection

## Data Available

| Source | 가용성 | 한계 |
|---|---|---|
| `dynamic_top100_*_panel.csv` (`동적유니버스포함`) | ✅ 있음 | rule 의 implementation 노출 |
| `시가총액 / 거래대금` PIT | ✅ 있음 (Round 2 = 0% estimated) | 정의 doc 필요 |
| Generation script | ❓ 확인 필요 (Step 1) | repo 안 또는 외부 |
| 전체 상장 list per date | ❌ 없음 | 외부 source 필요 (S5) |

## Kill Gates (Referee 명시)

| Kill gate | Decision |
|---|---|
| dynamic_top100 재현 불가 | FAIL |
| Generation rule undocumented | FAIL |
| Universe survivor-only | FAIL |
| Delisted / merged historical members absent | FAIL |
| Market cap / trading value non-PIT | FAIL |
| Top100 membership 이 깨진 adjusted OHLC 에 의존 | FAIL (Gate 5 dependency) |

## Required Outputs

| Output | 형식 |
|---|---|
| `defect_ledger.csv` | Round 3 schema |
| `audit_summary.md` | pass/fail + rule documentation status |
| `generation_script_status.md` | script 존재 여부 + 위치 + rule 명세 |
| `membership_reproducibility.md` | sample reproducibility test 결과 |
| `survivor_check.csv` | disappeared 258 ticker 중 top100 진입 history |
| `missing_source_update.md` | S5 register 업데이트 |

출력 위치: `reports/experiments/KR_TOP100_PIT_LINEAGE_AUDIT_001/`

## Pass / Fail Status

**Conditional**: Step 1 (script 존재) 결과에 따라 크게 달라짐:
- Script 있음 + rule documented → audit 진행 가능
- 둘 다 missing → 즉시 FAIL (rule 자체 미확인)

## Forbidden Outputs

(Round 3 no-performance rule 그대로)

## Codex Implementation Task

```
Implement KR-TOP100-PIT-LINEAGE-AUDIT-001 A0 AUDIT only.

ABSOLUTE PROHIBITIONS:
- No migration return / turnover return / strategy edge claim
- No NAV/CAGR/Sharpe/MDD
- No P08/paper/production
- Do not modify research_input_data/

Tasks (Allowed actions only):
1. Search repo for dynamic_top100 generation script (src/, scripts/, etc.).
2. Document selection rule if found; report missing if not.
3. Verify market_cap and trading_value PIT lineage (extend Round 2 finding).
4. Attempt membership reproducibility on sample dates.
5. Cross-reference disappeared 258 ticker with top100 entry history.
6. Compute membership transition frequency per ticker.
7. Identify transition outlier dates.
8. Verify all-listed candidate universe gap.

Outputs:
- reports/experiments/KR_TOP100_PIT_LINEAGE_AUDIT_001/defect_ledger.csv
- reports/experiments/KR_TOP100_PIT_LINEAGE_AUDIT_001/audit_summary.md
- reports/experiments/KR_TOP100_PIT_LINEAGE_AUDIT_001/generation_script_status.md
- reports/experiments/KR_TOP100_PIT_LINEAGE_AUDIT_001/membership_reproducibility.md
- reports/experiments/KR_TOP100_PIT_LINEAGE_AUDIT_001/survivor_check.csv
- reports/experiments/KR_TOP100_PIT_LINEAGE_AUDIT_001/missing_source_update.md

If any task requires return outcome: STOP.
```

## Result Summary / Bull-Bear-Referee Review

작성 금지.

## Related

- `docs/round3_referee_verdict_lock.md`
- `docs/round3_no_performance_rule.md`
- `docs/round3_defect_ledger_schema.md`
- `docs/round3_missing_source_register.md` (S5)
- `spec_KR_G5_ADJOHLC_CORPACT_AUDIT_A0.md` (Step 6 dependency)
- `spec_KR_ID_LIFECYCLE_MASTER_AUDIT_A0.md` (Step 5 cross-reference)
