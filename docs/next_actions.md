# Next Actions

이 프로젝트에서 "다음에 해야 할 것" 은 **오직 이 파일에서만** 적는다. 다른 가이드
파일은 현재 상태 / 정책 / 결과만 기록한다. 새 세션이 다른 파일을 읽다가 "next
phase = X 해라" 같은 문구에 끌려서 자동으로 그 방향으로 행동하는 lock-in 회피.

비어 있는 것이 정상이다. 사용자가 명시적으로 결정한 active 작업만 여기 적는다.

## Active

### BX01-KOSPI200-INCLUSION-RUNUP-DIAGNOSTIC-BACKTEST-DESIGN-A0 (opened 2026-05-31; initial pass 2026-05-31)

- **Phase pre-reg + addendum:** `reports/experiments/BX01_KOSPI200_index_event_source_A0/inclusion_runup_diagnostic_backtest_design_a0.md` (design spec) + `inclusion_runup_diagnostic_design_initial_pass.md` (initial pass report).
- **Decision channel:** user → claude-session AskUserQuestion "F — Narrow diagnostic backtest design" → Referee `ask_0015.md` / `ask_claude_52.md`. Procedural guard `ask_claude_53` for codex_claude_referee_relay.py pre-existing dirty file accepted.
- **Status: INITIAL PASS PRODUCED but NOT_CLOSE_READY_SCOPE_BREACH per Referee gate verdict 2026-05-31 (push #2 violated `ask_0015.md` no-push lock).**
- **Diagnostic LOCAL-ONLY DESIGN.** NOT approval to run backtest. Execution phase REMAINS CLOSED and requires a SEPARATE user + Referee decision.
- **Initial design package exists at commit `88e7f94`** (pushed to origin/main as part of the scope breach; design substance is intact).
- **Forward-only correction commit `d5ee3be` exists locally** (per `ask_claude_55`) and is **NOT pushed**. It adds the §9 addendum to the initial-pass report, the §14 addendum to the design spec, and earlier updates to this Active entry. No history rewrite (no amend / revert / reset / force-push).
- **A second narrow follow-up correction is being requested per `ask_claude_56`** to remove a stale §7 contradiction in the initial-pass report (§7 still recommended `DESIGN_READY_FOR_SEPARATE_DIAGNOSTIC_EXECUTION_DECISION` and falsely claimed "NOT `NOT_CLOSE_READY_SCOPE_BREACH` — verified §5", contradicting the corrected §5 push row and §9 addendum). The follow-up correction commit is also forward-only and NOT to be pushed per `ask_claude_56`.
- **Sample (realised matches pre-estimate exactly):** 65 main inclusion-addition events (5 Class A direct primary 2021-06 + 54 Class B snapshot-diff derived + 6 Class B title-linked secondary). 68 negative-control deletion candidates. 87 excluded with reason. 65 + 68 + 87 = 220 (preserve-all check).
- **NO returns / run-up / edge / Sharpe / hit-rate / strategy metric computed.** No price columns read. events_v3.csv UNCHANGED.
- **Current Referee gate: `NOT_CLOSE_READY_SCOPE_BREACH`.** Close is blocked because push occurred despite the explicit no-push lock and stale "close-ready" wording must be eliminated before any re-verdict.
- **Execution phase remains CLOSED** and requires a separate user + Referee decision regardless of any future re-verdict on the design phase.
- **Next:** Bridge follow-up correction report to Referee for re-review.

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

### BX01-KOSPI200-SPECIALS-TITLE-ENRICHMENT-A0 — CLOSED AS BACKLOG_TITLE_ENRICHMENT_PARTIAL_SECONDARY_LINKS / 6 OF 6 SCOPED SPECIAL ADDITIONS TITLE-LINKED AS SECONDARY-TRIANGULATED CANDIDATES / ADDITION-SIDE CLASS B CONFLATION PARTIALLY SEPARATED FOR 2021-12 2022-06 2024-06 / DELETIONS-REPLACEMENTS REMAIN UNRESOLVED / EVENTS_V3 UNCHANGED / NO PRIMARY PARSE OR BACKTEST OPENED (2026-05-31, via bridge, autonomous mode)

Referee directive `ask_claude_09.md` (formal gate verdict + close-housekeeping
after `ask_claude_08.md` resume / context-rebuild restatement of phase opened
by `ask_claude_07.md`; autonomous mode per user 2026-05-31 authorization).
**Referee 최종 verdict = BACKLOG_TITLE_ENRICHMENT_PARTIAL_SECONDARY_LINKS**
(via bridge 2026-05-31). Select A close + preserve D.

- Status: **CLOSED AS BACKLOG_TITLE_ENRICHMENT_PARTIAL_SECONDARY_LINKS**.
- 사전등록 + 보고서 `reports/experiments/BX01_KOSPI200_index_event_source_A0/
  specials_title_enrichment_initial_pass.md` (256 lines) + close note
  `reports/experiments/BX01_KOSPI200_index_event_source_A0/
  specials_title_enrichment_close_note.md` (이 phase).
- 산출 `data/acquired/bx01_kospi200_specials_title_enrichment_a0/`
  (title_enrichment_targets.csv 7 rows × 6 cols [6 scoped + 1 ESG sub-index
  caveat] + title_name_extractions.csv 6 × 5 + listing_name_crosscheck.csv
  6 × 8 + special_candidate_links.csv 6 × 9 +
  conflation_reconciliation_title_enriched.csv 3 × 6).
- 커밋 lineage: `065848e` (initial pass; accepted) → close-housekeeping
  commit (이 커밋).
- **Scope verified:** 6/6 main-index special notices = bbsSeq
  758/759/773/789/907/921 across affected Class B cycles 2021-12 / 2022-06 /
  2024-06. bbsSeq 1020 = out-of-scope ESG sub-index caveat only.
- **Title extraction:** deterministic regex; 5 `new_listing` matches
  (`^(.+?)\s*신규상장에\s*따른` → 758/759/773/789/907) + 1
  `transfer_listing` match (`^(.+?)\s*이전상장에\s*따른` → 921); all
  extraction_confidence=high.
- **Listing cross-check (LOCAL ONLY):** KOSPI 200 snapshot exact-name match
  (post-effective constituent); 6/6 matched at `high_secondary_triangulated`:
  카카오뱅크 323410 / 크래프톤 259960 / 카카오페이 377300 / LG에너지솔루션
  373220 / 에코프로머티 450080 / 포스코DX 022100.
- **Candidate links (6/6, secondary-triangulated only):**
  758→`BX01-DIFF-774-0006` (2021-12, 323410) /
  759→`BX01-DIFF-774-0005` (2021-12, 259960) /
  773→`BX01-DIFF-774-0009` (2021-12, 377300) /
  789→`BX01-DIFF-799-0026` (2022-06, 373220) /
  907→`BX01-DIFF-939-0070` (2024-06, 450080) /
  921→`BX01-DIFF-939-0067` (2024-06, 022100).
  Every link tagged side=`addition_candidate_title_derived`,
  source_basis=`title_name_extraction + kospi200_snapshot_exact_name`,
  confidence=`high_secondary_triangulated`. No link is primary, authoritative,
  validated, approved, executable, strategy-ready, production-ready, or
  paper-ready.
- **Reconciliation per cycle (addition side):** 2021-12 3/3 linked; 2022-06
  1/1 linked; 2024-06 2/2 linked. All three cycles tagged
  `ALL_ADDITIONS_LINKED__deletions_replacements_may_remain_unresolved`.
  Deletion / replacement side UNRESOLVED for all three cycles.
- **events_v3.csv UNCHANGED** (220 rows; 133 effective_dt_rulebook_derived;
  6 residual blockers — unchanged from rulebook-A0 + attachment-parse-A0
  carry-forward). NO events_v4.csv produced. Candidate-link CSV references
  v3 rows; nothing reclassified, deleted, or overwritten.
- **하드룰 유지 (Referee 직접 인용):** title-derived evidence is secondary and
  triangulated only; may help explain conflation but MUST NOT be used as
  primary parse; MUST NOT rewrite events_v3.csv into an authoritative
  recovered table; does NOT authorize any downstream modeling or execution.
  No primary parse / authoritative / validated / approved / executable /
  strategy-ready / production-ready / paper-ready claim on any row. No
  external network, no API, no download, no source recovery, no HWP / broker
  PDF / OCR / binary doc parser, no rulebook re-acquisition, no calendar
  extension, no 2026-06 fill, no convention/news/memory/rebalance fill, no
  Bull/Bear / P08 ops / measurement-layer / DART/parser / closed-family
  reopening, no MSCI/FTSE/KOSDAQ150/BX02-04 expansion,
  research_input_data/ unchanged, data/raw/ unchanged, no push, no
  self-close beyond this verdict, no next phase opened.
- **Referee verdict 근거 (수락):** all 6 directive-scoped special additions
  title-linked at `high_secondary_triangulated`; addition-side of 3 affected
  Class B cycles partially separated via secondary/triangulated evidence;
  deletion / replacement side UNRESOLVED for all 3 cycles (cannot be inferred
  from title alone); events_v3.csv unchanged; no events_v4.csv produced;
  research_input_data/ + data/raw/ unchanged; bbsSeq 1020 ESG sub-index
  out-of-scope caveat preserved; `git status --short` clean;
  `git show --check HEAD` clean. Material secondary progress (NOT
  FAIL_CLOSED). NOT a backtest gate / NOT a design PASS.
- **명시적 금지 (Referee, 별도 승인 없이는):** Resolving the deletion /
  replacement side requires a separate future user + Referee decision,
  likely involving a primary-source parse path such as HWP parser, broker
  PDF parse, or user-supplied attachment review. None of these are opened
  by this close.

### BX01-KOSPI200-TIER2-TIER3-SPECIALS-PARSE-A0 — CLOSED AS BACKLOG_TIER2_TIER3_STRUCTURED_SOURCE_GAP / 55 TIER 2-3 SPECIAL-SUPPLEMENTAL CATALOGUE ROWS VERIFIED / 0 OF 55 PARSEABLE IN STRUCTURED-SOURCE SCOPE / 16 HWP + 1 PDF + 38 NO-ATTACH + 0 XLSX-CSV-HTML / 3 OF 9 MAIN-INDEX CLASS B CYCLES REMAIN CONFLATED / 2025-12 ESG SUB-INDEX CAVEAT PRESERVED / NO HWP-PDF PARSING / NO EVENT CONSOLIDATION CHANGE / NO BACKTEST OR STRATEGY OPENED (2026-05-31, via bridge, autonomous mode)

Referee directive `ask_claude_06.md` (option C from rulebook-A0 close options;
autonomous mode per user 2026-05-31 authorization "외부 네트워크 허용 + 자율
모드"). Three Referee-required cleanup rounds (initial pass + ESG sub-index
scope fix + 2 stale-text passes). **Referee 최종 verdict =
BACKLOG_TIER2_TIER3_STRUCTURED_SOURCE_GAP** (via bridge 2026-05-31).

- Status: **CLOSED AS BACKLOG_TIER2_TIER3_STRUCTURED_SOURCE_GAP**.
- 사전등록 + 보고서 `reports/experiments/BX01_KOSPI200_index_event_source_A0/
  tier2_tier3_specials_parse_initial_pass.md`; 산출 `data/acquired/
  bx01_kospi200_tier2_tier3_specials_parse_a0/` (target_list.csv 55 rows 12-col
  w/ scope_flag + attempt_log.csv 220 rows + manifest.csv 10-col provenance +
  coverage_matrix.csv 55 rows + conflation_reconciliation.csv 9 rows +
  attempt_log/ OTP step1/step2 evidence; .gitattributes whitespace-exempt).
- 커밋 lineage: `f196280` (initial pass) → `64ed2f7` (ESG sub-index scope fix:
  bbsSeq=1020 out-of-scope) → `e8019ab` (stale-text §9) → `76fa552` (outputs-
  block §6 stale text) → close-housekeeping commit (이 커밋).
- **Catalogue target count VERIFIED: 55** (notice_index.json ∩ events_v3.csv =
  55 EXACT match; no halt). 54 in-scope main-index specials + 1 sub-index
  variant (bbsSeq=1020 KOSPI 200 ESG 수시변경 = out-of-scope per Referee
  2026-05-31 cleanup).
- **Format distribution (decisive):** **0/55 parseable in directive scope.**
  16 hwp + 1 pdf + 38 no-attach + 0 xlsx/csv/HTML-table. Per directive
  ("Parse clearly structured sources only: xlsx, csv, HTML tables"),
  parseable count = 0 regardless of network access.
- **Network probes (single sample bbsSeq=159):** OTP 2-step HTTP 200 +
  Content-Length: 0 (same blocker as BX01-source-A0 + missing-tier1-A0;
  route stopped) / direct static data.krx 404 + kind.krx 405 / Wayback
  empty. 220 attempt rows logged (55 × 4 classes).
- **Conflation reconciliation per Class B cycle (post-cleanup):** 3 of 9
  main-index cycles UNRESOLVED (2021-12: KraftON/KakaoBank/KakaoPay; 2022-06:
  LG에솔; 2024-06: 에코프로머티/포스코DX). 6 of 9 main-index clean (5 already
  clean: 2023-06/2023-12/2024-12/2025-06/2026-06; 1 with sub-index caveat:
  2025-12 has bbsSeq=1020 ESG sub-index out-of-scope). 48 of 55 specials
  fall pre-2021-06 (before Class B parsing started). Catalogue 55 vs main-
  index unresolved 6 specials × 3 cycles distinction explicit.
- **events_v3.csv UNCHANGED** (220 rows; 133 effective_dt_rulebook_derived
  filled; 6 residual blockers from rulebook-A0 carry-forward). NO
  events_v4.csv produced. NO tier2_tier3_candidate_events.csv produced.
- **하드룰 유지:** no HWP parser invoked / no broker PDF constituent parse /
  no 4-missing-Tier1 hwp-pdf parse / no rulebook re-acquisition / no calendar
  extension / no 2026-06 fill / no convention/news/memory/rebalance fill /
  no backtest/return/edge/strategy/P08/production/paper-live/execution / no
  Bull-Bear / no measurement-layer reopening / no parser reopening / no
  closed-family reopening / no MSCI/FTSE/KOSDAQ150/BX02-04 expansion / no
  row strategy-ready/executable/approved/production-ready/paper-ready /
  research_input_data/ unchanged / no push / no self-close.
- **Referee verdict 근거 (수락):** 55-row catalogue verified exact match;
  decisive format finding (0 xlsx in scope) shows the gap is source-format
  + persistent environmental blocker, not source-legal; main-index Class B
  conflation explicitly mapped (3/9 unresolved); bbsSeq=1020 ESG sub-index
  properly out-of-scope with caveat preserved. NOT FAIL_CLOSED (decomposable
  format-gap + named follow-on candidates); NOT a backtest gate.
- **다음 phase (Referee 발행 대기 — autonomous mode):** Referee recommends
  `BX01-KOSPI200-SPECIALS-TITLE-ENRICHMENT-A0` first — narrow local-only
  title-based + listing-name cross-check enrichment to PARTIALLY address the
  3 unresolved main-index Class B cycles WITHOUT opening HWP parser
  infrastructure or broker-PDF extraction. Will be labeled
  secondary/triangulated. Formal directive to come after close-housekeeping
  acceptance.

### BX01-KOSPI200-MISSING-TIER1-XLSX-ACQUIRE-A0 — CLOSED AS BACKLOG_MISSING_TIER1_STRUCTURED_SOURCE_GAP / 0 OF 4 MISSING TIER 1 STRUCTURED XLSX SOURCES ACQUIRED / PUBLIC NETWORK PATHS DOCUMENTED BUT BLOCKED OR EMPTY / USER-SUPPLIED HWP AND BROKER PDF FILES INVENTORIED BUT DEFERRED / NO HWP OR PDF PARSING / NO EVENT CONSOLIDATION CHANGE / NO BACKTEST OR STRATEGY OPENED (2026-05-31, via bridge, autonomous mode)

사용자 결정(2026-05-31, claude-session) "외부 네트워크 허용 + 자율 모드"로 BX01-rulebook
close 직후 Referee가 옵션 E를 first phase로 선택 → directive `ask_0010.md`. Two
Referee-required cleanup rounds (manifest 컬럼 / attempt-log+report consistency /
detail HTML 설명; 그 뒤 작은 stale-text). **Referee 최종 verdict =
BACKLOG_MISSING_TIER1_STRUCTURED_SOURCE_GAP** (via bridge 2026-05-31).

- Status: **CLOSED AS BACKLOG_MISSING_TIER1_STRUCTURED_SOURCE_GAP**.
- 사전등록 + 보고서 `reports/experiments/BX01_KOSPI200_index_event_source_A0/
  missing_tier1_xlsx_acquire_initial_pass.md`; 산출 `data/acquired/
  bx01_kospi200_missing_tier1_xlsx_acquire_a0/` (manifest.csv 10-col provenance
  schema + attempt_log.csv 40 rows + coverage_matrix.csv + raw/ 4 detail HTML +
  attempt_log/ OTP step1/step2 evidence; .gitattributes whitespace-exempt).
- 커밋 lineage: `0f78899` (initial pass) → `90ddd54` (3 Referee cleanups:
  manifest cols / attempt-log consistency / detail HTML 설명) → `e5db607`
  (tiny stale-text cleanup §3) → close-housekeeping commit (이 커밋).
- **시도 (28 + 12 = 40 attempt rows logged):** OTP 2-step (bbsSeq=555 단일 probe;
  HTTP 200 + Content-Length: 0 → 차단 동일; 추가 retry X) / Direct static
  data.krx.co.kr / kind.krx.co.kr / open.krx.co.kr / global.krx.co.kr (모두
  404/405) / Wayback Machine (no snapshots) / FinanceDataReader SnapDataReader
  (동일 OTP 차단) / Wikipedia ko (no 정기변경 history section) / namuwiki (403) /
  Korean news/broker mirror search (recent 2023+ only).
- **0/4 structured xlsx 획득.** events_v3.csv 변동 없음 (220 rows; 133
  effective_dt_rulebook_derived; 6 residual blockers — unchanged from
  rulebook-A0 close).
- **사용자 supplied 파일 inventory:** 18.6.hwp / 19.6.hwp (KRX hwp 보도자료) +
  20.6.pdf / 20.12.pdf (broker pdf) → 모두 DEFERRED per directive (no hwp parse,
  no broker pdf constituent parse this phase).
- **하드룰 유지 (Referee 직접 인용):** no HWP parsing, no broker PDF constituent
  parsing, no Tier 2/3 parse, no event consolidation change, no backtest, no
  strategy, no P08, no production/paper-live/execution; no OTP bypass / login /
  anti-bot; no closed-family / measurement-layer / parser reopening; no push;
  not FAIL_CLOSED; not a backtest gate; research_input_data/ unchanged.
- **다음 phase (Referee 발행 대기):** Referee가 `BX01-KOSPI200-TIER2-TIER3-
  SPECIALS-PARSE-A0` directive 발행할 것이라고 명시 — close housekeeping
  완료 후 별도 directive로.

### BX01-KOSPI200-RULEBOOK-EFFECTIVE-DT-A0 — CLOSED AS BACKLOG_EFFECTIVE_DT_PARTIAL_SECONDARY_BASIS / 9 OF 10 RULEBOOK-SCOPED TIER 1 CYCLES FILLED IN effective_dt_rulebook_derived UNDER PROVISIONAL SECONDARY BASIS / CANONICAL effective_dt REMAINS BLANK / 2026-06 CALENDAR CUTOFF PRESERVED / PRIMARY KRX RULEBOOK AND DERIVATIVES SPEC ACCESS BLOCKED / 6 RESIDUAL BLOCKERS PRESERVED / NO BACKTEST OR STRATEGY OPENED (2026-05-31, via bridge)

사용자 결정(2026-05-31)으로 BX01-attachment-parse-A0 close 직후 옵션 C (Rulebook-A0,
effective_dt 채움) 채택. Phase 발행 = Referee `ask_0009.md` / `ask_claude_05.md`. 두
halt+escalate (primary KRX 접근 차단 + futures-LTD basis) 모두 Referee 2026-05-31
hybrid (c) framework 으로 해결: secondary KRX-publisher-attributed + broker-hosted
KRX-attributed sources 가 strict provisional labels 와 함께 수용됨.
**Referee 최종 verdict = BACKLOG_EFFECTIVE_DT_PARTIAL_SECONDARY_BASIS** (via bridge
2026-05-31, after initial pass + 4 mandatory pre-close cleanups + final verdict).

- Status: **CLOSED AS BACKLOG_EFFECTIVE_DT_PARTIAL_SECONDARY_BASIS**. 사전등록
  source-A0 + attachment-parse-A0 + addendum `reports/experiments/BX01_KOSPI200_index_event_source_A0/rulebook_effective_dt_initial_pass.md`;
  코드 `src/audit/bx01/derive_effective_dt.py`; 산출 `data/acquired/
  bx01_kospi200_rulebook_effective_dt_a0/` (manifest.csv + per_cycle_effective_dt.csv
  + raw/ 6 artifacts ~2.2MB tracked; .gitattributes whitespace-exempted) + `data/
  acquired/bx01_kospi200_index_event_source_a0/events_v3.csv` (220 rows + 5 new
  effective_dt_* cols, preserve-all) + reconciliation_v3.csv.
- 커밋 lineage: `ab1efcd` (initial pass) → `b4571d2` (4 Referee cleanups) →
  close-housekeeping (이 커밋).
- **취득한 것 (provisional secondary basis):**
  - 9/10 Tier 1 cycles (2021-06, 2021-12, 2022-06, 2023-06, 2023-12, 2024-06,
    2024-12, 2025-06, 2025-12) 의 **`effective_dt_rulebook_derived` 컬럼** 채움.
    **canonical `effective_dt` 컬럼은 220 행 전체 BLANK 유지** (Referee 규칙:
    direct-from-attachment fill 없으면 빈 칸, 규칙/관행 fill 금지).
  - Rule basis (per row labeled): Mirae Asset Securities-hosted KOSPI200
    methodology v2 PDF §7.1 (KRX-publisher-attributed secondary) — "정기변경일 =
    KOSPI200 선물시장 6월/12월 결제월 최종거래일의 다음 매매거래일"; Hana 2020-05-25
    장내파생상품 거래설명서 p8+p15 (KRX-attributed secondary) — "각 결제월의 두
    번째 목요일"; local KRX trading calendar artifact (2010-01-04 .. 2026-05-22).
  - Reconciliation MATCH (evidence only, NOT fill basis): 2026-06 KRX press
    release for bbsSeq=1090 says effective 2026-06-12; rule predicts
    2026-06-11 Thu + 1 trading day = 2026-06-12 Fri. PERFECT match.
- **차단/보류된 것 — 6 residual blockers (3 carry-forward + 3 new):**
  1. (new) Primary KRX rulebook access — index.krx.co.kr OTP path blocked.
  2. (new) Primary KRX derivatives product spec access — same OTP path blocked.
  3. (new) 2026-06 calendar coverage cutoff at 2026-05-22 (1090 cycle effective
     unfilled).
  4. (carry) 4 Tier 1 cycles (2018-06 / 2019-06 / 2020-06 / 2020-12) skeleton
     only — hwp / broker pdf deferred.
  5. (carry) Class B regular vs intermediate-special conflation in derived rows.
  6. (carry) Tier 2 / Tier 3 specials deferred.
- **하드룰 유지:** diagnostic-only — 수익률/run-up/edge 계산 0; signals.csv/
  trades.csv/portfolio/P08/production/paper-live 0; parser/measurement-layer/
  DART body-parser/closed-family 재개 0; MSCI/FTSE/KOSDAQ150/BX02/BX03/BX04 확장
  0; Tier 2/3/hwp/broker pdf 0; KRX 캘린더 확장 0; 2026-06 press fill 0;
  convention/memory/news/rebalance fill 0; sandbox OTP retry 0; paid/licensed
  feed search 0; row 단 한 줄도 strategy-ready/executable/approved/
  production-ready/paper-ready 라벨 없음. research_input_data/정기변경/ 파일
  NEVER modified.
- **Referee verdict 근거 (수락):** 9 cycles filled은 의미 있는 진전 (0/220→133/145);
  Mirae 2021-11 §7.1 + Hana 2020-05-25 p8/p15 + local calendar 의 rule-cited
  derivation 적절; canonical effective_dt 0/220 유지 (직접 fill 없음); 2026-06
  press 일치 reconciliation 으로 preserved (fill basis 아님); .gitattributes
  whitespace-exemption narrow + manifest sha256 preserved. NOT FAIL_CLOSED
  (auditable + rule-cited + calendar-confirmed); NOT PASS_TO_DIAGNOSTIC_BACKTEST_DESIGN
  (6 residual blockers prevent).
- **명시적 금지 (Referee, 별도 승인 없이는):** Primary KRX 재취득 route, calendar
  extension, Tier 2/3 parse, hwp parser, broker pdf cross-check, missing Tier 1
  acquisition, diagnostic backtest design 모두 별도 사용자 + Referee 결정 필요.
  자동 재개 X. Push 도 별도 user 승인 필요.
- **사용자 선택지 (별도 결정 사항):** (A) Primary KRX 재취득 (user-supply
  pattern). (B) Calendar extension. (C) Tier 2/3 parse. (D) hwp parser phase.
  (E) Missing Tier 1 acquire. (F) Diagnostic backtest design (위 중 일부 해결 후).
  (G) 모두 backlog + standby.

### BX01-KOSPI200-ATTACHMENT-PARSE-A0 — CLOSED AS BACKLOG_ATTACHMENT_PARSE_GAP / TIER 1 PARTIAL CONSTITUENT PARSE COMPLETED / 2021-06 DIRECT CHANGE ROWS + SNAPSHOT-DIFF DERIVED ROWS PRESERVED WITH REGULAR-SPECIAL CONFLATION CAVEAT / LISTING XREF COMPLETED / EFFECTIVE_DATES STILL UNFILLED / NO BACKTEST OR STRATEGY OPENED (2026-05-31, via bridge)

사용자 결정(2026-05-30)으로 BX01-source-A0 closure 직후 옵션 B (사용자 직접 KRX
attachment 공급 + parse A0) 채택. 사용자가 `research_input_data/정기변경/` (read-only
protected dir) 에 17 파일 supply (11 xlsx + 4 hwp + 2 broker pdf) + 모든 파일을
date-coded form (`YY.M(M).ext`) 으로 rename → high-confidence cycle mapping. Phase
발행 = Referee `ask_0008.md` / `ask_claude_04.md`. Intake-time halt+escalate
triggered → Referee 2026-05-30 clarification extending directive with snapshot-diff
design (Class A direct + Class B diff strict conditions; Class C hwp + Class D
broker pdf deferred). **Referee 최종 verdict = BACKLOG_ATTACHMENT_PARSE_GAP** (via
bridge 2026-05-31, after 4 mandatory pre-close items executed + 2 stale-text
cleanup items).

- Status: **CLOSED AS BACKLOG_ATTACHMENT_PARSE_GAP**. 사전등록 source-A0 pre-reg +
  addendum `reports/experiments/BX01_KOSPI200_index_event_source_A0/attachment_parse_initial_pass.md`;
  코드 `src/audit/bx01/{build_coverage_matrix,parse_class_a,build_class_b_mapping_proposal,parse_class_b_with_diff,consolidate_v2,cross_check_listing_universe,rewrite_coverage_matrix_final}.py`;
  산출 `data/acquired/bx01_kospi200_index_event_source_a0/` (events_v2.csv +
  events_v2_xref.csv + events_class_a.csv + events_class_b_derived.csv +
  snapshots.csv + coverage_matrix_final.csv + reconciliation_v2.csv + manifest.csv;
  raw/ gitignored ; manifest record-of-record).
- 커밋 lineage: `daf7e10` (initial pass) → `c83bef7` (final pass: cross-check +
  matrix rewrite + report fixes) → close-housekeeping commit (this).
- **취득한 것:** 17 user-supplied 파일 cycle 매핑; Class A 직접 parse 1 cycle
  (2021-06, +5 add / -7 del); Class B consecutive snapshot-diff 9 Tier 1 cycles
  (2021-12 ~ 2026-06) + 1 bridge cycle (2022-12, not in Tier 1); v2 events =
  220행 (12 direct + 133 derived + 75 skeleton carry-forward); listing-name xref
  via PIT 조인 (138/145 = 95.2% ticker confirmed); coverage_matrix_final.csv
  (post-rename canonical mapping); coverage_matrix_prerename.csv (transparency
  preserved).
- **차단/보류된 것:** Class C 4 hwp deferred (hwp parser out-of-scope); Class D 2
  broker pdf deferred (secondary source authority, not record-of-record); 4/14
  Tier 1 cycles (2018-06, 2019-06, 2020-06, 2020-12) skeleton-only (hwp/pdf
  deferred); effective_dt 0/220 blank (Referee rule: direct-from-file only; not
  filled by rule/convention/diff/rebalance); Class B derived rows conflate
  regular review + intermediate special/supplemental events (named cases:
  2021-12 includes 크래프톤/카카오뱅크 2021-08 special + 카카오페이 2021-11
  special; 2022-06 includes LG에솔 2022-01 special; 2023-12 includes 에코프로머티
  2023-12 special; 2024-06 includes 포스코DX 2024-01 special) — preserved as
  caveat, not silently dropped.
- **하드룰 유지:** diagnostic-only — 수익률/run-up/edge 계산 0; signals.csv/trades.csv/
  portfolio/P08/production/paper-live 0; parser/measurement-layer/DART body-parser/
  closed-family 재개 0; MSCI/FTSE/KOSDAQ150 확장 0; Tier 2/3 / BX02 / BX03 / BX04
  진행 0; effective_dt rule-fill 0; row 단 한 줄도 strategy-ready/executable/approved/
  production-ready/paper-ready 라벨 없음; sandbox OTP 재시도 0; paid/licensed feed
  search 0.
- **Referee verdict 근거 (수락):** Class A direct + Class B snapshot-diff parse는
  notice-level skeleton에서 220행 보존형 산출물로 의미 있는 확장; direct vs
  derived 신뢰도 source_record_type으로 분리 유지; regular-special conflation은
  caveat로 보존 (FAIL 사유 아님); effective_dt 0/220 = 지시 정확 준수;
  Class C/D defer 적절; listing-name cross-check 완료 (95.2% ticker
  confirmation + 0 conflicts). NOT FAIL_CLOSED (parse 품질 materially 개선);
  NOT PASS_TO_DIAGNOSTIC_BACKTEST_DESIGN (effective_dt blank + 4 skeleton
  cycles + diff conflation + cross-check 후에도 미해결).
- **명시적 금지 (Referee, 별도 승인 없이는):** Tier 2/3 parse, hwp parser, broker
  pdf cross-check, rulebook-A0 for effective_dt, 4 missing Tier 1 acquisition,
  diagnostic backtest design, 모두 별도 사용자 + Referee 결정 필요. 자동 재개 X.
- **사용자 선택지 (Referee 제시; 다음 결정 사항):** (A) Tier 2/3 parse phase
  (deferred specials) — diff conflation 해결. (B) hwp parser 별도 phase — 4
  missing Tier 1 cycles 해결. (C) rulebook-A0 — effective_dt 채움. (D) 4 missing
  Tier 1 cycle 별도 acquire. (E) 모든 것 backlog + standby.

### BX01-KOSPI200-INDEX-EVENT-SOURCE-A0 — CLOSED AS BACKLOG_SOURCE_GAP / KRX NOTICE METADATA ACQUIRED / CONSTITUENT ATTACHMENTS BLOCKED BY ENVIRONMENTAL DOWNLOAD GAP / NO BACKTEST OR STRATEGY OPENED (2026-05-28, via bridge)

사용자 결정(2026-05-28)으로 연 Bull/Bear 1라운드 (4 카드: BX01 KOSPI200, BX02 MSCI Korea,
BX03 자사주매입, BX04 보호예수해제) 후 사용자가 BX01 source acquisition phase 직접
열기 결정 (Codex 채널 verbatim quote: `"bx01로 진행하자. 외부 작업은 익스큐터한테 부탁해서
진행하면 될거야. 외부 네트워크 접근도 허용할께."` + claude-session AskUserQuestion
parallel confirmation). Phase 발행은 Referee `ask_0006.md` / `ask_claude_02.md`.
**Referee 최종 verdict = BACKLOG_SOURCE_GAP** (via bridge, 2026-05-28).

- Status: **CLOSED AS BACKLOG_SOURCE_GAP**. 사전등록 `research/experiments/BX01_KOSPI200_index_event_source_A0.md`;
  코드 `src/audit/bx01/*.py`; 산출 `data/acquired/bx01_kospi200_index_event_source_a0/`
  (manifest.csv + events.csv + reconciliation.csv tracked; raw/ 디렉토리는 gitignored
  이지만 sha256 manifest 가 committed record-of-record); 보고서
  `reports/experiments/BX01_KOSPI200_index_event_source_A0/initial_pass.md`.
  커밋 lineage: `05a0b8c` (initial pass) → close housekeeping (이 커밋).
- **취득한 것:** 866-row KRX board MDCINFO005 metadata 2010-01-15..2026-05-27 (full target
  coverage); 85 KOSPI 200 main-index 구성종목 변경 notice (30 정기변경 + 55 special/특별
  변경/수시변경/특례편입); 11-field event table at NOTICE granularity (preserve-all);
  per-year reconciliation + missing-field census. PIT-anchored on KRX REG_DT.
- **차단된 것:** per-constituent add/delete 목록 (ticker, side, effective_dt)이 xlsx/hwp/
  pdf attachment에 묶여 있고, KRX 2-step OTP token download endpoint
  (`file.krx.co.kr/download.jspx`)이 sandbox network egress에서 HTTP 200 +
  Content-Length: 0으로 빈 응답을 일관되게 반환함. 다중 cookie/header/encoding 변형 +
  fresh OTP per attempt + 4 alternative endpoints + 직접 static-path probe + pykrx 모두
  동일 차단. 환경적 anti-bot/egress 차단으로 보임 — source-legal 문제 아님. NO paywall
  bypass, NO credential use, NO prohibited scraping.
- **events.csv 결손:** effective_dt 85/85 missing, ticker 85/85 missing, company_name
  71/85 missing — 모두 attachment 의존. 또한 ~10 sub-index variant row가 regular-review
  bucket에 섞여 있음 (initial_pass.md §5 caveat).
- **하드룰 유지:** diagnostic-only — 수익률/run-up/edge 계산 0; signals.csv/trades.csv/
  portfolio/P08/production/paper-live 0; parser/measurement-layer/closed-family 재개 0;
  MSCI/FTSE/KOSDAQ150 확장 0; row 단 한 줄도 strategy-ready/executable/approved/
  production-ready/paper-ready 라벨 없음.
- **Referee verdict 근거 (수락):** source 자체는 public + license-respecting, 차단은
  환경적 egress 문제이지 source-legal/methodological 문제 아님 → FAIL_CLOSED 아님.
  per-constituent table이 없고 near-miss control이 KRX notice만으로는 PIT-safe하게
  재구성 불가 → PASS_TO_DIAGNOSTIC_BACKTEST_DESIGN 불가. 따라서 BACKLOG_SOURCE_GAP.
- **명시적 금지 (Referee, 별도 승인 없이는):** attachment 재취득 retry, alternate network
  route, paid/licensed feed search, user-supplied attachment parsing, rulebook
  near-miss A0, diagnostic test 모두 별도 사용자 + Referee 결정 필요. 자동 재개 X.
- **사용자 선택지 (Referee 제시; 다음 결정 사항):** (A) attachment 재취득 경로 별도 승인 →
  constituent-level table 완성. (B) 사용자/외부 경로로 받은 KRX attachment 입력으로
  별도 parse A0 개시. (C) licensed/public equivalent feed source-discovery phase 개시.
  (D) BX01 backlog 유지 + standby.

### ATTR001 — Korean Equity Data Influence Map (diagnostic attribution sweep) — CLOSED AS CORRECTED PRESERVE-ALL DIAGNOSTIC INFLUENCE MAP / NO TRADABLE EDGE FOUND / DIAGNOSTIC-ONLY (2026-05-28, via bridge; Referee ATTR001_FINAL_SIGNOFF_OK)

사용자 결정(2026-05-28)으로 연 fresh-start attribution sweep. Executor+Referee 공동설계,
자율 실행. **Referee 최종 sign-off (ATTR001_FINAL_SIGNOFF_OK)** = 보정된 preserve-all
diagnostic 영향력 지도로 승인.

- Status: **CLOSED**. 사전등록 `research/experiments/ATTR001_korean_data_influence_map.md`;
  코드 `src/audit/attribution/attr001_*.py`; 산출+보강+`FINDINGS_corrected.md` under
  `reports/experiments/ATTR001_korean_data_influence_map/`. 커밋 lineage: 91271c5(pre-reg) →
  f3eed95(pass1) → 9248683(2a) → b66aa38(artifact fix+rerun) → c8eda16(보강).
- **핵심 결과:** 거래가능한 새 엣지 없음 — 전부 작거나(반전 5d IC ~−0.02), 알려졌거나(PEAD/
  자사주), 비용/회전 한계거나, 베타. "시장이 달라졌다"는 **포지셔닝 신호(외국인flow·대차변화
  5d)가 PRESENT에서 영향력 소멸**로 잡힘(새 양의 엣지 아님); borrow-ratio level은 현재도 음(-).
- **무결성:** dynamic-universe forward-return survivorship artifact 적발·수정(audit table);
  event matched-control이 효과 축소(실적 +1.4%→+0.36%); FDR=통계적 유의≠거래가능.
- **하드룰 유지:** diagnostic-only — 전략/P08/production/paper/live/닫힌-family 재개 아님.
  preserve-all(폐기 0, data_gated 포함). 후속 전략화는 별도 사용자 결정(Bull/Bear 경유). No
  next phase opened.

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
