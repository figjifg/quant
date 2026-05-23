# Next Actions

이 프로젝트에서 "다음에 해야 할 것" 은 **오직 이 파일에서만** 적는다. 다른 가이드
파일은 현재 상태 / 정책 / 결과만 기록한다. 새 세션이 다른 파일을 읽다가 "next
phase = X 해라" 같은 문구에 끌려서 자동으로 그 방향으로 행동하는 lock-in 회피.

비어 있는 것이 정상이다. 사용자가 명시적으로 결정한 active 작업만 여기 적는다.

## Active

### S2 OPENDART Body Parser Phase (2026-05-23 Referee Round 4.1 verdict)

**Referee Option A approved (conditional → verified)**. S2 phase 진입 승인.

**Conditions** (모두 충족 확인됨):
- ✅ Round 4.1 push 완료 (local HEAD == remote main = `9052ef1`)
- ✅ `panel_absence` → `not_in_dynamic_universe` rename 반영
- ✅ Round 4.1 10 outputs 모두 remote main 에 push
- ✅ Defect closure delta visible

**Scope** (Referee 명시):
- S2 OPENDART body parser build = **infrastructure repair only**
- NOT strategy testing / performance / Round 2 restart
- C2/C3 = parser output schema 후 구현

### Required S2 Parser Event Taxonomy (10 types)

| Event type | Purpose |
|---|---|
| 자사주 취득/처분/소각 | KR-DART-BODY-RETURN, shareholder return |
| CB / BW 발행 | overhang / dilution |
| 전환청구 | overhang effective supply |
| 유상증자 / 무상증자 | corporate action / dilution |
| 감자 | price adjustment / capital structure |
| 합병 / 분할 | lifecycle / adjustment |
| 추가상장 | supply pressure / tradability |
| 보호예수 해제 | overhang |
| 대주주 매도 | overhang / governance risk |
| 정정 / 철회 / 취소 | PIT correctness |

### Required Parser Output Schema (Referee 명시)

```
ticker / corp_code_dart / rcept_no / rcept_date / event_date / effective_date
/ event_type / amount_krw / shares / shares_before / shares_after / factor
/ cancellation_linkage / source / parser_confidence / manual_audit_status
/ pit_available_at
```

### S2 Phase Kill Gates (Referee 명시)

| Kill gate | Decision |
|---|---|
| Body XML bulk download 안정성 부족 | stop |
| Event type별 parser precision 수작업 audit 실패 | stop |
| 정정공시 linkage 불가 | partial only |
| Cancellation / withdrawal 처리 불가 | partial only |
| event_date / effective_date 구분 불가 | C3 integration 금지 |
| Shares / amount 단위 normalization 실패 | overhang/return component 금지 |
| PIT rcept_date lock 불가 | strategy linkage 금지 |
| C2 factor chain 재현 불가 | G5 full pass 금지 |
| Parser output 직접 strategy 테스트 시도 | protocol violation |

### End Condition (S2 phase 종료 시 산출)

S2 parser A0 report only:
- source coverage
- form coverage
- parser success/failure by event type
- manual audit result
- PIT timestamp lock
- correction/cancellation linkage
- event log schema output
- C2/C3 readiness

**NOT recommend strategy testing**. Referee 가 S2 parser A0 후 별도 판정.

### Executor HOW Decisions (2026-05-23 사용자 위임)

사용자가 HOW (sub-task ordering / decomposition / filter / sample size) 결정권을
executor 에게 위임. 산출:

- `research/experiments/S2_phase_master_ticket.md` — Codex 위임 master ticket
- `reports/experiments/S2_phase_kickoff/executor_brief_to_referee.md` — Referee brief

Sub-task ordering (5 waves, 9 sub-tasks):

| Wave | Sub-task | Owner |
|---|---|---|
| D1 | Bulk OPENDART body XML download + form survey | Codex |
| D2 | XML schema mapping per form (50 sample/form) | Codex |
| D3a | Parser Wave 1 — 자사주 (취득/처분/소각) | Codex |
| D3b | Parser Wave 2 — CB/BW + 전환청구 | Codex |
| D3c | Parser Wave 3 — 기타 7 type | Codex |
| D4 | Output schema integration (17 fields) | Codex |
| D5a | Manual audit sample extraction (30/event type, stratified by year) | Codex |
| D5b | Manual audit execution | 사용자 |
| D6 | C2/C3 readiness spec + A0 report assembly | Executor |

D3a/b/c 병렬 가능. Critical path ≈ 4-7 weeks. Total 6-10 weeks.

### Prerequisites (Pending User Action)

1. **OPENDART API key** confirmed available in local environment or untracked local `.env`
   (`research_input_data/.env`, gitignored); **not git-tracked and not pushed**.
2. D1 시작 전 50-disclosure dry run 으로 endpoint + key 검증.
3. (선택) Referee 가 executor HOW decisions 에 대해 accept / narrow / re-order / hold 중 선택.

## Pending (사용자 결정 시 시작)

### Hard prohibitions (Round 4.1 + S2 phase 동일 유지)

- No return backtest / NAV / CAGR / Sharpe / hit rate / alpha / excess return / MDD
- No post-event / migration / turnover / resume / reversal / flow-return
- No raw return as signal/outcome
- No Round 2 strategy restart
- No residual-event exclusion followed by testing
- No flow strategy testing
- **No DART body alpha test** (S2 가 parser 자체이므로 사용 X)
- No overhang alpha/filter test
- No production / paper / P08 / live readiness / shadow connection
- No parser result = strategy-ready

## Closed / Frozen (변경 시 사용자 결정 필요)

- P08_IEF30 frozen primary
- Strategy TEST + Round 2 cards (5) + 10 BACKLOG cards = REMAINS CLOSED
- 5 Round 3 cards all PARTIAL PASS (no FULL PASS)
- 34 Round 3 defects: **25 CLOSED + 8 PARTIAL + 1 DEFERRED-S2 (G5_000005)**
- Critical 6: 4 CLOSED + 1 PARTIAL + 1 DEFERRED-S2

## Cycle 1 Final State (2026-05-23)

| Round | Outcome |
|---|---|
| Round 1 | TEST 0 / BACKLOG 6 |
| Round 2 | TEST 0 / BACKLOG 5 + 1 infra (Option D) |
| Round 3 | 5 A0 AUDIT complete, 34 defects |
| Round 4 | Source acquisition (S1/S3/S4/S6) + W001 v2 (5/7 components) |
| Round 4 Partial Re-A0 | 5/5 PARTIAL PASS, 23/34 CLOSED |
| Round 4.1 | Residual closure sprint, 25/34 CLOSED, S2 entry criteria met |
| **Round 5 (next)** | **S2 OPENDART body parser phase (infrastructure repair only)** |

## Git Status

- Remote: `https://github.com/figjifg/quant.git` (public)
- Main: `9052ef1` Round 4.1 (= local, push 완료 2026-05-22)
- `.env`: `GITHUB_PASSWORD` 추가됨 (auto-push 가능, .gitignore 보호)
- Future push: credential 자동 (또는 `git push` 시 GITHUB_PASSWORD 사용)

## 룰

- 사용자 명시 결정 없이 여기 항목 추가 X
- 완료되면 제거 또는 closed 로 이동
- "future plan" / "should do" / "next phase" 류 표현은 다른 파일에서도 제