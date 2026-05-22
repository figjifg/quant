# KR-FLOW-UNIT-TIMESTAMP-AUDIT-001 — A0 Audit Spec (Priority 4 / lowest)

## Status
PRE-REGISTERED · **A0 AUDIT only** · 전략 아님
Round 3 Priority: 4 (lowest, Priority 1A + 1B + 2 + 3 통과 후)
Date: 2026-05-22

## Cycle Lineage

- Round 3 Bull idea #5
- Referee Round 3 lock: **A0 AUDIT (flow data lineage audit only; no flow strategy test)**
- Trigger: Round 2 의 KR-FLOW-ABSORPTION-001 (lineage-only BACKLOG) 확장
- F-family overlap 가장 큼 = 최후순위

## Scope

외국인 / 기관 수급 데이터의 sign, unit, timestamp, coverage 가 정확한지
검증. **이번 라운드 = flow data lineage audit only**. Flow strategy test 일체
금지.

## Hard Locks (Round 3 전체)

`docs/round3_no_performance_rule.md` 그대로 적용. 특히 **t+1 flow signal 사용
금지** (publication lag 확인 전).

## Allowed Audit Actions (Referee 명시)

| Audit | 허용 |
|---|---|
| Foreign / institution flow field definitions | ✅ |
| Positive / negative sign convention 확인 | ✅ |
| Unit consistency with trading_value | ✅ |
| Source timestamp / publication lag 확인 | ✅ |
| Missingness by year / stock / market | ✅ |
| Nonzero flow on nontradable days | ✅ |
| Official KRX sample reconciliation 필요 여부 | ✅ |
| Delisted / suspended names inclusion | ✅ |
| F-family warning registration | ✅ |

## Forbidden Actions

| Action | 금지 |
|---|---|
| Flow-return diagnostic | ❌ |
| t+1 flow alpha test | ❌ |
| F/I absorption performance table | ❌ |
| Flow-only baseline 성과 비교 | ❌ |
| Flow strategy 재개 | ❌ |

## Audit Workflow (Allowed only)

### Step 1 — Flow field definitions

Panel field 확인:
- `외국인순매매량` (volume)
- `기관순매매량` (volume)
- `외국인순매수금액추정` (value, KRW)
- `기관순매수금액추정` (value, KRW)
- `수급금액추정여부` (estimation flag, Round 2: 0% True ✅)

각 field 의 vendor doc / source documentation 확인 (현재 없음 = S6 defect)

### Step 2 — Sign convention

Sample 10-20 종목 × 10-20 거래일 verification:
- 알려진 외국인 매수 강세 / 매도 강세 사례 가져와 sign 확인
- "+" = 매수 ? "+" = 매도 ?
- 부호 확정 X 면 `sign_convention_unverified` defect

### Step 3 — Unit consistency

- `외국인순매수금액추정` 의 단위 (원? 백만 원?)
- `거래대금추정` 단위 와 비교 sanity
- Ratio 가 합리적 범위인지 sample audit
- 불일치 시 `unit_inconsistency` defect

### Step 4 — Source timestamp / publication lag

- Vendor 가 어느 시점에 flow data 제공? (장 마감 직후? 익일? 익영업일?)
- 어느 시점부터 안전하게 strategy 가 사용 가능?
- 현재 doc 없음 = `publication_lag_unknown` defect

### Step 5 — Missingness by year / stock / market

- 연도별 / 종목별 / 시장 (KOSPI / KOSDAQ) 별 missing flow 비율
- failed / suspended names 에 missingness 집중 = `missingness_concentrated_in_failed_names`

### Step 6 — Nonzero flow on nontradable days

- `tradable=False` 행에서 flow 값이 nonzero 인 경우 확인
- 정상 (장 마감 후 calc) vs 데이터 artifact 구분
- defect: `nonzero_flow_on_nontradable_day` (해석 caveat)

### Step 7 — Official KRX sample reconciliation 필요 여부

- 한국거래소 (krx.co.kr) 의 투자자별 거래실적 sample 과 비교 가능?
- 외부 source 와 reconciliation 가능성 평가

### Step 8 — Delisted / suspended names inclusion

- Disappeared 258 ticker 중 disappearance 직전 flow 패턴 audit
- Flow 가 누락되었는지 / 마지막까지 기록되었는지

### Step 9 — F-family warning registration

- F-family (이미 closed) 의 flow-following 결과와 본 카드 의 차별 mechanism
  사전 등록
- 단순히 F-family 재포장 위험 명시
- 향후 strategy 재개 시 글로벌 REJECT trigger 와 매칭

