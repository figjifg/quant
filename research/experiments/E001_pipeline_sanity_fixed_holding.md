# E001 — Pipeline sanity: single-name daily flow filter, fixed holding, full reporting

## Status
planned

## Purpose (not a strategy)
This experiment exists to validate the research infrastructure end-to-end,
not to discover alpha. Any positive return observed here must be treated as
non-evidence. The signal is intentionally simple and may underperform
baselines — that is acceptable. Promotion criteria are about *pipeline
correctness*, not Sharpe.

E001 is **not** the seed experiment listed in CLAUDE.md §10. It reuses a
similar surface form for convenience, but its success criteria are
infrastructure-level only.

## Hypothesis (infra-level)
Given KRX after-close investor-flow data on day T, a trivial filter
(foreign 5-day net buy ratio > 0 AND institution 5-day net buy ratio > 0)
executed at the T+1 open and exited at the T+5 close, with realistic costs,
produces a report whose timestamps, costs, trade ledger, equity curve, and
IS/OOS split are internally consistent and free of look-ahead.

## Failure mode being tested
- Look-ahead from same-day after-close flow to same-day execution
- Use of NXT-integrated 통합 columns where KRX-only is required
- Use of estimated 추정 fields without surfacing the estimate flag
- Universe drift: using a Top100 membership recomputed with future info
- Cost accounting: commission/tax/slippage not applied or applied at wrong leg
- Report build: missing IS/OOS split, missing baselines, missing trade ledger

## Strategy type
인프라 검증. (분류상 가장 가까운 것: 수급 지속)

## Signal definition
For each ticker on KRX trading day T, using only data available **strictly
before T+1 open**:

  fnv_5 = rolling_sum(외국인순매수금액추정, 5, ending at T)
        / rolling_sum(거래대금추정, 5, ending at T)
  inv_5 = rolling_sum(기관순매수금액추정,   5, ending at T)
        / rolling_sum(거래대금추정, 5, ending at T)

  signal_T = 1 if (fnv_5 > 0) AND (inv_5 > 0) else 0

Notes:
- 종가는 정규화된 `KRX종가` 컬럼만 사용한다. 사용자가 보는 `KRX종가`는
  로더가 항상 합성하는 단일 컬럼이며, 원본 CSV에 `KRX종가`가 없는 경우
  (pre-NXT 패널) `종가`에서 채워진다 — §"Source modules / equity_panel.py"
  의 정규화 규칙 참조. raw `종가` 컬럼은 본 실험 로직에서 직접 사용 금지.
- 거래대금 분모는 같은 5거래일 윈도. 윈도 내 결측이 하나라도 있으면 그 종목 그 날 signal = 0.
- 추정 플래그 정책 (data discovery 후 2026-05-13 갱신):
  - `수급금액추정여부`는 본 패널의 **모든 행에서 True** — Kiwoom 데이터는 수급
    금액을 항상 추정 산출하므로 품질 게이트가 아니라 단순 레이블. 본 필터에서
    제외하지 않는다.
  - `거래대금추정여부`는 1.14M 행 중 98 행만 True — 의미 있는 품질 플래그로
    유지. 헤드라인은 이 행만 5일 윈도에서 제외.
  - 진단 실험(`diagnostic_estimate_included`)은 이 98 행도 포함한 슬라이스.

## Entry rule
- signal_date = T
- execution_date = T+1 (first KRX trading day after T on the panel)
- entry_price = T+1 시가. 시가 결측이면 해당 종목 그날 제외.
- 가중치: signal_T = 1 인 후보 중 최대 5개. 후보 수가 5를 초과하면
  combined_flow_5 = (외국인+기관 5일 net buy ratio) 내림차순 상위 5종목.
- 동일 종목 중복 진입 금지. 이미 보유 중인 종목은 다음 진입에서 제외.
- 한 종목 비중 = 가용 현금의 1/min(5, 후보수). equal-weight, no rebalancing intra-trade.

