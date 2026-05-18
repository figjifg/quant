from __future__ import annotations

from collections.abc import Sequence

import pandas as pd

from src.features.stock_foreign_flow_score import build_stock_foreign_flow_scores
from src.features.stock_institution_flow_score import build_stock_institution_flow_scores
from src.features.stock_liquidity_score import build_stock_liquidity_scores
from src.features.stock_rs_score import build_stock_rs_scores, quarter_end_dates


COMBINED_VARIANTS = ("f006", "f007", "f008", "f009", "f010")


def build_stock_combined_scores(
    stock_daily: pd.DataFrame,
    sector_daily: pd.DataFrame,
    *,
    variant: str,
    signal_dates: Sequence[object] | None = None,
    short_window: int = 20,
    long_window: int = 60,
    flow_value_window: int = 20,
    flow_mcap_window: int = 60,
    liquidity_short_window: int = 20,
    liquidity_long_window: int = 120,
    volatility_window: int = 60,
    min_sector_stocks: int = 2,
) -> pd.DataFrame:
    """Build F006-F010 stock-level combined scores using signal-date data only."""
    if variant not in COMBINED_VARIANTS:
        raise ValueError(f"variant must be one of {COMBINED_VARIANTS}.")
    if volatility_window <= 0:
        raise ValueError("volatility_window must be positive.")

    selected_dates = (
        _normalize_signal_dates(signal_dates)
        if signal_dates is not None
        else quarter_end_dates(stock_daily)
    )
    rs = build_stock_rs_scores(
        stock_daily,
        sector_daily,
        signal_dates=selected_dates,
        short_window=short_window,
        long_window=long_window,
        min_sector_stocks=min_sector_stocks,
    )
    foreign = build_stock_foreign_flow_scores(
        stock_daily,
        signal_dates=selected_dates,
        value_window=flow_value_window,
        mcap_window=flow_mcap_window,
        min_sector_stocks=min_sector_stocks,
    )
    institution = build_stock_institution_flow_scores(
        stock_daily,
        signal_dates=selected_dates,
        value_window=flow_value_window,
        mcap_window=flow_mcap_window,
        min_sector_stocks=min_sector_stocks,
    )
    liquidity = build_stock_liquidity_scores(
        stock_daily,
        signal_dates=selected_dates,
        short_window=liquidity_short_window,
        long_window=liquidity_long_window,
        min_sector_stocks=min_sector_stocks,
    )
    volatility = _stock_volatility_frame(stock_daily, signal_dates=selected_dates, window=volatility_window)

    combined = rs.loc[
        :,
        [
            "signal_date",
            "ticker",
            "sector_code",
            "sector_name",
            "stock_rs_score",
            "raw_stock_rs_score",
        ],
    ].copy()
    combined = combined.merge(
        foreign.loc[
            :,
            [
                "signal_date",
                "ticker",
                "foreign_flow_20",
                "foreign_flow_60",
                "stock_foreign_flow_score",
                "raw_stock_foreign_flow_score",
            ],
        ],
        on=["signal_date", "ticker"],
        how="left",
        validate="one_to_one",
    )
    combined = combined.merge(
        institution.loc[
            :,
            [
                "signal_date",
                "ticker",
                "institution_flow_20",
                "institution_flow_60",
                "stock_institution_flow_score",
                "raw_stock_institution_flow_score",
            ],
        ],
        on=["signal_date", "ticker"],
        how="left",
        validate="one_to_one",
    )
    combined = combined.merge(
        liquidity.loc[
            :,
            [
                "signal_date",
                "ticker",
                "liquidity_change",
                "turnover_change",
                "stock_liquidity_score",
                "raw_stock_liquidity_score",
            ],
        ],
        on=["signal_date", "ticker"],
        how="left",
        validate="one_to_one",
    )
    combined = combined.merge(
        volatility,
        on=["signal_date", "ticker", "sector_code"],
        how="left",
        validate="one_to_one",
    )

    combined["flow_confirm_bonus"] = (
        combined["foreign_flow_20"].gt(0) & combined["foreign_flow_60"].gt(0)
    ).astype(float)
    combined["flow_confirm_penalty"] = (
        combined["foreign_flow_20"].lt(0) & combined["foreign_flow_60"].lt(0)
    ).astype(float)
    combined["foreign_positive"] = (
        combined["foreign_flow_20"].gt(0) & combined["foreign_flow_60"].gt(0)
    )
    combined["foreign_negative"] = (
        combined["foreign_flow_20"].lt(0) & combined["foreign_flow_60"].lt(0)
    )
    combined["institution_positive"] = (
        combined["institution_flow_20"].gt(0) & combined["institution_flow_60"].gt(0)
    )
    combined["institution_negative"] = (
        combined["institution_flow_20"].lt(0) & combined["institution_flow_60"].lt(0)
    )
    combined["alignment_adjustment"] = _alignment_adjustment(combined)
    combined["liquidity_confirm_bonus"] = combined["liquidity_change"].gt(1.0).astype(float)
    combined["extreme_volatility_penalty"] = combined["extreme_volatility"].fillna(False).astype(float)

    combined["raw_stock_combined_score"] = _raw_combined_score(combined, variant)
    valid_raw = combined["raw_stock_combined_score"].notna()
    sector_valid_counts = valid_raw.groupby([combined["signal_date"], combined["sector_code"]]).transform("sum")
    combined["eligible_for_score"] = valid_raw & sector_valid_counts.ge(min_sector_stocks)
    combined.loc[~combined["eligible_for_score"], "raw_stock_combined_score"] = pd.NA
    combined["stock_combined_score"] = combined.groupby(["signal_date", "sector_code"], group_keys=False)[
        "raw_stock_combined_score"
    ].transform(_zscore)
    combined["combined_variant"] = variant.upper()

    return combined.loc[
        :,
        [
            "signal_date",
            "ticker",
            "sector_code",
            "sector_name",
            "combined_variant",
            "stock_rs_score",
            "stock_foreign_flow_score",
            "stock_institution_flow_score",
            "stock_liquidity_score",
            "foreign_flow_20",
            "foreign_flow_60",
            "institution_flow_20",
            "institution_flow_60",
            "liquidity_change",
            "turnover_change",
            "volatility_60d",
            "sector_volatility_mean",
            "sector_volatility_std",
            "extreme_volatility",
            "flow_confirm_bonus",
            "flow_confirm_penalty",
            "alignment_adjustment",
            "liquidity_confirm_bonus",
            "extreme_volatility_penalty",
            "raw_stock_combined_score",
            "stock_combined_score",
            "eligible_for_score",
        ],
    ].reset_index(drop=True)


