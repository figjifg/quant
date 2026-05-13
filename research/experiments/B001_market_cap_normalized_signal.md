# B001 — Market-cap-normalized flow signal (B family experiment #1)

## Alpha family taxonomy
- **A family** (예전 E001~E004): 거래대금 정규화된 5일 누적 매수 신호.
  - A001 = `E001_pipeline_sanity_fixed_holding` (인프라 검증, 고정 5일)
  - A002 = `E002_dynamic_exit_volatility_stop` (cap_only 발견)
  - A003 = `E003_market_flow_gate` (kill)
  - A004 = `E004_signal_strength_top_quintile` (kill)
  - A 가족 최고 변형: A002 cap_only (OOS net +0.688, hit_rate 0.493).
- **B family** (시가총액 정규화 신호, 본 ticket부터): 5일 누적 매수를
  거래대금이 아니라 시가총액으로 정규화. 가족 첫 ticket = **B001**.
- 기존 `E###` 파일명은 git 이력 보존을 위해 그대로 둠. 신규 ticket은
  B-접두사 사용.

## Status
planned

## Purpose (alpha-level)
A004 review 결과 + 즉석 진단으로 확인된 사실: A002 cap_only 매매가
universe 중앙값 대비 **약 19배 큰 시가총액**의 종목에 집중됨. 직접
원인 두 가지 후보:
1. Universe 자체가 "거래대금 상위 100"이라 대형주 비중 큼 (고정 변수)
2. Tie-break 순위가 `combined_flow_5` (거래대금 정규화)인데, 이 척도
   자체에 size 편향이 잔존할 가능성

B001은 가설 (2) 를 단일 변수 변경으로 테스트한다. **신호 양수
필터는 그대로**, **순위 척도만** 거래대금 정규화 → 시가총액 정규화로
교체. 다른 모든 게 (universe, cap_only 청산, 비용, max_positions)
A002와 동일.

## Hypothesis
Tie-break 순위를 `combined_flow_5_mcap = (외국인+기관 5일 누적 매수
금액) / 시가총액(T)` 으로 바꾸면, A002 cap_only 대비
- 매매 종목의 시가총액 중앙값이 의미 있게 (≥ 30 %) 감소하고
- OOS net 수익률이 크게 나빠지지 않는다 (≥ −0.05 vs A002 cap_only)
- OOS 승률이 크게 나빠지지 않는다 (≥ −0.02)

즉 "시가총액 정규화는 size 편향을 완화하면서 알파를 잃지 않는다"가
약한 형태의 본 가설. 강한 형태는 "OOS net이 개선됨" — 이는 보너스
가설로, 약한 가설이 통과하면 그 위에서 후속 ticket으로 검증.

## Failure modes being tested
- **순위 척도 무관**: 시가총액 정규화든 거래대금 정규화든 동일한
  종목이 매매에 잡힘 — universe 자체가 size 편향의 진짜 원인.
- **새 척도 = 다른 종목 → 더 나쁜 결과**: size 편향 완화는 됐으나
  소형주 신호는 평균적으로 약함.
- **새 척도 = 다른 종목 → 비슷한 결과**: 통계적 평균이라 두 척도가
  서로 다른 매매를 잡지만 평균 수익은 유사.

## Strategy type
B 가족 첫 실험. Layer 1 신호 정의의 정규화 차원 변경.

## Signal definition (changed at the ranking step only)

### Sign filter (unchanged from A 가족)
```
fnv_5 = rolling_sum(외국인순매수금액추정, 5td) / rolling_sum(거래대금추정, 5td)
inv_5 = rolling_sum(기관순매수금액추정,   5td) / rolling_sum(거래대금추정, 5td)
sign_pass_T = (fnv_5(T) > 0) AND (inv_5(T) > 0)
```

These are the same `fnv_5` / `inv_5` that A001~A004 used. We keep them
because the **sign** decision is independent of normalization, and we
want to change only one thing.

### NEW ranking metric
```
combined_flow_5_mcap = rolling_sum(외국인+기관 순매수 금액, 5td)
                    / market_cap(T)
```

where `market_cap(T)` is the `시가총액추정` column value at the signal
date T for that ticker. `시가총액추정` is already in the panel — **no
new data source**.

NaN handling: if `시가총액추정(T)` is NaN or ≤ 0, the ticker is
ineligible for ranking on that day (excluded from candidates).

### Selection rule
On each signal_date T, among tickers passing the sign filter AND with
non-NaN positive `market_cap(T)`, rank by `combined_flow_5_mcap`
descending. The engine's slot mechanic (max 5 positions, one per
ticker) picks the top-ranked candidates each day.

