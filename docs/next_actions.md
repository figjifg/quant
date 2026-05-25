# Next Actions

이 프로젝트에서 "다음에 해야 할 것" 은 **오직 이 파일에서만** 적는다. 다른 가이드
파일은 현재 상태 / 정책 / 결과만 기록한다. 새 세션이 다른 파일을 읽다가 "next
phase = X 해라" 같은 문구에 끌려서 자동으로 그 방향으로 행동하는 lock-in 회피.

비어 있는 것이 정상이다. 사용자가 명시적으로 결정한 active 작업만 여기 적는다.

## Active

비어 있음. 다음 phase 진입 = 사용자 + Referee 명시 결정 필요.

## Closed / Frozen (변경 시 사용자 결정 필요)

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
| Round 6 | C2-C3-DESIGN-FINALIZATION (9 design-only outputs, **CLOSED**) → Measurement-layer A0 initial pass (P0-1/P0-2/P1 + P2 backlog registers, **CLOSED AS PARTIAL / DEFECT-FOUND**) → KR-OHLCV-QUARANTINE-ENFORCEMENT-A0 (8 outputs, **CLOSED AS DEFECT-FOUND** — 143 defects recorded; no patches applied) → KR-OHLCV-QUARANTINE-PATCH-PHASE (9 outputs + guard module + 19 tests + 6 patched files, **CLOSED AS PATCHED-PARTIAL / RESIDUAL BLOCKERS PRESERVED** — 45 residual blockers; runtime propagation not verified) → KR-OHLCV-RUNTIME-MASK-PROPAGATION-A0 (9 outputs, **CLOSED AS RUNTIME-VERIFIED FOR TESTED PATHS / RESIDUAL BLOCKERS PRESERVED** — 10/10 synthetic + 11,425 real invalid rows detected; backtest/universe gates verified active) → KR-OHLCV-RESIDUAL-BLOCKER-PATCH-PHASE (9 outputs + helper + 3 tests + 6 closed-strategy entry patches, **CLOSED AS RESIDUAL-BLOCKERS-REDUCED / OPS BLOCKERS PRESERVED** — 40 patched / 4 still_reopen_blocker / 1 false_positive; 6/6 smoke pass) → KR-KRX-CALENDAR-SOURCE-ACQUISITION-A0 (11 outputs + composite calendar, **CLOSED AS CALENDAR-SOURCE-RECONCILED / EXECUTION STILL CLOSED** — 4,034 dates 2010-2026; 4,021/4,021 t+1 match; 12 vendor-cutoff anomalies) → KR-LISTED-UNIVERSE-COVERAGE-A0 (12 outputs + monthly KRX universe, **CLOSED AS LISTED-UNIVERSE-SOURCE-ACQUIRED / PARTIAL LIFECYCLE / NOT SURVIVORSHIP-SAFE** — 3,653 official tickers vs 925 panel = 25.3% coverage; 2,728 official-only; 519 disappeared no-terminal) → KR-EXECUTABLE-STATUS-COVERAGE-A0 (12 outputs, **CLOSED AS EXECUTABLE-STATUS-SOURCE-ACQUIRED / PARTIAL COVERAGE / EXECUTION STILL CLOSED** — S3 KRX status events; 10,774 events / 1,855 tickers / 2018+ only; intraday halt + limit-lock + pre-2018 missing) → KR-EXECUTABLE-STATUS-LIMIT-LOCK-SOURCE-A0 (12 outputs, **CLOSED AS LIMIT-LOCK-PROXY-RECONCILED / PARTIAL COVERAGE / EXECUTION STILL CLOSED** — rule-derived 336 candidates; W001 v2 41 rows under-counted; conservative execution rule design; 9 defects) → KR-EXECUTABLE-STATUS-PRE2018-EXTENSION-A0 (12 outputs, **CLOSED AS PRE2018-STATUS-SOURCE-ACQUIRED / RECONCILED / EXECUTION STILL CLOSED** — OPENDART 2010-2017 acquired; 300,829 raw / 7,150 filtered events; pre_2018_status_coverage_gap closed) → KR-EXECUTABLE-EFFECTIVE-DATE-LINKAGE-A0 (12 outputs, **CLOSED AS EFFECTIVE-DATE-LINKAGE-AUDITED / PARTIAL / NOT GENERALIZABLE / EXECUTION STILL CLOSED** — 113 samples / 1.8% extraction rate; HTML-inline + S2 PARTIAL = core blocker) → KR-STATUS-EFFECTIVE-DATE-MANUAL-AUDIT-PHASE (12 outputs + build script + 195-ZIP cache, **CLOSED AS MANUAL-AUDIT-COMPLETED / SUPPORTS HTML-INLINE PARSER REOPEN / EXECUTION STILL CLOSED** — 195 samples / 56.4% extraction = 31× lift; bs4 HTML-inline; suspension 92.5% + resumption 90.2% parser-feasible; gate `MANUAL_AUDIT_SUPPORTS_PARSER_REOPEN`) |

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