## Exit rule
- 고정 보유: 진입일(T+1) 종가 기준 5 KRX 거래일 경과 후 종가에 청산.
- 즉 exit_date = (T+1) + 5 KRX trading days, exit_price = 그 날의 `KRX종가`.
- 신호 기반 조기 청산, intraday stop, trailing stop 모두 **없음**.
- 보유 중 거래정지·결측이 발생하면: 다음 유효 KRX종가 첫 등장일에 청산하고
  로그(`trades.csv`)에 사유 코드를 남긴다.

## Holding period
5 KRX trading days, fixed.

## Universe
- 1차 universe: `동적유니버스포함 == True` AND `KRX종가` 결측 아님.
- universe 멤버십은 신호일 T가 아니라 **T-1까지의 패널 슬라이스만으로 결정**.
  (universe drift 방지 검증 목적. T일 마감 후 갱신된 Top100을 T+1 진입 후보에
  반영하지 않는다. T+1 진입은 T-1까지 확정된 universe를 사용.)
- 2차 유동성 필터: T-1을 끝점으로 한 최근 20거래일 평균 `거래대금추정` ≥ 50억 원.
- KOSPI/KOSDAQ 구분 정보가 패널에 없으므로 본 실험에서는 분리하지 않는다.
  종목코드 자릿수 기반 휴리스틱으로 추정하지 않는다.

## Data assumptions
- IS source: `inputs/equity_panels/dynamic_top100_2018_2024_panel.csv`
- OOS source: `inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv`
- 2010~2016 panel은 본 실험에서 사용하지 않는다 (스키마·NXT 환경 상이).
- 2017~2024 panel도 본 실험에서는 사용하지 않는다 (2018 시작점과 중복).
- IS 기간: 2018-01-02 ~ 2022-12-30
- OOS 기간: 2023-01-02 ~ 2026-05-04
- Market flow / futures / macro / events: **본 실험에서는 사용하지 않는다.**
  순수 종목 패널만으로 파이프라인을 검증한다.
- 시간대: 모든 날짜는 KRX 거래일 기준. 캘린더는 IS panel에 실제로 등장한
  날짜 집합을 정답으로 본다 (별도 거래일 캘린더를 인위적으로 만들지 않는다).

## Cost assumptions
Per leg, per name, on traded notional:
- commission_bps        = 1.5
- tax_bps (sell only)   = 20.0   (KRX 거래세 가정. 추후 실제 세율로 보정)
- slippage_bps          = 5.0

Round-trip drag on a single trade ≈ commission 1.5 + slippage 5 (buy)
                                  + commission 1.5 + tax 20 + slippage 5 (sell)
                                  ≈ 33 bps of traded notional.
비용 0 변형은 `cost_sensitivity.csv` 진단 행으로만 존재. 헤드라인 metrics에
사용하지 않는다.

## Baseline comparison
- B0: cash (0% return)
- B1: KOSPI 지수 proxy. 별도 시계열이 없으므로 universe equal-weight buy & hold로 대체.
- B2: 동일 universe equal-weight, 5거래일 rebalance, 같은 비용 모델.
- B3: 가격 모멘텀 단독 — `recent_return_5 > 0` (수급 미사용), 그 외 동일.
B3 대비 우위 부재가 본 실험의 kill 사유는 **아니다**. 그러나 report.md는
비교를 반드시 포함한다.

## Parameters to test
없음. **파라미터 스윕 금지.**
- lookback = 5 (고정)
- holding = 5 (고정)
- max_positions = 5 (고정)
- 유동성 임계 = 50억 (고정)
- IS/OOS 경계 = 2023-01-01 (고정)

비용 감응만 `cost_sensitivity.csv`에 0×, 1×, 2×, 3× 변형으로 기록.
이는 진단이며 헤드라인에 사용하지 않는다.

## Parameters that must NOT be optimized
- lookback (5)
- holding period (5)
- max_positions (5)
- universe 유동성 임계 (50억)
- IS/OOS 분기 (2023-01-01)
- 비용 가정값 (헤드라인은 1×에 고정)

## Diagnostic split (within this ticket)
같은 코드 경로에서 다음 변형을 동시에 산출하되, **헤드라인은 (A)만 사용**.
나머지는 진단 행으로 `metrics.json` 안에 별도 키로 격납.

