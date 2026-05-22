# Round 3 No-Performance Rule

Date: 2026-05-22
Status: HARD LOCK for Round 3 전체
Origin: Referee Round 3 lock (`docs/round3_referee_verdict_lock.md`)

이 문서는 Round 3 에서 return / performance outcome 일체를 outcome 또는
signal 로 사용하지 못하도록 명문화한다.

## Why

Round 2 Step 5 에서 W001 v1 의 measurement layer 결함 확인:
- Adjusted OHLC 부재 → raw price 사용 시 split / 액면병합 / 증자 day 가
  +4583% 같은 false return 으로 잡힘 (147 events)
- Tradability flag 가 사실상 panel presence proxy
- True suspension / delisting / limit-lock 4-cause distinction 불가

따라서 어떤 return-based metric 도 의미 있는 alpha vs false alpha 판단에
사용 불가. 측정층이 복구되기 전 strategy performance 계산은 false alpha
생성 위험.

## Forbidden Metrics (Round 3 전체)

다음 metric 은 Round 3 의 모든 5 카드에서 **산출 자체 금지**:

| Metric | 금지 이유 |
|---|---|
| NAV | adjusted price 없이는 NAV 자체가 노이즈 |
| CAGR | NAV 의존 |
| Sharpe | return 의존 |
| Hit rate | return sign 의존 |
| Alpha | benchmark vs return 비교 |
| Excess return | return 의존 |
| MDD (as strategy performance) | NAV 의존 (단 데이터 lineage audit context 에서 distribution 자체는 metric X) |
| Post-event drift | event 후 return 측정 |
| Migration return | top100 entry/exit 후 return |
| Turnover return | turnover spike 후 return |
| Resume return | suspension 후 재개 return |
| Reversal return | spike 후 reversal return |
| Flow-return diagnostic | F/I flow + return joint |

## Forbidden Patterns

다음 pattern 들도 금지:

| Pattern | 금지 이유 |
|---|---|
| raw return 을 signal 로 사용 | 147 corporate action artifact 가 signal 에 침투 |
| raw return 을 outcome 으로 사용 | 동일 |
| adjusted OHLC repair 전 return-based diagnostic 재개 | Gate 5 fix 전제 조건 |
| tradability semantics 확인 전 entry/exit simulation 재개 | 4-cause distinction 필요 |
| top100 lineage 확인 전 migration/turnover universe strategy 재개 | PIT confirm 필요 |
| flow timestamp 확인 전 t+1 flow signal 사용 | publication lag 확인 필요 |
| lifecycle mapping 없이 delisted/merged/suspended names 제거 | survivorship 위험 |
| audit 통과 가능성을 strategy edge 가능성으로 해석 | 측정 무결성 ≠ alpha |
| P08 / production / paper / live readiness 연결 | quarantine 위반 |

## Allowed Outputs (Round 3 전체)

다음 6 output 만 허용:

| Output | 의미 |
|---|---|
| **defect ledger** | 발견한 데이터 / 코드 / lineage defect 의 row-level 기록 |
| **reconciliation rate** | repo 데이터 vs 외부 reference 일치 비율 (성과 X) |
| **pass / fail status** | 각 audit 항목별 PASS / FAIL / PARTIAL |
| **missing-source list** | 확보 필요한 official source 목록 |
| **repair feasibility report** | repair 가능성 + 사용자 host 작업량 추정 |
| **source requirement list** | 각 source 별 schema / coverage / acquisition path |

Defect ledger 표준 schema = `docs/round3_defect_ledger_schema.md`.

## Allowed Audit Actions (per spec)

각 spec 의 "허용 작업" 섹션에 명시된 audit action 만 가능:

- `spec_KR_G5_ADJOHLC_CORPACT_AUDIT_A0.md`
- `spec_KR_ID_LIFECYCLE_MASTER_AUDIT_A0.md`
- `spec_KR_TRADABILITY_SEMANTICS_AUDIT_A0.md`
- `spec_KR_TOP100_PIT_LINEAGE_AUDIT_A0.md`
- `spec_KR_FLOW_UNIT_TIMESTAMP_AUDIT_A0.md`

각 spec 의 "금지 작업" 섹션 + 이 문서의 forbidden patterns 이 조합 적용.

## Protocol Violations

다음 발생 시 protocol violation = Referee 에게 즉시 escalation:

1. 위 forbidden metric 중 하나라도 산출
2. Forbidden pattern 중 하나라도 시도
3. Allowed output 외 artifact 생성
4. Spec 사후 수정 (Bear 재심의 없이)
5. Round 3 결과를 P08 / paper tracking / production 에 연결

Executor (Claude Code / Codex) 는 위 발생 의심 시 즉시 작업 중단 + 사용자
보고.

## Round 3 → Round 4 Transition Conditions

Round 3 audit 5 카드가 모두 PASS (또는 ACCEPTABLE FINDING + repair path
명확) 시:

1. 사용자 host 작업으로 missing source 확보
2. Repair 후 측정층 sanity check (Round 2 Gate 1-6 재실행)
3. Referee 재승인
4. 그 후에야 새 strategy round (Round 4) 또는 기존 BACKLOG 카드 unblock 가능

Round 3 audit 자체에서 strategy 진입 X.

## Related

- `docs/round3_referee_verdict_lock.md` — Round 3 verdict
- `docs/round3_defect_ledger_schema.md` — defect ledger schema
- `docs/round3_missing_source_register.md` — missing source 목록
- `docs/round2_gate5_fail_lock.md` — Round 2 Step 5 lock (Round 3 trigger)
