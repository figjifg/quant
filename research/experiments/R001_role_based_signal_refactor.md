# R001 — Role-based signal refactor (engineering only, no alpha change)

## Status
planned

## Purpose (engineering, not alpha)
사용자가 짚은 architectural 원칙: Layer 1 안에서도 신호들이 **역할 별로
모듈화** 되어야 한다. 현재는 filter / trigger / ranking / exit 가 한 strategy
파일에 섞여 있어서:
- 한 신호가 동시에 여러 역할을 담당 (예: A001 의 `(fnv_5>0) AND (inv_5>0)`
  은 filter 와 trigger 둘 다)
- entanglement: B002 의 entry filter 와 exit signal 이 같은 변수의 거울
- 새 실험 ticket 마다 "이 ticket 이 어느 역할을 건드리는가"가 모호

본 ticket 은 **alpha 변경 없는 순수 리팩토링**. 모든 기존 실험은
byte-identical 결과를 내야 함.

## Hypothesis (refactor outcome, not alpha)
신호 역할을 4가지 (filter / trigger / ranking / exit) 로 분리하여
`src/roles/` 디렉터리에 두면, 향후 실험 ticket 은 명시적으로 "어느 역할의
어느 후보를 변경하는가" 를 한 줄로 선언할 수 있다. 그 결과:
- 한 ticket 안에서 변하는 변수가 명확함
- 사후 promote 시 어떤 역할 위에서 변경된 결과인지 추적 가능
- 코드 측 entanglement 가 디렉터리 구조 측에서 시각화됨

## Failure modes being tested
없음. 이건 alpha 실험이 아니라 코드 정리.

## Strategy type
**Engineering refactor only.** Alpha 변경 없음.

## Scope discipline

가장 엄격한 제약 — **zero semantic change**:

- 모든 기존 실험 (A001~A004, B001, B002) 의 backtest 결과가 refactor 전후
  byte-identical 해야 함. trades.csv, signals.csv, equity_curve.csv,
  metrics.json 까지.
- 기존 104 pytest 모두 그대로 통과.
- 새 unit test 는 추가 가능하지만 기존 test 의 expected value 는 절대
  수정 금지.

## Target directory structure (after refactor)

```
src/
  data/
    equity_panel.py       # unchanged
    universe.py           # unchanged
    market_flow.py        # unchanged (A003)
  features/
    flow_ratios.py        # raw rolling sums and ratios only
    market_gate.py        # raw market-gate features (A003)
  roles/                  # NEW
    __init__.py
    filters.py
    triggers.py
    rankings.py
    exits.py
  strategies/
    a001_fixed_holding.py     # renamed from e001_flow_filter.py — composes roles
    a002_cap_only.py          # NEW thin composer — was inline in engine for E002
    a003_market_gate.py       # renamed from e003_market_gate.py
    a004_strength_quintile.py # renamed from e004_strength_quintile.py
    b001_mcap_normalized.py   # unchanged file path
    b002_signal_reversal.py   # unchanged file path
    baselines.py              # unchanged
  backtest/
    calendar.py           # unchanged
    costs.py              # unchanged
    engine.py             # unchanged signature; internally may delegate to role modules but not required this ticket
  reporting/
    metrics.py            # unchanged
    report.py             # unchanged
  run_experiment.py       # updated to use new strategy module imports
```

Note on file renames: `src/strategies/e001_flow_filter.py` →
`a001_fixed_holding.py` etc. Use `git mv` to preserve history. Import
references throughout the codebase must be updated.

## Role module APIs

Each role module exposes pure functions. Strategies compose them.

### `src/roles/filters.py`

"Filter role: which stocks are eligible to be considered for entry today?"

```python
def filter_flow_sign_both_positive(flow_features: pd.DataFrame) -> pd.DataFrame:
    """Returns flow_features rows where (fnv_5 > 0) AND (inv_5 > 0).
    Preserves all columns. The single-filter used in A001-A004, B001, B002."""
```

Just this one filter function for now. Future tickets add more.

### `src/roles/triggers.py`

"Trigger role: among filtered tickers, when do we actually pull the trigger?"

```python
def trigger_immediate(filtered_features: pd.DataFrame) -> pd.DataFrame:
    """No additional trigger. Filter pass = immediate entry candidate.
    Returns filtered_features unchanged. The only trigger used across all
    A 가족 and B 가족 experiments so far."""
```

Just this one trigger for now. Future tickets add `trigger_acceleration`,
`trigger_volume_confirm`, etc.

### `src/roles/rankings.py`

"Ranking role: among triggered candidates, which to prioritize when slots
are limited?"

```python
def rank_by_combined_flow_5(triggered: pd.DataFrame) -> pd.DataFrame:
    """A 가족 default. Returns triggered with rank_score = combined_flow_5,
    sorted by (execution_date asc, rank_score desc, 종목코드 asc)."""

def rank_by_combined_flow_5_mcap(triggered: pd.DataFrame) -> pd.DataFrame:
    """B001 ranking. Returns triggered with rank_score = combined_flow_5_mcap,
    same sort order."""

def rank_by_recent_return_5(triggered: pd.DataFrame) -> pd.DataFrame:
    """B3 baseline (price momentum). Returns triggered with rank_score =
    recent_return_5, same sort order. Drops rows with NaN recent_return_5."""
```

### `src/roles/exits.py`

"Exit role: when does a held position close?"

