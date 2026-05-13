# B002 — Signal-reversal exit, bare alpha (B family experiment #2)

## Alpha family taxonomy
- A 가족: 거래대금 정규화 + 시간 기반 청산. A001(5일)~A004(quintile).
- B 가족: alpha 자체에서 비롯된 변경. B001(시총 정규화)→kill, B002 이 ticket.

## Status
planned

## Purpose (alpha-level)
A001~A004 + B001 다섯 차례 실험을 통해 다음 사실들이 정리됨:

- A002 cap_only OOS +0.688 가운데 약 +0.55 는 "size 효과" — 시총 3~5조
  thematic 중형주로 자연스럽게 몰린 결과. 알파 자체는 +0.14 수준.
- OOS 알파의 약 92%가 **2025 Q2 단일 분기**에 발생. 4년의 음수 시기와
  1년의 폭발 시기. 시장 환경 의존성 매우 큼.
- 20일 시간 cap은 이론적 근거 없는 임의의 숫자. 외국인 보유 기간이
  20일이라는 실증적 근거는 없음.

사용자 결정: 누적된 모든 조건을 덜어내고 **알파 자체와 알파에서 비롯된
청산 조건만** 가지고 다시 시작. "첫 단추를 제대로 끼우자."

## Hypothesis
진입은 `(fnv_5 > 0) AND (inv_5 > 0)` (A 가족의 알파 정의 그대로).
청산은 **신호의 정확한 부정**: 보유 중 어느 날 `(fnv_5 ≤ 0) OR (inv_5 ≤ 0)`
이면 그 다음 거래일 시가에 매도. **추세가 꺾이면 매도** 라는 추세추종의
자연스러운 청산.

검증할 것: 시간 기반 청산(고정 20일)이 아니라 신호 기반 청산으로 바꿔도
A002 cap_only의 OOS 수익률(+0.688) 수준을 유지하거나, 만약 떨어지더라도
**OOS net 양수는 유지** 한다. 동시에 평균 보유 기간이 외국인+기관 자금
유입의 자연스러운 길이를 보여준다 (이건 가설 아닌 description).

## Failure modes being tested
- **신호가 너무 자주 꺾여서 회전율 폭발**: 5일 누적이 음수로 자주
  넘나들면 청산이 며칠마다 일어나고 비용 누적. 알파는 사라짐.
- **신호가 거의 안 꺾여서 무한 보유**: 외국인+기관이 한 종목을 길게
  들고 있는 동안 5일 누적이 항상 양수. 사실상 buy-and-hold가 됨.
- **알파가 시간 cap에서 나온 것**: A002 cap_only가 우연히 20일에 최적
  타이밍에 청산했다면, 신호 기반 청산이 그 시점을 못 맞춰서 알파 감소.

이 세 가지 failure mode 모두 결과 보고 판단할 사항. 사전 동결한 pass/fail
threshold 없음.

## Strategy type
B 가족 두 번째 실험. **추세추종의 자연스러운 청산**을 처음 시도.

## Signal definition (unchanged from A 가족)

```
fnv_5 = rolling_sum(외국인순매수금액추정, 5td) / rolling_sum(거래대금추정, 5td)
inv_5 = rolling_sum(기관순매수금액추정,   5td) / rolling_sum(거래대금추정, 5td)
combined_flow_5 = (외국인+기관 5td) / 거래대금 5td  # tie-break 용도만
```

진입 조건:
```
entry_signal_T = (fnv_5(T) > 0) AND (inv_5(T) > 0)
```

`combined_flow_5` 는 슬롯 초과 시 tie-break (큰 값부터) 용도로만 사용
(A 가족과 동일).

## Entry rule (unchanged from A 가족)

- signal_date = T
- execution_date = T+1
- entry_price = T+1 KRX 09:00 시가
- 시가 NaN 또는 ≤ 0 → 진입 스킵
- 동일 종목 중복 진입 금지 (이미 보유 중이면 그 종목은 다음 진입 후보에서 제외)
- max_positions = 5

## Exit rule (NEW for B002)

매 거래일 d 에 대해, 보유 중 슬롯마다:

1. **신호 반전 체크**: 그 종목의 d-1까지 데이터로 계산한 `fnv_5(d-1) ≤ 0
   OR inv_5(d-1) ≤ 0` 인가? (즉, 그 종목의 5일 누적 신호가 두 컴포넌트
   중 하나라도 양수에서 비양수로 바뀌었는가?)
   - 그렇다 → 그 다음 거래일(d+1) 시가에 매도. exit_reason = "signal_reversal"
   - 아니다 → 보유 유지

2. **시가 결측 대응**: 청산 예정 거래일의 시가가 NaN 또는 ≤ 0 이면, 그
   다음 유효한 거래일 시가까지 청산 이연. exit_reason = "signal_reversal_fallback"

3. **period_end**: IS 또는 OOS 기간 끝나는 날까지 청산 안 됐으면 그 날
   KRX 종가로 강제 청산. exit_reason = "period_end"

**시간 cap 없음. 변동성 stop 없음. 손절·익절 없음.** 청산을 결정하는 유일한
근거는 신호 자체의 양·음.

