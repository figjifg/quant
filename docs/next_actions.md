# Next Actions

이 프로젝트에서 "다음에 해야 할 것" 은 **오직 이 파일에서만** 적는다. 다른 가이드
파일은 현재 상태 / 정책 / 결과만 기록한다. 새 세션이 다른 파일을 읽다가 "next
phase = X 해라" 같은 문구에 끌려서 자동으로 그 방향으로 행동하는 lock-in 회피.

비어 있는 것이 정상이다. 사용자가 명시적으로 결정한 active 작업만 여기 적는다.

## Active

### ATTR001 — Korean Equity Data Influence Map (diagnostic attribution sweep) — ACTIVE (2026-05-28, 사용자 결정, 자율 모드)

사용자 결정 (2026-05-28): 닫힌 과거 실패를 veto로 쓰지 않는 **fresh-start attribution
sweep** — 데이터별 단일신호 영향력을 레짐별(과거 2018-2021 vs 현재 2022+)로 측정. 경제/방법론
설계는 Executor + Referee 위임, **할 만한 데이터 다 끝낼 때까지 매 단계 사용자 승인 불필요(자율)**.

- **Status: ACTIVE.** 사전등록 = `research/experiments/ATTR001_korean_data_influence_map.md`
  (Executor+Referee 공동 설계; Referee 최종 sign-off 후 실행).
- **핵심 사용자 제약:** 결과 분석은 하되 **나쁘다고/무영향이라고 폐기·close 금지 — 전체 영향력
  맵 보존.** 유효성 문제는 폐기가 아니라 주석(status label)으로만 표시.
- **유지 가드레일 (자율로 못 넘김):** PIT/룩어헤드 금지, 세후+비용, random/placebo control,
  레짐분할 사전정의, 다중검정(FDR) 인지, "발견/alpha" 언어 금지. diagnostic-only.
- **하드룰:** P08 weight 변경 X; production/paper/live X; 원본 데이터(`data/raw`,
  `research_input_data`) 수정 X; DART body parser / KR-status 측정 재개 X; 닫힌-family는
  veto 아닌 caveat; KR long-short = 통계적 spread만(실행 주장 X).
- **산출:** 보존된 영향력 맵 under `reports/experiments/ATTR001_korean_data_influence_map/`.
- 완료 시 Executor+Referee 분석 → 사용자에 맵 보고. 후속 전략은 별도 사용자 결정.

(비어 있음 표시 해제 — 위 ATTR001 이 유일한 active 작업)