- (A) 추정 플래그 False 행만 사용 ← 헤드라인
- (B) 추정 플래그 무관, 추정 행 포함 ← 진단
- (C) 비용 0× / 2× / 3× ← `cost_sensitivity.csv`로 격납

(B)와 (A)의 메트릭 차이가 큰 경우, 추정 데이터 신뢰도 이슈로 별도 후속
티켓(E001-D1)을 만든다.

## Success criteria (infra-level, NOT alpha-level)
A. `signals.csv` 모든 행에서 signal_date < execution_date.
B. `trades.csv` 모든 행에서 entry_date ≤ exit_date 이며 (exit_date - entry_date)가
   KRX 거래일 기준 정확히 5.
C. `trades.csv`의 entry_price·exit_price가 패널의 시가/`KRX종가`와 정확히 일치
   (재현 가능 lookup으로 검증).
D. `metrics.json`에 IS와 OOS 블록이 분리되어 존재.
E. `cost_sensitivity.csv`가 비용 0×→3× 증가에 대해 단조 감소(net return) 또는
   동률을 보임.
F. `tests/test_no_lookahead.py`와 `tests/test_feature_timing.py`가 통과.
G. `report.md`가 baseline B0~B3 비교표를 포함.
H. `report.md`에 다음 메타 정보가 명시: 사용된 panel 파일, 통합거래량/통합종가
   사용 여부, 추정 플래그 처리 방식, 캘린더 정의 방식, **각 panel별
   `KRX종가` derivation 출처(native / from `종가` fallback)와
   `종가 ≠ KRX종가` 행 수**.

## Kill criteria
- A~H 중 하나라도 실패 → 인프라 수정 후 재실행. 결과의 알파 해석 금지.
- 동일자 체결, 미래 universe 사용, 비용 미반영 중 어느 하나라도 발견되면
  즉시 kill 후 회귀 테스트 추가.
- 시그널 일자와 체결 일자가 같은 행이 단 하나라도 발견되면 kill.

## Expected weaknesses
- 5일 holding fixed → 청산 로직 실험 부재.
- max_positions=5 → 분산 부족, 결과 노이즈 큼.
- 단일 lookback → 신호 강도·지속성 변수 부재.
- 비용 모델이 시장 충격을 반영하지 않음.
- universe가 dynamic Top100에 한정 → 생존편향 잔재.
- 본 실험의 어떤 양(+)의 성과도 알파 증거로 해석하지 않는다.

## Codex implementation task

Read this ticket end-to-end before writing code. Read `CLAUDE.md` and
`AGENTS.md`. `AGENTS.md` is the engineering rulebook; this section
specifies only what is unique to E001.

Do not change the hypothesis, parameters, IS/OOS boundary, universe
rules, cost defaults, exit rules, or success criteria above. If anything
in this ticket is ambiguous, **stop and ask in the PR description**
rather than guess. Adding parameters not listed here is a ticket
violation.

### Scope discipline

This is the first implementation in the repo. Build only what E001
imports. Do not scaffold modules that nothing uses. Do not add abstract
base classes for hypothetical future strategies. Three E001 strategy
variants share most of the engine (headline, B2, B3) — that is the
level at which abstraction is justified.

### Source modules (under `src/`)

- `src/data/equity_panel.py`
  - Load and row-concat:
    `research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv`
    and `research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv`.
  - Strip the BOM on the header. Parse `날짜` as `pandas.Timestamp` (date,
    no tz). Sort by `(종목코드, 날짜)`.
  - Validate that the required columns (see "Required columns" below)
    exist and have the expected dtypes. Estimate-flag columns
    (`수급금액추정여부`, `거래대금추정여부`, `동적유니버스포함`) must be
    boolean after load — coerce the literal "True"/"False" strings if
    needed and assert the result.
  - **`KRX종가` normalization.** After concatenation, ensure a single
    `KRX종가` column exists. For source CSVs that do not contain
    `KRX종가` (e.g., the pre-NXT `dynamic_top100_2018_2024_panel.csv`),
    populate `KRX종가` from `종가` for those rows — `종가` is the KRX
    close by definition in the pre-NXT era. Add a `krx_close_source`
    column per row taking values `"native"` (CSV had `KRX종가`) or
    `"from_종가_fallback"`. Verification: in panels where both
    columns exist on disk, every row must have `종가 == KRX종가` after
    load; assert this and raise on any mismatch (no silent overwrite).
  - Do not silently fill NaNs in any other column.

