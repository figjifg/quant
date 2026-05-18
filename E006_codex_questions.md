# E006 Codex Questions / Blockers

## Environment blocker

The E006 implementation compiles with the system Python, but the sandbox cannot run pytest or the experiment because the available interpreter has no project dependencies installed.

Observed commands:

```bash
python3 -m py_compile src/features/sector_combined_score.py src/strategies/e006_flow_plus_rs.py src/run_experiment.py tests/test_sector_combined_score.py tests/test_no_lookahead.py
python3 -m pytest tests/test_sector_combined_score.py tests/test_sector_flow_score.py tests/test_sector_rs_score.py -q
python3 -m src.run_experiment --config configs/backtests/e006.yaml
```

Results:

```text
py_compile: passed
pytest: /usr/bin/python3: No module named pytest
experiment run: ModuleNotFoundError: No module named 'pandas'
```

To complete the generated E006 outputs, run the following in the repo environment that has `requirements.txt` installed:

```bash
python -m pytest tests/test_sector_combined_score.py tests/test_no_lookahead.py -q
python -m pytest -q
python -m src.run_experiment --config configs/backtests/e006.yaml
```