청산 신호 확인 시점에 주의:
- 매수는 T+1 시가에 진행 (사용된 신호 = T일 마감 후 데이터)
- 매수 후 d일 마감 후 데이터로 청산 신호 평가 → d+1 시가에 매도
- 즉 청산도 신호일 t 데이터 → 체결일 t+1 시가 패턴으로 entry와 동일

## Holding period
가변. 신호가 자연스럽게 꺾이는 시점까지. 보유 기간의 분포가 실험 결과의
핵심 description 중 하나.

## Universe (unchanged from A 가족)

- 동적 Top100 포함 (`동적유니버스포함 == True` on most recent `날짜 ≤ T-1`)
- 20-row mean 거래대금추정 ≥ 50억 원
- 거래대금추정여부 == False on each of 5 signal-window rows

## Data assumptions

**Locked data set**: 동일 panel 둘. 추가 데이터 없음.

- IS: dynamic_top100_2018_2024_panel.csv
- OOS: dynamic_top100_2025_2026_krx_panel.csv
- IS period: 2018-01-02 ~ 2022-12-30
- OOS period: 2023-01-02 ~ 2026-05-04

## Cost assumptions (unchanged)
- commission_bps = 1.5, tax_bps_sell = 20.0, slippage_bps = 5.0
- cost_sensitivity_multipliers = [0.0, 1.0, 2.0, 3.0]

## Baseline comparison

**Layer 1 — direct head-to-head**
- `B_A002_replay` — A002 cap_only 재실행. 같은 진입 신호·universe, 청산만
  20일 cap. 시간 청산 vs 신호 청산의 head-to-head.

**Layer 2 — context**
- B0_cash, B1, B2, B3 — 기존대로 (E001 vintage defects 인정하고 유지)

## Parameters to test
**None.** 단일 점. 자유도 0.

| Parameter | Value | Rationale |
|---|---|---|
| 청산 조건 | (fnv_5 ≤ 0) OR (inv_5 ≤ 0) | 진입 조건의 정확한 부정. 임계값·버퍼 없음 |
| 시간 cap | **없음** | 의도적 제거 |
| Vol stop | **없음** | 의도적 제거 |
| Max positions | 5 | A 가족 carry-over |
| 모든 universe / cost params | A 가족과 동일 | Lock |

## Parameters that must NOT be optimized
- 청산 임계값 (≤ 0 strictly, no -0.01 buffer)
- 시간 cap 도입 (의도적으로 없음)
- 다른 모든 A 가족 carry-over
- IS/OOS boundary

만약 후속 실험에서 청산 임계값에 버퍼를 두거나 시간 cap을 다시 도입한다면,
**별도 사전 등록 ticket** 으로.

## Diagnostic split (within this ticket)

- **(A) B002 headline** — signal reversal exit
- **(B) A002_replay** — 20-day cap exit (cap_only)
- (No other variants this ticket — keep it simple per the user's
  "strip everything" directive.)

## Reportable metrics (no pass/fail thresholds this time)

사용자의 "차후 계획은 결과 보고 진행" 지침에 따라 사전 pass/fail
threshold 없음. 결과 보고 사용자가 판단할 description metrics:

1. **OOS net total_return** of (A) and (B)
2. **OOS hit_rate** of (A) and (B)
3. **OOS trade_count** of (A) and (B)
4. **OOS average holding period (trading days)** of (A) and (B)
   — 평균 보유 기간 분포가 이번 실험의 핵심 새 정보
5. **OOS cost_paid_total** of (A) and (B)
6. **OOS turnover** of (A) and (B)
7. **연도별 OOS hit_rate 와 누적 pnl** of (A) — regime dependency 재확인
8. **OOS 평균 보유 기간 분포** (mean, median, percentiles) — 외국인+기관
   신호의 자연스러운 지속 길이

추가 디스크립티브 지표:
- exit_reason 분포 (signal_reversal vs period_end vs fallback)
- cost-0 OOS net of (A) and (B) — 비용 절감 효과 vs 정보 가치 분해

## Kill criteria (minimal — only for clearly broken outcomes)

- pytest regression on A 가족 suite
- OOS trade_count < 30 (통계 신뢰 부족)
- 모든 trade가 period_end 로 청산됨 (signal reversal 한 번도 안 발동 = 신호 정의 버그)

## Expected weaknesses

- **고빈도 청산 가능성**: 5일 누적 신호가 짧은 변동에 자주 음수로 넘나들면
  trade 평균 보유가 3~5일로 떨어지고 회전율 ↑. A002 의 회전율 절감 효과가
  사라짐.
- **장기 보유 가능성**: 외국인+기관이 한 종목을 길게 들고 있는 동안 5일
  누적이 계속 양수면 사실상 buy-and-hold. 자본 효율 ↓.
- **두 컴포넌트의 OR 조건**: 한쪽만 음수로 가도 청산. 더 보수적(빠른 청산).
  AND 조건(둘 다 음수일 때만 청산)으로 바꾸면 보유 더 길어짐. 본 ticket은
  OR 사용 (사용자가 제안한 "신호 = 둘 다 양수의 부정 = OR" 논리 그대로).

