from __future__ import annotations

import math
from collections.abc import Sequence

import pandas as pd


REQUIRED_STOCK_COLUMNS = ("date", "ticker", "sector_code", "sector_name", "daily_return")
REQUIRED_SECTOR_COLUMNS = ("date", "sector_code", "sector_name", "cap_weighted_return")


def build_stock_rs_scores(
    stock_daily: pd.DataFrame,
    sector_daily: pd.DataFrame,
    *,
    signal_dates: Sequence[object] | None = None,
    short_window: int = 20,
    long_window: int = 60,
    min_sector_stocks: int = 2,
) -> pd.DataFrame:
    """Compute sector-relative stock RS scores with signal-date data only."""
    _require_columns(stock_daily, REQUIRED_STOCK_COLUMNS, "stock_daily")
    _require_columns(sector_daily, REQUIRED_SECTOR_COLUMNS, "sector_daily")
    if short_window <= 0 or long_window <= 0:
        raise ValueError("short_window and long_window must be positive.")
    if min_sector_stocks <= 0:
        raise ValueError("min_sector_stocks must be positive.")

    stocks = _normalize_stock_daily(stock_daily)
    stocks = stocks.dropna(subset=["sector_code"]).copy()
    sectors = _normalize_sector_daily(sector_daily)
    stocks = stocks.merge(
        sectors.loc[:, ["date", "sector_code", "sector_cap_weighted_return"]],
        on=["date", "sector_code"],
        how="left",
        validate="many_to_one",
    )
    if stocks["sector_cap_weighted_return"].isna().any():
        missing = (
            stocks.loc[stocks["sector_cap_weighted_return"].isna(), ["date", "sector_code"]]
            .drop_duplicates()
            .head(5)
            .to_dict("records")
        )
        raise ValueError(f"sector_daily is missing cap_weighted_return for stock rows: {missing}")

    stocks = stocks.sort_values(["ticker", "date"]).reset_index(drop=True)
    by_stock = stocks.groupby("ticker", sort=False)
    stocks["stock_return_20d"] = by_stock["daily_return"].transform(
        lambda values: _rolling_compound_return(values, short_window)
    )
    stocks["stock_return_60d"] = by_stock["daily_return"].transform(
        lambda values: _rolling_compound_return(values, long_window)
    )

    sectors = sectors.sort_values(["sector_code", "date"]).reset_index(drop=True)
    by_sector = sectors.groupby("sector_code", sort=False)
    sectors["sector_return_20d"] = by_sector["sector_cap_weighted_return"].transform(
        lambda values: _rolling_compound_return(values, short_window)
    )
    sectors["sector_return_60d"] = by_sector["sector_cap_weighted_return"].transform(
        lambda values: _rolling_compound_return(values, long_window)
    )
    stocks = stocks.merge(
        sectors.loc[:, ["date", "sector_code", "sector_return_20d", "sector_return_60d"]],
        on=["date", "sector_code"],
        how="left",
        validate="many_to_one",
    )

    stocks["stock_rs_20"] = stocks["stock_return_20d"] - stocks["sector_return_20d"]
    stocks["stock_rs_60"] = stocks["stock_return_60d"] - stocks["sector_return_60d"]
    stocks["raw_stock_rs_score"] = stocks[["stock_rs_20", "stock_rs_60"]].mean(axis=1, skipna=False)

    selected_dates = _normalize_signal_dates(signal_dates) if signal_dates is not None else quarter_end_dates(stocks)
    scores = stocks.loc[stocks["date"].isin(selected_dates)].copy()
    sector_counts = scores.groupby(["date", "sector_code"])["ticker"].transform("count")
    scores["eligible_for_score"] = sector_counts.ge(min_sector_stocks)
    scores.loc[~scores["eligible_for_score"], "raw_stock_rs_score"] = pd.NA
    scores["stock_rs_score"] = scores.groupby(["date", "sector_code"], group_keys=False)[
        "raw_stock_rs_score"
    ].transform(_zscore)
    return scores.loc[
        :,
        [
            "date",
            "ticker",
            "sector_code",
            "sector_name",
            "daily_return",
            "sector_cap_weighted_return",
            "stock_return_20d",
            "sector_return_20d",
            "stock_rs_20",
            "stock_return_60d",
            "sector_return_60d",
            "stock_rs_60",
            "raw_stock_rs_score",
            "stock_rs_score",
            "eligible_for_score",
        ],
    ].rename(columns={"date": "signal_date"}).reset_index(drop=True)


