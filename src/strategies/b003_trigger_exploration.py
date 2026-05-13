from __future__ import annotations

import pandas as pd

from src.roles.exits import exit_signal_reversal
from src.roles.filters import filter_flow_sign_both_positive
from src.roles.rankings import rank_by_combined_flow_5
from src.roles.triggers import (
    trigger_acceleration,
    trigger_freshness,
    trigger_immediate,
    trigger_persistence_3d,
)


TRIGGER_CANDIDATES = ("immediate", "freshness", "acceleration", "persistence_3d")
FEATURE_COLUMNS = (
    "execution_date",
    "signal_date",
    "종목코드",
    "fnv_5",
    "inv_5",
    "combined_flow_1",
    "combined_flow_5",
)
UNIVERSE_COLUMNS = ("execution_date", "signal_date", "종목코드")


def build_b003_trigger_exploration(
    flow_features: pd.DataFrame,
    universe: pd.DataFrame,
) -> tuple[dict[str, pd.DataFrame], dict[str, object]]:
    """Build B003 trigger variants on the fixed B002 carrier roles."""
    _require_columns(flow_features, FEATURE_COLUMNS, "flow_features")
    _require_columns(universe, UNIVERSE_COLUMNS, "universe")

    merged = universe.merge(
        flow_features.loc[:, list(FEATURE_COLUMNS)],
        on=list(UNIVERSE_COLUMNS),
        how="inner",
        validate="one_to_one",
    )
    filtered = filter_flow_sign_both_positive(merged)
    triggered = {
        "immediate": trigger_immediate(filtered),
        "freshness": trigger_freshness(filtered, flow_features),
        "acceleration": trigger_acceleration(filtered, flow_features),
        "persistence_3d": trigger_persistence_3d(filtered, flow_features),
    }
    candidates = {name: rank_by_combined_flow_5(triggered[name]) for name in TRIGGER_CANDIDATES}
    return candidates, exit_signal_reversal(flow_features)


def _require_columns(data: pd.DataFrame, columns: tuple[str, ...], name: str) -> None:
    missing = [column for column in columns if column not in data.columns]
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")
