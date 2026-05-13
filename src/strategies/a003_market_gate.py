from __future__ import annotations

import pandas as pd

from src.roles.rankings import rank_by_combined_flow_5
from src.strategies.a001_fixed_holding import build_e001_flow_filter_candidates


GATE_KEY_COLUMNS = ("signal_date", "execution_date")


def build_e003_market_gated_candidates(
    flow_features: pd.DataFrame,
    universe: pd.DataFrame,
    market_gate_features: pd.DataFrame,
    gate_column: str,
) -> pd.DataFrame:
    """Build E001 candidates and drop rows where the selected market gate is off."""
    if gate_column not in market_gate_features.columns:
        raise ValueError(f"market_gate_features is missing gate column: {gate_column}")
    _require_columns(market_gate_features, GATE_KEY_COLUMNS, "market_gate_features")

    candidates = build_e001_flow_filter_candidates(flow_features, universe)
    if candidates.empty:
        return candidates

    gate = market_gate_features.loc[:, [*GATE_KEY_COLUMNS, gate_column]].copy()
    for column in GATE_KEY_COLUMNS:
        gate[column] = pd.to_datetime(gate[column], errors="raise").astype("datetime64[ns]")
    if gate.duplicated(list(GATE_KEY_COLUMNS)).any():
        raise ValueError("market_gate_features contains duplicate signal/execution date rows.")

    merged = candidates.merge(
        gate,
        on=list(GATE_KEY_COLUMNS),
        how="left",
        validate="many_to_one",
    )
    filtered = merged.loc[merged[gate_column].fillna(False).astype(bool), candidates.columns].copy()
    return rank_by_combined_flow_5(filtered)


def _require_columns(data: pd.DataFrame, columns: tuple[str, ...], name: str) -> None:
    missing = [column for column in columns if column not in data.columns]
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")