def build_stock_forward_returns(stock_daily: pd.DataFrame, signal_dates: Sequence[object]) -> pd.DataFrame:
    """Compound each stock's daily_return from T+1 through the next signal date."""
    _require_columns(stock_daily, REQUIRED_STOCK_COLUMNS, "stock_daily")
    daily = _normalize_stock_daily(stock_daily)
    dates = _normalize_signal_dates(signal_dates)
    rows: list[dict[str, object]] = []
    for index, signal_date in enumerate(dates[:-1]):
        forward_end = dates[index + 1]
        window = daily.loc[daily["date"].gt(signal_date) & daily["date"].le(forward_end)]
        if window.empty:
            continue
        for (ticker, sector_code, sector_name), group in window.groupby(
            ["ticker", "sector_code", "sector_name"], sort=True
        ):
            returns = pd.to_numeric(group["daily_return"], errors="coerce").dropna()
            forward_return = float((1.0 + returns).prod() - 1.0) if not returns.empty else float("nan")
            rows.append(
                {
                    "signal_date": signal_date,
                    "forward_end_date": forward_end,
                    "ticker": ticker,
                    "sector_code": sector_code,
                    "sector_name": sector_name,
                    "forward_return": forward_return,
                }
            )
    return pd.DataFrame(rows)


def build_stock_rank_ic_diagnostics(
    scores: pd.DataFrame,
    forward_returns: pd.DataFrame,
    *,
    score_column: str = "stock_rs_score",
    mode: str = "universe",
) -> pd.DataFrame:
    data = _score_forward_frame(scores, forward_returns, score_column)
    rows: list[dict[str, object]] = []
    for signal_date, group in data.groupby("signal_date", sort=True):
        rows.append(_rank_ic_row(signal_date, group, score_column=score_column, mode=mode))
    pooled = _rank_ic_row("ALL", data, score_column=score_column, mode=mode)
    result = pd.DataFrame([*rows, pooled])
    summary = _series_summary(result.loc[~result["signal_date"].eq("ALL"), "rank_ic"])
    result.loc[result["signal_date"].eq("ALL"), "rank_ic_mean_quarterly"] = summary["mean"]
    result.loc[result["signal_date"].eq("ALL"), "rank_ic_std_quarterly"] = summary["std"]
    result.loc[result["signal_date"].eq("ALL"), "rank_ic_t_stat"] = summary["t_stat"]
    result.loc[result["signal_date"].eq("ALL"), "n_quarters"] = summary["n"]
    return result


def build_stock_top_bottom_spread_diagnostics(
    scores: pd.DataFrame,
    forward_returns: pd.DataFrame,
    *,
    score_column: str = "stock_rs_score",
    mode: str = "universe",
    k: int = 5,
) -> pd.DataFrame:
    if k <= 0:
        raise ValueError("k must be positive.")
    data = _score_forward_frame(scores, forward_returns, score_column)
    rows: list[dict[str, object]] = []
    for signal_date, group in data.groupby("signal_date", sort=True):
        rows.append(_spread_row(signal_date, group, score_column=score_column, mode=mode, k=k))
    result = pd.DataFrame(rows)
    if not result.empty:
        summary = _series_summary(result["spread"])
        result = pd.concat(
            [
                result,
                pd.DataFrame(
                    [
                        {
                            "signal_date": "ALL",
                            "mode": mode,
                            "top_mean_forward_return": float(result["top_mean_forward_return"].mean()),
                            "bottom_mean_forward_return": float(result["bottom_mean_forward_return"].mean()),
                            "spread": summary["mean"],
                            "spread_std": summary["std"],
                            "spread_t_stat": summary["t_stat"],
                            "positive_spread_ratio": _positive_ratio(result["spread"]),
                            "n_quarters": summary["n"],
                        }
                    ]
                ),
            ],
            ignore_index=True,
        )
    return result


def quarter_end_dates(daily: pd.DataFrame) -> list[pd.Timestamp]:
    dates = pd.to_datetime(daily["date"], errors="raise").dt.normalize().drop_duplicates().sort_values()
    return list(pd.Series(dates).groupby(dates.dt.to_period("Q")).max())


def _rank_ic_row(signal_date: object, group: pd.DataFrame, *, score_column: str, mode: str) -> dict[str, object]:
    valid = group.dropna(subset=[score_column, "forward_return"])
    if mode == "within_sector":
        sector_values = [
            _spearman(sector_group[score_column], sector_group["forward_return"])
            for _, sector_group in valid.groupby("sector_code", sort=True)
            if len(sector_group) >= 2
        ]
        rank_ic = float(pd.Series(sector_values).mean()) if sector_values else float("nan")
    elif mode == "universe":
        rank_ic = _spearman(valid[score_column], valid["forward_return"]) if len(valid) >= 2 else float("nan")
    else:
        raise ValueError("mode must be 'universe' or 'within_sector'.")
    return {"signal_date": signal_date, "mode": mode, "n_stocks": int(len(valid)), "rank_ic": rank_ic}


def _spread_row(
    signal_date: object,
    group: pd.DataFrame,
    *,
    score_column: str,
    mode: str,
    k: int,
) -> dict[str, object]:
    valid = group.dropna(subset=[score_column, "forward_return"])
    if mode == "within_sector":
        top_values = []
        bottom_values = []
        for _, sector_group in valid.groupby("sector_code", sort=True):
            ranked = sector_group.sort_values([score_column, "ticker"], ascending=[False, True])
            if len(ranked) >= k * 2:
                top_values.append(float(ranked.head(k)["forward_return"].mean()))
                bottom_values.append(float(ranked.tail(k)["forward_return"].mean()))
        top = float(pd.Series(top_values).mean()) if top_values else float("nan")
        bottom = float(pd.Series(bottom_values).mean()) if bottom_values else float("nan")
    elif mode == "universe":
        ranked = valid.sort_values([score_column, "ticker"], ascending=[False, True])
        if len(ranked) >= k * 2:
            top = float(ranked.head(k)["forward_return"].mean())
            bottom = float(ranked.tail(k)["forward_return"].mean())
        else:
            top = bottom = float("nan")
    else:
        raise ValueError("mode must be 'universe' or 'within_sector'.")
    return {
        "signal_date": signal_date,
        "mode": mode,
        "top_mean_forward_return": top,
        "bottom_mean_forward_return": bottom,
        "spread": top - bottom if pd.notna(top) and pd.notna(bottom) else float("nan"),
    }