Exits are slightly different from filters/triggers/rankings because they
interact with the engine's per-day loop. We expose them as parameter-
builder functions:

```python
def exit_time_cap(holding_cap_days: int) -> dict:
    """A001/A002 default. Returns engine kwargs:
    {'holding': holding_cap_days, 'vol_stop_k': None,
     'vol_stop_atr_window': 20, 'atr_features': None,
     'signal_exit_features': None}."""

def exit_volatility_stop_plus_cap(
    holding_cap_days: int, k: float, atr_window: int, atr_features: pd.DataFrame
) -> dict:
    """A002 original headline (vol stop + cap). Returns engine kwargs with
    vol_stop_k and atr_features set."""

def exit_signal_reversal(flow_features: pd.DataFrame) -> dict:
    """B002 default. Returns engine kwargs:
    {'holding': <safety_only>, 'signal_exit_features': flow_features[
       ['종목코드', '날짜', 'fnv_5', 'inv_5']
    ], 'vol_stop_k': None, 'atr_features': None}.
    The `holding` value should be the engine's existing safety cap default
    (e.g., very large number) since B002 has no time cap."""
```

## Strategy composer pattern

Each strategy module becomes thin:

```python
# src/strategies/a002_cap_only.py
from src.roles import filters, triggers, rankings, exits

def a002_cap_only_setup(
    flow_features: pd.DataFrame, universe: pd.DataFrame, *,
    holding_cap_days: int = 20,
) -> tuple[pd.DataFrame, dict]:
    """Compose A002 cap_only roles. Returns (candidates, engine_kwargs)."""
    filtered = filters.filter_flow_sign_both_positive(flow_features)
    triggered = triggers.trigger_immediate(filtered)
    # Universe join happens here (same as current build_e001_flow_filter_candidates)
    candidates = ... # merge with universe, drop ineligible, apply ranking
    candidates = rankings.rank_by_combined_flow_5(candidates)
    engine_kwargs = exits.exit_time_cap(holding_cap_days=holding_cap_days)
    return candidates, engine_kwargs
```

`run_experiment` then calls `a002_cap_only_setup(...)` and passes both to
`run_candidate_backtest`. Backwards compatibility preserved.

## Codex implementation task

Read this ticket end-to-end. Base commit = latest `main`.

### Order of work

Commit (Claude commits) after each boundary that leaves the test suite green.

1. **Create `src/roles/` skeleton** — empty module files + `__init__.py`.
   No imports yet. pytest must still pass.
2. **Extract filter logic** into `filters.py`. Update one strategy
   (start with a001) to use it. Verify a001's tests still pass.
3. **Extract trigger logic** (the simplest — just a pass-through for now).
   Update a001. Verify tests.
4. **Extract ranking logic** into `rankings.py`. Update strategies that
   use it (a001, a002 indirectly via candidates, b001). Verify tests.
5. **Extract exit logic** into `exits.py`. Update strategies. Verify
   tests.
6. **Rename strategy files** (e001 → a001, e003 → a003, e004 → a004).
   Use `git mv`. Update all imports throughout the codebase. Verify
   tests.
7. **End-to-end regression check**: re-run each existing experiment on
   the real panels. Compare trades.csv, signals.csv, equity_curve.csv,
   metrics.json byte-for-byte with the pre-refactor outputs already
   committed under reports/experiments/. Any difference is a bug.

### Critical regression checks at step 7

For each of A001/A002/A003/A004/B001/B002:

```bash
# Save pre-refactor outputs to a temp location, then rerun and diff:
cp reports/experiments/E001_pipeline_sanity_fixed_holding/trades.csv /tmp/pre_a001_trades.csv
python -m src.run_experiment --config configs/backtests/a001.yaml  # adjust config experiment_id
diff /tmp/pre_a001_trades.csv reports/experiments/E001_pipeline_sanity_fixed_holding/trades.csv
# Must be empty.
```

Note: config files reference `experiment_id` like `E001`, `E002`, etc.
Either keep config experiment_ids unchanged (so dispatcher still finds
them) or update both configs and dispatcher in lockstep. Recommend
**keep config experiment_id unchanged** to minimize friction — only
file/module/test names change, not the public dispatcher contract.

Equally, the `reports/experiments/` folder names should **remain
unchanged** (E001_pipeline_sanity..., etc.) so the historical record
is preserved.

### What MUST stay byte-identical
- All `reports/experiments/*/trades.csv`
- All `reports/experiments/*/signals.csv`
- All `reports/experiments/*/equity_curve.csv`
- All `reports/experiments/*/metrics.json`
- All `reports/experiments/*/cost_sensitivity.csv`
- (If `report.md` includes a generation timestamp, that field is
  exempted; numerics must match.)

### What can change
- Source file paths and module names under `src/strategies/`
- Internal function signatures inside `src/strategies/`
- Test file imports (must still pass)
- `run_experiment.py` imports

### Out of scope for R001
- Engine signature changes (keep `vol_stop_k`, `atr_features`,
  `signal_exit_features` parameters as-is)
- New signal definitions (no new filters, triggers, rankings, or exits
  beyond what already exists in the codebase)
- Changes to costs, calendar, universe, market_flow, market_gate
- Documentation updates beyond docstrings of new role functions
- `configs/backtests/*.yaml` file renames
- `reports/experiments/*/` folder renames

## Result summary
DO NOT FILL until refactor is complete.

## Claude review
DO NOT FILL until tests + regression checks confirm zero semantic change.
