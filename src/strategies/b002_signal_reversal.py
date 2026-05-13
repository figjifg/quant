from __future__ import annotations

import pandas as pd

from src.roles.exits import exit_signal_reversal
from src.roles.filters import filter_flow_sign_both_positive
from src.roles.rankings import rank_by_combined_flow_5
from src.roles.triggers import trigger_immediate


FEATURE_COLUMNS = (
    "execution_date",
    "signal_date",
    "종목코드",
    "fnv_5",
    "inv_5",
    "combined_flow_5",
)
UNIVERSE_COLUMNS = ("execution_date", "signal_date", "종목코드")


def build_b002_candidates(
    flow_features: pd.DataFrame,
    universe: pd.DataFrame,
) -> pd.DataFrame:
    """Build B002 entry candidates using the unmodified A-family alpha signal."""
    _require_columns(flow_features, FEATURE_COLUMNS, "flow_features")
    _require_columns(universe, UNIVERSE_COLUMNS, "universe")

    merged = universe.merge(
        flow_features.loc[:, list(FEATURE_COLUMNS)],
        on=list(UNIVERSE_COLUMNS),
        how="inner",
        validate="one_to_one",
    )
    candidates = trigger_immediate(filter_flow_sign_both_positive(merged))
    return rank_by_combined_flow_5(candidates)


def build_b002_signal_exit_features(flow_features: pd.DataFrame) -> pd.DataFrame:
    """Return post-close signal components used by the B002 reversal exit."""
    return exit_signal_reversal(flow_features)["signal_exit_features"]


def _require_columns(data: pd.DataFrame, columns: tuple[str, ...], name: str) -> None:
    missing = [column for column in columns if column not in data.columns]
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")
