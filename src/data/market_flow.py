from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.backtest.calendar import KRXTradingCalendar


REQUIRED_COLUMNS = ("date", "kospi_foreign_net", "kospi_institution_net")
NUMERIC_COLUMNS = ("kospi_foreign_net", "kospi_institution_net")


def load_market_flow(path: Path | str, calendar: KRXTradingCalendar) -> pd.DataFrame:
    """Load KOSPI market-flow rows aligned to the equity-panel calendar.

    - Rows whose dates are not in the calendar are dropped.
    - Rows where either flow column is NaN are dropped after logging
      the count and the affected date range. Such dates become
      "missing from market_flow" downstream; the gate feature builder
      treats them as conservative gate-off, the same handling already
      in place for start-of-period rows without a full 5-day prior
      window. Per the E003 ticket amendment (2026-05-13).
    - Raises only on missing required columns or duplicate date rows.
    """
    frame = pd.read_csv(path, encoding="utf-8-sig")
    _require_columns(frame, REQUIRED_COLUMNS)

    result = frame.loc[:, list(REQUIRED_COLUMNS)].copy()
    result["date"] = pd.to_datetime(result["date"], errors="raise").dt.normalize()
    for column in NUMERIC_COLUMNS:
        result[column] = pd.to_numeric(result[column], errors="raise")

    if result.duplicated("date").any():
        raise ValueError("Market-flow file contains duplicate date rows.")

    calendar_dates = pd.Index(calendar.dates)
    result = result.loc[result["date"].isin(calendar_dates)].copy()

    nan_mask = result.loc[:, list(NUMERIC_COLUMNS)].isna().any(axis=1)
    if bool(nan_mask.any()):
        dropped = result.loc[nan_mask, "date"]
        print(
            f"[load_market_flow] Dropping {len(dropped)} NaN row(s) "
            f"from {dropped.min().date()} to {dropped.max().date()}; "
            "downstream gate treats these dates as gate-off."
        )
        result = result.loc[~nan_mask].copy()

    return result.sort_values("date").set_index("date")


def _require_columns(frame: pd.DataFrame, columns: tuple[str, ...]) -> None:
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise ValueError(f"Market-flow file is missing required columns: {missing}")
