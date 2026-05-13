from __future__ import annotations

import pandas as pd


def exit_time_cap(holding_cap_days: int) -> dict[str, object]:
    """Return engine kwargs for a fixed holding-period cap."""
    return {
        "holding": holding_cap_days,
        "vol_stop_k": None,
        "vol_stop_atr_window": 20,
        "atr_features": None,
        "signal_exit_features": None,
    }


def exit_volatility_stop_plus_cap(
    holding_cap_days: int,
    k: float,
    atr_window: int,
    atr_features: pd.DataFrame,
) -> dict[str, object]:
    """Return engine kwargs for volatility stop plus fixed holding cap."""
    return {
        "holding": holding_cap_days,
        "vol_stop_k": k,
        "vol_stop_atr_window": atr_window,
        "atr_features": atr_features,
        "signal_exit_features": None,
    }


def exit_signal_reversal(flow_features: pd.DataFrame) -> dict[str, object]:
    """Return engine kwargs for B002's signal-reversal exit."""
    _require_columns(flow_features, ("날짜", "종목코드", "fnv_5", "inv_5"), "flow_features")
    return {
        "holding": 5,
        "vol_stop_k": None,
        "vol_stop_atr_window": 20,
        "atr_features": None,
        "signal_exit_features": flow_features.loc[:, ["날짜", "종목코드", "fnv_5", "inv_5"]].copy(),
    }


def _require_columns(data: pd.DataFrame, columns: tuple[str, ...], name: str) -> None:
    missing = [column for column in columns if column not in data.columns]
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")
