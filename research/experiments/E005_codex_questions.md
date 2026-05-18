# E005 Codex Questions

## Blocker

The workspace Python environment cannot run the required verification or
experiment because core dependencies are not installed:

- `pytest`: command not found
- `python3 -m pytest`: `No module named pytest`
- `python3` import check: `No module named pandas`

Network access and package installation were not approved for this task, so I
stopped before generating E005 report outputs.

## Question

Which environment should Codex use to run E005?

Expected next step after the environment is available:

```bash
python3 -m pytest tests/test_sector_rs_score.py
python3 -m pytest
python3 -m src.run_experiment --config configs/backtests/e005.yaml
```
