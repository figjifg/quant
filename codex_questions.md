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