## Codex implementation task

Read this ticket end-to-end. Read AGENTS.md, CLAUDE.md, and at least the
A002 review (E002_review) for cap_only context. Base commit = latest
`main`.

### Scope discipline (additive only)

Touch:
- `src/backtest/engine.py` — add optional `signal_exit_features`
  parameter and a new exit-condition path. Engine signature extension:

```python
def run_candidate_backtest(
    panel, calendar, candidates, costs, period_start, period_end,
    *, max_positions=5, holding=5, initial_cash=1.0,
    vol_stop_k=None, vol_stop_atr_window=20, atr_features=None,
    signal_exit_features=None,
) -> BacktestResult
```

When `signal_exit_features is not None`, the engine uses signal-based
exit logic and **ignores `holding`** (no time cap). When None, behavior
unchanged.

`signal_exit_features` is a DataFrame with columns:
`종목코드`, `날짜`, `fnv_5`, `inv_5`. Per (종목코드, d-1) lookup.

Daily routine in signal-exit mode:
1. For each held slot, look up `fnv_5(slot.ticker, current_date)` and
   `inv_5(slot.ticker, current_date)`. (d-1 in the slot's day index = d
   in this loop's previous iteration; just use the current_date's signal
   values for the held ticker. Document this timing explicitly.)
2. If `fnv_5 ≤ 0 OR inv_5 ≤ 0` (or either is NaN, treated as ≤ 0 for
   safety): schedule exit at next trading day open, exit_reason =
   "signal_reversal".
3. On the scheduled exit day, exit at 시가. If 시가 NaN or ≤ 0, defer
   to next valid open, exit_reason = "signal_reversal_fallback".

Engine must continue to support A 가족 backwards compatibility:
- `signal_exit_features=None` + `vol_stop_k=None` → fixed-holding (A001)
- `signal_exit_features=None` + `vol_stop_k=2.0` → vol stop + cap (A002 headline)
- `signal_exit_features=None` + `vol_stop_k=None` + `holding=20` → cap_only (A002 reverted)
- `signal_exit_features=<frame>` → B002 mode (this ticket)

- `src/strategies/b002_signal_reversal.py` (NEW)
  - Single function `build_b002_candidates(flow_features, universe)`
    returning A001-style candidates with the standard schema.
  - Plus `build_b002_signal_exit_features(flow_features)` returning the
    `signal_exit_features` frame for the engine.
- `src/run_experiment.py` — add `experiment_id == "B002"` dispatch.
  Two runs: (A) B002 with signal exit + (B) A002 cap_only re-run.
  Plus B0~B3 baselines, cost sensitivity on (A), cost-0 for (A) and
  (B).
- `configs/backtests/b002.yaml` (NEW).
- `tests/test_engine_signal_exit.py` (NEW) — 5 cases:
  1. Signal reversal triggers exit on next-day open
  2. Signal stays positive → position held indefinitely until period_end
  3. NaN signal during hold treated as reversal (conservative)
  4. signal_exit_features=None preserves A 가족 fixed-holding behavior
  5. Fallback when next-day open is NaN

### Configuration file

```yaml
experiment_id: B002
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
  max_positions: 5
exit:
  type: signal_reversal
costs:
  commission_bps: 1.5
  tax_bps_sell:   20.0
  slippage_bps:   5.0
cost_sensitivity_multipliers: [0.0, 1.0, 2.0, 3.0]
output_dir: reports/experiments/B002_signal_reversal_exit
```

No `holding` key in `strategy` (intentionally absent because signal-exit
mode ignores it). No `exit.vol_stop_k` (intentionally absent).
Validation: `exit.type` must be exactly `signal_reversal` for this
ticket.

### Output files

Under `reports/experiments/B002_signal_reversal_exit/`:
- config.yaml, metrics.json, trades.csv, signals.csv,
  equity_curve.csv, cost_sensitivity.csv, report.md
- **holding_period_distribution.csv** — histogram of OOS trade holding
  periods (in KRX trading days), with mean/median/percentile rows for
  both (A) B002 and (B) A002_replay
- **exit_reason_breakdown.csv** — count and percentage by exit_reason
  for both (A) and (B), IS and OOS separately

종목코드 zero-padding still preserved.

### Tests

Existing 96 tests must remain green. New `test_engine_signal_exit.py`
brings ~5 more → ~101.

### Order of work
Commit (Claude commits) after each green-test boundary.

1. Engine extension + tests.
2. Strategy module + tests.
3. CLI dispatch + config.
4. Real-panel run.

### Completion criteria
- pytest fully green
- `python -m src.run_experiment --config configs/backtests/b002.yaml`
  produces every required output
- Both holding_period_distribution.csv and exit_reason_breakdown.csv
  populated

### Out of scope for B002

- Time cap of any kind (including 60d/90d safety net)
- Vol stop
- Different exit conditions (AND instead of OR, or threshold buffer)
- Universe changes
- Sector or market gate
- New data sources

## Result summary
DO NOT FILL until backtest is complete.

## Claude review
DO NOT FILL until result files are read.
