from __future__ import annotations

import pandas as pd


def filter_flow_sign_both_positive(flow_features: pd.DataFrame) -> pd.DataFrame:
    """Return rows where both 5-day foreign and institutional flows are positive."""
    _require_columns(flow_features, ("fnv_5", "inv_5"), "flow_features")
    return flow_features.loc[flow_features["fnv_5"].gt(0) & flow_features["inv_5"].gt(0)].copy()


def _require_columns(data: pd.DataFrame, columns: tuple[str, ...], name: str) -> None:
    missing = [column for column in columns if column not in data.columns]
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")
