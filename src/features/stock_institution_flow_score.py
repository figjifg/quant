from __future__ import annotations

from collections.abc import Sequence

import pandas as pd

from src.features.stock_rs_score import quarter_end_dates


REQUIRED_STOCK_COLUMNS = (
    "date",
    "ticker",
    "sector_code",
    "sector_name",
    "market_cap",
    "traded_value",
    "institution_net_buy_amount",
    "daily_return",
)


def build_stock_institution_flow_scores(
    stock_daily: pd.DataFrame,
    *,
    signal_dates: Sequence[object] | None = None,
    value_window: int = 20,
    mcap_window: int = 60,
    min_sector_stocks: int = 2,
) -> pd.DataFrame:
    """Compute stock-level institution flow scores with signal-date data only.

    Missing stock-level institution flow inputs are preserved as NaN. A stock
    is score-eligible only when both rolling components are fully observed.
    """
    _require_columns(stock_daily, REQUIRED_STOCK_COLUMNS, "stock_daily")
    if value_window <= 0 or mcap_window <= 0:
        raise ValueError("value_window and mcap_window must be positive.")
    if min_sector_stocks <= 0:
        raise ValueError("min_sector_stocks must be positive.")

    stocks = _normalize_stock_daily(stock_daily).dropna(subset=["sector_code"]).copy()
    stocks = stocks.sort_values(["ticker", "date"]).reset_index(drop=True)
    by_stock = stocks.groupby("ticker", sort=False)

    stocks["institution_net_buy_amount_20d"] = by_stock["institution_net_buy_amount"].transform(
        lambda values: values.rolling(value_window, min_periods=value_window).sum()
    )
    stocks["traded_value_20d"] = by_stock["traded_value"].transform(
        lambda values: values.rolling(value_window, min_periods=value_window).sum()
    )
    stocks["institution_net_buy_amount_60d"] = by_stock["institution_net_buy_amount"].transform(
        lambda values: values.rolling(mcap_window, min_periods=mcap_window).sum()
    )
    stocks["institution_flow_20"] = stocks["institution_net_buy_amount_20d"] / stocks["traded_value_20d"]
    stocks["institution_flow_60"] = stocks["institution_net_buy_amount_60d"] / stocks["market_cap"]
    invalid_denominator = stocks["traded_value_20d"].le(0) | stocks["market_cap"].le(0)
    stocks.loc[invalid_denominator, ["institution_flow_20", "institution_flow_60"]] = pd.NA
    stocks["raw_stock_institution_flow_score"] = stocks[
        ["institution_flow_20", "institution_flow_60"]
    ].mean(axis=1, skipna=False)

    selected_dates = _normalize_signal_dates(signal_dates) if signal_dates is not None else quarter_end_dates(stocks)
    scores = stocks.loc[stocks["date"].isin(selected_dates)].copy()
    valid_raw = scores["raw_stock_institution_flow_score"].notna()
    sector_valid_counts = valid_raw.groupby([scores["date"], scores["sector_code"]]).transform("sum")
    scores["eligible_for_score"] = valid_raw & sector_valid_counts.ge(min_sector_stocks)
    scores.loc[~scores["eligible_for_score"], "raw_stock_institution_flow_score"] = pd.NA
    scores["stock_institution_flow_score"] = scores.groupby(["date", "sector_code"], group_keys=False)[
        "raw_stock_institution_flow_score"
    ].transform(_zscore)
    return scores.loc[
        :,
        [
            "date",
            "ticker",
            "sector_code",
            "sector_name",
            "market_cap",
            "traded_value",
            "institution_net_buy_amount",
            "daily_return",
            "institution_net_buy_amount_20d",
            "traded_value_20d",
            "institution_flow_20",
            "institution_net_buy_amount_60d",
            "institution_flow_60",
            "raw_stock_institution_flow_score",
            "stock_institution_flow_score",
            "eligible_for_score",
        ],
    ].rename(columns={"date": "signal_date"}).reset_index(drop=True)


def _normalize_stock_daily(stock_daily: pd.DataFrame) -> pd.DataFrame:
    daily = stock_daily.loc[:, REQUIRED_STOCK_COLUMNS].copy()
    daily["date"] = pd.to_datetime(daily["date"], errors="raise").dt.normalize()
    daily["ticker"] = daily["ticker"].astype("string").str.zfill(6)
    daily["sector_code"] = _sector_code(daily["sector_code"])
    daily["sector_name"] = daily["sector_name"].astype("string")
    for column in ("market_cap", "traded_value", "institution_net_buy_amount", "daily_return"):
        daily[column] = pd.to_numeric(daily[column], errors="coerce")
    return daily


def _normalize_signal_dates(signal_dates: Sequence[object]) -> list[pd.Timestamp]:
    return sorted(pd.to_datetime(pd.Index(signal_dates), errors="raise").normalize().unique())


def _sector_code(values: pd.Series) -> pd.Series:
    return values.astype("string").str.strip().str.replace(r"\.0$", "", regex=True).str.zfill(2)


def _zscore(values: pd.Series) -> pd.Series:
    valid = pd.to_numeric(values, errors="coerce")
    std = valid.std(ddof=0)
    if pd.isna(std) or std == 0:
        return pd.Series(pd.NA, index=values.index, dtype="Float64")
    return (valid - valid.mean()) / std


def _require_columns(data: pd.DataFrame, columns: tuple[str, ...], name: str) -> None:
    missing = [column for column in columns if column not in data.columns]
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")
