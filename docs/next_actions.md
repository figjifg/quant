# Next Actions

이 프로젝트에서 "다음에 해야 할 것" 은 **오직 이 파일에서만** 적는다. 다른 가이드
파일은 현재 상태 / 정책 / 결과만 기록한다. 새 세션이 다른 파일을 읽다가 "next
phase = X 해라" 같은 문구에 끌려서 자동으로 그 방향으로 행동하는 lock-in 회피.

비어 있는 것이 정상이다. 사용자가 명시적으로 결정한 active 작업만 여기 적는다.

## Active (사용자 결정 진행 중)

### Cycle 1 Round 3 CLOSED + Round 4 framework 정의 완료 (2026-05-22)

**Round 3 = CLOSED**. Final verdict + 34 defects preserve + Round 4 framework
모두 정의됨.

**Round 4 = W001 v2 Infrastructure Repair + Re-A0** (NOT Bull alpha round).

Round 4 본 phase = **definition only**. 작성 완료:
- `docs/round3_final_referee_lock.md`
- `docs/round3_missing_source_register.md` (priority + S5 resolved)
- `docs/W001_v2_infrastructure_repair_plan.md` (7 components requirements)
- `docs/W001_v2_reA0_gate_spec.md` (Re-A0 trigger + pass criteria)

**Active strategy TEST = 0. Performance test authorized = 0.**

### Round 4.1 W001 v2.1 Residual Closure Sprint (2026-05-22 Referee 승인 후)

6 tasks 모두 완료, 10 required outputs 작성.

| Task | Result |
|---|---|
| 1 Tradability naming | ✅ `panel_absence` → `not_in_dynamic_universe` (code + tests) |
| 2 KRX suspension cross-ref | ✅ S3 vs pykrx volume=0 = **99.4% match** (= direct exchange equivalent) |
| 3 Flow full-year stratified | ✅ 90.7% foreign / 94.4% institution within ±5%, sign 100% |
| 4 Top100 tie-break audit | ✅ 894 mismatch records ledger (54% boundary, 46% off-boundary) |
| 5 G5 residual 35 case file | ✅ 1 strategy-relevant case (선도전기 2026-04-29) |
| 6 Permanent ID hardening | ✅ 50 fallback case ledger + 4 stability tests |

Defect closure: Round 4 23 CLOSED → Round 4.1 **25 CLOSED** (+2: TRAD_000001 + FLOW_000007-eqv).

5 카드 모두 PARTIAL PASS 유지 (No FAIL, No REGRESSION, No FULL PASS).

S2 phase entry criteria: ✅ 모두 충족 (G5 stable + tradability resolved + flow not blocking).

### Partial Re-A0 결과 (2026-05-22 Referee Option B 승인 후)

**Infrastructure Gate = PARTIAL CLOSED** (5/5 카드 PARTIAL PASS, no FAIL, no REGRESSION).

**34 defects 최종**:
- **CLOSED: 23 (67.6%)** ← Round 3 의 FAIL/OPEN/PARTIAL 중 22 → CLOSED
- PARTIAL: 10 (29.4%)
- DEFERRED-S2: 1 (G5_000005 만)
- OPEN: 0
- REGRESSION: 0

**Critical 6 중**: 3 CLOSED + 2 PARTIAL + 1 DEFERRED-S2.

5 카드 verdict (Referee 허용 범위 안):
- KR-G5-ADJOHLC-CORPACT-AUDIT-001: PARTIAL PASS WITH S2/C3 DEFERRED
- KR-ID-LIFECYCLE-MASTER-AUDIT-001: PARTIAL PASS (fallback ticker-based)
- KR-TRADABILITY-SEMANTICS-AUDIT-001: PARTIAL PASS WITH S3 SEMANTICS RESIDUAL
- KR-TOP100-PIT-LINEAGE-AUDIT-001: PARTIAL PASS (99.78/100 full-period)
- KR-FLOW-UNIT-TIMESTAMP-AUDIT-001: PARTIAL PASS FOR DATA AUDIT

Strategy TEST + Round 2 cards + Production / paper / P08 / live = **REMAINS CLOSED**.

9 required outputs 작성 완료:
- `docs/round4_partial_reA0_referee_lock.md`
- `reports/experiments/round4_partial_reA0/` (8 files)

### W001 v2 Code Components (2026-05-22, source 활용 완료)

5/7 components implemented (S1+S3+S4+S6 사용, S2 parser 별도):

