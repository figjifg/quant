from __future__ import annotations

import math
from collections.abc import Sequence

import pandas as pd


REQUIRED_SECTOR_COLUMNS = (
    "date",
    "sector_code",
    "sector_name",
    "n_stocks",
    "sum_market_cap",
    "sum_traded_value",
    "sum_foreign_net_buy_amount",
    "cap_weighted_return",
)


def build_sector_flow_scores(
    sector_daily: pd.DataFrame,
    *,
    signal_dates: Sequence[object] | None = None,
    value_window: int = 20,
    mcap_window: int = 60,
    min_stocks: int = 3,
) -> pd.DataFrame:
    """Compute quarter-end sector Flow Score with signal-date-only lookbacks."""
    _require_columns(sector_daily, REQUIRED_SECTOR_COLUMNS, "sector_daily")
    if value_window <= 0 or mcap_window <= 0:
        raise ValueError("value_window and mcap_window must be positive.")
    if min_stocks <= 0:
        raise ValueError("min_stocks must be positive.")

    daily = _normalize_sector_daily(sector_daily)
    daily = daily.sort_values(["sector_code", "date"]).reset_index(drop=True)
    by_sector = daily.groupby("sector_code", sort=False)
    daily["foreign_net_buy_20d"] = by_sector["sum_foreign_net_buy_amount"].transform(
        lambda values: values.rolling(value_window, min_periods=value_window).sum()
    )
    daily["traded_value_20d"] = by_sector["sum_traded_value"].transform(
        lambda values: values.rolling(value_window, min_periods=value_window).sum()
    )
    daily["foreign_net_buy_60d"] = by_sector["sum_foreign_net_buy_amount"].transform(
        lambda values: values.rolling(mcap_window, min_periods=mcap_window).sum()
    )
    daily["flow_by_value_20d"] = daily["foreign_net_buy_20d"] / daily["traded_value_20d"]
    daily["flow_by_mcap_60d"] = daily["foreign_net_buy_60d"] / daily["sum_market_cap"]
    daily.loc[daily["traded_value_20d"].le(0), "flow_by_value_20d"] = pd.NA
    daily.loc[daily["sum_market_cap"].le(0), "flow_by_mcap_60d"] = pd.NA
    daily["raw_flow_score"] = daily[["flow_by_value_20d", "flow_by_mcap_60d"]].mean(axis=1, skipna=False)

    selected_dates = _normalize_signal_dates(signal_dates) if signal_dates is not None else quarter_end_dates(daily)
    scores = daily.loc[daily["date"].isin(selected_dates)].copy()
    scores["eligible_for_score"] = scores["n_stocks"].ge(min_stocks)
    scores.loc[~scores["eligible_for_score"], "raw_flow_score"] = pd.NA
    scores["flow_score"] = scores.groupby("date", group_keys=False)["raw_flow_score"].transform(_zscore)
    return scores.loc[
        :,
        [
            "date",
            "sector_code",
            "sector_name",
            "n_stocks",
            "sum_market_cap",
            "sum_traded_value",
            "sum_foreign_net_buy_amount",
            "foreign_net_buy_20d",
            "traded_value_20d",
            "foreign_net_buy_60d",
            "flow_by_value_20d",
            "flow_by_mcap_60d",
            "raw_flow_score",
            "flow_score",
            "eligible_for_score",
        ],
    ].rename(columns={"date": "signal_date"}).reset_index(drop=True)


def build_sector_forward_returns(
    sector_daily: pd.DataFrame,
    signal_dates: Sequence[object],
) -> pd.DataFrame:
    """Compound each sector's cap-weighted return from T+1 through next quarter-end."""
    _require_columns(sector_daily, REQUIRED_SECTOR_COLUMNS, "sector_daily")
    daily = _normalize_sector_daily(sector_daily)
    dates = _normalize_signal_dates(signal_dates)
    rows: list[dict[str, object]] = []
    for index, signal_date in enumerate(dates[:-1]):
        forward_end = dates[index + 1]
        window = daily.loc[daily["date"].gt(signal_date) & daily["date"].le(forward_end)]
        if window.empty:
            continue
        for (sector_code, sector_name), group in window.groupby(["sector_code", "sector_name"], sort=True):
            returns = pd.to_numeric(group["cap_weighted_return"], errors="coerce").dropna()
            if returns.empty:
                forward_return = float("nan")
            else:
                forward_return = float((1.0 + returns).prod() - 1.0)
            rows.append(
                {
                    "signal_date": signal_date,
                    "forward_end_date": forward_end,
                    "sector_code": sector_code,
                    "sector_name": sector_name,
                    "forward_return": forward_return,
                }
            )
    return pd.DataFrame(rows)


def build_rank_ic_diagnostics(scores: pd.DataFrame, forward_returns: pd.DataFrame) -> pd.DataFrame:
    data = _score_forward_frame(scores, forward_returns)
    rows = []
    for signal_date, group in data.groupby("signal_date", sort=True):
        valid = group[["flow_score", "forward_return"]].dropna()
        rows.append(
            {
                "signal_date": signal_date,
                "n_sectors": int(len(valid)),
                "rank_ic": _spearman(valid["flow_score"], valid["forward_return"]) if len(valid) >= 2 else float("nan"),
            }
        )
    result = pd.DataFrame(rows)
    if not result.empty:
        summary = _series_summary(result["rank_ic"])
        result = pd.concat(
            [
                result,
                pd.DataFrame(
                    [
                        {
                            "signal_date": "ALL",
                            "n_sectors": int(result["n_sectors"].sum()),
                            "rank_ic": summary["mean"],
                            "rank_ic_std": summary["std"],
                            "rank_ic_t_stat": summary["t_stat"],
                            "n_quarters": summary["n"],
                        }
                    ]
                ),
            ],
            ignore_index=True,
        )
    return result