## Data Available

| Source | 가용성 | 한계 |
|---|---|---|
| Panel flow columns (외국인 / 기관 순매매량, 순매수금액추정) | ✅ 있음 | sign / unit / timestamp doc X |
| `수급금액추정여부` flag | ✅ 0% True (Round 2 확인) | 추정 없음 ✅ |
| KRX 공식 투자자별 거래실적 archive | ❌ 없음 | S6 source 필요 |

## Kill Gates (Referee 명시)

| Kill gate | Decision |
|---|---|
| Positive sign 검증 불가 | FAIL |
| Unit 불일치 | FAIL |
| Timestamp / publication timing unknown | FAIL |
| Official KRX sample mismatch material | FAIL |
| Missingness 가 failed / suspended names 에 집중 | FAIL |
| 이후 flow strategy 가 flow-only baseline 을 못 이김 | **future strategy KILL** (이번 audit X) |

## Required Outputs

| Output | 형식 |
|---|---|
| `defect_ledger.csv` | Round 3 schema |
| `audit_summary.md` | pass/fail + F-family warning |
| `sign_convention_sample.csv` | 10-20 × 10-20 sample verification |
| `unit_consistency_check.md` | flow value / trading value ratio sanity |
| `publication_lag_assessment.md` | timestamp / lag 확인 + S6 필요 fields |
| `missingness_breakdown.csv` | year × stock × market breakdown |
| `f_family_warning_log.md` | F-family overlap 위험 사전 등록 |
| `missing_source_update.md` | S6 register 업데이트 |

출력 위치: `reports/experiments/KR_FLOW_UNIT_TIMESTAMP_AUDIT_001/`

## Pass / Fail Status

**Audit 결과 = informational + S6 source request**. Strategy 진입 = 별도
사이클 + Bear 재심의 + Referee 재승인 필요 (이번 라운드에서 strategy
authorization 0).

## Forbidden Outputs

(Round 3 no-performance rule 그대로)

## Codex Implementation Task

```
Implement KR-FLOW-UNIT-TIMESTAMP-AUDIT-001 A0 AUDIT only.

ABSOLUTE PROHIBITIONS:
- No flow-return diagnostic
- No t+1 flow alpha test
- No F/I absorption performance table
- No flow strategy resume
- No NAV/CAGR/Sharpe/MDD
- No P08/paper/production
- Do not modify research_input_data/

Tasks (Allowed actions only):
1. Document flow fields (외국인 / 기관 순매매량, 순매수금액추정).
2. Sample sign convention verification (10-20 stocks × 10-20 days).
3. Unit consistency check (flow value vs trading_value ratio).
4. Document publication lag (or mark unknown).
5. Compute missingness by year / stock / market.
6. Verify nonzero flow on nontradable days behavior.
7. Document KRX sample reconciliation feasibility (no actual reconciliation
   in this audit; just feasibility report).
8. Cross-reference disappeared tickers' flow pattern.
9. Register F-family overlap warning (no return computation).

Outputs:
- reports/experiments/KR_FLOW_UNIT_TIMESTAMP_AUDIT_001/defect_ledger.csv
- reports/experiments/KR_FLOW_UNIT_TIMESTAMP_AUDIT_001/audit_summary.md
- reports/experiments/KR_FLOW_UNIT_TIMESTAMP_AUDIT_001/sign_convention_sample.csv
- reports/experiments/KR_FLOW_UNIT_TIMESTAMP_AUDIT_001/unit_consistency_check.md
- reports/experiments/KR_FLOW_UNIT_TIMESTAMP_AUDIT_001/publication_lag_assessment.md
- reports/experiments/KR_FLOW_UNIT_TIMESTAMP_AUDIT_001/missingness_breakdown.csv
- reports/experiments/KR_FLOW_UNIT_TIMESTAMP_AUDIT_001/f_family_warning_log.md
- reports/experiments/KR_FLOW_UNIT_TIMESTAMP_AUDIT_001/missing_source_update.md

If any task requires return outcome or flow strategy test: STOP.
Round 3 lowest priority + strictest no-strategy lock.
```

## Result Summary / Bull-Bear-Referee Review

작성 금지.

## Related

- `docs/round3_referee_verdict_lock.md`
- `docs/round3_no_performance_rule.md`
- `docs/round3_defect_ledger_schema.md`
- `docs/round3_missing_source_register.md` (S6)
- `research/experiments/lineage_only_KR_FLOW_ABSORPTION_A0.md` (Round 2 lineage-only BACKLOG, 본 카드와 일부 overlap)
- 기존 F-family findings (closed)
