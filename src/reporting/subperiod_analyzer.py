from __future__ import annotations

from typing import Any

import pandas as pd

from src.backtest.engine import BacktestResult
from src.reporting.metrics import compute_metrics, metrics_is_oos


def year_breakdown(
    result: BacktestResult,
    calendar: object,
    *,
    years: tuple[int, ...],
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for year in years:
        start = pd.Timestamp(year=year, month=1, day=1)
        end = pd.Timestamp(year=year, month=12, day=31)
        block = metrics_is_oos(result.equity_curve, result.trades, start, end, start, end, calendar)["is"]
        rows.append(
            {
                "year": year,
                "trades": int(block["trade_count"]),
                "net": float(block["total_return"]),
                "annualized": float(block["annualized_return"]),
                "max_DD": float(block["max_drawdown"]),
                "sharpe": float(block["sharpe"]),
            }
        )
    return pd.DataFrame(rows)


def rolling_year_sharpe(
    result: BacktestResult,
    calendar: object,
    *,
    start_year: int,
    end_year: int,
    window_years: int = 3,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for ending_year in range(start_year + window_years - 1, end_year + 1):
        start = pd.Timestamp(year=ending_year - window_years + 1, month=1, day=1)
        end = pd.Timestamp(year=ending_year, month=12, day=31)
        block = metrics_is_oos(result.equity_curve, result.trades, start, end, start, end, calendar)["is"]
        rows.append(
            {
                "ending_year": ending_year,
                "start_year": start.year,
                "end_year": ending_year,
                "sharpe": float(block["sharpe"]),
            }
        )
    return pd.DataFrame(rows)


def spike_years(per_year: pd.DataFrame, total_return: float, *, threshold: float = 0.30) -> pd.DataFrame:
    if total_return <= 0.0 or per_year.empty:
        return pd.DataFrame(columns=["year", "net", "contribution"])
    data = per_year.loc[:, ["year", "net"]].copy()
    data["contribution"] = pd.to_numeric(data["net"], errors="raise") / total_return
    return data.loc[data["contribution"].gt(threshold)].reset_index(drop=True)


def subperiod_metrics_row(
    *,
    name: str,
    start: object,
    end: object,
    net_result: BacktestResult,
    cost_0_result: BacktestResult,
    calendar: object,
    positive_years: int,
) -> dict[str, Any]:
    net = compute_metrics(net_result.equity_curve, net_result.trades, calendar)
    cost_0 = compute_metrics(cost_0_result.equity_curve, cost_0_result.trades, calendar)
    return {
        "subperiod": name,
        "start": pd.Timestamp(start).date().isoformat(),
        "end": pd.Timestamp(end).date().isoformat(),
        "trades": int(net["trade_count"]),
        "net": float(net["total_return"]),
        "cost0": float(cost_0["total_return"]),
        "Sharpe": float(net["sharpe"]),
        "annualized": float(net["annualized_return"]),
        "MaxDD": float(net["max_drawdown"]),
        "pos_years": int(positive_years),
    }
