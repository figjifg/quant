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


def exit_signal_reversal_z(z_features: pd.DataFrame) -> dict[str, object]:
    """Return engine kwargs for z-score-relative signal-reversal exits."""
    _require_columns(z_features, ("날짜", "종목코드", "fnv_5_z", "inv_5_z"), "z_features")
    signal_exit_features = z_features.loc[:, ["날짜", "종목코드", "fnv_5_z", "inv_5_z"]].rename(
        columns={"fnv_5_z": "fnv_5", "inv_5_z": "inv_5"}
    )
    return {
        "holding": 5,
        "vol_stop_k": None,
        "vol_stop_atr_window": 20,
        "atr_features": None,
        "signal_exit_features": signal_exit_features.copy(),
    }


def exit_signal_reversal_rel(rel_features: pd.DataFrame) -> dict[str, object]:
    """Return engine kwargs for median-relative signal-reversal exits."""
    _require_columns(rel_features, ("날짜", "종목코드", "fnv_5_rel", "inv_5_rel"), "rel_features")
    signal_exit_features = rel_features.loc[:, ["날짜", "종목코드", "fnv_5_rel", "inv_5_rel"]].rename(
        columns={"fnv_5_rel": "fnv_5", "inv_5_rel": "inv_5"}
    )
    return {
        "holding": 5,
        "vol_stop_k": None,
        "vol_stop_atr_window": 20,
        "atr_features": None,
        "signal_exit_features": signal_exit_features.copy(),
    }


def exit_on_gate_off(gate_off_signal_dates: set[pd.Timestamp]) -> dict[str, object]:
    """Return engine kwargs for exits at next open after a regime gate-off flip."""
    return {
        "holding": 5,
        "vol_stop_k": None,
        "vol_stop_atr_window": 20,
        "atr_features": None,
        "signal_exit_features": None,
        "gate_exit_signal_dates": {pd.Timestamp(date).normalize() for date in gate_off_signal_dates},
    }


def _require_columns(data: pd.DataFrame, columns: tuple[str, ...], name: str) -> None:
    missing = [column for column in columns if column not in data.columns]
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")
