# S2 Phase Kickoff — Executor Brief to Referee

Date: 2026-05-23
Origin: Referee Round 4.1 verdict (Option A approved, conditional ✅)
Author: Claude Code (executor role)
Audience: Referee + 사용자
Scope: HOW decisions made by executor under user-delegated authority (2026-05-23 message)

## Section 1 — Verification of Round 4.1 Prerequisites

Referee Round 4.1 immediate prerequisite check = **4/4 PASS**.

| Check | Status | Evidence |
|---|---|---|
| HEAD == origin/main | ✅ | `9052ef1` (both local and remote) |
| 10 Round 4.1 artifacts on origin/main | ✅ 10/10 | `git cat-file -e origin/main:<path>` confirmed each |
| `src/utils/tradability.py` rename on origin/main | ✅ | line 95-97 TRADABLE_STATES has `not_in_dynamic_universe`; rename annotated in comment |
| Backward-compat alias preserved | ✅ | line 112 `"panel_absence": "not_in_dynamic_universe"` in deprecated map |
| `not_in_dynamic_universe` ≠ non-tradable exchange status | ✅ | included in TRADABLE_STATES (tradable side); used at line 241 for in_universe=False classification |

→ S2 full parser phase entry condition met. No verification residual.

## Section 2 — Round 4.1 Accepted State (Reaffirm)

| Metric | Value |
|---|---|
| 5/5 cards | PARTIAL PASS (no FAIL, no REGRESSION) |
| Defect closure | 25 CLOSED / 8 PARTIAL / 1 DEFERRED-S2 / 0 OPEN / 0 REGRESSION |
| Critical 6 | 4 CLOSED / 1 PARTIAL / 1 DEFERRED-S2 |
| Strategy TEST + Round 2 + 10 BACKLOG | REMAINS CLOSED |
| P08_IEF30 frozen | Maintained |
| Audit-first 12 (6/6 catches) | Maintained as official charter |

## Section 3 — Executor HOW Decisions

사용자가 2026-05-23 메시지에서 HOW 결정권을 executor 에게 위임. 아래는 executor 가 단독 결정한 사항. Referee 가 narrowing 또는 ordering 변경하면 따른다.

### 3.1 Sub-task decomposition (9 sub-tasks, 5 waves)

| Wave | Sub-task | Owner | Depends |
|---|---|---|---|
| D1 | Bulk OPENDART body XML download + form survey | Codex | API key |
| D2 | XML schema mapping per form (50 sample/form) | Codex | D1 |
| D3a | Parser Wave 1 — 자사주 (취득/처분/소각) | Codex | D2 |
| D3b | Parser Wave 2 — CB/BW + 전환청구 | Codex | D2 |
| D3c | Parser Wave 3 — 유증/무증/감자/합병·분할/추가상장/보호예수/대주주매도/정정·취소 | Codex | D2 |
| D4 | Output schema integration (17 fields) | Codex | D3a/b/c |
| D5a | Manual audit sample extraction (30/event type stratified by year) | Codex | D3 |
| D5b | Manual audit execution | 사용자 | D5a |
| D6 | C2/C3 readiness spec + S2 parser A0 report assembly | Executor | D4 + D5b |

Parallelization: D3a / D3b / D3c 가 D2 완료 후 병렬 가능. D5a 는 wave 단위로 시작 가능.

Rationale:
- 자사주 우선 (D3a) = KR-DART-BODY-RETURN-001 의 main unblock 후보 (Round 1 backlog)
- CB/BW + 전환청구 두 번째 (D3b) = overhang event 의 main 후보
- 나머지 (D3c) = parser complexity 더 높음 (보호예수 / 대주주 매도 = 분류 까다로움)

### 3.2 Filter scope

- Period: 2018-01-01 ~ 2026-05-22 (R000 inputs 와 동일 범위)
- Universe: KOSPI + KOSDAQ (S4 listed companies 와 동일)
- Disclosure form mapping = 16 form names → 10 event types (S2_phase_master_ticket.md 표 참조)

### 3.3 Manual audit sample size

- **30 per event type** (Referee range 20-50 mid)
- Stratified by year (2018-2026 8 buckets)
- Total ≈ 300 manual reviews

### 3.4 Output paths

- Raw XML: `data/acquired/round4/s2_dart_body/raw_xml/`
- Parsed: `data/acquired/round4/s2_dart_body/parsed/`
- A0 report: `reports/experiments/S2_phase_parser_A0/`

(전체 구조 = master ticket 의 "Output paths" 섹션)

### 3.5 Codex delegation unit

- **1 master ticket** + ordered sub-task checklist (단일 파일 `research/experiments/S2_phase_master_ticket.md`)
- 사유: sub-task 간 schema/path/code 의존이 강해 multi-ticket fragmentation 비용 > 단일 ticket 통합 비용

### 3.6 What executor will NOT do unilaterally

- Strategy entry decision after S2 — Referee separate verdict 필요
- Manual audit sample 검토 — 사용자 직접
- Promote parser output to strategy — protocol violation
- Modify Referee lock items (taxonomy / schema / hard prohibitions / end condition)

## Section 4 — Prerequisites Pending User Action

1. **OPENDART API key** 환경 변수 (`OPENDART_API_KEY`) 셋업 필요.
   - 현재 repo `.env` 파일 부재 (확인됨). 사용자가 이전 S2 feasibility test 시 직접 사용.
   - D1 시작 전 50-disclosure dry run 으로 endpoint + key 검증 필요.

2. Codex 환경에 위 key 노출 방법 확정 (보안 review 후).

3. (선택) Referee 의 sub-task ordering / sample size / filter scope push back 또는 승인.

## Section 5 — Timeline Estimate

| Wave | Duration | Owner |
|---|---|---|
| D1 | 2-3 days | Codex |
| D2 | 3-5 days | Codex |
| D3a (자사주) | 1-2 weeks | Codex |
| D3b (CB/BW) | 1-2 weeks | Codex |
| D3c (기타) | 1-2 weeks | Codex |
| D4 | 3-5 days | Codex |
| D5a | 1-2 days | Codex |
| D5b | 1-2 weeks | 사용자 manual |
| D6 | 1 week | Executor |

**Total: 6-10 weeks** (기존 5-9 주 estimate + manual audit 사용자 시간 포함).

D3a/b/c 병렬 시 critical path ≈ 4-7 weeks.

## Section 6 — Compliance Reaffirm

- ✅ Infrastructure repair only — no strategy testing
- ✅ 11 hard prohibitions 모두 master ticket 에 명시
- ✅ 17-field output schema 그대로 채용
- ✅ Kill gates 그대로 채용
- ✅ End condition = S2 parser A0 report only (8 items)
- ✅ "Do not recommend strategy testing" — A0 report 결론부 명시 예정

## Section 7 — Referee Approval Request

위 HOW decisions 에 대해 Referee 가 다음 중 선택:

- **(a) Accept as-is** — executor 결정 그대로 실행
- **(b) Narrow** — 특정 wave 제거 또는 sample 수 조정 또는 filter scope 축소
- **(c) Re-order** — D3a/b/c 우선순위 변경
- **(d) Hold** — 추가 prerequisite 요구 (예: D1 dry run 보고 후 D2 진입)

선택 후 사용자가 OPENDART API key 셋업하면 D1 dry run 부터 시작.

## Related

- `research/experiments/S2_phase_master_ticket.md` (Codex 위임 ticket)
- `docs/round4_1_v2_1_referee_lock.md` (Referee verdict)
- `docs/next_actions.md` (active list)
- `reports/experiments/round4_1_v2_1/S2_phase_decision_brief.md` (Round 4.1 brief)
