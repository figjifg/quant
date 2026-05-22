# Step 5 A0 Verdict Lock (Cycle 1)

Date: 2026-05-22
Cycle: First Bull/Bear/Referee multi-LLM cycle
Step: 5 (Claude/Codex executor A0 data audit)
Referee verdict: LOCKED (이 문서는 Referee Step 5 decision 의 official record)

## End State (Referee lock)

- Active TEST count: **0**
- BACKLOG count: **6**
- Original strategy REJECT count: **0**
- Reduced proxy variants: blocked or REJECT-triggered

## Card-by-Card Outcome

### KR-PASSIVE-REBALANCE-001 A형 — DOWNGRADED FROM TEST → BACKLOG

**Reason** (Referee 그대로):
- Required KRX/index-provider official announcement date plus confirmed
  inclusion/exclusion basket does not exist in repo
- Current available data is not an index event calendar
- DART, ETF AUM, fund holding changes, futures, or breadth data may not be
  used as substitutes

**A0 verdict**: FAIL (Data lineage Item 1 = FAIL → 2-12 N/A)

### KR-OVERHANG-AVOID-001 filter형 — DOWNGRADED FROM TEST → BACKLOG

**Reason** (Referee 그대로):
- Current DART data is title-flag binary only
- Fixed scope requires overhang intensity, potential shares / free float,
  event severity, and fuller event taxonomy
- Current data cannot detect conversion request, additional listing, or
  lockup release
- Binary title flag exclusion would alter the pre-registered spec and risks
  triggering the title-keyword / proxy REJECT boundary

**A0 verdict**: PARTIAL (Data lineage Item 1 = PARTIAL, but Bear fixed
scope core measurement variables 결손 → spec 미충족)

## Why No Backtest

Referee 명시:
- Do not run any backtest
- Do not invoke Codex for performance testing
- Do not modify production, paper, P08, live readiness, or shadow tracks

근거:
- 두 카드 모두 사전 등록 fixed scope 의 핵심 데이터 요건 미충족
- Reduced / proxy 변형 진행 시 Bear 의 글로벌 REJECT trigger 영역에 진입
  ("DART 본문 대신 제목 키워드 확장", "사후 확정 결과를 발표일 신호 사용")
- 사전 등록 spec 변경 = Referee + Bear 재심의 없이 금지

## Forbidden Actions

### KR-PASSIVE-REBALANCE-001 A형
- No proxy substitution
- No post-hoc reconstruction from final index membership
- No B-type prediction model
- No performance test

### KR-OVERHANG-AVOID-001 filter형
- No binary flag reduced TEST under the current ID
- No return backtest using title flags only
- No standalone alpha framing
- No long-short framing
- No production linkage

## Optional (non-performance only)

Overhang title flags coverage / precision audit plan 작성 가능. 단:
- Returns / alpha / excess performance / NAV / Sharpe / CAGR / MDD /
  portfolio results 포함 X
- 별도 weak diagnostic ID 사용 (KR-OVERHANG-AVOID-001 ID 사용 X)

이 optional 작업은 사용자 명시 결정 시에만 진행.

## Cycle Position

```
✅ Step 1 — Bull 5 ideas
✅ Step 2 — Bear 5 refutations (18-item analysis)
✅ Step 3 — Referee TEST 2 / BACKLOG 4 / REJECT 0 lock
✅ Step 4 — Claude executor pre-registered spec drafted
✅ Step 5 — A0 data audit → both TEST cards downgraded to BACKLOG
⏸  Step 6-9 — not reached this cycle (no backtest, no result interpretation)
```

## Framework Significance

이 사이클의 결과 = "alpha discovery 실패" 가 아니라 "audit-first framework
의도대로 작동":
- Bear 의 사전 분석 + Referee 의 fixed scope lock + executor 의 A0 audit
  세 layer 가 모두 data prerequisite 부족을 catch
- 진짜 bottleneck = 데이터 인프라 (KRX index event calendar + DART body
  parser) 임을 cycle 자체로 확인
- False alpha 차단 framework 7/7 catches (기존 Q/R/S/X-ETF001/X-ETF900/
  X-KR001 + 첫 사이클 두 카드)

## Related Documents

- `docs/backlog_A0_queue.md` — 두 데이터 인프라 task
- `docs/data_gap_KR_PASSIVE_REBALANCE.md` — KRX index data 누락 필드
- `docs/data_gap_KR_OVERHANG_AVOID.md` — DART body parser 필드 / parser 요건
- `research/experiments/KR_PASSIVE_REBALANCE_001_A_test.md` — 사전 등록 spec (lock 됨, 사용 X)
- `research/experiments/KR_OVERHANG_AVOID_001_filter_test.md` — 사전 등록 spec (lock 됨, 사용 X)
- `docs/backlog_register.md` — 전체 BACKLOG 등록
- `docs/next_actions.md` — active TEST = 0 반영
- `x_lab/closed_register.md` / `x_lab/final_status.md` — X-Lab status 반영
- `~/.claude/projects/-home-jin-code-quant/memory/project_first_bull_bear_cycle.md` — cycle 결과 메모리
