from __future__ import annotations

import pandas as pd


FEATURE_COLUMNS = (
    "execution_date",
    "signal_date",
    "종목코드",
    "fnv_5",
    "inv_5",
    "combined_flow_5",
    "combined_flow_5_mcap",
)
UNIVERSE_COLUMNS = ("execution_date", "signal_date", "종목코드")


def build_b001_mcap_normalized_candidates(
    flow_features: pd.DataFrame,
    universe: pd.DataFrame,
) -> pd.DataFrame:
    """Build B001 entry candidates ranked by market-cap-normalized flow."""
    _require_columns(flow_features, FEATURE_COLUMNS, "flow_features")
    _require_columns(universe, UNIVERSE_COLUMNS, "universe")

    merged = universe.merge(
        flow_features.loc[:, list(FEATURE_COLUMNS)],
        on=list(UNIVERSE_COLUMNS),
        how="inner",
        validate="one_to_one",
    )
    candidates = merged.loc[
        merged["fnv_5"].gt(0)
        & merged["inv_5"].gt(0)
        & merged["combined_flow_5_mcap"].notna()
    ].copy()
    return candidates.sort_values(
        ["execution_date", "combined_flow_5_mcap", "종목코드"],
        ascending=[True, False, True],
    ).reset_index(drop=True)


def _require_columns(data: pd.DataFrame, columns: tuple[str, ...], name: str) -> None:
    missing = [column for column in columns if column not in data.columns]
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")