- `src/backtest/calendar.py`
  - Derive the KRX trading-day calendar as the sorted unique set of
    dates that appear with at least one non-null `KRX종가` row across
    the merged panel. The panel is the single source of truth — do not
    fetch a calendar elsewhere.
  - Provide `next_trading_day(date)` and `add_trading_days(date, n)`.
    Convention: `add_trading_days(d, 1) == next_trading_day(d)`, so
    `add_trading_days(d, 5)` is the 5th trading day strictly after `d`.

- `src/data/universe.py`
  - For each candidate execution date `D`, return the set of tickers
    eligible to be entered at the `D` open. Eligibility uses **only**
    panel rows with `날짜 <= D-1` (where `D-1` is the previous KRX
    trading day under the derived calendar).
  - Rules:
    1. `동적유니버스포함 == True` on the most recent `날짜 <= D-1` row.
    2. Mean of `거래대금추정` over the last 20 KRX trading days ending
       at `D-1` is `>= 5_000_000_000` KRW.
    3. For the **headline** slice: every one of the 5 rows used by the
       signal (i.e., `날짜` in {`D-5`, `D-4`, `D-3`, `D-2`, `D-1`} for a
       signal observed on `D-1`) must have `거래대금추정여부 == False`.
       (`수급금액추정여부` is universally True in the Kiwoom panel and is
       therefore not part of the gate — see Signal definition notes.)
       The diagnostic slice skips rule 3.

- `src/features/flow_ratios.py`
  - Per `(종목코드, 날짜)` features:
    - `traded_value_5    = rolling_sum(거래대금추정,        5, label='right')`
    - `foreign_net_5     = rolling_sum(외국인순매수금액추정, 5, label='right')`
    - `institution_net_5 = rolling_sum(기관순매수금액추정,   5, label='right')`
    - `fnv_5             = foreign_net_5 / traded_value_5`
    - `inv_5             = institution_net_5 / traded_value_5`
    - `combined_flow_5   = (foreign_net_5 + institution_net_5) / traded_value_5`
    - `recent_return_5   = KRX종가 / KRX종가.shift(5) - 1` (for B3 only)
  - If any of the 5 input rows for a rolling window is missing or NaN,
    the output for that `(ticker, date)` is NaN. No forward-fill.
  - Attach `signal_date = 날짜` and
    `execution_date = calendar.next_trading_day(signal_date)`.

- `src/strategies/e001_flow_filter.py`
  - Headline signal: `signal = (fnv_5 > 0) & (inv_5 > 0)`.
  - Tie-break for max-positions: rank by `combined_flow_5` descending.

- `src/strategies/baselines.py`
  - B0 — cash. Equity curve flat at 1.0.
  - B1 — at the **first IS trading day** (and again at the first OOS
    trading day, independently), allocate cash equally across all
    tickers eligible by `universe` rules on that date. Hold to the
    period end with no rebalancing. If a held ticker has a missing
    `KRX종가` for K consecutive trading days, force-exit at the
    last-known `KRX종가` and hold cash for that slot. Same cost model
    as headline.
  - B2 — every 5 KRX trading days (anchored at the period start),
    rebalance to equal weights across **all** tickers eligible by
    `universe` rules on the rebalance date. Same cost model.
  - B3 — identical to the headline engine (same slot mechanics, same
    holding period, same exit rule, same cost model) except the signal
    is `recent_return_5 > 0` instead of `(fnv_5 > 0) & (inv_5 > 0)`.
    Tie-break by `recent_return_5` descending.

- `src/backtest/costs.py`
  - Pure functions:
    `buy_cost(notional, cfg) = notional * (commission_bps + slippage_bps) / 1e4`
    `sell_cost(notional, cfg) = notional * (commission_bps + slippage_bps + tax_bps) / 1e4`
  - All bps values come from the config file, never from code constants.