def build_top_bottom_spread_diagnostics(
    scores: pd.DataFrame,
    forward_returns: pd.DataFrame,
    *,
    k: int = 3,
) -> pd.DataFrame:
    if k <= 0:
        raise ValueError("k must be positive.")
    data = _score_forward_frame(scores, forward_returns)
    rows = []
    for signal_date, group in data.groupby("signal_date", sort=True):
        valid = group.dropna(subset=["flow_score", "forward_return"]).sort_values(
            ["flow_score", "sector_code"], ascending=[False, True]
        )
        if len(valid) < k * 2:
            top = bottom = spread = float("nan")
        else:
            top = float(valid.head(k)["forward_return"].mean())
            bottom = float(valid.tail(k)["forward_return"].mean())
            spread = top - bottom
        rows.append(
            {
                "signal_date": signal_date,
                "top_mean_forward_return": top,
                "bottom_mean_forward_return": bottom,
                "spread": spread,
            }
        )
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


def build_subperiod_diagnostics(rank_ic: pd.DataFrame, spread: pd.DataFrame) -> pd.DataFrame:
    ic = _drop_summary_rows(rank_ic, "rank_ic")
    sp = _drop_summary_rows(spread, "spread")
    data = ic.merge(sp, on="signal_date", how="inner")
    data["year"] = pd.to_datetime(data["signal_date"], errors="raise").dt.year
    periods: list[tuple[str, pd.Series]] = [
        ("2010_2017", data["year"].between(2010, 2017)),
        ("2018_2026", data["year"].between(2018, 2026)),
        ("spike_years_2020_2025_2026", data["year"].isin([2020, 2025, 2026])),
        ("excluding_spike_years", ~data["year"].isin([2020, 2025, 2026])),
    ]
    periods.extend((f"year_{year}", data["year"].eq(year)) for year in (2020, 2025, 2026))
    rows = []
    for label, mask in periods:
        subset = data.loc[mask].copy()
        ic_summary = _series_summary(subset["rank_ic"])
        spread_summary = _series_summary(subset["spread"])
        rows.append(
            {
                "period": label,
                "n_quarters": int(len(subset)),
                "rank_ic_mean": ic_summary["mean"],
                "rank_ic_std": ic_summary["std"],
                "rank_ic_t_stat": ic_summary["t_stat"],
                "spread_mean": spread_summary["mean"],
                "spread_std": spread_summary["std"],
                "spread_t_stat": spread_summary["t_stat"],
                "positive_spread_ratio": _positive_ratio(subset["spread"]),
            }
        )
    return pd.DataFrame(rows)


def quarter_end_dates(sector_daily: pd.DataFrame) -> list[pd.Timestamp]:
    dates = pd.to_datetime(sector_daily["date"], errors="raise").dt.normalize().drop_duplicates().sort_values()
    return list(pd.Series(dates).groupby(dates.dt.to_period("Q")).max())


def diagnostics_pass(rank_ic: pd.DataFrame, spread: pd.DataFrame) -> bool:
    rank_summary = rank_ic.loc[rank_ic["signal_date"].eq("ALL")]
    spread_summary = spread.loc[spread["signal_date"].eq("ALL")]
    if rank_summary.empty or spread_summary.empty:
        return False
    return bool(
        float(rank_summary.iloc[0]["rank_ic"]) >= 0.05
        and float(spread_summary.iloc[0]["spread_t_stat"]) >= 2.0
    )


def _score_forward_frame(scores: pd.DataFrame, forward_returns: pd.DataFrame) -> pd.DataFrame:
    data = scores.loc[:, ["signal_date", "sector_code", "sector_name", "flow_score"]].copy()
    data["signal_date"] = pd.to_datetime(data["signal_date"], errors="raise").dt.normalize()
    data["sector_code"] = data["sector_code"].astype("string").str.zfill(2)
    forward = forward_returns.copy()
    forward["signal_date"] = pd.to_datetime(forward["signal_date"], errors="raise").dt.normalize()
    forward["sector_code"] = forward["sector_code"].astype("string").str.zfill(2)
    return data.merge(
        forward.loc[:, ["signal_date", "sector_code", "forward_end_date", "forward_return"]],
        on=["signal_date", "sector_code"],
        how="inner",
        validate="one_to_one",
    )


def _normalize_sector_daily(sector_daily: pd.DataFrame) -> pd.DataFrame:
    daily = sector_daily.loc[:, REQUIRED_SECTOR_COLUMNS].copy()
    daily["date"] = pd.to_datetime(daily["date"], errors="raise").dt.normalize()
    daily["sector_code"] = daily["sector_code"].astype("string").str.zfill(2)
    daily["sector_name"] = daily["sector_name"].astype("string")
    for column in (
        "n_stocks",
        "sum_market_cap",
        "sum_traded_value",
        "sum_foreign_net_buy_amount",
        "cap_weighted_return",
    ):
        daily[column] = pd.to_numeric(daily[column], errors="coerce")
    return daily


def _normalize_signal_dates(signal_dates: Sequence[object]) -> list[pd.Timestamp]:
    return sorted(pd.to_datetime(pd.Index(signal_dates), errors="raise").normalize().unique())


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


def _drop_summary_rows(frame: pd.DataFrame, value_column: str) -> pd.DataFrame:
    data = frame.loc[~frame["signal_date"].astype(str).eq("ALL")].copy()
    data[value_column] = pd.to_numeric(data[value_column], errors="coerce")
    return data


def _require_columns(frame: pd.DataFrame, columns: Sequence[str], name: str) -> None:
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")
