# Next Actions

이 프로젝트에서 "다음에 해야 할 것" 은 **오직 이 파일에서만** 적는다. 다른 가이드
파일은 현재 상태 / 정책 / 결과만 기록한다. 새 세션이 다른 파일을 읽다가 "next
phase = X 해라" 같은 문구에 끌려서 자동으로 그 방향으로 행동하는 lock-in 회피.

비어 있는 것이 정상이다. 사용자가 명시적으로 결정한 active 작업만 여기 적는다.

## Active

_없음_. 2026-05-24 Referee verdict 로 KR-OHLCV-RUNTIME-MASK-PROPAGATION-A0 종료
(CLOSED AS RUNTIME-VERIFIED FOR TESTED PATHS / RESIDUAL BLOCKERS PRESERVED). 다음
phase 진입은 사용자/Referee 의 별도 명시적 결정 필요.

## Closed / Frozen (변경 시 사용자 결정 필요)

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
| Round 6 | C2-C3-DESIGN-FINALIZATION (9 design-only outputs, **CLOSED**) → Measurement-layer A0 initial pass (P0-1/P0-2/P1 + P2 backlog registers, **CLOSED AS PARTIAL / DEFECT-FOUND**) → KR-OHLCV-QUARANTINE-ENFORCEMENT-A0 (8 outputs, **CLOSED AS DEFECT-FOUND** — 143 defects recorded; no patches applied) → KR-OHLCV-QUARANTINE-PATCH-PHASE (9 outputs + guard module + 19 tests + 6 patched files, **CLOSED AS PATCHED-PARTIAL / RESIDUAL BLOCKERS PRESERVED** — 45 residual blockers; runtime propagation not verified) → KR-OHLCV-RUNTIME-MASK-PROPAGATION-A0 (9 outputs, **CLOSED AS RUNTIME-VERIFIED FOR TESTED PATHS / RESIDUAL BLOCKERS PRESERVED** — 10/10 synthetic + 11,425 real invalid rows detected; backtest/universe gates verified active) |

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
