# Codex Questions / Blockers

## 2026-05-18 E011/E012/E013 batch

- Blocker: local sandbox Python environment does not have `pandas` installed.
- Impact: `python3 -m src.run_experiment --config configs/backtests/e011.yaml` stops at import time with `ModuleNotFoundError: No module named 'pandas'`.
- Also unavailable: `pytest` (`python3 -m pytest ...` reports `No module named pytest`).

Run after installing the repo dependencies:

```bash
python3 -m src.run_experiment --config configs/backtests/e011.yaml
python3 -m src.run_experiment --config configs/backtests/e012.yaml
python3 -m src.run_experiment --config configs/backtests/e013.yaml
python3 -m pytest tests/test_e011_strategy.py tests/test_e012_strategy.py tests/test_e013_strategy.py
```

## 2026-05-18 E014/E015 batch

- Blocker: local sandbox Python environment still does not have `pandas` installed.
- Impact: `python3 -m src.run_experiment --config configs/backtests/e014.yaml` stops at import time with `ModuleNotFoundError: No module named 'pandas'`.
- Also unavailable: `pytest` command is not installed.
- Completed locally: `python3 -m py_compile src/run_experiment.py src/strategies/e014_rs_breadth_top4.py src/strategies/e015_validation.py tests/test_e014_strategy.py tests/test_e015_strategy.py`.

Run after installing the repo dependencies:

```bash
python3 -m src.run_experiment --config configs/backtests/e014.yaml
python3 -m src.run_experiment --config configs/backtests/e015.yaml
python3 -m pytest tests/test_e014_strategy.py tests/test_e015_strategy.py tests/test_no_lookahead.py
```

## 2026-05-18 H007/H008/H009 batch

- H008 pass/fail issue: the pre-registered spike-year exclusion criterion failed.
- Observed result: `exclude_2020_2025` H001 cumulative return is `0.926100`, below the required `1.30`.
- Other H008 gates passed: 3x cost `2.958140`, 5x cost `2.424757`, +20bps slippage `3.196910`, max single-year contribution share `0.130782`.
- Decision needed from research owner: mark H008 robustness as FAIL on spike-exclusion, revise the criterion in a new ticket, or define an alternate spike-exclusion methodology.
