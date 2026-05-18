from __future__ import annotations

from collections.abc import Sequence

import pandas as pd

from src.features.sector_flow_score import (
    build_rank_ic_diagnostics as _build_flow_rank_ic_diagnostics,
    build_sector_forward_returns,
    build_subperiod_diagnostics,
    build_top_bottom_spread_diagnostics as _build_flow_top_bottom_spread_diagnostics,
    diagnostics_pass,
    quarter_end_dates,
)
from src.features.sector_flow_score import _require_columns, _zscore


REQUIRED_STOCK_COLUMNS = (
    "date",
    "ticker",
    "sector_code",
    "sector_name",
    "market_cap",
    "foreign_net_buy_amount",
    "daily_return",
)
REQUIRED_KOSPI_COLUMNS = ("date", "cap_weighted_return")


def build_sector_breadth_scores(
    stock_daily: pd.DataFrame,
    kospi_daily: pd.DataFrame,
    *,
    signal_dates: Sequence[object] | None = None,
    window: int = 20,
    min_stocks: int = 3,
) -> pd.DataFrame:
    """Compute quarter-end strict sector breadth using data through each signal date."""
    _require_columns(stock_daily, REQUIRED_STOCK_COLUMNS, "stock_daily")
    _require_columns(kospi_daily, REQUIRED_KOSPI_COLUMNS, "kospi_daily")
    if window <= 0:
        raise ValueError("window must be positive.")
    if min_stocks <= 0:
        raise ValueError("min_stocks must be positive.")

    daily = _normalize_stock_daily(stock_daily)
    kospi = _normalize_kospi_daily(kospi_daily)
    daily = daily.merge(kospi, on="date", how="left", validate="many_to_one")
    if daily["kospi_cap_weighted_return"].isna().any():
        missing = (
            daily.loc[daily["kospi_cap_weighted_return"].isna(), "date"]
            .drop_duplicates()
            .head(5)
            .dt.date
            .tolist()
        )
        raise ValueError(f"kospi_daily is missing cap_weighted_return for stock dates: {missing}")

    daily = daily.sort_values(["ticker", "date"]).reset_index(drop=True)
    by_ticker = daily.groupby("ticker", sort=False)
    daily["foreign_net_buy_20d"] = by_ticker["foreign_net_buy_amount"].transform(
        lambda values: values.rolling(window, min_periods=window).sum()
    )
    daily["stock_return_20d"] = by_ticker["daily_return"].transform(
        lambda values: (1.0 + values)
        .rolling(window, min_periods=window)
        .apply(lambda window_values: window_values.prod() - 1.0, raw=True)
    )

    kospi = kospi.sort_values("date").reset_index(drop=True)
    kospi["kospi_return_20d"] = (1.0 + kospi["kospi_cap_weighted_return"]).rolling(
        window, min_periods=window
    ).apply(lambda values: values.prod() - 1.0, raw=True)
    daily = daily.merge(kospi.loc[:, ["date", "kospi_return_20d"]], on="date", how="left")
    daily["stock_rel_ret_20d"] = daily["stock_return_20d"] - daily["kospi_return_20d"]

    selected_dates = _normalize_signal_dates(signal_dates) if signal_dates is not None else quarter_end_dates(daily)
    selected = daily.loc[daily["date"].isin(selected_dates)].copy()
    selected["foreign_positive"] = selected["foreign_net_buy_20d"].gt(0)
    selected["relative_strength_positive"] = selected["stock_rel_ret_20d"].gt(0)
    selected["strict_positive"] = selected["foreign_positive"] & selected["relative_strength_positive"]
    selected.loc[selected[["foreign_net_buy_20d", "stock_rel_ret_20d"]].isna().any(axis=1), "strict_positive"] = False

    grouped = selected.groupby(["date", "sector_code", "sector_name"], sort=True)
    scores = grouped.agg(
        n_stocks=("ticker", "nunique"),
        n_foreign_positive=("foreign_positive", "sum"),
        n_relative_strength_positive=("relative_strength_positive", "sum"),
        n_strict_positive=("strict_positive", "sum"),
    ).reset_index()
    scores["sector_breadth_value"] = scores["n_foreign_positive"] / scores["n_stocks"]
    scores["sector_breadth_strict"] = scores["n_strict_positive"] / scores["n_stocks"]
    scores["eligible_for_score"] = scores["n_stocks"].ge(min_stocks)
    scores.loc[~scores["eligible_for_score"], "sector_breadth_strict"] = pd.NA
    scores["breadth_score"] = scores.groupby("date", group_keys=False)["sector_breadth_strict"].transform(_zscore)
    return scores.loc[
        :,
        [
            "date",
            "sector_code",
            "sector_name",
            "n_stocks",
            "n_foreign_positive",
            "n_relative_strength_positive",
            "n_strict_positive",
            "sector_breadth_value",
            "sector_breadth_strict",
            "breadth_score",
            "eligible_for_score",
        ],
    ].rename(columns={"date": "signal_date"}).reset_index(drop=True)


def build_rank_ic_diagnostics(scores: pd.DataFrame, forward_returns: pd.DataFrame) -> pd.DataFrame:
    return _build_flow_rank_ic_diagnostics(_as_flow_score_frame(scores), forward_returns)


def build_top_bottom_spread_diagnostics(
    scores: pd.DataFrame,
    forward_returns: pd.DataFrame,
    *,
    k: int = 3,
) -> pd.DataFrame:
    return _build_flow_top_bottom_spread_diagnostics(_as_flow_score_frame(scores), forward_returns, k=k)


def _as_flow_score_frame(scores: pd.DataFrame) -> pd.DataFrame:
    _require_columns(scores, ("signal_date", "sector_code", "sector_name", "breadth_score"), "scores")
    data = scores.loc[:, ["signal_date", "sector_code", "sector_name", "breadth_score"]].copy()
    return data.rename(columns={"breadth_score": "flow_score"})


def _normalize_stock_daily(stock_daily: pd.DataFrame) -> pd.DataFrame:
    daily = stock_daily.loc[:, REQUIRED_STOCK_COLUMNS].copy()
    daily["date"] = pd.to_datetime(daily["date"], errors="raise").dt.normalize()
    daily["ticker"] = daily["ticker"].astype("string").str.zfill(6)
    daily["sector_code"] = _normalize_sector_code(daily["sector_code"])
    daily["sector_name"] = daily["sector_name"].astype("string")
    for column in ("market_cap", "foreign_net_buy_amount", "daily_return"):
        daily[column] = pd.to_numeric(daily[column], errors="coerce")
    return daily


def _normalize_kospi_daily(kospi_daily: pd.DataFrame) -> pd.DataFrame:
    kospi = kospi_daily.loc[:, REQUIRED_KOSPI_COLUMNS].copy()
    kospi["date"] = pd.to_datetime(kospi["date"], errors="raise").dt.normalize()
    kospi["kospi_cap_weighted_return"] = pd.to_numeric(kospi["cap_weighted_return"], errors="coerce")
    return kospi.loc[:, ["date", "kospi_cap_weighted_return"]]


def _normalize_sector_code(values: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(values, errors="coerce")
    normalized = values.astype("string")
    numeric_mask = numeric.notna()
    normalized.loc[numeric_mask] = numeric.loc[numeric_mask].astype("Int64").astype("string")
    return normalized.str.zfill(2)


def _normalize_signal_dates(signal_dates: Sequence[object]) -> list[pd.Timestamp]:
    return sorted(pd.to_datetime(pd.Index(signal_dates), errors="raise").normalize().unique())
