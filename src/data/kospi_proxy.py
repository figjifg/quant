from __future__ import annotations

from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = ("date", "cap_weighted_return")
OUTPUT_COLUMNS = ("kospi_proxy_level", "kospi_proxy_sma_200")


def load_kospi_proxy(path: str | Path, *, window: int = 200) -> pd.DataFrame:
    """Load KOSPI breadth returns and derive a cumulative proxy level."""
    if window <= 0:
        raise ValueError("window must be positive.")

    frame = pd.read_csv(path, encoding="utf-8-sig")
    return build_kospi_proxy(frame, window=window)


def build_kospi_proxy(frame: pd.DataFrame, *, window: int = 200) -> pd.DataFrame:
    """Build proxy level and same-day SMA from cap-weighted returns."""
    if window <= 0:
        raise ValueError("window must be positive.")
    _require_columns(frame, REQUIRED_COLUMNS, "kospi_proxy_source")

    data = frame.loc[:, list(REQUIRED_COLUMNS)].copy()
    data["date"] = pd.to_datetime(data["date"], errors="raise").astype("datetime64[ns]")
    data["cap_weighted_return"] = pd.to_numeric(data["cap_weighted_return"], errors="raise")
    if data["date"].duplicated().any():
        raise ValueError("KOSPI proxy source contains duplicate date rows.")

    data = data.sort_values("date").reset_index(drop=True)
    level = (1.0 + data["cap_weighted_return"]).cumprod()
    result = pd.DataFrame(
        {
            "kospi_proxy_level": level.to_numpy(),
            "kospi_proxy_sma_200": level.rolling(window, min_periods=window).mean().to_numpy(),
        },
        index=pd.Index(data["date"], name="date"),
    )
    return result.loc[:, list(OUTPUT_COLUMNS)]


def _require_columns(data: pd.DataFrame, columns: tuple[str, ...], name: str) -> None:
    missing = [column for column in columns if column not in data.columns]
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")
