# Round 2 Step 5 Gate 5 Fail Lock

Date: 2026-05-22
Cycle: First Bull/Bear/Referee multi-LLM cycle · Round 2 Step 5
Referee verdict: LOCKED (**Option D** selected)
Status: Round 2 strategy diagnostic 중단

## Decision Summary

**Selected option: Option D**

KR-LIQ-FRAGILITY-AVOID-001 = **A0 KILL under current data**.

- 전략 가설 자체의 영구 REJECT 아님
- W001 v1 / dynamic_top100 panel 의 measurement layer 가 성과 진단에 부적합 = **infrastructure finding**

## Card-by-Card Lock

| Card | Step 4 status | Step 5 결과 | Referee 결정 |
|---|---|---|---|
| KR-LIQ-FRAGILITY-AVOID-001 | TEST | Gate 5 FAIL | **A0 KILL / BACKLOG-INFRA** |
| KR-TRADABILITY-RESUME-RISK-001 | TEST | 영향 받음 | strategy diagnostic 중단, **infrastructure audit only** |
| KR-LIQ-MIGRATION-001 | TEST | 영향 받음 | **BACKLOG 대기 (Gate 5 fix 까지)** |
| KR-TURNOVER-ATTENTION-001 | TEST | 영향 받음 | **BACKLOG 대기 (Gate 5 fix 까지)** |
| KR-FLOW-ABSORPTION-001 | BACKLOG | 변경 없음 | lineage-only BACKLOG 유지 |

## Round 2 Current State

```
Active strategy TEST              : 0
Infrastructure audit allowed      : 1 (KR-TRADABILITY-RESUME-RISK-001)
BACKLOG / blocked (Round 2)       : 4
Original strategy REJECT          : 0
Current KR-LIQ implementation     : A0 KILL
```

## Why Option D (Referee 근거)

| 발견 | 의미 |
|---|---|
| Adjusted columns 없음 | return / limit / jump 계산 오염 |
| \|daily return\| > 50% events 147건 | adjusted price 가 없는 명백한 증거 |
| `adjust_for_corporate_actions()` 호출 후 147건 unchanged | 조정 함수가 실제 조정 X (alias 만 생성) |
| Split day 가 false limit move 로 잡힐 위험 | fragility signal 직접 오염 |
| 같은 panel 을 Priority 2-4 가 사용 | Round 2 TEST 4개 모두 영향권 |

KR-LIQ-FRAGILITY-AVOID-001 의 핵심 signal (locked-limit incidence / exit
fragility / tail feasibility) 가 raw price artifact 에 직접 노출.

→ event ledger / controls / performance diagnostic 진입 시 false alpha
생성 위험. 따라서 진입 금지.

## Rejected Options

| 옵션 | Referee 판단 |
|---|---|
| Option A — 모든 카드 즉시 KILL | 너무 넓음. 전략 가설이 아니라 infrastructure 결함이 핵심 |
| Option B — adjusted OHLC source acquire 후 대기 | unblock 경로로 채택하되 현재 즉시 실행 X |
| Option C — 147건 제외 후 signal 재정의 | **불허**. spec 사후 변경 + Bear 재심의 전 금지. 147건만 제외해도 raw return / limit / suspension / corp action / panel absence 가 섞임 |
| Option D — infrastructure finding + KR-LIQ KILL + backlog 등록 | **선택** |

## Hard Prohibitions (현재 lock, 위반 시 protocol violation)

- Event ledger 구축 (strategy performance 용)
- Return backtest 실행
- NAV / CAGR / Sharpe / alpha / excess return / MDD 산출
- Spec 사후 수정
- 147 건 extreme-return events 제외 후 testing 계속
- Tail-risk 개선 주장
- Alpha 주장
- Production / paper tracking / P08 / live readiness / shadow track 연결
- Priority 3-4 strategy audit 진입 (Gate 5 repair + Referee 재승인 전)

## Allowed Next Actions (7개, Referee 명시)