def _score_forward_frame(scores: pd.DataFrame, forward_returns: pd.DataFrame, score_column: str) -> pd.DataFrame:
    required = ["signal_date", "ticker", "sector_code", score_column]
    _require_columns(scores, tuple(required), "scores")
    _require_columns(forward_returns, ("signal_date", "ticker", "forward_return"), "forward_returns")
    data = scores.loc[:, required].copy()
    data["signal_date"] = pd.to_datetime(data["signal_date"], errors="raise").dt.normalize()
    data["ticker"] = data["ticker"].astype("string").str.zfill(6)
    data["sector_code"] = data["sector_code"].astype("string").str.zfill(2)
    forward = forward_returns.copy()
    forward["signal_date"] = pd.to_datetime(forward["signal_date"], errors="raise").dt.normalize()
    forward["ticker"] = forward["ticker"].astype("string").str.zfill(6)
    return data.merge(
        forward.loc[:, ["signal_date", "ticker", "forward_end_date", "forward_return"]],
        on=["signal_date", "ticker"],
        how="inner",
        validate="one_to_one",
    )


def _rolling_compound_return(values: pd.Series, window: int) -> pd.Series:
    numeric = pd.to_numeric(values, errors="coerce")
    return (1.0 + numeric).rolling(window, min_periods=window).apply(lambda window_values: window_values.prod(), raw=True) - 1.0


def _normalize_stock_daily(stock_daily: pd.DataFrame) -> pd.DataFrame:
    daily = stock_daily.loc[:, REQUIRED_STOCK_COLUMNS].copy()
    daily["date"] = pd.to_datetime(daily["date"], errors="raise").dt.normalize()
    daily["ticker"] = daily["ticker"].astype("string").str.zfill(6)
    daily["sector_code"] = _sector_code(daily["sector_code"])
    daily["sector_name"] = daily["sector_name"].astype("string")
    daily["daily_return"] = pd.to_numeric(daily["daily_return"], errors="coerce")
    return daily


def _normalize_sector_daily(sector_daily: pd.DataFrame) -> pd.DataFrame:
    daily = sector_daily.loc[:, REQUIRED_SECTOR_COLUMNS].copy()
    daily["date"] = pd.to_datetime(daily["date"], errors="raise").dt.normalize()
    daily["sector_code"] = _sector_code(daily["sector_code"])
    daily["sector_name"] = daily["sector_name"].astype("string")
    daily["sector_cap_weighted_return"] = pd.to_numeric(daily["cap_weighted_return"], errors="coerce")
    return daily.loc[:, ["date", "sector_code", "sector_name", "sector_cap_weighted_return"]].drop_duplicates(
        ["date", "sector_code"], keep="last"
    )


def _normalize_signal_dates(signal_dates: Sequence[object]) -> list[pd.Timestamp]:
    return sorted(pd.to_datetime(pd.Index(signal_dates), errors="raise").normalize().unique())


def _sector_code(values: pd.Series) -> pd.Series:
    return values.astype("string").str.strip().str.replace(r"\.0$", "", regex=True).str.zfill(2)


def _zscore(values: pd.Series) -> pd.Series:
    valid = pd.to_numeric(values, errors="coerce")
    mean = valid.mean()
    std = valid.std(ddof=0)
    if pd.isna(std) or std == 0:
        return pd.Series(pd.NA, index=values.index, dtype="Float64")
    return (valid - mean) / std


def _spearman(left: pd.Series, right: pd.Series) -> float:
    value = left.corr(right, method="spearman")
    return float(value) if pd.notna(value) else float("nan")


def _series_summary(values: pd.Series) -> dict[str, float | int]:
    valid = pd.to_numeric(values, errors="coerce").dropna()
    n = int(len(valid))
    mean = float(valid.mean()) if n else float("nan")
    std = float(valid.std(ddof=1)) if n > 1 else float("nan")
    t_stat = float(mean / (std / math.sqrt(n))) if n > 1 and std > 0 else float("nan")
    return {"n": n, "mean": mean, "std": std, "t_stat": t_stat}


def _positive_ratio(values: pd.Series) -> float:
    valid = pd.to_numeric(values, errors="coerce").dropna()
    return float(valid.gt(0).mean()) if not valid.empty else float("nan")


def _require_columns(data: pd.DataFrame, columns: tuple[str, ...], name: str) -> None:
    missing = [column for column in columns if column not in data.columns]
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")
