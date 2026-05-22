# Round 2 Referee Verdict Lock

Date: 2026-05-22
Cycle: First Bull/Bear/Referee multi-LLM cycle, **Round 2**
Step: 3 (Referee lock after Bull Round 2 + Bear refutation)
Status: LOCKED

## Scope of This Round

이 Round 는 **production approval / paper candidate / alpha approval 아님**.

판정 범위 = **repo-resident data 기반 A0 diagnostic-only queue**.

## Strategy Pool Status

### Round 1 cards (unchanged, Step 5 lock 유지)

| Category | Count |
|---|---|
| TEST | 0 |
| BACKLOG | 6 |
| REJECT | 0 |

### Round 2 cards (new)

| Strategy ID | Referee Verdict | 허용 범위 |
|---|---|---|
| KR-LIQ-FRAGILITY-AVOID-001 | TEST | A0 diagnostic only, exclusion filter only |
| KR-TRADABILITY-RESUME-RISK-001 | TEST | infrastructure A0 first, strategy diagnostic second |
| KR-LIQ-MIGRATION-001 | TEST | strict hidden-momentum controls required |
| KR-TURNOVER-ATTENTION-001 | TEST | lower-priority A0 diagnostic, migration 과 중복 감시 |
| KR-FLOW-ABSORPTION-001 | BACKLOG | lineage-only audit only, no performance diagnostic |

**Round 2 lock**: A0 TEST 4 / BACKLOG 1 / REJECT 0

## Definition of TEST in This Round

**TEST = 성과 backtest 승인 아님.**

TEST = A0 event-ledger / data-lineage / tradability / placebo / matched-control
**diagnostic 승인** 만.

A0 통과 **전** 에는 다음 표 작성 금지:
- NAV
- CAGR
- Sharpe
- alpha
- excess return

KR-FLOW-ABSORPTION-001 = performance diagnostic 자체 금지 (lineage-only audit
only).

## Work Queue (Referee 승인 순서)

| Priority | Strategy ID | Action |
|---|---|---|
| 1 | KR-LIQ-FRAGILITY-AVOID-001 | A0 event-ledger + fragility filter diagnostic |
| 2 | KR-TRADABILITY-RESUME-RISK-001 | tradability lineage audit → resume event ledger |
| 3 | KR-LIQ-MIGRATION-001 | dynamic_top100 entry ledger + hidden momentum controls |
| 4 | KR-TURNOVER-ATTENTION-001 | PIT turnover lineage + attention baselines |
| 5 | KR-FLOW-ABSORPTION-001 | lineage-only audit, no performance |

## Allowed Artifacts (Round 2)

1. `docs/round2_referee_verdict_lock.md` (this file)
2. `docs/round2_global_A0_gates.md`
3. `docs/round2_event_ledger_schema.md`
4. `research/experiments/spec_KR_LIQ_FRAGILITY_AVOID_A0.md`
5. `research/experiments/spec_KR_TRADABILITY_RESUME_RISK_A0.md`
6. `research/experiments/spec_KR_LIQ_MIGRATION_A0.md`
7. `research/experiments/spec_KR_TURNOVER_ATTENTION_A0.md`
8. `research/experiments/lineage_only_KR_FLOW_ABSORPTION_A0.md`

## Forbidden (Round 2 lock)

- Return backtest 실행 (모든 카드, A0 lineage + event-ledger gate 통과 전)
- KR-FLOW-ABSORPTION-001 의 performance diagnostic (이 사이클 내내 금지)
- Production / paper / P08 / live readiness / shadow track 연결
- 사이클 진행 중 spec 사후 수정 (Bear 재심의 없이)
- Reduced / proxy 변형 (global REJECT trigger 영역)

## Non-Negotiable Gates (요약)

자세한 정의 = `docs/round2_global_A0_gates.md`

1. Permanent identifier (delisting / merge / rename / ticker change / suspension 포함)
2. Survivorship (dynamic_top100 사후 생존 universe X)
3. Tradability semantics (true suspension / limit-lock / panel absence / data missing 구분)
4. Locked limit (limit-up 매수 / limit-down 매도 가능 가정 금지)
5. Adjusted OHLC sanity (split / merge / reduction / 증자 / 거래재개 왜곡 제거)
6. Market cap PIT (restated / 사후 보정 X)
7. Event ledger (모든 카드 필수)
8. Controls (random / matched non-signal / simple baseline 필수)
9. Performance language (production / paper / P08 / live readiness 연결 금지)
10. Metric 우선순위 (locked-position incidence → exit infeasibility → left-tail → MDD → after-cost → turnover-adjusted; CAGR/Sharpe/gross return 후순위)

## End State After Round 2 Lock

| Category | Round 1 | Round 2 | Total |
|---|---:|---:|---:|
| TEST (A0 diagnostic only) | 0 | 4 | 4 |
| BACKLOG | 6 | 1 | 7 |
| REJECT | 0 | 0 | 0 |

## Cycle Position

```
Round 1:
✅ Step 1 Bull 5 ideas
✅ Step 2 Bear refutations
✅ Step 3 Referee lock (TEST 2 / BACKLOG 4)
✅ Step 4 Claude pre-registered spec drafted
✅ Step 5 A0 audit → both TEST → BACKLOG (Referee lock)
🛑 Step 6-9 not reached

Round 2:
✅ Step 1 Bull 5 ideas (new)
✅ Step 2 Bear refutations
✅ Step 3 Referee lock (TEST 4 / BACKLOG 1) ← 지금
🔄 Step 4 Claude pre-registered A0 spec drafting ← 진행 중
⏸  Step 5 A0 audit per card (priority 순서)
⏸  Step 6-9 Bear interpretation → Bull rebuttal → Referee decision
```

## Related Documents

- `docs/round2_global_A0_gates.md` — 10 non-negotiable gates 정의
- `docs/round2_event_ledger_schema.md` — 공통 event ledger schema
- `docs/step5_A0_verdict_lock.md` — Round 1 Step 5 lock (기존 6 BACKLOG)
- `docs/backlog_A0_queue.md` — Round 1 데이터 인프라 task
- `docs/backlog_register.md` — 전체 BACKLOG 등록
- `docs/next_actions.md` — Round 2 active 작업 list

## Note from Referee

> 이전 업로드 파일 일부는 원문 재조회 만료. 위 판정은 Round 2 메모 텍스트 +
> 현재까지 대화에서 고정된 작업 경계를 기준으로 잠근 것. 원문 파일과
> line-by-line 대조 필요 시 재업로드 필요.
