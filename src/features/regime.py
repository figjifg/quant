from __future__ import annotations

import pandas as pd


REQUIRED_COLUMNS = ("kospi_proxy_level", "kospi_proxy_sma_200")


def regime_gate_on(kospi_proxy: pd.DataFrame) -> pd.Series:
    """Return KOSPI proxy SMA gate state by signal date."""
    _require_columns(kospi_proxy, REQUIRED_COLUMNS, "kospi_proxy")
    level = pd.to_numeric(kospi_proxy["kospi_proxy_level"], errors="coerce")
    sma = pd.to_numeric(kospi_proxy["kospi_proxy_sma_200"], errors="coerce")
    gate = level.gt(sma) & sma.notna()
    return pd.Series(gate.to_numpy(dtype=bool), index=kospi_proxy.index, name="regime_gate_on")


def regime_state_log(kospi_proxy: pd.DataFrame) -> pd.DataFrame:
    """Return reportable regime state rows indexed by signal_date."""
    gate = regime_gate_on(kospi_proxy)
    return pd.DataFrame(
        {
            "signal_date": pd.to_datetime(kospi_proxy.index, errors="raise"),
            "kospi_proxy_level": kospi_proxy["kospi_proxy_level"].to_numpy(),
            "kospi_proxy_sma_200": kospi_proxy["kospi_proxy_sma_200"].to_numpy(),
            "regime_gate_on": gate.to_numpy(dtype=bool),
        }
    )


def _require_columns(data: pd.DataFrame, columns: tuple[str, ...], name: str) -> None:
    missing = [column for column in columns if column not in data.columns]
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")