- `src/backtest/engine.py`
  - Slot-based execution. State: 5 fixed slots, each either empty or
    holding `(ticker, entry_date, entry_price, notional, exit_date)`.
  - For each trading day `D` in the period:
    1. **Exits first.** For every slot whose `exit_date == D`, sell at
       that ticker's `KRX종가` on `D`. Cash receives
       `position_shares * exit_price - sell_cost(position_shares * exit_price, cfg)`.
       The slot becomes empty. Record an entry in `trades.csv` with
       `exit_reason = "holding_period"`.
       - If `KRX종가` is missing on `D` for that ticker, defer to the
         next trading day with a non-null `KRX종가` for that ticker and
         set `exit_reason = "missing_price_fallback"`.
    2. **Mark-to-market** held positions at `KRX종가` on `D`. Equity =
       cash + sum(slot notional at MTM).
    3. **Entries.** Look up `signals` rows where
       `execution_date == D` AND `signal == True`. Drop tickers already
       held in any slot. Rank remaining by `combined_flow_5` (or
       `recent_return_5` for B3) descending. Take the top
       `(5 - filled_slots)`. For each taken ticker:
        - If `시가` on `D` is missing, skip the entry (record nothing).
        - Position notional = `equity_at_open / 5`.
        - Shares = `notional / 시가`.
        - Cash decrements by
          `notional + buy_cost(notional, cfg)`.
        - Slot stores `exit_date = add_trading_days(D, 5)`.
  - At period end (last day of IS or OOS), force-exit all remaining
    slots at that day's `KRX종가` and record
    `exit_reason = "period_end"`.

- `src/reporting/metrics.py`
  - Compute for IS and OOS **separately** (and for each baseline, and
    for the diagnostic estimate-included slice):
    `total_return`, `annualized_return`, `annualized_volatility`,
    `sharpe` (rf = 0), `max_drawdown`, `hit_rate`,
    `average_trade_return`, `median_trade_return`, `profit_factor`,
    `average_holding_period`, `trade_count`, `turnover`,
    `cost_paid_total`, `return_before_cost`, `return_after_cost`,
    `exposure_ratio`, `max_consecutive_losses`.
  - `turnover` = sum of buy notional over period / average NAV.
  - `exposure_ratio` = average (NAV − cash) / NAV over period.
  - Annualization uses 252 KRX trading days.

- `src/reporting/report.py`
  - Render `report.md` deterministically from `metrics.json` + a
    metadata dict. Codex-written content is limited to: metadata block
    (panels used, IS/OOS dates, 추정 row policy, 통합 column policy,
    calendar source), IS metric table, OOS metric table, baseline
    comparison table (rows = {headline, B0, B1, B2, B3}; columns = a
    fixed subset of metrics), cost-sensitivity table, and a list of
    diagnostic keys.
  - No interpretive prose. Numbers in `report.md` must match
    `metrics.json` byte-for-byte at the displayed precision.

- `src/run_experiment.py`
  - CLI entry point:
    `python -m src.run_experiment --config configs/backtests/e001.yaml`.
  - Reads the config, runs headline + diagnostics + baselines +
    cost-sensitivity grid, writes all output files to
    `reports/experiments/E001_pipeline_sanity_fixed_holding/`.

### Required columns from the equity panel

The engine consumes only these columns from the merged panel:
`날짜`, `종목코드`, `시가`, `KRX종가`, `거래대금추정`,
`외국인순매수금액추정`, `기관순매수금액추정`,
`수급금액추정여부`, `거래대금추정여부`, `동적유니버스포함`.

Do not depend on `종목명`, `종가` (integrated), `시가총액추정`,
`상장주식수`, or any `통합*여부` column for the headline run. If a
diagnostic needs them, isolate that read.

### Configuration file

`configs/backtests/e001.yaml` must contain:

```yaml
experiment_id: E001
panels:
  - research_input_data/inputs/equity_panels/dynamic_top100_2018_2024_panel.csv
  - research_input_data/inputs/equity_panels/dynamic_top100_2025_2026_krx_panel.csv
periods:
  is:
    start: 2018-01-02
    end:   2022-12-30
  oos:
    start: 2023-01-02
    end:   2026-05-04
universe:
  require_dynamic_top100: true
  min_avg_traded_value_20d: 5_000_000_000
  exclude_estimated_flag_rows: true  # headline only
strategy:
  lookback: 5
  holding: 5
  max_positions: 5
costs:
  commission_bps: 1.5
  tax_bps_sell:   20.0
  slippage_bps:   5.0
cost_sensitivity_multipliers: [0.0, 1.0, 2.0, 3.0]
output_dir: reports/experiments/E001_pipeline_sanity_fixed_holding
```

No additional keys. No hidden defaults in code.

### Tests (under `tests/`)

- `tests/test_data_schema.py` — required columns present, dates
  parseable, BOM stripped, estimate-flag columns are `bool` after load.
- `tests/test_feature_timing.py` — on a hand-crafted 30-day, 3-ticker
  panel, assert `fnv_5` at date T equals the closed-form computation
  using only rows with `날짜 <= T`. Mutating any row with `날짜 > T`
  must not change the output (regression case for forward leakage).
- `tests/test_no_lookahead.py` — run the full E001 pipeline on a small
  synthetic panel. Assert:
    - Every `signals.csv` row has `signal_date < execution_date`.
    - Every `trades.csv` row has `entry_date <= exit_date`, and the
      number of trading days between them under the derived calendar
      is exactly 5 (or `exit_reason != "holding_period"`).
    - `entry_price` matches the panel's `시가` at
      `(ticker, execution_date)` exactly.
    - `exit_price` matches the panel's `KRX종가` at
      `(ticker, exit_date)` exactly when
      `exit_reason == "holding_period"`.
    - Universe selection for `execution_date == D` reads no panel row
      with `날짜 >= D`.
- `tests/test_backtest_engine.py` — slot accounting on a fixture:
    - Never more than 5 simultaneous positions.
    - No duplicate entries on the same ticker while held.
    - Exit cash matches `shares * exit_price * (1 - sell_cost_bps / 1e4)`
      to 1e-6 absolute.

### Output files

Under `reports/experiments/E001_pipeline_sanity_fixed_holding/`:
- `config.yaml` (copy of the input config used for the run)
- `metrics.json`
- `trades.csv`
- `signals.csv`
- `equity_curve.csv`
- `cost_sensitivity.csv`
- `report.md`

### Order of work

Commit after each green test boundary.

1. `src/data/equity_panel.py` + `tests/test_data_schema.py`.
2. `src/backtest/calendar.py` (unit-tested inline in the same module
   test, or in `test_backtest_engine.py`).
3. `src/features/flow_ratios.py` + `tests/test_feature_timing.py`.
4. `src/data/universe.py` (its no-lookahead behavior is covered by
   `test_no_lookahead.py` in step 7).
5. `src/backtest/costs.py` + `src/backtest/engine.py` (headline only)
   + `tests/test_backtest_engine.py`.
6. `src/strategies/e001_flow_filter.py`, then
   `src/strategies/baselines.py`.
7. `tests/test_no_lookahead.py` end-to-end on a synthetic panel.
8. `src/reporting/metrics.py` + `src/reporting/report.py`.
9. `src/run_experiment.py` and `configs/backtests/e001.yaml`.
10. Run the full E001 backtest on the real panels. Verify
    success-criteria A–H above.

### Completion criteria

- `pytest` is green.
- `python -m src.run_experiment --config configs/backtests/e001.yaml`
  produces every required output file with no manual steps.
- `report.md` and `metrics.json` agree on every displayed number.
- Ticket success criteria A–H are satisfied.
- The PR description lists every place where the implementation chose
  one reading of an under-specified spec, and explains why.

### Out of scope for this ticket

- Any strategy parameter sweep beyond `cost_sensitivity_multipliers`.
- Sector / market-cap / regime breakdowns.
- Plot generation.
- Live data, API calls, downloads, or any network access.
- Reading `market_flow/`, `futures/`, `macro_features/`, or `events/`.
- KOSPI / KOSDAQ distinction.
- Any abstraction designed for a hypothetical future ticket.

## Result summary
DO NOT FILL until backtest is complete and files exist on disk.

## Claude review
DO NOT FILL until result files are read.