> Note (2026-05-26): 측정 레이어 LOCAL-only 데이터 정리/설계증명 chain 은 사실상 소진.
> 다음 방향(parser-change / 수동판정 / 외부소스 복구 / standby)은 별도의 사용자 + Referee
> 결정이 있어야만 시작한다. 자동 재개 X.
>
> DECIDED STANDBY (2026-05-26): Referee(Codex) + Executor(Claude) 공동 권고 = 측정 레이어를
> 현재 fail-closed 휴지 상태로 정지하고 standby. **사용자가 이 권고를 수락**했다 ("측정 정지
> + standby"). parser-change / 수동판정 / 외부소스 복구는 열지 않는다. 측정 레이어 잔여는
> 진짜 부재/상대성으로 확정 (42 zip = OPENDART status-014 / 170 table = 값 "-" / 23 unhandled
> = 22 relative-or-absent + 1 guarded '21.5.3 후보). 다음에 작업을 재개한다면 자연스러운 방향은
> P08_IEF30 운영 거버넌스 / live-readiness (U/V/N/W/Z ops 티켓) 이며, 이는 별도 결정 사항이다.
> 측정 레이어 재개 또는 P08 ops 착수 모두 사용자의 새 명시적 결정 필요.

## Closed / Frozen (변경 시 사용자 결정 필요)

### W000-DATA-INFRASTRUCTURE-ACQUISITION — CLOSED AS W000 DATA INFRASTRUCTURE ACQUISITION COMPLETED FOR ITEMS 1/2/6 / ITEMS 3/4 DEFERRED BY USER DECISION / ITEM 5 DART PARSER STANDBY PRESERVED / NO STRATEGY OR EXECUTION REOPENED (2026-05-28, via relay)

Referee formal close verdict (2026-05-28, via file-mode relay; Select A close + preserve
D): close the W000 track at the current accepted state on the **user's explicit decision**
(close at items 1/2/6 complete; defer items 3/4/5). Full close note:
`docs/w000_acquisition_close_note.md`.

- Status: **CLOSED**. Accepted commits: `88e4da0` (open+plan) / `b1df5e4` (verified status)
  / `ee5a189` (item 2) / `2778926` (item 6) / `b5f83d5` (doc-state correction).
- **Item 1 PIT sector:** already DONE on disk (no acquisition; "2018 gap" was a sample artifact).
- **Item 2 Korean total return:** acquired+validated (`ee5a189`, yfinance). DATA INFRA ONLY.
  Caveats: research-grade Yahoo proxy / 22 delisted no_data / pre-2018 not covered.
- **Item 6 KRX borrow:** acquired+validated (`2778926`, DATA.GO.KR). DATA INFRA ONLY.
  Caveats: balance/contract/repaid shares only — no fee / short-rebate / restriction list /
  buy-in (separate future source decision if ever pursued).
- **Item 3 execution data:** DEFERRED by user decision; not acquired; likely infeasible
  (broker fills / historical quotes); reopen only by a new user + source decision.
- **Item 4 survivorship-safe US PIT universe:** DEFERRED by user decision; not acquired;
  needs a chosen PIT membership dataset; reopen only by a new user + source decision.
- **Item 5 DART body parser / KR-status measurement:** STANDBY preserved; do not reopen
  here (needs a separate user + Referee decision).

**Hard locks preserved:** no `data/raw/` or `research_input_data/` edits; acquired raw
artifacts remain gitignored under `data/acquired/**`; no API key printed/committed/logged;
no P08_IEF30 weight change; no strategy/backtest/execution/paper/live claim; W000 Hard Rule
active (acquiring data does NOT reopen Q-family / sector / event / Korean long-short /
KR-status work). Accepted W000 datasets are lineage/coverage evidence ONLY until a separate
future ticket approves any use. No next W000 phase opened.

### KR-STATUS-PARSER-UNHANDLED-FORMAT-DESIGN-PROOF-A0 — CLOSED AS UNHANDLED-FORMAT DESIGN PROOF COMPLETED / ONE GUARDED FUTURE PARSER-CHANGE CANDIDATE RECORDED / RELATIVE-TBD AND NON-TARGET VALUES PRESERVED FAIL-CLOSED / EXECUTION STILL CLOSED (2026-05-26, via relay)

Referee final verdict (2026-05-26, via relay): **Select A (accept initial pass) +
preserve D (all strategy/execution/downstream work remains closed).** Authorized by the
user's explicit decision to open a LOCAL-ONLY unhandled-format parser-design proof phase.
**NOT** download/API, source-recovery, parser-change, or manual-adjudication approval.

- Status: **CLOSED**. Accepted commit: initial pass `da6b403`. Code:
  `src/audit/measurement_a0/p_parser_unhandled_format_design_proof.py`.
- 9 required deliverables ACCEPTED + CLOSE_NOTE.md.

**Accepted result:** read-only, proof-only design analysis over exactly the **23 rows**
with prior taxonomy `label_present_but_value_in_unhandled_format` (23) / parse status
`label_no_value` (23) / feasibility bucket `parser_design_candidate` (23) / design theme
`date_format_or_relative_date_handling` (23); no non-target row.
Value pattern (sum 23): **relative_or_tbd_marker 19 / other_ambiguous 2 /
date_range_or_period_text 1 / absolute_date_unhandled_format 1**.
Design-proof bucket (sum 23): **relative_tbd_keep_fail_closed 19 /
ambiguous_requires_manual_or_later_design 2 / out_of_scope_keep_fail_closed 1 /
future_parser_change_candidate_guarded 1**.
Required future approval (sum 23): **none_keep_fail_closed 20 /
manual_adjudication_approval_required 2 /
parser_change_verdict_after_design_proof_review 1**. `git show --check HEAD` passes.

**Only one genuine guarded parser-change candidate:** `20210430900254` — proof-only value
`'21.5.3`, proof-only normalized `2021-05-03` (a 2-digit-year format the parser's 4-digit
patterns miss). This is **NOT accepted as an effective date and NOT parser output**;
guardrail = century disambiguation + label-kind confirmation; needs a separate
parser-change verdict. The other **22 rows remain fail-closed**: 19 are relative/TBD/
deadline expressions ("…제출일 익일" / "1년 이내…限"); 1 is a period resolving to delisting
(out of scope); 2 contain parseable **suspension timestamps** (정지일시), NOT resumption
dates, requiring separate manual-adjudication approval if pursued. The latter 2 correct
the prior taxonomy's "date-like fragment not parser-recognized" framing (the format IS
recognized; the resumption value is absent).

**Accepted limits:** proof-only / planning evidence only; no parser code/rule/version
change approved or occurred; no src/parsers/ edit approved or occurred; no download/API/
source-recovery/body-repair occurred; no manual adjudication occurred; no row marked
parsed/recovered/safe/validated/approved/executable/authoritative/strategy-ready/
execution-ready/production-ready; no effective date accepted/finalized; rcept_dt remains
forbidden as an effective-date fallback; all 23 rows fail-closed. Future parser-change,
manual adjudication, source-channel, downstream, strategy, and execution work each
require a separate user + Referee verdict.

This phase made no parser change, no downloads/API, no manual adjudication, no
downstream/C2-C3/event-log/executable-status-table/strategy/execution. No next phase
opened. **After this close, LOCAL-only measurement cleaning is effectively exhausted.**

### KR-STATUS-PARSER-TABLE-CONTEXT-DESIGN-PROOF-A0 — CLOSED AS TABLE-CONTEXT DESIGN PROOF COMPLETED / NO VALUE-BEARING TABLE DATE FOUND / TABLE-CONTEXT PARSER-CHANGE SURFACE REDUCED / FAIL-CLOSED ROW STATE PRESERVED / EXECUTION STILL CLOSED (2026-05-26, via relay)

Referee final verdict (2026-05-26, via relay): **Select A (accept initial pass) +
preserve D (all strategy/execution research remains closed).** Authorized by the user's
explicit decision to open a LOCAL-ONLY table-context parser-design proof phase. **NOT**
download/API, source-recovery, parser-change, or manual-adjudication approval.

- Status: **CLOSED**. Accepted commit: initial pass `0560234`. Code:
  `src/audit/measurement_a0/p_parser_table_context_design_proof.py`.
- 9 required deliverables ACCEPTED + CLOSE_NOTE.md.

**Accepted result:** read-only table/structure proof over exactly the **170 rows** with
feasibility_bucket=needs_table_context_design (prior taxonomy
label_present_but_attachment_or_table_context_required; attachment count 0; no
non-target row). Structure class: label_in_table_value_empty_or_dash = 170. Design-proof
bucket: **out_of_scope_keep_fail_closed 170** (future parser-change candidate buckets 0).
False-positive risk: blocked_not_evaluable 170. Required-future-approval:
none_keep_fail_closed 170. Matched table value cell: **170/170 explicit "-"**; parseable
date in matched value cell: **0/170**. `git show --check HEAD` passes.

**Accepted interpretation:** the prior `needs_table_context_design` feasibility label was
OVER-OPTIMISTIC for these 170 rows. Table/structure-aware extraction recovers no date
because the matched value cell is explicitly empty/dash (resumption/release date not yet
determined). These 170 are **NOT a table-context parser-change opportunity**. The
suspension-timestamp observation is accepted only as an aside / future candidate note —
NOT actioned, NOT approved; it requires a separate future user + Referee verdict.

**Accepted limits:** proof-only / planning evidence only; no parser code/rule/version
change approved; no src/parsers/ change occurred or is authorized; no effective date
accepted/finalized; no row parsed/recovered/executable/safe/authoritative/validated/
approved/strategy-ready/execution-ready/production-ready; all 170 remain fail-closed.
Future parser-change, manual adjudication, source-channel work, downstream wiring,
strategy, or execution each requires a separate user + Referee verdict.

This phase made no parser change, no downloads/API, no manual adjudication, no
downstream/strategy/execution work. No next phase opened.

### KR-STATUS-PARSER-NONEXTRACTED-FEASIBILITY-A0 — CLOSED AS PARSER NON-EXTRACTED FEASIBILITY TRIAGE COMPLETED / PLANNING-ONLY DESIGN ROUTES RECORDED / FAIL-CLOSED ROW STATE PRESERVED / EXECUTION STILL CLOSED (2026-05-26, via relay)

Referee final verdict (2026-05-26): **Select A (accept Pass 2) + preserve D.**
Authorized by the user's explicit decision to open a local-only feasibility/design-triage
phase (NOT download/parser-change/adjudication approval).

- Status: **CLOSED**. Accepted commits: initial pass `d0d2079` + Pass 2 `a6a2dce`.
  Code: `src/audit/measurement_a0/p_parser_nonextracted_feasibility.py`.
- 8 required deliverables ACCEPTED + CLOSE_NOTE.md.

**Accepted result:** local-only design-triage over the 711 parser non-extracted rows.
Splits reconciled exactly (511 no_label_match + 200 label_no_value; taxonomy
499+170+23+18+1). Feasibility buckets (sum 711): **522 parser_design_candidate / 170
needs_table_context_design / 18 correction_workflow_only / 1 out_of_scope_or_keep_fail_closed**.
Required-future-approval: 499 parser_change_verdict_after_design_proof + 193
parser_change_verdict + 18 manual_adjudication_approval + 1 none_keep_fail_closed.

**Pass 2 corrections (Select B):** (1) CSV line endings CRLF→LF (write_csv now uses
lineterminator="\n"); (2) renamed blocker column parser_design_alone_sufficient →
future_parser_design_route_possible + added planning_only_note (NOT current sufficiency
/ NOT approval). `git show --check HEAD` passes after Pass 2.

**Accepted limits:** feasibility/design labels are PLANNING EVIDENCE ONLY; no parser
code/rule/version change approved; no row parsed/recovered/executable/safe/authoritative/
validated/approved/ready; all 711 fail-closed. Future parser-change / manual
adjudication / source work each needs a separate user + Referee verdict.

This phase made no parser change, no downloads/API, no manual adjudication, no
downstream/strategy/execution. No next phase opened.

### KR-STATUS-ZIP-UNPARSEABLE-SOURCE-RECOVERY-A0 — CLOSED AS OPENDART-CHANNEL SOURCE RECOVERY ATTEMPT COMPLETED FOR 42 ZIP-UNPARSEABLE ROWS / STATUS-014 SOURCE ABSENCE REPRODUCED / ZIP-UNPARSEABLE FAIL-CLOSED RESIDUALS PRESERVED / EXECUTION STILL CLOSED (2026-05-26, via relay)

Referee final verdict (2026-05-26): **Select A (accept) + preserve D.** Authorized by
the user's explicit decision + explicit OPENDART download approval. First (and only)
external-download phase this session.

- Status: **CLOSED**. Initial pass commit accepted: `cf4ad41`. Code:
  `src/audit/measurement_a0/p_zip_unparseable_source_recovery.py`.
- 8 required deliverables ACCEPTED + CLOSE_NOTE.md.

**Accepted key results:** re-acquired all 42 zip_unparseable rows (39 correction + 3
non-correction) from OPENDART document.xml. **42/42 returned OPENDART status 014
(파일이 존재하지 않습니다 / file does not exist)** — NOT auth/quota. **42/42 re-acquired
payloads byte-identical to the prior cache (1 sha256, 147 bytes)** → the prior "corrupt
cache" was itself the persisted 014 error payload, never a real document. 0 recovered
readable ZIP; 42/42 remain zip_unparseable / fail-closed. read-only parser N/A (0
readable). Defect ledger NONE sentinel (unrecovered = expected residuals).

**Accepted caveats:** proves source absence ONLY for the authorized OPENDART
document.xml channel (NOT every external source); KRX/KIND or other-source recovery
needs a separate user + Referee verdict; source_recovery_status is availability
evidence only. **Local-artifact nuance:** the raw 42 artifacts + DATA_CATALOG_NOTE.md
under `data/acquired/zip_unparseable_source_recovery_a0/` are gitignored local evidence
(NOT committed); the committed manifest of record is
`source_recovery_artifact_inventory.csv` (paths + sha256 + readability). No row became
parsed/recovered/executable/safe/authoritative/validated/approved/strategy-ready/
execution-ready/production-ready.

Existing corrupt cache preserved unchanged; OPENDART key never printed/committed/logged.
No next phase opened.

### KR-STATUS-MEASUREMENT-A0-HANDOFF-STATE-MANIFEST-A0 — CLOSED AS MEASUREMENT-A0 HANDOFF STATE MANIFEST COMPLETED / VERIFIED FAIL-CLOSED HANDOFF INDEX PRESERVED / EXECUTION STILL CLOSED (2026-05-26, via relay)

Referee final verdict REF-CLOSE-012 (2026-05-26): **CLOSED AS MEASUREMENT-A0 HANDOFF
STATE MANIFEST COMPLETED / VERIFIED FAIL-CLOSED HANDOFF INDEX PRESERVED / EXECUTION
STILL CLOSED.** Option A accepted + Option D preserved (close after housekeeping; next
phase NOT opened in the close pass).

- Status: **CLOSED**. Initial pass commit accepted: `f65b2bf`. Code:
  `src/audit/measurement_a0/p_measurement_a0_handoff_state_manifest.py`.
- 9 required deliverables ACCEPTED + CLOSE_NOTE.md.

**Accepted result:** compact deterministic handoff index over the accepted closed
measurement_A0 state (REF-CLOSE-007..011). 5/5 CLOSE_NOTEs + key outputs present;
6/6 lock-consistency checks PASS; 4/4 worklist state checks PASS (862/862 unique,
WL-00001..WL-00862, no forbidden outcome columns); 12/12 sha256 inventory present;
0 defects. Records accepted commit lineage REF-CLOSE-001..011 + canonical counts
12,187/12,145/42/511/200/862/711/166/39/3.

**Close-note nuance:** measurement_a0_output_inventory.csv was generated at f65b2bf
(while Active), so its docs/next_actions.md sha256 is initial-pass evidence and is
EXPECTED to differ post-close (close empties Active); the inventory is preserved
UNCHANGED (not regenerated). All other inventoried files (6 key outputs + 5
CLOSE_NOTEs) remain valid post-close.

**Accepted limits:** handoff/index only; carries NO approval authority; authorizes no
source recovery / downloads / API / parser design-or-change / manual adjudication /
validation / event-log / executable-status table / strategy / execution / production /
paper / live / P08 / shadow. No row marked parsed/recovered/executable/safe/
authoritative/validated/approved/strategy-ready/execution-ready/production-ready.

This phase made no new data; no edits to closed artifacts. Per the verdict, the next
phase was NOT opened in the close pass.

### KR-STATUS-MANUAL-REVIEW-WORKLIST-VIEWS-A0 — CLOSED AS MANUAL-REVIEW WORKLIST VIEWS COMPLETED / NAVIGATION-ONLY FAIL-CLOSED WORKLIST PRESERVED / EXECUTION STILL CLOSED (2026-05-26, via relay)

Referee final verdict REF-CLOSE-011 (2026-05-26): **CLOSED AS MANUAL-REVIEW WORKLIST
VIEWS COMPLETED / NAVIGATION-ONLY FAIL-CLOSED WORKLIST PRESERVED / EXECUTION STILL
CLOSED.** Option A accepted + Option D preserved (close after Pass 2 corrective pass;
next phase NOT opened in the close pass).

- Status: **CLOSED**. Accepted commits: Pass 1 `290f532` (partial) + Pass 2 `d67950c`
  (final corrective). Code:
  `src/audit/measurement_a0/p_manual_review_worklist_views.py`.
- 10 required deliverables ACCEPTED + CLOSE_NOTE.md.

**Pass history:** Pass 1 carried an exact `recovered` outcome column → Referee
required Pass 2 (Option B). Pass 2 removed ALL outcome/status columns; worklist now
carries only navigation fields + read-only review_note + WARNING-only
blocked_action_boundary + the single fail-closed marker manual_review_required=True;
input-packet fail-closed flags VERIFIED in integrity check (not carried); forbidden
scan uses the EXACT directive list and PASSES.

**Accepted result:** deterministic, fail-closed, navigation-only worklist over the
862-row packet — 862 rows / 862 unique (== packet set); WL-00001..WL-00862; 18 columns
(no outcome columns); 7 per-bucket shards; 12/12 integrity PASS; 0 build defects.
blocked_action_boundary warning-only (not approval); no row marked parsed/recovered/
executable/safe/authoritative/validated/approved/strategy-ready/execution-ready/
production-ready.

This phase made no new data; navigation/index only; no edits to closed artifacts; no
downloads/API/credentials/body-repair/parser-change/rerun/candidate-rerun/source-
recovery/parser-design/manual-adjudication/downstream-wiring/C2-C3/event-log/
executable-status-table/strategy/execution. Per the verdict, the next phase was NOT
opened in the close pass.

### KR-STATUS-RESIDUAL-MANUAL-REVIEW-PACKET-CONSOLIDATION-A0 — CLOSED AS RESIDUAL MANUAL-REVIEW PACKET CONSOLIDATION COMPLETED / HUMAN-REVIEW-ONLY FAIL-CLOSED INDEX PRESERVED / EXECUTION STILL CLOSED (2026-05-26, via relay)

Referee final verdict REF-CLOSE-010 (2026-05-26): **CLOSED AS RESIDUAL MANUAL-REVIEW
PACKET CONSOLIDATION COMPLETED / HUMAN-REVIEW-ONLY FAIL-CLOSED INDEX PRESERVED /
EXECUTION STILL CLOSED.** Option A accepted + Option D preserved (close after
housekeeping; next phase NOT opened in the close pass).

- Status: **CLOSED**. Initial pass commit accepted: `32e30f8`. Code:
  `src/audit/measurement_a0/p_residual_manual_review_packet_consolidation.py`.
- 10 required deliverables ACCEPTED + CLOSE_NOTE.md.

**Accepted result:** single fail-closed, human-review-only TRIAGE/INDEX over all 862
blocker-register rows keyed by rcept_no (packet set == register set exactly). Bucket
counts (sum 862): parser_generic_or_contextual_label 499 /
parser_table_or_attachment_context 170 / correction_manual_review 110 /
source_recovery_required 42 / parser_unhandled_format 23 /
rejected_wrong_candidate_quarantine 17 / mixed_or_multi_blocker 1. Both prior audit
sentinels clean (rowkey mismatch NONE, fail-closed violation NONE); 0 build defects;
every row fail-closed.

**Accepted packet limits:** source_recovery_required = review bucket only (NOT
recovery approval / NO download authorization); parser_* buckets = review only (NOT
parser-design approval); correction_* buckets = review only (NOT downstream authority
/ supersession wiring / executable status); example rows = inspection samples only
(NOT validation). Design-only fields not promoted.

This phase made no new data; index/triage only (no residual fixed); no downloads/API/
credentials/body-repair/parser-change/rerun/candidate-rerun/body-confirmation-rerun/
source-recovery/parser-design/downstream-wiring/C2-C3/event-log/executable-status-
table/strategy/execution; no edits to closed artifacts. Per the verdict, the next
phase was NOT opened in the close pass.

### KR-STATUS-FAIL-CLOSED-INVARIANT-AUDIT-A0 — CLOSED AS FAIL-CLOSED INVARIANT AUDIT COMPLETED / FIELD-LEVEL FAIL-CLOSED FLAGS PRESERVED / EXECUTION STILL CLOSED (2026-05-26, via relay)

Referee final verdict REF-CLOSE-009 (2026-05-26): **CLOSED AS FAIL-CLOSED INVARIANT
AUDIT COMPLETED / FIELD-LEVEL FAIL-CLOSED FLAGS PRESERVED / EXECUTION STILL CLOSED.**
Option A accepted + Option D preserved (close after housekeeping; next phase NOT
opened in the close pass).

- Status: **CLOSED**. Initial pass commit accepted: `bbfbbaa`. Code:
  `src/audit/measurement_a0/p_fail_closed_invariant_audit.py`.
- 9 required deliverables ACCEPTED + CLOSE_NOTE.md.

**Accepted result — CLEAN PASS (field level):** the THIRD verification dimension
(after count locks REF-007 + row-key set locks REF-008). 30/30 invariant-matrix
checks PASS; 8/8 correction-confidence-gate PASS; 9/9 source-recovery-gate PASS;
22/22 forbidden-truthy scans PASS (0 forbidden flag True anywhere); 0 violations.

**Accepted field-level locks:** 862 register + 711 taxonomy + 166 correction
fail-closed (manual_review_required=True; no executable/safe/authoritative/ready
truthy flags); 42 manifest recovery-gated; high_validated (17) design-only NOT wired;
rejected_wrong_candidate (17) quarantined NOT dropped. Universe scoping accepted:
manual_review_required=True on the 753 residuals only (11,434 extracted legitimately
False); executable_or_safe=False universe-wide (12,187).

**Close-note nuance preserved:** positive design-evidence fields (link_validated,
supersession_ready) remain DESIGN-ONLY evidence — NOT downstream authority / execution
safety / strategy readiness / wired supersession — accepted only because
downstream_authoritative=False and supersession_wired=False stay locked.

This phase made no new data; no downloads/API/credentials/body-repair/parser-change/
rerun/candidate-rerun/body-confirmation-rerun/source-recovery/parser-design/
downstream-wiring/C2-C3/event-log/executable-status-table/strategy/execution; no
edits to closed artifacts. Per the verdict, the next phase was NOT opened in the
close pass.

### KR-STATUS-RESIDUAL-ROWKEY-INTEGRITY-AUDIT-A0 — CLOSED AS RESIDUAL ROWKEY INTEGRITY AUDIT COMPLETED / ROWKEY SET LOCKS PRESERVED / EXECUTION STILL CLOSED (2026-05-26, via relay)

Referee final verdict REF-CLOSE-008 (2026-05-26): **CLOSED AS RESIDUAL ROWKEY
INTEGRITY AUDIT COMPLETED / ROWKEY SET LOCKS PRESERVED / EXECUTION STILL CLOSED.**
Option A accepted + Option D preserved (close after housekeeping; next phase NOT
opened in the close pass).

- Status: **CLOSED**. Initial pass commit accepted: `73c68a8`. Code:
  `src/audit/measurement_a0/p_residual_rowkey_integrity_audit.py`.
- 9 required + 1 supporting deliverables ACCEPTED + CLOSE_NOTE.md.

**Accepted result — CLEAN PASS (set level):** verified the accepted count locks hold
at the exact rcept_no SET level (not merely aggregate counts). 0 duplicate keys across
all 6 ledgers; 5/5 exact set-equality checks PASS; subset matrix all PASS; status +
fail-closed flags consistent; 0 mismatches.

**Accepted LOCKED row-key sets:** 42 zip (universe == register == manifest); 39
correction-zip (adjudication == register == manifest); 3 non-correction-zip (register
== manifest); 711 parser non-extracted (universe no_label∪label_no_value == register
== taxonomy); 166 correction (links == adjudication == register); 862 register == 753
universe-non-extracted ∪ 166 correction with 57-key overlap preserved (753+166−57=862).

This phase made no new data; no downloads/API/credentials/body-repair/parser-change/
rerun/candidate-rerun/body-confirmation-rerun/source-recovery/parser-design/
downstream-wiring/C2-C3/event-log/executable-status-table/strategy/execution; no edits
to closed artifacts. Per the verdict, the next phase was NOT opened in the close pass.

### KR-STATUS-LOCAL-ARTIFACT-CONSISTENCY-AUDIT-A0 — CLOSED AS LOCAL ARTIFACT CONSISTENCY AUDIT COMPLETED / ACCEPTED COUNT LOCKS PRESERVED / EXECUTION STILL CLOSED (2026-05-26, via relay)

Referee final verdict REF-CLOSE-007 (2026-05-26): **CLOSED AS LOCAL ARTIFACT
CONSISTENCY AUDIT COMPLETED / ACCEPTED COUNT LOCKS PRESERVED / EXECUTION STILL
CLOSED.** Option A accepted + Option D preserved (close after housekeeping; next
phase NOT opened in the close pass).

- Status: **CLOSED**. Initial pass commit accepted: `1643fd2`. Code:
  `src/audit/measurement_a0/p_local_artifact_consistency_audit.py`.
- 10 required + 6 optional/supporting deliverables ACCEPTED + CLOSE_NOTE.md.

**Accepted result — CLEAN PASS:** meta-audit of the 6 recently-closed
measurement-layer phases. 19/19 count reconciliations PASS (recomputed from source
CSVs); 4/4 derived identities PASS; 25/25 CLOSE_NOTE numbers present; next_actions
consistent; hard-lock phrase audit 0 affirmative scope-drift (175 trigger lines all
reviewed-benign); 0 consistency defects.

**Accepted LOCKED canonical counts:** universe 12,187 / usable html_inline 12,145 /
zip_unparseable 42 / no_label_match 511 / label_no_value 200 / blocker register 862 /
parser non-extracted 711 / correction 166 / correction-zip 39 / non-correction-zip 3.
Derived: 711=511+200; 42=39+3; 862=753+109; 12,187=12,145+42.

This phase made no new data; no downloads/API/credentials/body-repair/parser-change/
rerun/downstream-wiring/C2-C3/event-log/executable-status-table/strategy/execution.
Per the verdict, the next phase was NOT opened in the close pass.

### KR-STATUS-SOURCE-RECOVERY-CANDIDATE-MANIFEST-A0 — CLOSED AS SOURCE-RECOVERY CANDIDATE MANIFEST COMPLETED / RECOVERY-GATED FAIL-CLOSED STATE PRESERVED / EXECUTION STILL CLOSED (2026-05-26, via relay)

Referee final verdict REF-CLOSE-006 (2026-05-26): **CLOSED AS SOURCE-RECOVERY
CANDIDATE MANIFEST COMPLETED / RECOVERY-GATED FAIL-CLOSED STATE PRESERVED / EXECUTION
STILL CLOSED.** Option A (initial pass accepted; closed after housekeeping).

- Status: **CLOSED**. Initial pass commit accepted: `1a9de6a`. Code:
  `src/audit/measurement_a0/p_source_recovery_candidate_manifest.py`.
- 11 required + 3 optional deliverables ACCEPTED + CLOSE_NOTE.md.

**Accepted key results:** local manifest of the **42** zip_unparseable source defects
= **39 correction + 3 non-correction**. event_category 23 suspension + 19 resumption;
source_period 25 pre_2018 + 17 post_2018; 39 corrections all
zip_unparseable_requires_source_recovery (underlying 5-tier 20 no_link + 12 medium +
7 low). All 42 recovery-gated + fail-closed: recovery_performed=False,
requires_separate_verdict=True, requires_download_approval=True,
safe_for_current_use=False; manual_review_required=True; executable_or_safe /
downstream_authoritative / parsed_clean_and_usable / strategy_ready / production_ready
= False.

**Accepted limits:** all 42 corrupt cached ZIPs are locally irrecoverable; this is a
local manifest only, NOT recovery; no row recovered/repaired/parsed/safe; no
effective_date; no parser change. Future recovery needs a separate Referee verdict +
explicit download/API approval.

This phase did NOT perform recovery/downloads/API/body-repair, change parser code, or
open strategy/backtest/execution/C2-C3/event-log/executable-status-table/production/
paper/P08/live/shadow.

### KR-STATUS-PARSER-NONEXTRACTED-LOCAL-TAXONOMY-A0 — CLOSED AS PARSER NON-EXTRACTED LOCAL TAXONOMY COMPLETED / FAIL-CLOSED PARSE STATUS PRESERVED / EXECUTION STILL CLOSED (2026-05-26, via relay)

Referee final verdict REF-CLOSE-005 (2026-05-26): **CLOSED AS PARSER NON-EXTRACTED
LOCAL TAXONOMY COMPLETED / FAIL-CLOSED PARSE STATUS PRESERVED / EXECUTION STILL
CLOSED.** Option A (initial pass accepted; closed after housekeeping).

- Status: **CLOSED**. Initial pass commit accepted: `d97f9a7`. Code:
  `src/audit/measurement_a0/p_parser_nonextracted_local_taxonomy.py` (read-only use
  of parser helpers; parser source unchanged).
- 10 required + 4 optional deliverables ACCEPTED + CLOSE_NOTE.md.

**Accepted key results:** local root-cause taxonomy for the 711 parser non-extracted
rows (511 no_label_match + 200 label_no_value). Root causes sum to 711: 499
only_generic_or_contextual_label / 170 label_present_but_attachment_or_table_context_
required / 23 label_present_but_value_in_unhandled_format / 18
correction_disclosure_manual_only / 1 title_body_mismatch. Reconciliation:
no_label_match 511 = 499+11+1; label_no_value 200 = 170+23+7. Correction overlap 11
no_label + 7 label_no_value = 18. (Honest finding: the label_no_value bulk = 170
table/structure-context rows where the date label is a column header and the value
sits in a non-adjacent cell lost in HTML→text flattening.)

**Accepted limits:** all 711 fail-closed (parse_status preserved 511/200;
manual_review_required=True; executable_or_safe / downstream_authoritative /
parsed_clean_and_usable / strategy_ready / production_ready / effective_date_extracted
= False); no root-cause class implies parser success; no parser change / extraction
upgrade / row reclassification. `parser_design_backlog_candidates.md` is DESIGN-ONLY,
NOT approved.

This phase did NOT change parser code, extract effective_date, perform
downloads/API/body-repair, or open parser-design/strategy/backtest/execution/C2-C3/
event-log/executable-status-table/production/paper/P08/live/shadow. A future
parser-design/feasibility phase (e.g. for the 170 table-context or 23 unhandled-format
rows) needs its own Referee verdict; parser changes remain forbidden until then.

### KR-STATUS-RESIDUAL-BLOCKER-REGISTER-A0 — CLOSED AS RESIDUAL BLOCKER REGISTER COMPLETED / FAIL-CLOSED MANUAL-REVIEW STATE PRESERVED / EXECUTION STILL CLOSED (2026-05-26, via relay)

Referee final verdict REF-CLOSE-004 (2026-05-26): **CLOSED AS RESIDUAL BLOCKER
REGISTER COMPLETED / FAIL-CLOSED MANUAL-REVIEW STATE PRESERVED / EXECUTION STILL
CLOSED.** Option A (initial pass accepted; closed after housekeeping).

- Status: **CLOSED**. Initial pass commit accepted: `9bb4a2d`. Code:
  `src/audit/measurement_a0/p_residual_blocker_register.py`.
- 10 required + 3 optional deliverables ACCEPTED + CLOSE_NOTE.md.

**Accepted key results:** pure-local consolidation of all prior measurement-layer
residual blockers into ONE fail-closed, row-level register keyed by `rcept_no`.
**862 unique rows** = (universe non-extracted residuals: 42 zip_unparseable + 511
no_label_match + 200 label_no_value = 753) ∪ (166 corrections) = 753 + 109
parser-extracted corrections. Multi-label blocker tags (manual_review_required 862 /
parser_no_label_match 511 / parser_label_no_value 200 / correction_manual_review_
required 166 / source_zip_unparseable 42 / source_recovery_required 42 / correction
outcome tags 127). **39 correction zip ⊂ 42 universe zip** verified (3 non-correction).

**Accepted limits:** all 862 fail-closed (manual_review_required=True;
executable_or_safe / downstream_authoritative / parsed_clean_and_usable /
strategy_ready / production_ready = False); 42 zip need separate source-recovery
verdict + download approval; 511 no_label + 200 label_no_value non-extracted manual-
review-only; 166 corrections non-authoritative. NOT an event log / executable-status
table / downstream wiring.

This phase did NOT open residual-source recovery, downloads/API/body-repair,
strategy/backtest/execution/C2-C3/event-log/executable-status-table/production/paper/
P08/live/shadow. Future source-recovery for the 42 zip_unparseable needs its own
Referee verdict + download approval.

### KR-STATUS-CORRECTION-RESIDUAL-LOCAL-ADJUDICATION-A0 — CLOSED AS CORRECTION RESIDUAL LOCAL ADJUDICATION PACKET COMPLETED / SOURCE-RECOVERY REQUIREMENTS PRESERVED / EXECUTION STILL CLOSED (2026-05-26, via relay)

Referee final verdict REF-CLOSE-003 (2026-05-26): **CLOSED AS CORRECTION RESIDUAL
LOCAL ADJUDICATION PACKET COMPLETED / SOURCE-RECOVERY REQUIREMENTS PRESERVED /
EXECUTION STILL CLOSED.** Option A (initial pass accepted; closed after housekeeping).

- Status: **CLOSED**. Initial pass commit accepted: `6e35624`. Code:
  `src/audit/measurement_a0/p_correction_residual_local_adjudication.py`.
- 10 required + 3 optional deliverables ACCEPTED + CLOSE_NOTE.md.

**Accepted key results:** pure-local packaging of the 166 correction rows (from the
closed full-universe phase) into a residual-ACTION ledger + manual-review packet. NO
downloads / API / body repair / recovery. 5-tier control reproduces accepted
**17/52/7/73/17**. Residual action classes (sum to 166): 17 accepted_high_validated_
design_only / 40 body_confirms_candidate_but_below_high / 17 rejected_wrong_candidate_
quarantined / 37 no_link_original_not_found / 15 no_link_insufficient_evidence / 1
no_link_cross_category_blocked / **39 zip_unparseable_requires_source_recovery**
(zip priority pulls 20 no_link + 12 medium + 7 low). Cross-tab reconciles to 166.

**Accepted limits:** all 166 remain `manual_review_required`;
`downstream_authoritative=False` + `supersession_wired=False` on all 166; the 39
zip_unparseable `recovery_performed=False` (need separate verdict + download
approval; overlap universe-level 42); 17 rejected quarantined (not dropped); 40
body-confirmed-below-high + 73 no_link remain manual-review-only; 17 high_validated
design-only; no row executable/strategy-ready/downstream-authoritative.

This phase did NOT open residual-source recovery, perform downloads/API/body-repair,
or open strategy/backtest/execution/C2-C3/production/paper/P08/live/shadow. Future
`correction-residual-source-recovery` for the 39 zip_unparseable bodies needs its
own Referee verdict + download approval.

### KR-STATUS-CORRECTION-LINKAGE-FULL-UNIVERSE-VALIDATION-A0 — CLOSED AS CORRECTION-LINKAGE FULL-UNIVERSE VALIDATED WITH BODY-GATED CONFIDENCE / ZIP-UNPARSEABLE AND WRONG-CANDIDATE RESIDUALS PRESERVED / EXECUTION STILL CLOSED (2026-05-26, via relay)

Referee final verdict REF-CLOSE-002 (2026-05-26): **CLOSED AS CORRECTION-LINKAGE
FULL-UNIVERSE VALIDATED WITH BODY-GATED CONFIDENCE / ZIP-UNPARSEABLE AND
WRONG-CANDIDATE RESIDUALS PRESERVED / EXECUTION STILL CLOSED.** Initial pass accepted
**with a mandatory wording correction** (the word "AUTHORITATIVE" removed → "body-gated
classifier"); closed after wording patch + housekeeping.

- Status: **CLOSED**. Initial pass commit accepted: `e110165`. Code:
  `src/audit/measurement_a0/p_correction_linkage_full_universe_validation.py`.
- 12 required + 2 optional deliverables ACCEPTED + CLOSE_NOTE.md.

**Accepted key results:** ran the accepted Pass-3 body-confirmation gate across all
**166** in-scope corrections (Pass 3 ran it on the ~72-row sample only; body coverage
since expanded ~11.5%→~98.3%, so all 166 now have cached bodies: 127 html_inline + 39
zip_unparseable). Score-only control reproduces Pass-3 **35/42/18/71/0 EXACTLY**.
Body-gated post-body 5-tier (sums to 166): **17 high_validated / 52 medium / 7 low /
73 no_link / 17 rejected_wrong_candidate**. Movement: of 35 score-only-high → 17 stay
(body confirms), 12 → medium (ALL zip_unparseable), 6 → rejected (html body present,
candidate unreferenced). Source-blocked 56 (39 zip_unparseable + 17 non_extracted);
40 other_manual_review. link_validated 17; supersession 17 (design-only).

**Accepted limits:** 39 zip_unparseable correction bodies = source defects (overlap
universe-level 42); 17 rejected_wrong_candidate quarantined; all 166 remain
`manual_review_required`; even the 17 high_validated stay manual-review under the
conservative framework; medium/low/no_link/blocked NOT authoritative; no correction
row executable/strategy-ready; supersession NOT wired.

This phase did NOT open residual-source recovery, strategy testing, backtesting,
execution simulation, C2/C3, or any production/paper/P08/live/shadow. Future
`correction-residual-source-recovery` for the 39 zip_unparseable bodies needs its own
Referee verdict + download approval.

### S2-HTML-INLINE-PARSER-UNIVERSE-RESIDUAL-RECONCILIATION-A0 — CLOSED AS UNIVERSE RESIDUALS RECONCILED / ZIP-UNPARSEABLE RESIDUALS PRESERVED / EXECUTION STILL CLOSED (2026-05-26, via relay)

Referee final verdict REF-CLOSE-001 (2026-05-26): **CLOSED AS UNIVERSE RESIDUALS
RECONCILED / ZIP-UNPARSEABLE RESIDUALS PRESERVED / EXECUTION STILL CLOSED.**

- Status: **CLOSED** (option A — initial pass accepted, closed after housekeeping).
- Initial pass commit accepted: `6510f5a`. Code: `src/audit/measurement_a0/p_universe_residual_reconciliation.py`.
- 8 required + 2 optional deliverables ACCEPTED + CLOSE_NOTE.md.

**Accepted key results (exact reconciliation of the 12,187-row in-scope universe):**

- in-scope universe: 12,187; cache file present: 12,187.
- usable html_inline: **12,145 = 99.66% (NOT 100%)**.
- universe residual: **42, ALL zip_unparseable**; unavailable / structured_xml /
  attachment_only / other = 0.
- exact reconcile: 12,145 usable + 42 residual = 12,187.
- parse status: extracted 11,434 / no_label_match 511 / label_no_value 200 /
  body_unavailable 42.
- target-set accounting unchanged: 162 + 5,579 + 3 = 5,744; target body_unavailable = 0.

**Accepted limits:** 42 zip_unparseable remain residual source defects
(manual_review_required / unavailable); 511 no_label + 200 label_no_value are usable
html_inline but non-extracted → remain manual_review_required, NOT executable/safe;
NO 100% universe-completion claim; NO strategy-readiness implication.

This phase did NOT open residual-source recovery, strategy testing, execution
simulation, C2-C3, or any production/paper/P08/live/shadow. Future
`residual-source-recovery` for the 42 zip_unparseable needs its own Referee verdict
+ download approval.

### S2-HTML-INLINE-PARSER-BODY-COVERAGE-COMPLETION-A0 — CLOSED AS BODY-COVERAGE COMPLETED FOR TARGET SET / RESIDUAL SOURCE DEFECTS PRESERVED / EXECUTION STILL CLOSED (2026-05-25)

Referee final verdict 2026-05-25: **CLOSED AS BODY-COVERAGE COMPLETED FOR TARGET
SET / RESIDUAL SOURCE DEFECTS PRESERVED / EXECUTION STILL CLOSED — 5,744 remaining
target rows; 162 already cached; 5,582 attempted; 5,579 successful downloads;
target body_unavailable 5,744→0; 5,577 new extractions; universe body coverage
estimate ~98.3%; 88-row holdout 100%; 3 zip_unparseable residual defects; no
strategy testing.**

- Status: **CLOSED AS BODY-COVERAGE COMPLETED FOR TARGET SET / RESIDUAL SOURCE
  DEFECTS PRESERVED / EXECUTION STILL CLOSED**.
- Initial pass commit accepted: `b3a971d`
- 13 deliverables ACCEPTED + CLOSE_NOTE.md.
- Code: `src/audit/measurement_a0/p_body_coverage_completion.py`.
- Parser: `krx_status_html_inline-1.1.0` used as-is.

**Acquisition results:**

- Remaining target rows: 5,744; already cached at start: 162; attempted: 5,582;
  successes: **5,579** (99.95%); zip_unparseable: 3.
- 0 api_no_document / 0 rate_limited / 0 credential_or_api_error / 0 retry_needed
  / 0 not_attempted_due_to_budget.

**Target-set coverage delta:**

- body_unavailable on remaining: 5,744 → **0** (100% coverage shift).
- 5,577 new extractions; 164 no_label_match; 0 label_no_value; 3
  out_of_scope_body_format.

**Universe-level coverage estimate (NOT 100%, ~98.3%):**

- In-scope universe: 12,187.
- Body available now: ~11,977 / 12,187 ≈ **98.3%** (up from ~52.5%).
- Accepted as estimate; not a claim of perfect 100% coverage.

**Validation holdout (88 rows from newly-extracted):**

- success rate: 88/88 = **100.0%**.
- 0 FP / 0 wrong_date / 0 missed_date / 0 correction_not_forced_manual_review.

**Defect ledger (3 rows):**

- `zip_unparseable`: 3 (residual source defects).
- All other classes: 0.
- `body_unavailable_remaining (within target set)`: 0.

**Gate state: `READY_FOR_NEXT_A0_REVIEW`** (per Referee enum).

Important accepted boundary (Referee-mandated distinction):
- **Target-set residual** = 0 body_unavailable on the 5,744-row target set.
- **Universe-level / non-target residual** = ~210 rows in the 12,187-row in-scope
  universe still do NOT have an HTML-inline body. Includes 3 zip_unparseable
  from this phase plus prior `out_of_scope_body_format` rows.
- ALL residuals (target + universe-level) remain `manual_review_required` /
  `unavailable` and MUST NOT be treated as parsed / executable / safe.
- This phase does NOT describe the 12,187-row universe as 100% body-complete.
- No card is strategy-ready.

9 future-phase candidates (none active, separate Referee verdict each):

| Phase candidate | Purpose |
|---|---|
| `S2-HTML-INLINE-PARSER-UNIVERSE-RESIDUAL-RECONCILIATION-A0` | Reconcile universe-level residual body coverage gap. **Referee-strongest next candidate.** |
| `KR-STATUS-CORRECTION-LINKAGE-FULL-UNIVERSE-VALIDATION-A0` | Correction linkage beyond sample. |
| `KR-STATUS-EFFECTIVE-DATE-MANUAL-AUDIT-EXPANSION` | More manual samples (delisting / liquidation / managed / alert). |
| `S2-DELISTING-LIQUIDATION-PARSER-FEASIBILITY-A0` | Separate feasibility. |
| `KR-INTRADAY-HALT-SOURCE-BACKLOG` | Intraday halt / VI / circuit-breaker. |
| `KR-EXECUTABLE-STATUS-LIMIT-LOCK-OFFICIAL-SOURCE-A0` | Direct KRX/KOSCOM official limit-lock. |
| `KR-LIMIT-LOCK-CORPORATE-ACTION-ADJUSTMENT-A0` | CA effects on prev-close limit. |
| `KR-LISTED-UNIVERSE-DAILY-LIFECYCLE-REFINEMENT-A0` | Monthly → daily lifecycle. |
| `KR-OPS-NAV-UPDATE-QUARANTINE-PATCH-PHASE` | 4 ops blockers. |

Strategy testing remains **premature**. Auto-start forbidden.

### S2-HTML-INLINE-PARSER-BODY-COVERAGE-EXPANSION-A0 — CLOSED AS BODY-COVERAGE-EXPANDED AND VALIDATED FOR AVAILABLE ROWS / INCOMPLETE COVERAGE / EXECUTION STILL CLOSED (2026-05-25)

Referee final verdict 2026-05-25: **CLOSED AS BODY-COVERAGE-EXPANDED AND
VALIDATED FOR AVAILABLE ROWS / INCOMPLETE COVERAGE / EXECUTION STILL CLOSED —
10,744 target body_unavailable rows; 5,000 attempted; 4,996 successful downloads;
4,526 new extractions; target coverage shift 46.5%; estimated in-scope body
coverage ~52.5%; 84-row holdout 100% success; 5,744 body_unavailable rows
preserved; no strategy testing.**

- Status: **CLOSED AS BODY-COVERAGE-EXPANDED AND VALIDATED FOR AVAILABLE ROWS /
  INCOMPLETE COVERAGE / EXECUTION STILL CLOSED**.
- Initial pass commit accepted: `1d8a67f`
- 12 deliverables ACCEPTED + CLOSE_NOTE.md.
- Code: `src/audit/measurement_a0/p_body_coverage_expansion.py`.
- Parser: `krx_status_html_inline-1.1.0` used as-is (no feature change).

**Acquisition results:**

- Download budget: 5,000; attempted: 5,000; successes: **4,996** (99.92%).
- All 4,996 successes were html_inline; 0 structured_xml / 0 attachment_only /
  0 api_no_document / 0 rate_limited / 0 credential errors / 4 zip_unparseable.
- Not attempted due to budget: 5,744 (preserved as defects, NOT silently dropped).

**Coverage delta on target rows:**

- body_unavailable: 10,744 → 5,744.
- body_available: 0 → 5,000.
- New extractions: 4,526; no_label_match: 296; label_no_value: 174.
- Coverage shift on target rows: **46.54%**.
- Universe-level body availability estimate: ~6,398 / 12,187 ≈ **52.5%** (up
  from ~11.5%; lift ≈ +41 percentage points).

**Validation holdout (84 rows from newly extracted):**

- success rate: 84/84 = **100.0%**.
- wrong_date: 0; missed_date: 0; false_positive: 0.
- correction_not_forced_manual_review: 0.
- Parser behavior preserved.

**Defect ledger (5,748 rows):**

- `body_unavailable_remaining`: 5,744 (preserved per Referee rule).
- `zip_unparseable`: 4.
- All other defect classes: 0.

**Gate state: `READY_FOR_NEXT_A0_REVIEW`** (per Referee enum).

Important accepted boundary:
- 5,744 target rows remain body_unavailable. These are NOT failed documents — most were `not_attempted_in_this_run` because the run hit the download budget.
- body_unavailable rows MUST remain manual_review_required / unavailable.
- No body_unavailable row may be treated as parsed / executable / safe.
- Phase did NOT complete S2 globally.
- Phase did NOT create C2/C3 event log.
- Phase did NOT authorise execution simulation or strategy testing.
- No card is strategy-ready.

9 future-phase candidates (none active, separate Referee verdict each):

| Phase candidate | Purpose |
|---|---|
| `S2-HTML-INLINE-PARSER-BODY-COVERAGE-COMPLETION-A0` | Attempt remaining 5,744 body_unavailable rows. **Referee-strongest next candidate.** |
| `KR-STATUS-CORRECTION-LINKAGE-FULL-UNIVERSE-VALIDATION-A0` | Correction linkage beyond sample. |
| `KR-STATUS-EFFECTIVE-DATE-MANUAL-AUDIT-EXPANSION` | Manual samples for delisting / liquidation / managed / alert. |
| `S2-DELISTING-LIQUIDATION-PARSER-FEASIBILITY-A0` | Attachment-heavy feasibility. |
| `KR-INTRADAY-HALT-SOURCE-BACKLOG` | Intraday halt / VI / circuit-breaker. |
| `KR-EXECUTABLE-STATUS-LIMIT-LOCK-OFFICIAL-SOURCE-A0` | Direct KRX/KOSCOM official limit-lock. |
| `KR-LIMIT-LOCK-CORPORATE-ACTION-ADJUSTMENT-A0` | CA effects on prev-close limit. |
| `KR-LISTED-UNIVERSE-DAILY-LIFECYCLE-REFINEMENT-A0` | Monthly → daily lifecycle. |
| `KR-OPS-NAV-UPDATE-QUARANTINE-PATCH-PHASE` | 4 ops blockers. |

Strategy testing remains **premature**. Auto-start forbidden.

### S2-HTML-INLINE-PARSER-FULL-UNIVERSE-VALIDATION-A0 — CLOSED AS FULL-UNIVERSE-PARSER-VALIDATED FOR SUSPENSION / RESUMPTION ONLY / AVAILABLE-BODY SCOPE / EXECUTION STILL CLOSED (2026-05-25)

Referee final verdict 2026-05-25: **CLOSED AS FULL-UNIVERSE-PARSER-VALIDATED FOR
SUSPENSION / RESUMPTION ONLY / AVAILABLE-BODY SCOPE / EXECUTION STILL CLOSED —
parser 1.1.0 period_change_disclosure fix accepted; 12,187 in-scope rows parsed;
1,331 extracted; 180-row holdout 99.4% success; 0 false positives; 1 wrong_date;
19/20 Pass-1 wrong rows fixed; correction policy unchanged; body_unavailable rows
preserved; no strategy testing.**

- Status: **CLOSED AS FULL-UNIVERSE-PARSER-VALIDATED FOR SUSPENSION / RESUMPTION
  ONLY / AVAILABLE-BODY SCOPE / EXECUTION STILL CLOSED**.
- 2 accepted commits: Pass 1 `20fbdf6` (evidence) + Pass 2 `38acaf9` (close-ready).
- Code: parser 1.0.0 → 1.1.0 (`src/parsers/krx_status_html_inline.py`);
  34/34 tests (`tests/test_krx_status_html_inline.py`);
  2 validation scripts at `src/audit/measurement_a0/p_full_universe_parser_validation*.py`.
- 24 deliverables ACCEPTED (12 Pass-1 + 12 Pass-2) + CLOSE_NOTE.md.

**Pass-1 (commit 20fbdf6) baseline:**
- 12,187 in-scope rows parsed; 1,402 bodies cached after 400 prefetch (11.5% body coverage).
- 1,327 extracted (10.89% overall; 94.65% given body).
- 0 negative-control FP / 5,737.
- 184-row holdout / 89.1% success / 20 wrong_date all from `period_change_disclosure` pattern.
- Gate `FULL_UNIVERSE_VALIDATION_REQUIRES_MORE_WORK`.

**Pass-2 (commit 38acaf9) targeted fix:**
- Parser 1.0.0 → 1.1.0: `PERIOD_CHANGE_RE` + `select_after_change_period_hit()` helper.
  AFTER markers: 변경후 / 변경 후 / 정정후 / 정정 후 / 변경된 / 정정된.
  BEFORE markers: 변경전 / 변경 전 / 정정전 / 정정 전 / 당초.
- Ordinary suspension / resumption / negative-control / correction handling unchanged.
- 34/34 tests passing.
- Validation-script Korean-date verification fix accepted transparently.
- Extracted: 1,327 → 1,331 (+4).
- Period_change rows in universe: 3,030; 320 took 1.1.0 path.
- 180-row holdout / 99.4% success / 0 FP / 1 wrong_date / 0 regression.
- Pass-1 wrong rows revisited: 19/20 fixed = **95.0% fix rate**.
- Correction policy: 35 allowed / 131 blocked (UNCHANGED).
- Gate state: **READY_FOR_NEXT_A0_REVIEW**.

Important accepted boundary (Referee-locked):
- "Full-universe validation" = parser applied to full in-scope universe;
  body_unavailable rows preserved and marked; available-body parser behavior
  validated with holdout; negative controls checked at full-universe scale.
- It does NOT mean every 12,187 in-scope row has a downloaded body.
- Body coverage remains incomplete (88.5% body_unavailable).
- `body_unavailable` rows remain manual_review_required / unavailable.
- No unavailable body may be treated as executable, parsed, or safe by default.
- No card is strategy-ready.

9 future-phase candidates (none active, separate Referee verdict each):

| Phase candidate | Purpose |
|---|---|
| `S2-HTML-INLINE-PARSER-BODY-COVERAGE-EXPANSION-A0` | Increase body availability for 10,000+ body_unavailable rows. **Referee-strongest next candidate.** |
| `KR-STATUS-CORRECTION-LINKAGE-FULL-UNIVERSE-VALIDATION-A0` | Correction linkage beyond sample across all in-scope correction rows. |
| `KR-STATUS-EFFECTIVE-DATE-MANUAL-AUDIT-EXPANSION` | More manual samples (delisting / liquidation / managed / alert). |
| `S2-DELISTING-LIQUIDATION-PARSER-FEASIBILITY-A0` | Separate feasibility for delisting / liquidation (attachment-heavy). |
| `KR-INTRADAY-HALT-SOURCE-BACKLOG` | Intraday halt / VI / circuit-breaker. |
| `KR-EXECUTABLE-STATUS-LIMIT-LOCK-OFFICIAL-SOURCE-A0` | Direct KRX/KOSCOM official limit-lock. |
| `KR-LIMIT-LOCK-CORPORATE-ACTION-ADJUSTMENT-A0` | CA effects on prev-close limit. |
| `KR-LISTED-UNIVERSE-DAILY-LIFECYCLE-REFINEMENT-A0` | Monthly → daily lifecycle / merger / rename / code reuse. |
| `KR-OPS-NAV-UPDATE-QUARANTINE-PATCH-PHASE` | 4 ops blockers. |

Strategy testing remains **premature**. Auto-start forbidden.

### KR-STATUS-CORRECTION-LINKAGE-A0 — CLOSED AS CORRECTION-LINKAGE VALIDATED FOR SAMPLE / HIGH_VALIDATED ONLY / EXECUTION STILL CLOSED (2026-05-25)

Referee final verdict 2026-05-25: **CLOSED AS CORRECTION-LINKAGE VALIDATED FOR
SAMPLE / HIGH_VALIDATED ONLY / EXECUTION STILL CLOSED — Pass 3 body-confirmation
gate accepted; 72-row manual validation; sample link rate 78.1%; 10 wrong
candidates quarantined; 0 residual false positives in linked pool; 35
high_validated universe candidates; 71 no_link remain; supersession design-only;
no strategy testing.**

- Status: **CLOSED AS CORRECTION-LINKAGE VALIDATED FOR SAMPLE / HIGH_VALIDATED
  ONLY / EXECUTION STILL CLOSED**.
- 3 accepted commits: Pass 1 `3d09033` (evidence) + Pass 2 `565f0d3` (evidence) +
  Pass 3 `2f890d7` (close-ready).
- Code: 3 audit scripts under `src/audit/measurement_a0/`
  (`p_status_correction_linkage.py`, `_pass2.py`, `_pass3.py`).
- Deliverables ACCEPTED:
  - Pass 1: 12 base-name outputs.
  - Pass 2: 12 `pass2_*` outputs.
  - Pass 3: 12 `pass3_*` outputs + 1 detail CSV.
  - CLOSE_NOTE.md.

**Pass 3 validation method (accepted):**

- Stricter scoring penalties: long_window > 365d −1.0; raw_pool_no_base_form −1.0;
  paren_reason mismatch −1.0; generic_title_root −0.5; cross_category extra −0.5.
- Body-confirmation gate: `high_validated` requires `body_format = html_inline`
  AND (`body_refs_title` OR `body_refs_date`). Body unavailable caps at
  `medium_needs_manual`. Body cross-check fail with high score →
  `rejected_wrong_candidate`.
- 5-tier confidence enum: `high_validated` / `medium_needs_manual` /
  `low_needs_manual` / `no_link` / `rejected_wrong_candidate`.

**Universe-level confidence (166 in-scope; body-confirmation run on sample only):**

- high_validated: 35
- medium_needs_manual: 42
- low_needs_manual: 18
- no_link: 71
- rejected_wrong_candidate: 0 (universe-level)

**Pass 3 manual validation (72 rows):**

- linked_unambiguous: 9
- linked_likely: 16
- rejected_wrong_candidate: 10 (Pass-2 wrong cases quarantined by Pass-3 gate)
- manual_review_required: 7
- no_original_found: 30
- Eligible: 32; linked total: 25.
- **Sample link rate: 78.1%**.
- Residual FP in linked pool: 0 (by construction — every linked row has body
  cross-check support).
- Date-change markers: 59 / 72 = 82%.

**Remaining no_link classification (71 rows):**

- `original_not_in_raw_pool`: 44
- `insufficient_evidence`: 25
- `original_likely_cross_category_not_allowed`: 1
- `original_possible_but_title_too_generic`: 1

**Supersession readiness (design-only):**

- 9 rows tagged `supersession_ready = yes`.
- Conditions: `high_validated` AND body-confirmed AND date-change marker AND NOT
  cross-category.
- No wiring. No C2/C3. No execution simulation. No strategy use.

**Parser interaction:** unchanged. Correction rows still forced to
`manual_review_required`. No `parser_extracts_correction_without_manual_review`
defect.

**Important remaining limits:**

- 71 / 166 in-scope corrections remain `no_link`.
- 42 + 18 `medium_needs_manual` / `low_needs_manual` rows remain manual review only.
- Cross-category links capped at medium; not supersession-ready.
- Full-universe correction-linkage validation has NOT run.
- Parser output remains limited to suspension / resumption HTML-inline scope.
- Delisting / liquidation / managed / alert parser remain out of scope.
- No card is strategy-ready.

9 future-phase candidates (none active, separate Referee verdict each):

| Phase candidate | Purpose |
|---|---|
| `S2-HTML-INLINE-PARSER-FULL-UNIVERSE-VALIDATION-A0` | Validate parser + correction-linkage against broader status-event universe. **Referee-strongest next candidate.** |
| `KR-STATUS-CORRECTION-LINKAGE-FULL-UNIVERSE-VALIDATION-A0` | Isolate correction-linkage validation across all 166 in-scope corrections + beyond. |
| `KR-STATUS-EFFECTIVE-DATE-MANUAL-AUDIT-EXPANSION` | More manual samples (delisting / liquidation / managed / alert). |
| `S2-DELISTING-LIQUIDATION-PARSER-FEASIBILITY-A0` | Separate feasibility for delisting / liquidation (attachment-heavy). |
| `KR-INTRADAY-HALT-SOURCE-BACKLOG` | Intraday halt / VI / circuit-breaker. |
| `KR-EXECUTABLE-STATUS-LIMIT-LOCK-OFFICIAL-SOURCE-A0` | Direct KRX/KOSCOM official limit-lock. |
| `KR-LIMIT-LOCK-CORPORATE-ACTION-ADJUSTMENT-A0` | CA effects on prev-close limit. |
| `KR-LISTED-UNIVERSE-DAILY-LIFECYCLE-REFINEMENT-A0` | Monthly → daily lifecycle. |
| `KR-OPS-NAV-UPDATE-QUARANTINE-PATCH-PHASE` | 4 ops blockers. |

Strategy testing remains **premature**. Auto-start forbidden.

**Scope**: Measurement-layer correction-linkage A0 only. Build and audit correction-
linkage logic for OPENDART/KRX exchange-status disclosures. Initial scope limited to
**suspension_related + resumption_related** categories, HTML-inline status
disclosures, correction-flagged rows + candidate originals, and parser outputs from
the prior S2-HTML-INLINE-PARSER-REOPEN-PHASE.

**Hard scope exclusions**:
- No delisting parser.
- No liquidation parser.
- No managed / alert parser.
- No DART body alpha.
- No overhang parser.
- No all-event event log finalization.
- No C2/C3 wiring.
- No strategy testing.
- No performance diagnostics.
- No execution simulation.
- No production / paper / P08 / live readiness / shadow-track work.

**Reason**: S2-HTML-INLINE-PARSER-REOPEN-PHASE closed validated for suspension /
resumption HTML-inline samples but 25 / 25 correction-flagged rows were forced to
manual review. Correction linkage remains unresolved. Likely linkage key =
corp_code + base_form + series_marker + time-window logic.

**Primary source-of-truth (read-only)**:
- `S2_HTML_INLINE_PARSER_REOPEN_PHASE/correction_handling_status.md`
- `S2_HTML_INLINE_PARSER_REOPEN_PHASE/parser_validation_results.csv`
- `S2_HTML_INLINE_PARSER_REOPEN_PHASE/parser_defect_ledger.csv`
- `S2_HTML_INLINE_PARSER_REOPEN_PHASE/downstream_blockers_after_parser_reopen.md`
- `KR_STATUS_EFFECTIVE_DATE_MANUAL_AUDIT_PHASE/correction_manual_review.md`
- `KR_STATUS_EFFECTIVE_DATE_MANUAL_AUDIT_PHASE/manual_effective_date_audit.csv`
- `KR_EXECUTABLE_EFFECTIVE_DATE_LINKAGE_A0/correction_cancellation_effective_date_check.md`
- `data/acquired/round5_manual_audit_samples/`, `round5_dart_pre2018/`, `round4/s3_krx_status/`
- `src/parsers/krx_status_html_inline.py`

**10 allowed task groups**: correction-flagged universe construction / base-form
normalization / series-marker extraction / candidate original-report search / link
scoring / manual validation sample / supersession rule design / parser interaction
check / defect ledger / gate status update.

**Correction-linkage gate enum (Referee-permitted)**: `DATA_SOURCE_FAIL` / `PARTIAL`
/ `CORRECTION_LINKAGE_DESIGNED_BUT_NOT_VALIDATED` /
`CORRECTION_LINKAGE_VALIDATED_FOR_SAMPLE_ONLY` /
`CORRECTION_LINKAGE_REQUIRES_MORE_WORK` / `READY_FOR_NEXT_A0_REVIEW`. Do NOT mark
execution simulation open. Do NOT mark strategy testing open. Do NOT mark parser
output strategy-ready.

**Allowed code artifacts**:
- Small linkage / scoring script under `src/audit/measurement_a0/`.
- Small helper functions for report_nm normalization if needed.
- NO strategy code. NO performance code. NO execution simulation wiring. NO C2/C3
  wiring. NO production / paper / P08 / live code modification.

**Required outputs (12)**: see `correction_linkage_referee_lock.md`.

**Output 경로**: `reports/experiments/measurement_A0/KR_STATUS_CORRECTION_LINKAGE_A0/`

**Important boundary**:
- Correction-linkage A0 only.
- Passing this phase does NOT reopen strategy testing.
- Passing this phase does NOT open execution simulation automatically.
- Passing this phase does NOT complete S2 globally.
- Passing this phase only clarifies whether correction-flagged suspension /
  resumption status disclosures can be linked to originals.

## Closed / Frozen (변경 시 사용자 결정 필요)

### S2-HTML-INLINE-PARSER-REOPEN-PHASE — CLOSED AS HTML-INLINE-PARSER-VALIDATED FOR SUSPENSION / RESUMPTION ONLY / EXECUTION STILL CLOSED (2026-05-25)

Referee final verdict 2026-05-25: **CLOSED AS HTML-INLINE-PARSER-VALIDATED FOR
SUSPENSION / RESUMPTION ONLY / EXECUTION STILL CLOSED — 108 in-scope samples;
90.7% exact match; suspension 92.5%; resumption 87.8%; 0 negative-control false
positives; correction rows forced to manual review; no strategy testing.**

- Status: **CLOSED AS HTML-INLINE-PARSER-VALIDATED FOR SUSPENSION / RESUMPTION ONLY
  / EXECUTION STILL CLOSED**.
- Initial pass commit accepted: `93661e0`
- 12 deliverables ACCEPTED.
- Code: `src/parsers/krx_status_html_inline.py` + `__init__.py`;
  `tests/test_krx_status_html_inline.py` (**26 / 26 passing**);
  `src/audit/measurement_a0/p_html_inline_parser_validation.py`.
- Sample: 195 reused from manual audit / 108 in-scope (suspension 67 + resumption 41)
  / 87 negative controls.
- Validation:
  - overall exact match 90.7%,
  - suspension exact match 92.5% (62/67),
  - resumption exact match 87.8% (36/41),
  - negative-control false positives 0,
  - correction-flagged forced to manual review 25/25.
- Defects: 14 total (8 correction_requires_manual_review / 3 missed_suspension_date /
  2 html_unparseable / 1 missed_resumption_date; 0 unsupported_category_false_positive,
  0 wrong_date_extracted, 0 ambiguous_multiple_dates).
- Gate state: **HTML_INLINE_PARSER_VALIDATED_FOR_SUSPENSION_RESUMPTION_ONLY**.

Important boundary (Referee-locked):
- Validated only for suspension_related + resumption_related + HTML-inline body
  + (effective_date / suspension_start / suspension_end / resumption_date /
  resumption_time) fields.
- NOT validated for delisting / liquidation / managed / investment_alert /
  short_term_overheated / overhang / DART body alpha / all-event event log.
- Validation scope = 108 in-scope samples, NOT the 17,924-row status-event universe.
- Parser outputs MUST NOT be treated as strategy-ready.
- No card is strategy-ready.

9 future-phase candidates (none active, separate Referee verdict each):

| Phase candidate | Purpose |
|---|---|
| `KR-STATUS-CORRECTION-LINKAGE-A0` | Correction linkage via corp_code + base_form + series_marker. **Referee-strongest next candidate.** |
| `S2-HTML-INLINE-PARSER-FULL-UNIVERSE-VALIDATION-A0` | Validate parser beyond 108-sample subset against broader status-event universe. |
| `KR-STATUS-EFFECTIVE-DATE-MANUAL-AUDIT-EXPANSION` | More manual samples (delisting / liquidation / managed / alert). |
| `S2-DELISTING-LIQUIDATION-PARSER-FEASIBILITY-A0` | Separate feasibility for delisting / liquidation (attachment-heavy). |
| `KR-INTRADAY-HALT-SOURCE-BACKLOG` | Intraday halt / VI / circuit-breaker. |
| `KR-EXECUTABLE-STATUS-LIMIT-LOCK-OFFICIAL-SOURCE-A0` | Direct KRX/KOSCOM official limit-lock. |
| `KR-LIMIT-LOCK-CORPORATE-ACTION-ADJUSTMENT-A0` | CA effects on prev-close limit. |
| `KR-LISTED-UNIVERSE-DAILY-LIFECYCLE-REFINEMENT-A0` | Monthly → daily lifecycle. |
| `KR-OPS-NAV-UPDATE-QUARANTINE-PATCH-PHASE` | 4 ops blockers. |

Strategy testing + backtesting remain **premature**. Auto-start forbidden.

### KR-STATUS-EFFECTIVE-DATE-MANUAL-AUDIT-PHASE — CLOSED AS MANUAL-AUDIT-COMPLETED / SUPPORTS HTML-INLINE PARSER REOPEN / EXECUTION STILL CLOSED (2026-05-25)

Referee final verdict 2026-05-25: **CLOSED AS MANUAL-AUDIT-COMPLETED / SUPPORTS
HTML-INLINE PARSER REOPEN / EXECUTION STILL CLOSED — 195 samples; 56.4% extraction;
suspension 92.5% and resumption 90.2% parser-feasible; delisting/liquidation
attachment-blocked; correction linkage still open; strategy testing remains closed.**

- Status: **CLOSED AS MANUAL-AUDIT-COMPLETED / SUPPORTS HTML-INLINE PARSER REOPEN /
  EXECUTION STILL CLOSED**.
- Initial pass commit accepted: `046cf20`
- 12 deliverables ACCEPTED.
- Sample plan: 195 samples (within 150-200 target). Buckets accepted as delivered.
- Body format: 188 html_inline / 7 unparseable / 0 structured_xml / 0 download_failed.
- Effective-date extraction: 110 / 195 = **56.4%** (31× lift over prior simple-regex
  A0 1.8%). bs4-driven HTML-inline label extraction.
- Label inventory: 30 (label × category × format) tuples; 12 distinct Korean date
  labels observed.
- Classification distribution: explicit_suspension_period 63 / no_date_found 60 /
  explicit_resumption_date 36 / ambiguous_date 18 / explicit_effective_date 10 /
  body_unavailable 7 / explicit_liquidation_period 1.
- rcept_dt relation: 139 unknown / 27 equal_to_rcept_dt / 18 after_rcept_dt /
  11 before_rcept_dt. `rcept_dt` lock remains permanent.
- Reliability: 110 high / 18 medium / 67 low.
- Parser feasibility (overall): **parser_feasible_html_inline**. Suspension 92.5% +
  resumption 90.2% drive the lift; delisting 3.8% / liquidation / investment_alert /
  short_term_overheated remain attachment-blocked; managed 28.6% needs custom rules.
- 5 effective-date defect updates: effective_date_unextracted_majority → partial;
  html_inline_unparsed → parser_required; correction_linkage_partial still_open;
  rcept_dt_default_forbidden → closed (lock permanent); body_download_failures →
  closed (0/195).
- Gate state: **MANUAL_AUDIT_SUPPORTS_PARSER_REOPEN**.

Important boundary (Referee-locked):
- Manual audit completed.
- Parser reopen is NOT automatic.
- This phase did NOT implement a parser.
- This phase did NOT reopen S2.
- Execution simulation remains closed.
- Strategy testing remains closed.
- No card is strategy-ready.

8 future-phase candidates (none active, separate Referee verdict each):

| Phase candidate | Purpose |
|---|---|
| `S2-HTML-INLINE-PARSER-REOPEN-PHASE` | Reopen parser work for HTML-inline status disclosures. Initial scope = suspension_related + resumption_related only. **Referee-strongest next candidate.** |
| `KR-STATUS-EFFECTIVE-DATE-MANUAL-AUDIT-EXPANSION` | Add more manual samples (delisting / liquidation / managed / alert). |
| `KR-STATUS-CORRECTION-LINKAGE-A0` | Resolve correction linkage using corp_code + base_form + series_marker. |
| `KR-INTRADAY-HALT-SOURCE-BACKLOG` | Intraday halt / VI / circuit-breaker source. |
| `KR-EXECUTABLE-STATUS-LIMIT-LOCK-OFFICIAL-SOURCE-A0` | Direct KRX/KOSCOM official limit-lock acquisition. |
| `KR-LIMIT-LOCK-CORPORATE-ACTION-ADJUSTMENT-A0` | CA effects on prev-close limit. |
| `KR-LISTED-UNIVERSE-DAILY-LIFECYCLE-REFINEMENT-A0` | Monthly → daily lifecycle / merger linkage / rename / code reuse. |
| `KR-OPS-NAV-UPDATE-QUARANTINE-PATCH-PHASE` | 4 ops blockers (touches ops/paper/live). |

Strategy testing + backtesting remain **premature**. Auto-start forbidden.

### KR-EXECUTABLE-EFFECTIVE-DATE-LINKAGE-A0 — CLOSED AS EFFECTIVE-DATE-LINKAGE-AUDITED / PARTIAL / NOT GENERALIZABLE / EXECUTION STILL CLOSED (2026-05-25)

Referee final verdict 2026-05-25: **CLOSED AS EFFECTIVE-DATE-LINKAGE-AUDITED / PARTIAL
/ NOT GENERALIZABLE / EXECUTION STILL CLOSED — 17,924 combined status events; 113
stratified samples; effective-date extraction 2/113 = 1.8%; rcept_dt not safe as
effective date; HTML-inline / S2 parser dependency remains; execution simulation still
closed.**

- Status: **CLOSED AS EFFECTIVE-DATE-LINKAGE-AUDITED / PARTIAL / NOT GENERALIZABLE /
  EXECUTION STILL CLOSED**.
- Initial pass commit accepted: `7ff7d0a`
- 12 deliverables ACCEPTED.
- Combined universe: pre-2018 (7,150) + post-2018 (10,774) = 17,924.
- Sample: 113 stratified (suspension 30 / resumption 30 / delisting 30 / managed bucket
  20 / liquidation 3) — pre + post balanced.
- Extraction method breakdown (canonical per repo artifact):
  - `unavailable`: 109 (regex matched no body field)
  - `official_body_date`: 2 (only successful extractions)
  - `body_unavailable`: 2 (download/parse failure)
- Extraction rate: **1.8%** (2 / 113).
- 1 sample showed `effective_date_after_rcept_dt`, confirming rcept_dt ≠ effective date.
- 5 defects: effective_date_unextracted_majority / rcept_dt_default_forbidden /
  body_download_failures / correction_linkage_partial / html_inline_unparsed.
- Gate state: **PARTIAL**.
- Core blocker: KRX status events are HTML-inline; S2 OPENDART Body Parser CLOSED AS
  PARTIAL prevents bulk effective-date extraction.

Conservative rule design (design-only): Use explicit body/title date when extractable;
unknown effective date = fail-closed; do not auto-unblock resumption based on rcept_dt;
delisting/liquidation require explicit date/period; corrections supersede prior only
when linked.

7 future-phase candidates (none active, separate Referee verdict each):

| Phase candidate | Purpose |
|---|---|
| `S2-HTML-INLINE-PARSER-REOPEN-PHASE` | Reopen parser work specifically for HTML-inline status disclosures. |
| `KR-STATUS-EFFECTIVE-DATE-MANUAL-AUDIT-PHASE` | Manual review of larger status-event sample. |
| `KR-INTRADAY-HALT-SOURCE-BACKLOG` | Intraday halt / VI / circuit-breaker source. |
| `KR-EXECUTABLE-STATUS-LIMIT-LOCK-OFFICIAL-SOURCE-A0` | Direct KRX/KOSCOM official limit-lock acquisition. |
| `KR-LIMIT-LOCK-CORPORATE-ACTION-ADJUSTMENT-A0` | CA effects on prev-close limit. |
| `KR-LISTED-UNIVERSE-DAILY-LIFECYCLE-REFINEMENT-A0` | Monthly → daily lifecycle. |
| `KR-OPS-NAV-UPDATE-QUARANTINE-PATCH-PHASE` | 4 ops blockers. |

Strategy testing + backtesting remain **premature**.

### KR-EXECUTABLE-STATUS-PRE2018-EXTENSION-A0 — CLOSED AS PRE2018-STATUS-SOURCE-ACQUIRED / RECONCILED / EXECUTION STILL CLOSED (2026-05-24)

Referee final verdict 2026-05-24: **CLOSED AS PRE2018-STATUS-SOURCE-ACQUIRED /
RECONCILED / EXECUTION STILL CLOSED — full 2010-2017 OPENDART pblntfty=I corpus
acquired; 300,829 raw rows; 7,150 filtered status events; pre_2018_status_coverage_gap
closed; effective-date and intraday halt gaps remain; execution simulation still
closed.**

- Status: **CLOSED AS PRE2018-STATUS-SOURCE-ACQUIRED / RECONCILED / EXECUTION STILL CLOSED**.
- Initial pass commit accepted: `0d80010`
- 12 deliverables ACCEPTED.
- Source: OPENDART pblntfty=I (거래소공시) acquired 2010-01-01 → 2017-12-31 with
  OPENDART_API_KEY. 3-month chunks × pagination. ~3000 API calls, ~25 min runtime.
- Raw: 300,829 rows. Filtered status events: 7,150 (suspension 3,211 / resumption
  2,058 / delisting 1,683 / managed 178 / short_term_overheated 10 / investment_alert
  8 / liquidation 2).
- Reconciliation against 2010-2017 panel + lifecycle + W001 v2 terminal accepted.
- `pre_2018_status_coverage_gap` (from KR-EXECUTABLE-STATUS-COVERAGE-A0): open → **CLOSED**.
- Gate state: **PRE2018_STATUS_RECONCILED_BUT_EXECUTION_STILL_CLOSED**.
- Now compatible with the 2018+ S3 status-event pipeline.

Accepted limitations: rcept_dt = filing date ≠ effective status date (S2 PARTIAL);
intraday halt source still missing; official limit-lock source still missing; 293,679
"other" pool requires sample audit; 7 events missing stock_code; panel absence ≠
non-tradable; rcept_dt MUST NOT be treated as effective status date without audit.

6 future-phase candidates (none active, separate Referee verdict each):

| Phase candidate | Purpose |
|---|---|
| `KR-EXECUTABLE-EFFECTIVE-DATE-LINKAGE-A0` | Link rcept_dt → actual effective status date (depends on DART body / sample audit). **Referee-recommended next** for practical backtest-readiness. |
| `KR-INTRADAY-HALT-SOURCE-BACKLOG` | Intraday halt / VI / circuit-breaker source (likely external/commercial). |
| `KR-EXECUTABLE-STATUS-LIMIT-LOCK-OFFICIAL-SOURCE-A0` | Direct KRX/KOSCOM official limit-lock acquisition. |
| `KR-LIMIT-LOCK-CORPORATE-ACTION-ADJUSTMENT-A0` | Audit CA effects on prev-close limit calculations. |
| `KR-LISTED-UNIVERSE-DAILY-LIFECYCLE-REFINEMENT-A0` | Monthly → daily lifecycle; merger linkage; rename; code reuse. |
| `KR-OPS-NAV-UPDATE-QUARANTINE-PATCH-PHASE` | Patch the 4 remaining ops blockers (touches ops/paper/live). |

Strategy testing remains **premature**. Backtesting remains premature.

### KR-EXECUTABLE-STATUS-LIMIT-LOCK-SOURCE-A0 — CLOSED AS LIMIT-LOCK-PROXY-RECONCILED / PARTIAL COVERAGE / EXECUTION STILL CLOSED (2026-05-24)

Referee final verdict 2026-05-24: **CLOSED AS LIMIT-LOCK-PROXY-RECONCILED / PARTIAL
COVERAGE / EXECUTION STILL CLOSED — official KRX limit-lock log not acquired;
rule-derived proxy found 336 close-at-limit candidates; W001 v2 limit_lock_candidate
under-counted; conservative execution rule design documented; execution simulation
remains closed.**

- Status: **CLOSED AS LIMIT-LOCK-PROXY-RECONCILED / PARTIAL COVERAGE / EXECUTION STILL CLOSED**.
- Initial pass commit accepted: `8d0003b`
- 12 deliverables ACCEPTED.
- Source: rule-derived proxy from KRX historical price-limit rule (±15% pre-2015-06-15
  / ±30% post). Official KRX limit-lock log NOT in repo.
- 1,141,751 panel rows scanned; **325 upper + 11 lower = 336 rule-derived candidates**.
- W001 v2 limit_lock_candidate set (41 rows) is **UNDER-COUNTED**: only 2 matched
  rule; 39 W001-only-no-rule-support; 334 rule-only.
- OHLCV overlap: 123 panel_absence / 63 true_suspension / 19 delisting_transition /
  1 data_missing / 2 limit_lock_candidate. Quarantine + executable-status OUTRANK
  limit candidate label.
- Conservative execution rule design (asymmetric upper/lower fail-closed) documented;
  design-only.
- 9 defects: official_source_unavailable / W001 under-counted / no direction in W001 /
  close-at-limit vs locked indistinguishable / CA prev_close adjustment / IPO day-1 /
  VI not captured / W001 candidate no rule support / panel_absence overlap.
- Gate state: **PARTIAL**.

Accepted limitations: official log missing; KRX 단일가매매 endpoint not acquired;
rule-derived close-at-limit ≠ locked; CA distorts prev_close calculation; first-listing
day rule differs; VI / circuit breaker not captured; W001 v2 proxy lacks direction.

6 future-phase candidates (none active, separate Referee verdict each):

| Phase candidate | Purpose |
|---|---|
| `KR-EXECUTABLE-STATUS-PRE2018-EXTENSION-A0` | Extend S3 executable-status coverage pre-2018. **Referee-recommended next** for practical backtest-readiness path. |
| `KR-EXECUTABLE-STATUS-LIMIT-LOCK-OFFICIAL-SOURCE-A0` | Attempt direct KRX/KOSCOM official limit-lock or single-price-session source acquisition. |
| `KR-LIMIT-LOCK-CORPORATE-ACTION-ADJUSTMENT-A0` | Audit CA effects on prev-close limit calculations. |
| `KR-INTRADAY-HALT-SOURCE-BACKLOG` | Intraday halt / VI / circuit-breaker source (likely external/commercial). |
| `KR-LISTED-UNIVERSE-DAILY-LIFECYCLE-REFINEMENT-A0` | Monthly → daily lifecycle; merger linkage; rename; code reuse. |
| `KR-OPS-NAV-UPDATE-QUARANTINE-PATCH-PHASE` | Patch the 4 remaining ops blockers (touches ops/paper/live). |

Strategy testing remains **premature**. Backtesting remains premature.

### KR-EXECUTABLE-STATUS-COVERAGE-A0 — CLOSED AS EXECUTABLE-STATUS-SOURCE-ACQUIRED / PARTIAL COVERAGE / EXECUTION STILL CLOSED (2026-05-24)

Referee final verdict 2026-05-24: **CLOSED AS EXECUTABLE-STATUS-SOURCE-ACQUIRED /
PARTIAL COVERAGE / EXECUTION STILL CLOSED — S3 KRX status events reconciled; 10,774
events, 1,855 tickers, 2018+ coverage; intraday halt, official limit-lock, and pre-2018
status coverage missing; execution simulation remains closed.**

- Status: **CLOSED AS EXECUTABLE-STATUS-SOURCE-ACQUIRED / PARTIAL COVERAGE / EXECUTION
  STILL CLOSED**.
- Initial pass commit accepted: `712d45b`
- 12 deliverables ACCEPTED.
- Primary source: S3 KRX status events (OPENDART pblntfty=I 거래소공시 filtered);
  10,774 events / 1,855 tickers / 2018-01-01 → 2026-05-06.
- Reconciliation (S3 vs W001 v2 tradable_state):
  - matched_status: 63
  - official_status_but_panel_absent: 9,551 (selection-bias artefact, not true
    disagreement)
  - requires_manual_review: 762
  - proxy_only: 304
  - official_resumption_but_repo_other: 94
- Lifecycle cross-check: 1,723 with-terminal / 132 not-in-lifecycle.
- OHLCV overlap: 41 limit_lock_candidate rows remain candidate-only.
- 4 defects: intraday_halt_source_missing / pre_2018_status_coverage_gap /
  no_tradable_state_label_for_managed_alert_liquidation / limit_lock_proxy_only.
- Gate state: **PARTIAL**.
- Execution simulation remains CLOSED. Strategy testing remains CLOSED.

Accepted limitations: semi-official OPENDART (not direct KRX feed); 2018+ only;
intraday halts NOT covered; official limit-lock log NOT covered; managed/alert/
liquidation labels lack W001 tradable_state equivalents; effective status dates may
differ from rcept_date (DART body parsing PARTIAL).

5 future-phase candidates (none active, separate Referee verdict each):

| Phase candidate | Purpose |
|---|---|
| `KR-EXECUTABLE-STATUS-PRE2018-EXTENSION-A0` | Extend executable-status coverage pre-2018 |
| `KR-EXECUTABLE-STATUS-LIMIT-LOCK-SOURCE-A0` | Acquire official upper/lower-limit lock source |
| `KR-INTRADAY-HALT-SOURCE-BACKLOG` | KRX/KOSCOM intraday halt source (likely commercial) |
| `KR-LISTED-UNIVERSE-DAILY-LIFECYCLE-REFINEMENT-A0` | Monthly → daily lifecycle; merger linkage; rename; code reuse |
| `KR-OPS-NAV-UPDATE-QUARANTINE-PATCH-PHASE` | Patch the 4 remaining ops blockers (touches ops/paper/live) |

Strategy testing remains **premature**. Backtesting remains premature.

### KR-LISTED-UNIVERSE-COVERAGE-A0 — CLOSED AS LISTED-UNIVERSE-SOURCE-ACQUIRED / PARTIAL LIFECYCLE / NOT SURVIVORSHIP-SAFE (2026-05-24)

Referee final verdict 2026-05-24: **CLOSED AS LISTED-UNIVERSE-SOURCE-ACQUIRED / PARTIAL
LIFECYCLE / NOT SURVIVORSHIP-SAFE — monthly KRX listed-universe snapshots acquired;
3,653 official ever-listed tickers vs 925 repo panel tickers; 2,728 official-only
tickers; 519 disappeared without terminal event; strategy testing remains closed.**

- Status: **CLOSED AS LISTED-UNIVERSE-SOURCE-ACQUIRED / PARTIAL LIFECYCLE / NOT
  SURVIVORSHIP-SAFE**.
- Initial pass commit accepted: `dbd847b`
- 12 deliverables ACCEPTED.
- Source acquired: pykrx `get_market_ticker_list(date, market)` with KRX_ID auth;
  monthly first-trading-day snapshots 2010-01 → 2026-05; 197 snapshots / 441,359 rows
  / 3,653 unique tickers (KOSPI+KOSDAQ).
- Storage: `data/acquired/krx_listed_universe/krx_listed_monthly_snapshots_2010_2026.csv`
  (gitignored; reproducible).
- Reconciliation: 925 matched / 0 panel-only / 2,728 official-only (74.7% panel
  blind spot).
- 519 disappeared without W001 v2 terminal event.
- 519 defect-ledger entries.
- Gate state: **PARTIAL** (per Referee-permitted enum).
- **Survivorship-safe claim explicitly REJECTED.** Repo panel = liquidity-biased
  dynamic_top100, not full all-market universe.
- Permanent ID: DART corp_code stable; KRX_TICKER fallback temporary (50 found in
  official snapshots); blocks full strategy pass.

Accepted limitations:
- Monthly resolution (±1 month listing/delisting precision).
- KONEX excluded.
- Merger linkage / rename history / code reuse / intraday status NOT in source.
- Source does NOT solve execution feasibility / DART body event-log gaps / strategy
  reopen.

4 future-phase candidates (none active, separate Referee verdict each):

| Phase candidate | Purpose |
|---|---|
| `KR-EXECUTABLE-STATUS-COVERAGE-A0` | Acquire / validate official executable-status / halt / limit-lock source. **Referee-recommended next** for execution feasibility. |
| `KR-LISTED-UNIVERSE-DAILY-LIFECYCLE-REFINEMENT-A0` | Monthly → daily lifecycle resolution; merger linkage; rename history; code reuse. Optional. |
| `KR-OPS-NAV-UPDATE-QUARANTINE-PATCH-PHASE` | Patch the 4 remaining ops blockers (touches ops/paper/live). |
| `KR-CLOSED-STRATEGY-CODEPATH-QUARANTINE-A0` | Optional follow-up before any strategy reopen. Lower priority. |

Strategy testing remains **premature**. Backtesting remains premature. Future strategy
review must explicitly account for the listed-universe limitation: repo panel is
dynamic_top100 / liquidity-biased, not full all-market survivorship-safe universe.

### KR-KRX-CALENDAR-SOURCE-ACQUISITION-A0 — CLOSED AS CALENDAR-SOURCE-RECONCILED / EXECUTION STILL CLOSED (2026-05-24)

Referee final verdict 2026-05-24: **CLOSED AS CALENDAR-SOURCE-RECONCILED — composite
2010-2026 KRX calendar acquired; 4,021/4,021 t+1 mappings match prior union calendar;
12 official-only vendor-cutoff dates; execution simulation still closed.**

- Status: **CLOSED AS CALENDAR-SOURCE-RECONCILED / EXECUTION STILL CLOSED**.
- Initial pass commit accepted: `d27a851`
- 11 deliverables ACCEPTED.
- Composite source ACCEPTED with L1/L2 provenance:
  - L1: pykrx 005930 OHLCV (2014-03-03 → 2026-05-22, 3,000 dates, authoritative).
  - L2: market_flow_2010_2017_krx_trading_days.csv (2010-01-04 → 2014-03-02, 1,034
    dates, secondary reference per Referee-permitted).
  - Total: 4,034 dates 2010-01-04 → 2026-05-22.
- Reconciliation: 4,022 matched / 0 repo-only / 12 official-only (all 2026-05-07 →
  2026-05-22 vendor-cutoff dates).
- T+1 mapping: 4,021/4,021 match (100%); 0 mismatches.
- Execution-simulation gate: `CALENDAR_SOURCE_RECONCILED_BUT_EXECUTION_STILL_CLOSED`.
- Calendar source no longer the main blocker. Other blockers remain
  (listed-universe / executable-status / residual ops).
- Calendar storage: `data/acquired/krx_calendar/krx_official_calendar_2010_2026.csv`
  (gitignored; reproducible via build script).
- No credential committed.

Limitations:
- Composite, not a single direct official KRX holiday endpoint.
- pre-2014 layer uses existing KRX-tagged market_flow source as secondary reference.
- pykrx 005930 may undercount rare dates (no material mismatch found).
- Date-level only; no intraday halt / shortened session / executable-status metadata.
- This phase does NOT certify execution readiness / survivorship safety / tradability.

4 future-phase candidates (none active, separate Referee verdict each):

| Phase candidate | Purpose |
|---|---|
| `KR-LISTED-UNIVERSE-COVERAGE-A0` | Acquire / validate official listed-universe / lifecycle coverage. **Referee-recommended next** for cleanest path toward safe future backtesting. |
| `KR-EXECUTABLE-STATUS-COVERAGE-A0` | Acquire / validate official executable-status / halt / limit-lock source. Natural next if priority = execution feasibility. |
| `KR-OPS-NAV-UPDATE-QUARANTINE-PATCH-PHASE` | Patch the 4 remaining ops blockers (touches ops/paper/live-related code). |
| `KR-CLOSED-STRATEGY-CODEPATH-QUARANTINE-A0` | Optional follow-up before any strategy reopen. Lower priority while strategy testing closed. |

Strategy testing remains **premature**.

### KR-OHLCV-RESIDUAL-BLOCKER-PATCH-PHASE — CLOSED AS RESIDUAL-BLOCKERS-REDUCED / OPS BLOCKERS PRESERVED (2026-05-24)

Referee final verdict 2026-05-24: **CLOSED AS RESIDUAL-BLOCKERS-REDUCED — 40 patched,
1 false_positive_static_scan, 4 ops blockers preserved; 6/6 closed-strategy entry guards
smoke-tested; no strategy testing.**

- Status: **CLOSED AS RESIDUAL-BLOCKERS-REDUCED / OPS BLOCKERS PRESERVED** (not clean
  full pass — 4 ops blockers preserved per production lock).
- Initial pass commit accepted: `3942904`
- 9 deliverables ACCEPTED.
- Code patches accepted:
  - `src/utils/ohlcv_quarantine.py` helper `assert_panel_has_valid_mask` (lightweight
    fail-closed gate).
  - `tests/test_ohlcv_quarantine.py` 22/22 passing.
  - 6 closed-strategy entry functions patched (baselines / b004 / c003 / d004 / p002 /
    p003); 6/6 smoke pass.
- Patch status (45 total): 40 patched / 4 still_reopen_blocker (ops) / 1
  false_positive_static_scan.
- Closed strategies remain CLOSED. Ops / paper / live remain LOCKED.
- Original `KR_OHLCV_QUARANTINE_ENFORCEMENT_A0` defect ledger preserved unchanged.

5 future-phase candidates (none active, separate Referee verdict each):

| Phase candidate | Purpose |
|---|---|
| `KR-OPS-NAV-UPDATE-QUARANTINE-PATCH-PHASE` | Patch the remaining 4 `src/ops/nav_update.py` blockers. Touches ops/paper/live-related code paths — requires explicit Referee approval. |
| `KR-KRX-CALENDAR-SOURCE-ACQUISITION-A0` | Acquire authoritative KRX calendar. **Referee-recommended next direction if priority = execution-simulation readiness.** |
| `KR-LISTED-UNIVERSE-COVERAGE-A0` | After official listed-universe / lifecycle source acquired. DATA BACKLOG. |
| `KR-EXECUTABLE-STATUS-COVERAGE-A0` | After official executable-status source acquired. DATA BACKLOG. |
| `KR-CLOSED-STRATEGY-CODEPATH-QUARANTINE-A0` | Optional follow-up before any strategy reopen. Lower priority now (entry guards added + smoke-tested). |

Strategy testing remains **premature**.

### KR-OHLCV-RUNTIME-MASK-PROPAGATION-A0 — CLOSED AS RUNTIME-VERIFIED FOR TESTED PATHS / RESIDUAL BLOCKERS PRESERVED (2026-05-24)

Referee final verdict 2026-05-24: **CLOSED AS RUNTIME-VERIFIED FOR TESTED PATHS — 10/10
synthetic tests passed; 11,425 real invalid rows detected and filtered; backtest /
universe fail-closed gates verified; 45 residual blockers preserved; no strategy
testing.**

- Status: **CLOSED AS RUNTIME-VERIFIED FOR TESTED PATHS / RESIDUAL BLOCKERS PRESERVED**
  (not full-market / not strategy / not production-readiness pass).
- Initial pass commit accepted: `0d2b4aa`
- 9 deliverables ACCEPTED.
- 10/10 synthetic invalid-row runtime tests passed.
- Real spot check on kiwoom_2010_2016 (1,093,386 rows): **11,425** invalid rows
  detected = exact match with prior P1 OHLCV invariant audit nonpositive finding.
- Backtest entry: `run_candidate_backtest` raises `OhlcvQuarantineError` without mask.
- Universe builder: rejects panel without mask; filters invalid rows when present.
- Feature path: `stock_rs_score.py` records `require_guarded_field_use("daily_return", ...)`;
  other feature builders remain `upstream_guarded` under patch-phase decision.
- 45 residual blockers classified by runtime_status (none deleted, none downgraded;
  all retain `reopen_blocker=true`).
- Runtime verification = tested paths only. Does not certify all possible future
  strategy paths. Does not remove residual blockers. Does not reopen any strategy.
- No new source-code patches in this verification phase.

5 future-phase candidates (none active, separate Referee verdict each):

| Phase candidate | Purpose |
|---|---|
| `KR-OHLCV-RESIDUAL-BLOCKER-PATCH-PHASE` | Address the 45 remaining residual blockers. **Most natural next if priority = reducing blockers before strategy work.** |
| `KR-CLOSED-STRATEGY-CODEPATH-QUARANTINE-A0` | Audit closed strategy paths directly before any strategy reopen. |
| `KR-KRX-CALENDAR-SOURCE-ACQUISITION-A0` | Acquire / reconcile authoritative KRX calendar. **Most natural next if priority = execution-simulation readiness.** |
| `KR-LISTED-UNIVERSE-COVERAGE-A0` | After official listed-universe / lifecycle source is acquired. Currently DATA BACKLOG. |
| `KR-EXECUTABLE-STATUS-COVERAGE-A0` | After official executable-status source is acquired. Currently DATA BACKLOG. |

Strategy testing remains **premature**.

### KR-OHLCV-QUARANTINE-PATCH-PHASE — CLOSED AS PATCHED-PARTIAL / RESIDUAL BLOCKERS PRESERVED (2026-05-24)

Referee final verdict 2026-05-24: **CLOSED AS PATCHED-PARTIAL — 42 patched, 37
upstream_guarded, 44 still_reopen_blocker, 19 audit_only_no_patch_needed, 1
future_work; runtime propagation not verified.**

- Status: **CLOSED AS PATCHED-PARTIAL / RESIDUAL BLOCKERS PRESERVED** (not clean pass —
  45 residual blockers remain visible).
- Initial pass commit accepted: `2fd9e4e`
- 9 deliverables ACCEPTED.
- Guard module + 19 passing tests ACCEPTED.
- 6 code patch files ACCEPTED (`src/data/equity_panel.py`, `market_flow.py`,
  `universe.py`, `sector_aggregator.py`, `backtest/engine.py`,
  `features/stock_rs_score.py`).
- Patch status distribution (143 defects): 42 patched / 37 upstream_guarded / 44
  still_reopen_blocker / 19 audit_only_no_patch_needed / 1 not_patched_requires_future_work.
- 45 residual blockers preserved (44 still_reopen_blocker + 1 future_work) — visible,
  not deleted, not suppressed, not downgraded; block any future strategy reopen.
- Static rescan +3 accepted as local-window scanner limitation; informational only.
- `defect_patch_plan.csv` is authoritative per-defect patch-status record.
- Runtime mask propagation **NOT verified** by this phase.
- Original KR_OHLCV_QUARANTINE_ENFORCEMENT_A0 defect ledger preserved unchanged.

3 future-phase candidates (none active, separate Referee verdict each):

| Phase candidate | Purpose |
|---|---|
| `KR-OHLCV-RUNTIME-MASK-PROPAGATION-A0` | Verify masks propagate through actual runtime data flows. **Recommended next if user chooses to continue.** |
| `KR-OHLCV-RESIDUAL-BLOCKER-PATCH-PHASE` | Address the 44 still_reopen_blocker + 1 future_work rows. |
| `KR-CLOSED-STRATEGY-CODEPATH-QUARANTINE-A0` | Audit closed-strategy paths against accidental reactivation. |

(Older candidates remain: `KR-KRX-CALENDAR-SOURCE-ACQUISITION-A0`,
`KR-LISTED-UNIVERSE-COVERAGE-A0`, `KR-EXECUTABLE-STATUS-COVERAGE-A0`.
All require fresh Referee verdict.)

### KR-OHLCV-QUARANTINE-ENFORCEMENT-A0 — CLOSED AS DEFECT-FOUND (2026-05-23)

Referee final verdict 2026-05-23: **CLOSED AS DEFECT-FOUND — 143 defects recorded; no
patches applied.**

- Status: **CLOSED AS DEFECT-FOUND** (not PASS — presence of 51 LEAK + 92 MISSING_GUARD
  prevents clean pass).
- Initial pass commit accepted: `06a2dfa`
- 8 deliverables ACCEPTED.
- 143 defects ACCEPTED (51 high + 92 medium); preserved in ledger with additional
  `current_runtime_risk` + `reopen_blocker=true` annotation columns (additive only —
  original severity / classification unchanged).
- `required_patch_register.md` = documentation-only source of truth for any future
  patch phase.
- Static-scan limit accepted (does not verify runtime mask propagation).
- Closed-strategy callsites remain in ledger as reopen blockers (not removed, not
  suppressed, not reclassified).

3 new candidate phases enumerated (none active, none auto-start):

| Phase candidate | Purpose |
|---|---|
| `KR-OHLCV-QUARANTINE-PATCH-PHASE` | Implement guard patches for the 143 findings. **Recommended next if user chooses to continue.** |
| `KR-OHLCV-RUNTIME-MASK-PROPAGATION-A0` | Verify invalid-row masks propagate through actual runtime data flows. |
| `KR-CLOSED-STRATEGY-CODEPATH-QUARANTINE-A0` | Audit closed-strategy code paths against accidental reactivation with invalid OHLCV usage. |

(Older measurement-layer A0 candidates remain: `KR-KRX-CALENDAR-SOURCE-ACQUISITION-A0`,
`KR-LISTED-UNIVERSE-COVERAGE-A0`, `KR-EXECUTABLE-STATUS-COVERAGE-A0`. All require fresh
Referee verdict.)

### Measurement-layer A0 initial pass — CLOSED AS PARTIAL / DEFECT-FOUND (2026-05-23)

Referee verdict 2026-05-23 로 5 카드 initial pass 인수. Commit `78543b4` accepted.

| Phase id | Status |
|---|---|
| `KR-FIELD-METADATA-CONTRACT-A0-001` | **ACCEPTED / PARTIAL-GUARDED** — 27 datasets / 372 cols / 0 UNKNOWN / 196 ALLOW / 176 ALLOW_WITH_GUARD / 0 QUARANTINE / 31 ambiguity defects. ALLOW_WITH_GUARD 사용 = 호출부 guard 문서화 필수 |
| `KR-CALENDAR-PANEL-ALIGN-A0-001` | **ACCEPTED / PARTIAL** — 0 off-calendar / 0 missing / 0 duplicate. T+1 reproducible vs union calendar. 그러나 authoritative KRX calendar source = **UNRESOLVED** → execution simulation CLOSED |
| `KR-OHLCV-UNIT-INVARIANT-A0-001` | **ACCEPTED / DEFECT-FOUND** — 4.9M rows / 58,649 OHLC violations / 53,556 nonpos / 0 negative. Pattern = OHL=0 with close>0 (vendor non-trading-row 협약). **Quarantine 의무** — 절대 price 관측 / halt 증거 / suspension 증거 / alpha signal 로 해석 금지 |
| `KR-LISTED-UNIVERSE-COVERAGE-BACKLOG-001` | **DATA BACKLOG** — official source 미획득. Panel 만으로 survivorship safety 증명 불가 |
| `KR-EXECUTABLE-STATUS-BACKLOG-001` | **DATA BACKLOG** — official source 미획득. Panel presence / volume>0 / tradable_state 만으로 executable status 증명 불가 |

Artifact 보존 (Referee lock):
- 20 files under `reports/experiments/measurement_A0/` — 삭제 / 재작성 금지
- 3 reproducible builds under `src/audit/measurement_a0/` — 삭제 금지
- Defect ledgers 재해석을 strategy 증거로 사용 금지

Possible future phases (none active, separate Referee verdict each):

| Phase id | Purpose | Note |
|---|---|---|
| `KR-OHLCV-QUARANTINE-ENFORCEMENT-A0` | Verify OHL=0 / nonpos / invalid OHLC rows excluded or guarded in all downstream code paths | Referee-recommended next infrastructure step (NOT auto-start) |
| `KR-KRX-CALENDAR-SOURCE-ACQUISITION-A0` | Acquire / reconcile authoritative KRX trading calendar; close calendar-source ambiguity | measurement-layer only |
| `KR-LISTED-UNIVERSE-COVERAGE-A0` | Begin only after official listed-universe / lifecycle source acquired | currently DATA BACKLOG |
| `KR-EXECUTABLE-STATUS-COVERAGE-A0` | Begin only after official executable-status source acquired | currently DATA BACKLOG |

### C2-C3-DESIGN-FINALIZATION — CLOSED (2026-05-23)

Referee 가 2026-05-23 verdict 로 phase 종료 + bundle 인수.

- Status: design-only, no wiring
- Bundle: `reports/experiments/C2_C3_design_finalization/` (9 outputs)
- Commit: `720b34c` (accepted by Referee)
- Design contracts (locked):
  - 10 input states + priority order
  - event_source_state rules across 14 event types
  - not_available 명시 (zero 처리 금지)
  - correction-unlinked → audit queue (never event)
  - corporate_action_day = unpopulated until all gates pass
  - 6 parser output acceptance gates
  - Future phase dependency graph + no auto-progression

### S2 OPENDART Body Parser Phase — CLOSED AS PARTIAL (2026-05-23)

Referee 최종 verdict (2026-05-23):

- D3a = **PARTIAL**
- D3b = **PARTIAL / NOT C3-ready**
- D3c = **CLOSED** (never opened)
- C2/C3 integration = **DESIGN-ONLY**
- Strategy testing = remains CLOSED
- Performance diagnostics = remains CLOSED
- Production / paper / P08 / live = UNCHANGED

S2 final A0 report bundle: `reports/experiments/S2_phase_final_A0/` (11 files,
including `S2_parser_A0_final_report.md`).

### Future phases (Referee approval required, none active)

| Phase candidate | Trigger |
|---|---|
| `S2-D3A-ONE-MORE-PASS-PHASE` | Narrowly targeted parser pass on 2 deterministic D3a forms (자기주식취득결과보고서 + 주식소각결정). ~1-2 weeks. |
| `S2-D3B-CUSTOM-PARSER-PHASE` | ACODE 11324/11325 custom parsers + conversion_request family + SECTION/COVER text scanner. ~4-7 weeks. |
| `S2-D3C-OPEN-PHASE` | After D3a + D3b state resolved. HTML/free-text heavy. |
| `S2-MANUAL-AUDIT-PHASE` | 30 samples per event type ≈ 500 disclosures full manual audit. |
| `C2-C3-DESIGN-FINALIZATION` | Design-only (allowed under current verdict). No wiring. |

Reopen 시 = 각 phase 별 fresh Referee approval (scope, kill gates, manual audit
requirements, time budget) 필요. 현 S2 phase 의 자동 연속 X.

### Other closed / frozen items (unchanged)

- P08_IEF30 frozen primary
- Strategy TEST + Round 2 cards (5) + 10 BACKLOG cards = REMAINS CLOSED
- 5 Round 3 cards all PARTIAL PASS (no FULL PASS)
- 34 Round 3 defects: 25 CLOSED + 8 PARTIAL + 1 DEFERRED-S2 (G5_000005, still
  DEFERRED — S2 parser cannot deliver C3 reclassification input)
- Critical 6: 4 CLOSED + 1 PARTIAL + 1 DEFERRED-S2

## New hard prohibitions added (Referee 2026-05-24/25 closes)

- No `rcept_dt` treated as effective status date without a separate effective-date
  linkage audit (2026-05-24).
- No `effective_date` inferred from `rcept_dt` fallback (2026-05-25; reinforced by
  KR-EXECUTABLE-EFFECTIVE-DATE-LINKAGE-A0 close).

## Hard prohibitions (continuing under measurement-layer A0 close)

- No return backtest / NAV / CAGR / Sharpe / hit rate / alpha / excess return / MDD
- No post-event drift / migration / turnover / resume / reversal / flow-return
- No raw return as signal/outcome / raw jump alpha / price-only mean reversion
- No generic value / quality / momentum / RS ranking
- No Round 2 strategy restart
- No flow strategy testing
- No DART body alpha test / overhang alpha/filter test
- No executable assumption from panel presence
- No survivorship-safe claim without official listed universe
- No use of ALLOW_WITH_GUARD fields without documented guard
- No use of invalid OHLCV rows without quarantine
- No production / paper / P08 / live readiness / shadow connection
- No parser result described as strategy-ready
- No card may be described as strategy-ready
- No D3c full implementation
- No C2/C3 integration (only design allowed)
- No unified all-event event log finalization

## Cycle 1 Final State (2026-05-23)

| Round | Outcome |
|---|---|
| Round 1 | TEST 0 / BACKLOG 6 |
| Round 2 | TEST 0 / BACKLOG 5 + 1 infra (Option D) |
| Round 3 | 5 A0 AUDIT complete, 34 defects |
| Round 4 | Source acquisition (S1/S3/S4/S6) + W001 v2 (5/7 components) |
| Round 4 Partial Re-A0 | 5/5 PARTIAL PASS, 23/34 CLOSED |
| Round 4.1 | Residual closure sprint, 25/34 CLOSED, S2 entry criteria met |
| Round 5 | S2 OPENDART body parser phase — D1 dry run / D2 schema mapping / D3 v1+v2+v3 / Triage / **CLOSED AS PARTIAL** |
| Round 6 | C2-C3-DESIGN-FINALIZATION (9 design-only outputs, **CLOSED**) → Measurement-layer A0 initial pass (P0-1/P0-2/P1 + P2 backlog registers, **CLOSED AS PARTIAL / DEFECT-FOUND**) → KR-OHLCV-QUARANTINE-ENFORCEMENT-A0 (8 outputs, **CLOSED AS DEFECT-FOUND** — 143 defects recorded; no patches applied) → KR-OHLCV-QUARANTINE-PATCH-PHASE (9 outputs + guard module + 19 tests + 6 patched files, **CLOSED AS PATCHED-PARTIAL / RESIDUAL BLOCKERS PRESERVED** — 45 residual blockers; runtime propagation not verified) → KR-OHLCV-RUNTIME-MASK-PROPAGATION-A0 (9 outputs, **CLOSED AS RUNTIME-VERIFIED FOR TESTED PATHS / RESIDUAL BLOCKERS PRESERVED** — 10/10 synthetic + 11,425 real invalid rows detected; backtest/universe gates verified active) → KR-OHLCV-RESIDUAL-BLOCKER-PATCH-PHASE (9 outputs + helper + 3 tests + 6 closed-strategy entry patches, **CLOSED AS RESIDUAL-BLOCKERS-REDUCED / OPS BLOCKERS PRESERVED** — 40 patched / 4 still_reopen_blocker / 1 false_positive; 6/6 smoke pass) → KR-KRX-CALENDAR-SOURCE-ACQUISITION-A0 (11 outputs + composite calendar, **CLOSED AS CALENDAR-SOURCE-RECONCILED / EXECUTION STILL CLOSED** — 4,034 dates 2010-2026; 4,021/4,021 t+1 match; 12 vendor-cutoff anomalies) → KR-LISTED-UNIVERSE-COVERAGE-A0 (12 outputs + monthly KRX universe, **CLOSED AS LISTED-UNIVERSE-SOURCE-ACQUIRED / PARTIAL LIFECYCLE / NOT SURVIVORSHIP-SAFE** — 3,653 official tickers vs 925 panel = 25.3% coverage; 2,728 official-only; 519 disappeared no-terminal) → KR-EXECUTABLE-STATUS-COVERAGE-A0 (12 outputs, **CLOSED AS EXECUTABLE-STATUS-SOURCE-ACQUIRED / PARTIAL COVERAGE / EXECUTION STILL CLOSED** — S3 KRX status events; 10,774 events / 1,855 tickers / 2018+ only; intraday halt + limit-lock + pre-2018 missing) → KR-EXECUTABLE-STATUS-LIMIT-LOCK-SOURCE-A0 (12 outputs, **CLOSED AS LIMIT-LOCK-PROXY-RECONCILED / PARTIAL COVERAGE / EXECUTION STILL CLOSED** — rule-derived 336 candidates; W001 v2 41 rows under-counted; conservative execution rule design; 9 defects) → KR-EXECUTABLE-STATUS-PRE2018-EXTENSION-A0 (12 outputs, **CLOSED AS PRE2018-STATUS-SOURCE-ACQUIRED / RECONCILED / EXECUTION STILL CLOSED** — OPENDART 2010-2017 acquired; 300,829 raw / 7,150 filtered events; pre_2018_status_coverage_gap closed) → KR-EXECUTABLE-EFFECTIVE-DATE-LINKAGE-A0 (12 outputs, **CLOSED AS EFFECTIVE-DATE-LINKAGE-AUDITED / PARTIAL / NOT GENERALIZABLE / EXECUTION STILL CLOSED** — 113 samples / 1.8% extraction rate; HTML-inline + S2 PARTIAL = core blocker) → KR-STATUS-EFFECTIVE-DATE-MANUAL-AUDIT-PHASE (12 outputs + build script + 195-ZIP cache, **CLOSED AS MANUAL-AUDIT-COMPLETED / SUPPORTS HTML-INLINE PARSER REOPEN / EXECUTION STILL CLOSED** — 195 samples / 56.4% extraction = 31× lift; bs4 HTML-inline; suspension 92.5% + resumption 90.2% parser-feasible; gate `MANUAL_AUDIT_SUPPORTS_PARSER_REOPEN`) → S2-HTML-INLINE-PARSER-REOPEN-PHASE (12 outputs + parser module + 26/26 tests + validator, **CLOSED AS HTML-INLINE-PARSER-VALIDATED FOR SUSPENSION / RESUMPTION ONLY / EXECUTION STILL CLOSED** — 108 in-scope samples / 90.7% overall exact-match / suspension 92.5% / resumption 87.8% / 0 negative-control FPs / 14 defects; gate `HTML_INLINE_PARSER_VALIDATED_FOR_SUSPENSION_RESUMPTION_ONLY`) → KR-STATUS-CORRECTION-LINKAGE-A0 (3-pass evidence: Pass 1 3d09033 + Pass 2 565f0d3 + Pass 3 2f890d7; 12 outputs each + CLOSE_NOTE.md + 3 audit scripts, **CLOSED AS CORRECTION-LINKAGE VALIDATED FOR SAMPLE / HIGH_VALIDATED ONLY / EXECUTION STILL CLOSED** — Pass-3 body-confirmation gate + 5-tier confidence enum; 72-row sample 78.1% link rate; 35 high_validated universe; 10 wrong-candidate quarantined; 0 residual FP in linked pool; 9 supersession_ready design-only; gate `READY_FOR_NEXT_A0_REVIEW`) → S2-HTML-INLINE-PARSER-FULL-UNIVERSE-VALIDATION-A0 (Pass 1 20fbdf6 + Pass 2 38acaf9; 12 outputs each + CLOSE_NOTE.md + parser 1.1.0 + 34/34 tests + validation scripts, **CLOSED AS FULL-UNIVERSE-PARSER-VALIDATED FOR SUSPENSION / RESUMPTION ONLY / AVAILABLE-BODY SCOPE / EXECUTION STILL CLOSED** — 12,187 in-scope parsed / 1,402 bodies cached after 400 prefetch / 1,331 extracted / 0 negative-control FP / 5,737 / period_change parser fix 95% fix rate / 180-row holdout 99.4% / 1 wrong_date / correction policy unchanged) → S2-HTML-INLINE-PARSER-BODY-COVERAGE-EXPANSION-A0 (commit 1d8a67f; 12 outputs + CLOSE_NOTE.md + acquisition script, **CLOSED AS BODY-COVERAGE-EXPANDED AND VALIDATED FOR AVAILABLE ROWS / INCOMPLETE COVERAGE / EXECUTION STILL CLOSED** — 10,744 target / 5,000 attempts / 4,996 success (99.92%) / 4,526 new extractions / 46.5% target coverage shift / universe body coverage 11.5%→52.5% / 84-row holdout 100% / 0 FP / 0 wrong / 0 regression / 5,744 body_unavailable preserved) → S2-HTML-INLINE-PARSER-BODY-COVERAGE-COMPLETION-A0 (commit b3a971d; 13 outputs + CLOSE_NOTE.md + completion script, **CLOSED AS BODY-COVERAGE COMPLETED FOR TARGET SET / RESIDUAL SOURCE DEFECTS PRESERVED / EXECUTION STILL CLOSED** — 5,744 remaining target / 162 already cached / 5,582 attempts / 5,579 success (99.95%) / 5,577 new extractions / target body_unavailable 5,744→0 / universe body coverage 52.5%→~98.3% / 88-row holdout 100% / 3 zip_unparseable defects / 0 not_attempted_due_to_budget) → S2-HTML-INLINE-PARSER-UNIVERSE-RESIDUAL-RECONCILIATION-A0 (commit 6510f5a, **first phase run via Codex↔Claude relay**; 8+2 outputs + CLOSE_NOTE.md + reconciliation script, **CLOSED AS UNIVERSE RESIDUALS RECONCILED / ZIP-UNPARSEABLE RESIDUALS PRESERVED / EXECUTION STILL CLOSED** — exact reconcile of 12,187 universe: usable html_inline 12,145 = 99.66% NOT 100% / residual 42 all zip_unparseable / 0 missing/structured/attachment / corrects prior ~210 estimate / target-set 162+5,579+3=5,744 confirmed) |

## Git Status

- Remote: `https://github.com/figjifg/quant.git` (public)
- Main: latest = S2 final A0 close commit (verifiable via `git log`)
- `.env`: secrets gitignored, defense-in-depth patterns added
- Push: ASKPASS pattern via `research_input_data/.env` `GITHUB_PASSWORD`

## 룰

- 사용자 명시 결정 없이 여기 항목 추가 X
- 완료되면 제거 또는 closed 로 이동
- "future plan" / "should do" / "next phase" 류 표현은 다른 파일에서도 제거
- S2 phase 종료 후 새 phase 진입 = Referee 별도 verdict 필요