| # | Artifact |
|---|---|
| 1 | `docs/round2_gate5_fail_lock.md` (이 파일) |
| 2 | Backlog task `W001-V1-ADJUSTED-OHLC-CORPORATE-ACTION-AUDIT-001` |
| 3 | `docs/data_gap_adjusted_ohlc.md` |
| 4 | `reports/experiments/W001_V1_AUDIT/corporate_action_artifact_ledger.csv` (147 건) |
| 5 | `docs/tradability_semantics_audit.md` |
| 6 | `adjust_for_corporate_actions()` alias bug 검증 + 문서화 |
| 7 | KR-TRADABILITY-RESUME-RISK-001 infrastructure audit only (tradability flag lineage / 4-cause / extreme return × tradability flag 교차 / `next_executable_date()` 검증) |

## KR-TRADABILITY-RESUME-RISK-001 Allowed Scope (Referee 명시)

**Allowed**:
- Tradability flag lineage 확인
- `tradable=false` 원인 분해
- True suspension vs limit-lock vs panel absence vs data missing 구분
- `next_executable_date()` 동작 검증
- 147 개 extreme return event 와 tradability flag 교차표
- Corporate action artifact ledger 작성
- Adjusted OHLC missing issue 문서화

**Forbidden**:
- 재개 후 5d / 20d / 63d return diagnostic
- Long-only exclusion filter 성과
- Event-driven return table
- NAV / CAGR / Sharpe / MDD

## Unblock Conditions (Round 2 strategy diagnostic 재개)

| Required | 내용 |
|---|---|
| Adjusted OHLCV source | adjusted open/high/low/close 또는 신뢰 가능한 adjusted return |
| Corporate action event source | split / reverse split / capital reduction / rights issue / merger / suspension / resumption |
| Adjustment verification | 147 건 extreme return 의 root cause 분류 후 적절한 처리 |
| Function repair | `adjust_for_corporate_actions()` 가 alias 가 아니라 실제 조정 수행 |
| Permanent ID mapping | KRX ticker only 에서 corp_code / permanent identifier 보강 |
| dynamic_top100 lineage | 사후 생존 universe 아님 confirm |
| Tradability semantics | true suspension / limit-lock / panel absence / missing 분리 |
| Executable rule | limit-up / down / suspension / 재개일 체결 가능성 보수적 처리 |

이 조건 통과 → Gate 1-6 재실행 → event ledger 진입 가능.

## Framework Significance

이번 결과 = **Round 2 실패가 아니라 W001 v1 한국 주식 research stack 의
핵심 measurement defect 를 잡은 정상적인 A0 결과**.

지금 backtest 로 밀고 가면 false alpha 가능성 높음.

False alpha 차단 framework: **9/9 catches** (기존 8 + 이번 Round 2 Step 5).

## Cycle Position

```
Round 1:
✅ Step 1-5 (Step 5 lock: TEST 0 / BACKLOG 6)

Round 2:
✅ Step 1 Bull 5 ideas
✅ Step 2 Bear refutations
✅ Step 3 Referee lock (TEST 4 / BACKLOG 1)
✅ Step 4 Claude pre-registered A0 spec drafting
✅ Step 5 A0 audit Priority 1 → Gate 5 FAIL → Referee Option D lock
🔄 Step 5b Infrastructure audit + backlog 등록 (지금)
⏸  Step 5c (Gate 5 repair + Referee 재승인 후) Priority 2-4 진입
⏸  Step 6-9 not reached
```

## Related Documents

- `docs/round2_referee_verdict_lock.md` — Round 2 Step 3 lock
- `docs/round2_global_A0_gates.md` — 10 gates 정의
- `docs/data_gap_adjusted_ohlc.md` — adjusted OHLC 부재 문서
- `docs/tradability_semantics_audit.md` — 4-cause distinction audit
- `docs/backlog_register.md` — W001-V1 audit backlog task 등록
- `reports/experiments/KR_LIQ_FRAGILITY_AVOID_001/gate_check.md` — Step 5 audit 결과
- `reports/experiments/W001_V1_AUDIT/` — infrastructure audit artifacts