(In A002, the ranking was `combined_flow_5` descending. That's the
single change.)

## Entry / Exit / Universe / Cost / IS-OOS
All unchanged from A002 cap_only:
- Entry: T+1 KRX 09:00 시가
- Exit: holding_cap = 20 KRX trading days at KRX종가, vol_stop_k = None
- Universe: 동적 Top100 + 거래대금 ≥ 50억 + Rule 3 거래대금추정여부=False
- Costs: 1.5 / 20 / 5 bps
- IS: 2018-01-02 ~ 2022-12-30, OOS: 2023-01-02 ~ 2026-05-04

## Data assumptions
**Locked data set**: same two panels A 가족이 썼던 것 그대로.
**No new data**. `시가총액추정` column is already in those panels.

If `시가총액추정여부 == True` for a row (estimated market cap), the row
is still used for ranking. We do NOT add a third estimate-flag
filter — too many filters compound noise. (Estimated mcap rows ratio
in our panel is small enough this is unlikely to dominate.)

## Cost assumptions (unchanged)

## Baseline comparison

**Layer 1 — direct head-to-head**
- `B_A002_cap_only` — A002 cap_only rerun on the same period.
  Direct head-to-head: same universe, same signal sign filter, same
  exit, only ranking metric differs.

**Layer 2 — context**
- `B0_cash`, `B1`, `B2`, `B3` — preserved (with the known E001-vintage
  defects in B0/B1/B2; not E003-F1 territory yet).

## Parameters to test
**None. Single point.**

| Parameter | Value | Rationale |
|---|---|---|
| Normalization divisor | `시가총액추정(T)` | The new variable. Single point. |
| Sign filter | `(fnv_5 > 0) AND (inv_5 > 0)` | Unchanged from A 가족 |
| All exit/universe/cost params | Same as A002 cap_only | Lock to isolate the ranking change |

## Parameters that must NOT be optimized
- Normalization divisor (시가총액(T), not e.g. 5-day average mcap, not log-mcap, not √mcap)
- Sign filter (unchanged)
- All A002 cap_only carry-overs

## Diagnostic split (within this ticket)
- **(A) B001 headline** — sign filter + mcap-normalized ranking + cap_only
- **(B) A002 baseline** — sign filter + 거래대금-normalized ranking + cap_only (re-run)
- **(C) Trade composition diagnostic** — for each of (A) and (B),
  emit a small CSV with median market cap of entered tickers, by
  year. Diagnostic only; informs interpretation regardless of pass/fail.

## Success criteria (alpha-level)

All four must hold for `promote`:

1. **Trade composition shifted**: OOS median market cap of (A) trades
   is at least **30 % lower** than OOS median market cap of (B)
   trades. (If this fails, the ranking change didn't actually
   redirect selection — the universe is the size-bias source.)
2. **No big return loss**: OOS net total_return (A) ≥ OOS net total
   return (B) − 0.05. The "weak hypothesis" — we are not requiring
   improvement, just no significant degradation.
3. **No big hit-rate loss**: OOS hit_rate (A) ≥ OOS hit_rate (B) − 0.02.
4. **Trade count ≥ 50** for both (A) and (B) OOS.

Optional bonus criterion (for `promote` with strong evidence):
5. **OOS net total_return (A) > (B)** AND **cost-0 OOS (A) > cost-0 OOS (B)**.

## Kill criteria

Any one → `kill`:
- OOS net total_return (A) < (B) − 0.10 (signal lost too much alpha)
- OOS median mcap (A) within 10 % of (B) (ranking change had no effect — hypothesis falsified at the mechanism level)
- pytest regression on E001–E004 (A 가족) suite

## Expected weaknesses
- **Single-point parameter** for normalization basis (시가총액(T)).
  Other divisors (log mcap, 5-day average mcap, sqrt mcap) are
  out of scope. If results suggest one of those would be better,
  that's a new pre-registered ticket.
- **Universe still large-cap heavy.** Even after mcap-normalized
  ranking, our pool is still "Top 100 by 거래대금". To truly
  diversify size, universe itself would need to expand. That is
  out of scope for B001.
- **시가총액 추정 노이즈.** Some mcap values are flagged estimated.
  We do not filter those — unlike the 거래대금추정여부 rule kept on
  signal rows.

## Codex implementation task

Read this ticket end-to-end. Read `CLAUDE.md`, `AGENTS.md`, and at
least the A002 (E002) review for cap_only context. Base commit = the
latest `main`.

### Scope discipline (additive only)

Touch:
- `src/features/flow_ratios.py` — add `combined_flow_5_mcap` column.
  Computed per (종목코드, 날짜) as
  `(외국인순매수금액추정 5td sum + 기관순매수금액추정 5td sum) / 시가총액추정(at 날짜)`.
  If `시가총액추정` is NaN or ≤ 0 at 날짜, the new column is NaN.