def _raw_combined_score(scores: pd.DataFrame, variant: str) -> pd.Series:
    rs = pd.to_numeric(scores["stock_rs_score"], errors="coerce")
    if variant == "f006":
        flow = pd.to_numeric(scores["stock_foreign_flow_score"], errors="coerce")
        return pd.concat([rs, flow], axis=1).mean(axis=1, skipna=False)
    if variant == "f007":
        return rs + scores["flow_confirm_bonus"] - scores["flow_confirm_penalty"]
    if variant == "f008":
        return rs + scores["alignment_adjustment"]
    if variant == "f009":
        return rs + scores["liquidity_confirm_bonus"] - scores["extreme_volatility_penalty"]
    if variant == "f010":
        flow_confirm = rs + scores["flow_confirm_bonus"] - scores["flow_confirm_penalty"]
        liquidity_confirm = rs + scores["liquidity_confirm_bonus"]
        return pd.concat([rs, flow_confirm, liquidity_confirm], axis=1).mean(axis=1, skipna=False) - scores[
            "extreme_volatility_penalty"
        ]
    raise ValueError(f"Unknown variant: {variant}")


def _alignment_adjustment(scores: pd.DataFrame) -> pd.Series:
    adjustment = pd.Series(0.0, index=scores.index)
    both_positive = scores["foreign_positive"] & scores["institution_positive"]
    foreign_only = scores["foreign_positive"] & ~scores["institution_positive"]
    both_negative = scores["foreign_negative"] & scores["institution_negative"]
    foreign_negative_only = scores["foreign_negative"] & ~scores["institution_negative"]
    adjustment.loc[both_positive] = 1.0
    adjustment.loc[foreign_only] = 0.5
    adjustment.loc[foreign_negative_only] = -0.5
    adjustment.loc[both_negative] = -1.0
    return adjustment


def _stock_volatility_frame(
    stock_daily: pd.DataFrame,
    *,
    signal_dates: Sequence[object],
    window: int,
) -> pd.DataFrame:
    required = ("date", "ticker", "sector_code", "daily_return")
    _require_columns(stock_daily, required, "stock_daily")
    daily = stock_daily.loc[:, required].copy()
    daily["date"] = pd.to_datetime(daily["date"], errors="raise").dt.normalize()
    daily["ticker"] = daily["ticker"].astype("string").str.zfill(6)
    daily["sector_code"] = daily["sector_code"].astype("string").str.strip().str.replace(
        r"\.0$", "", regex=True
    ).str.zfill(2)
    daily["daily_return"] = pd.to_numeric(daily["daily_return"], errors="coerce")
    daily = daily.sort_values(["ticker", "date"]).reset_index(drop=True)
    daily["volatility_60d"] = daily.groupby("ticker", sort=False)["daily_return"].transform(
        lambda values: values.rolling(window, min_periods=window).std(ddof=0)
    )
    selected_dates = _normalize_signal_dates(signal_dates)
    scores = daily.loc[daily["date"].isin(selected_dates), ["date", "ticker", "sector_code", "volatility_60d"]].copy()
    scores["sector_volatility_mean"] = scores.groupby(["date", "sector_code"])["volatility_60d"].transform("mean")
    scores["sector_volatility_std"] = scores.groupby(["date", "sector_code"])["volatility_60d"].transform(
        lambda values: values.std(ddof=0)
    )
    threshold = scores["sector_volatility_mean"] + scores["sector_volatility_std"]
    scores["extreme_volatility"] = scores["volatility_60d"].gt(threshold)
    return scores.rename(columns={"date": "signal_date"}).reset_index(drop=True)


def _normalize_signal_dates(signal_dates: Sequence[object]) -> list[pd.Timestamp]:
    return sorted(pd.to_datetime(pd.Index(signal_dates), errors="raise").normalize().unique())


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
