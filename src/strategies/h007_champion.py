from __future__ import annotations

from pathlib import Path
from typing import Any

from src.run_experiment import run_h001_experiment


def run_h007_champion_registration(config: dict[str, Any], config_path: str | Path) -> None:
    """Register H001 under H007 without changing the frozen H001 carrier."""
    h001_config = dict(config)
    h001_config["experiment_id"] = "H001"
    run_h001_experiment(h001_config, Path(config_path))