- `src/strategies/b001_mcap_normalized.py` (NEW) — analog of
  `e001_flow_filter` but uses `combined_flow_5_mcap` for ranking
  instead of `combined_flow_5`. Same sign filter
  `(fnv_5 > 0) AND (inv_5 > 0)`. Drop candidates with NaN
  `combined_flow_5_mcap`.
- `src/run_experiment.py` — add `experiment_id == "B001"` dispatch
  and `run_b001_experiment(config, config_path)`. Runs (A) headline,
  (B) A002 cap_only re-run, baselines B0~B3, cost sensitivity on (A),
  cost_0 diagnostics for (A) and (B), and a separate
  `trade_mcap_composition.csv` reporting median entry mcap by year
  for both (A) and (B).
- `configs/backtests/b001.yaml` (NEW)
- `tests/test_flow_ratios_mcap.py` (NEW) — synthetic panel: verify
  `combined_flow_5_mcap` formula, NaN handling, prior-row safety.
- `tests/test_b001_strategy.py` (NEW) — synthetic candidates panel:
  verify the sign filter still applies, ranking uses the new column,
  ties broken consistently with A002 (lexicographic on 종목코드 ascending).

**Do NOT touch**:
- engine, calendar, costs, universe, baselines, metrics, report,
  market-flow loader (A003 module), market-gate features (A003),
  quintile strategy (A004), and all A 가족 strategy files. They stay
  for replays and regression.

### Configuration file

`configs/backtests/b001.yaml`:

```yaml
experiment_id: B001
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
  exclude_estimated_flag_rows: true
strategy:
  lookback: 5
  holding: 20
  max_positions: 5
exit:
  vol_stop_k: null
  vol_stop_atr_window: 20
normalization:
  divisor: 시가총액
costs:
  commission_bps: 1.5
  tax_bps_sell:   20.0
  slippage_bps:   5.0
cost_sensitivity_multipliers: [0.0, 1.0, 2.0, 3.0]
output_dir: reports/experiments/B001_market_cap_normalized_signal
```

Strict validation. `normalization.divisor` is surface-of-record;
the only accepted value is `시가총액` in this ticket. Reject other
values with a clear error.

### Runs to produce

1. **headline** (A) — B001 strategy with mcap-normalized ranking
2. **A002_replay** (B) — A002 cap_only re-run as direct head-to-head
3. **B0, B1, B2, B3** — context baselines
4. **diagnostic_estimate_included** — same as A 가족 convention
5. **cost_sensitivity** — (A) at multipliers [0, 1, 2, 3]
6. **cost_0_headline**, **cost_0_A002_replay** — for criterion 5 (optional bonus)
7. **trade_mcap_composition.csv** — for criterion 1 verification

### Output files (under `reports/experiments/B001_market_cap_normalized_signal/`)
- `config.yaml`, `metrics.json`, `trades.csv` (headline (A)),
  `signals.csv` (A candidates), `equity_curve.csv` (A),
  `cost_sensitivity.csv`, `report.md`,
  `trade_mcap_composition.csv` (NEW for this ticket)

`종목코드` preserved as 6-digit string (zero-pad fix carried).

### Tests (new files)

`tests/test_flow_ratios_mcap.py`:
- formula: numerator and denominator both correct
- NaN mcap → NaN output
- ≤ 0 mcap → NaN output
- prior-row safety: mutating future panel rows must not change the value at T

`tests/test_b001_strategy.py`:
- sign filter still applies
- ranking by combined_flow_5_mcap, not combined_flow_5
- tie-break on equal combined_flow_5_mcap goes by 종목코드 ascending
- NaN combined_flow_5_mcap candidates dropped

### Order of work
Commit (Claude commits) after each green-test boundary.

1. Feature extension + tests.
2. Strategy module + tests.
3. CLI dispatch and config.
4. Real-panel run on locked data set.

### Completion criteria
- pytest fully green (no A 가족 regression)
- `python -m src.run_experiment --config configs/backtests/b001.yaml`
  produces all required outputs
- All 4 required success criteria computable from `metrics.json` and
  `trade_mcap_composition.csv`

### Out of scope for B001
- Other normalization bases (log mcap, sqrt mcap, 5-day avg mcap)
- Entry trigger (당일 fnv_1 > 5일 평균) — separate ticket, B002 candidate
- Changing universe to lift size cap
- Changing exit, costs, sign filter

## Result summary
DO NOT FILL until backtest is complete.

## Claude review
DO NOT FILL until result files are read.
