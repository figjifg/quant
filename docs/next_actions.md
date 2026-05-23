# Next Actions

이 프로젝트에서 "다음에 해야 할 것" 은 **오직 이 파일에서만** 적는다. 다른 가이드
파일은 현재 상태 / 정책 / 결과만 기록한다. 새 세션이 다른 파일을 읽다가 "next
phase = X 해라" 같은 문구에 끌려서 자동으로 그 방향으로 행동하는 lock-in 회피.

비어 있는 것이 정상이다. 사용자가 명시적으로 결정한 active 작업만 여기 적는다.

## Active — KR-OHLCV-QUARANTINE-ENFORCEMENT-A0 (Referee verdict 2026-05-23)

**Scope**: Measurement-layer A0 only. Verify invalid OHLCV rows are excluded or
explicitly guarded in all downstream code paths. **Audit-only — no patches** (separate
Referee approval required for any patch phase; documentation-only clarification allowed).

**Reason**: P1 finding (58,649 OHLC ordering violations + 53,556 nonpos rows, all
matching OHL=0 / `close>0` vendor non-trading-row signature). Referee lock requires
quarantine; before any future diagnostic can safely use OHLCV, enforcement must be
audited.

**6 allowed task groups**:
1. Build invalid-row contract (signatures: OHL=0/close>0, nonpos, ordering, neg volume,
   neg trading value, missing adjusted) — separate vendor non-trading-row convention
   from true missing data; no suspension/halt inference.
2. Scan downstream code paths (src/, research/, backtest/, scripts/, reports build
   scripts) for raw + adjusted OHLCV / volume / trading value / Change / tradable_state
   / dynamic universe reads.
3. Verify quarantine enforcement (exclude / mask / explicit flag before downstream use)
   — signal construction / event ledger / execution sim / t+1 mapping / tradability
   logic / universe construction / future diagnostic. Audit-only — no perf diagnostic.
4. Field guard audit (cross-check ALLOW_WITH_GUARD fields from P0-1; if used without
   guard, record defect).
5. Defect classification (PASS / GUARDED / MISSING_GUARD / INVALID_ROW_LEAK /
   AMBIGUOUS / NOT_APPLICABLE) — record defects first, no silent fixes.
6. Patch recommendation only (documentation; no implementation unless Referee approves
   a separate patch phase).

**Required outputs (8)**:
- `quarantine_enforcement_referee_lock.md`
- `invalid_ohlcv_row_contract.md`
- `downstream_ohlcv_usage_inventory.csv`
- `allow_with_guard_usage_audit.csv`
- `quarantine_enforcement_summary.md`
- `invalid_row_leak_defect_ledger.csv`
- `required_patch_register.md`
- `downstream_blockers_after_quarantine_a0.md`

**Pass criteria**:
- All downstream OHLCV consumers inventoried.
- Invalid-row signatures explicitly defined.
- Every invalid-row use is guarded / blocked / recorded as a defect.
- Every ALLOW_WITH_GUARD use has documented guard or a defect.
- No invalid OHLCV row silently treated as a valid price observation.
- No invalid OHLCV row interpreted as halt/suspension evidence without official source.
- No performance metric generated.

**Kill / fail gates**:
- Any downstream path uses invalid OHLCV without guard.
- Any code treats OHL=0/close>0 rows as valid price observations.
- Any code infers halt/suspension/executable status from invalid OHLCV alone.
- Any ALLOW_WITH_GUARD field used without documented guard.
- Any return / alpha / NAV / Sharpe / CAGR / MDD / strategy metric produced.
- Any strategy testing started.

**Output 경로**: `reports/experiments/measurement_A0/KR_OHLCV_QUARANTINE_ENFORCEMENT_A0/`

## Closed / Frozen (변경 시 사용자 결정 필요)

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
| Round 6 | C2-C3-DESIGN-FINALIZATION (9 design-only outputs, **CLOSED**) → Measurement-layer A0 initial pass (P0-1/P0-2/P1 + P2 backlog registers, **CLOSED AS PARTIAL / DEFECT-FOUND**) |

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