| Component | 구현 | 위치 |
|---|---|---|
| **C1** adjusted OHLC integration | ✅ panel merge | `data/processed/w001_v2/panel_with_adjusted_ohlc_2018_2026.csv` (1.14M rows, 175 → 35 extreme = 80% reduction) |
| **C4** permanent_id_master | ✅ 100% coverage | `data/processed/w001_v2/permanent_id_master.csv` (DART 783 + KRX fallback 50) |
| **C5** full tradable_state | ✅ S3 wired in | `src/utils/tradability.py` (executable 14% / panel_absence 82% / true_suspension 2.84% / delisting_transition 1.18% / data_missing 0.009% / limit_lock 0.004%) |
| **C6** listing_status module | ✅ S3 events | `data/processed/w001_v2/listing_status_events.csv` (10,769 events), `listing_status_terminal.csv` (1,854 tickers) |
| **C7** flow t+1 safe wrapper | ✅ S6 reconciliation helper | `src/utils/flow_safe.py` (new module) |
| **C2** corporate action factor chain | ⏳ S2 parser 후 | (5-9주 별도 phase) |
| **C3** corporate action event log | ⏳ S2 parser 후 | (5-9주 별도 phase) |

Tests: W001 5 → 7 (2 new). Full suite **427 passed** (이전 420 + 새 7, regression 없음).

### Round 4 Source Acquisition (2026-05-22, 사용자 API key 활용 완료)

사용자 보유 API key (`.env`: KRX_ID/PW, OPENDART_API_KEY, KIS_APP_KEY 등 12 keys) 활용 → mandatory sources 4/4 + S2 verified:

| Source | Status | 결과 |
|---|---|---|
| **S1** Adjusted OHLC | ✅ COMPLETE | pykrx 833 ticker × 1.58M rows. **147 가짜 split artifact → 22 (85% 감소)**. 미래산업 79→3700 → 정상 -1.36% |
| **S3** KRX Status Events | ✅ COMPLETE | OPENDART pblntf=I, 425,294 raw / 10,774 filtered (suspension 5,466 / delisting 2,878 / resumption 1,171). Disappeared 258 ticker 의 53.1% cover |
| **S4** KRX Listed Master | ✅ COMPLETE | 9 snapshot 3,154 unique tickers. **Panel 815 / 815 모두 cover (100%)** |
| **S6** KRX Official Flow | ✅ VERIFIED (sample) | Sign 100%, ±5% 내 95% (FLOW_000007 CRITICAL close 근접) |
| **S2** OPENDART Body | ✅ feasibility verified | ZIP > XML download OK. Parser 5-9주 별도 phase (`docs/s2_opendart_body_parser_plan.md`) |

Acquired artifacts: `data/acquired/round4/` (자세히 = `ACQUISITION_SUMMARY.md`).

### W001 v1.x Code Fixes (2026-05-22, source 없이 가능 부분 완료)

Referee Round 4 deliverable 중 "code fix paths without source" 부분 진행:

| 변경 | 파일 |
|---|---|
| `adjust_for_corporate_actions()` docstring 명확화 + `adjusted_*_source = "unadjusted_raw_alias"` marker | `src/utils/corporate_action.py` |
| 새 `tradable_state()` 함수 + `TRADABLE_STATES` enum (4-cause partial categorical) | `src/utils/tradability.py` |
| Top100 generation rule module docstring (= 거래대금추정 top 100, reverse-engineered) | `src/data/universe.py` |
| 2 새 test (alias marker + tradable_state partial) | `tests/test_w001_korean_utils.py` |

Test suite: 420 passed (regression 없음).

실제 panel `tradable_state()` 분포:
- panel_absence: 789,429 (81.5%)
- executable: 172,002 (17.7%)
- data_missing: 7,450 (0.77%)
- limit_lock_candidate: 327 (0.03%)
- Reserved (W001 v2 source 필요): true_suspension / delisting_transition / corporate_action_day

이 fix 들은 informational / documentation 개선. **defect 공식 closure = Re-A0
까지 보류** (Referee 명시). 단 일부 defect 의 partial mitigation:
- G5_000002 (alias-only critical): naming/doc 부분 close, 가격 조정은 v2
- G5_000003 (metadata only high): docstring 명확화로 misleading risk 감소
- TRAD_000004 (zero_volume conflation medium): partial categorical 로 4-cause 일부 분리
- TOP_000001 (generation script missing medium): 규칙 docstring 으로 cover

### 진행 중 작업

Round 4 definition phase 완료 + W001 v1.x source-free code fix 완료. 다음 단계 = 사용자 결정:

1. **사용자 host 작업 (S1/S2/S3/S6 mandatory + S4 optional acquire)** — 자세히 `docs/round3_missing_source_register.md`
2. **W001 v2 code fix** (사용자 명시 후 시작 가능):
   - W001 v1.x (source 없이): tradable_state skeleton / 함수 doc / generation script doc
   - W001 v2 (source 후): 7 components 모두
3. **Re-A0 실행** (W001 v2 완료 후): 5 audit 재실행 → defect closure status

자세한 sequencing = `docs/W001_v2_infrastructure_repair_plan.md` +
`docs/W001_v2_reA0_gate_spec.md`.

### Forbidden (Round 4 hard lock, Referee 명시)

- Performance tests
- NAV / CAGR / Sharpe / hit rate / alpha / excess return / MDD / post-event drift / migration / turnover / resume / reversal / flow-return
- Raw return as signal or outcome
- Round 2 strategy diagnostic 재시작
- 147 extreme-return events 제외 후 testing 계속
- Flow data strategy testing (100% estimated + S6 missing 상태)
- Production / paper tracking / P08 / live readiness / shadow 연결

## Pending (사용자 의지 시작 가능, 일정 X)

### Round 4 mandatory sources (사용자 host)

자세히: `docs/round3_missing_source_register.md`

- **S1** Adjusted OHLC source (mandatory, Adjusted OHLC repair)
- **S2** Corporate Action Event Log (mandatory, 147 events classification)
- **S3** KRX Suspension / Delisting / Managed Status (mandatory, Tradability 4-cause)
- **S6** Flow Vendor Documentation (mandatory, 100% estimated 정정)
- **S4** Permanent ID fallback (needed for full lifecycle pass, 6% non-DART)

S5 = ✅ RESOLVED (reverse-engineered = 거래대금추정 top 100, external source 불필요).

### Round 4 code fix paths

자세히: `docs/W001_v2_infrastructure_repair_plan.md`

- W001 v1.x (immediate, source 없이 가능): **✅ COMPLETED (2026-05-22)**
  - `tradable_state` skeleton (4-cause partial categorical)
  - `adjust_for_corporate_actions()` docstring + alias marker
  - Generation script documentation
- W001 v2 (S source acquire 후, 사용자 결정 후):
  - C1 adjusted OHLC integration
  - C2 factor chain
  - C3 event log loader
  - C4 permanent ID master
  - C5 full tradable_state
  - C6 listing status module
  - C7 flow t+1 safe wrapper

### Round 1 backlog (Round 3 와 partial overlap)

- Task Q1 — KRX index event calendar (Round 1)
- Task Q2 — DART body parser (Round 1, S2 와 overlap)

### 기존 운영

- T007 broker worksheet 채우기 (사용자 host 작업)
- 세무 전문가 상담 (선택)

## Closed / Frozen (변경 시 사용자 결정 필요)

- P08_IEF30 frozen primary
- X-Lab full closed (Cycle 1 효과: TEST 0)
- 10 family closed (E/F/G/K/J/Q/R/S/X-ETF/X-KR pair)
- W001 v1 long-only certified (단 Round 2/3 에서 measurement layer 한계 finding 명확화); v2 = Round 4 phase

## Cycle 1 Final State

| Round | Active TEST | A0 AUDIT | BACKLOG | REJECT |
|---|---:|---:|---:|---:|
| Round 1 | 0 | 0 | 6 | 0 |
| Round 2 | 0 | 0 | 5 + 1 infra | 0 |
| Round 3 | 0 | 5 complete (34 defects) | 0 | 0 |
| Round 4 (definition) | 0 | (Re-A0 future) | (preserved) | 0 |
| **Total** | **0** | **5** | **12** | **0** |

## 사이클 위치

```
Round 1: Step 1-5 종료 (TEST 0 / BACKLOG 6)
Round 2: Step 1-5 종료 Option D (TEST 0 / BACKLOG 5 + 1 infra)
Round 3: Step 1-5 종료, Final Referee Lock (5 audits complete, 34 defects)
Round 4: Definition phase 완료 (4 artifacts)
  ⏸  Source acquisition (사용자 host) — pending 사용자 결정
  ⏸  W001 v2 code work — pending 사용자 결정
  ⏸  Re-A0 — W001 v2 완료 후
Round 5+: (조건부) Referee 재승인 후 strategy round 가능
```

False alpha 차단 framework: **9/9 catches** + 34 data layer defects 공식 등록.

## 룰

- 사용자 명시 결정 없이 여기 항목 추가 X
- 완료되면 제거 또는 closed 로 이동
- "future plan" / "should do" / "next phase" 류 표현은 다른 파일에서도 제거
