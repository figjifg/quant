from __future__ import annotations

import math
from collections.abc import Sequence

import numpy as np
import pandas as pd


METRIC_KEYS = (
    "total_return",
    "annualized_return",
    "annualized_volatility",
    "sharpe",
    "max_drawdown",
    "hit_rate",
    "average_trade_return",
    "median_trade_return",
    "profit_factor",
    "average_holding_period",
    "trade_count",
    "turnover",
    "cost_paid_total",
    "return_before_cost",
    "return_after_cost",
    "exposure_ratio",
    "max_consecutive_losses",
)


def compute_metrics(
    equity_curve: pd.DataFrame,
    trades: pd.DataFrame,
    calendar: object | None = None,
) -> dict[str, float | int]:
    """Compute E001 metrics from an equity curve and trade ledger."""
    _require_columns(equity_curve, ("net_value", "cash"), "equity_curve")
    _require_columns(
        trades,
        ("entry_date", "exit_date", "entry_price", "exit_price", "notional_at_entry", "buy_cost", "sell_cost"),
        "trades",
    )

    nav = pd.to_numeric(equity_curve["net_value"], errors="coerce")
    total_return = _total_return(nav)
    annualized_return = _annualized_return(total_return, len(equity_curve))
    annualized_volatility = _annualized_volatility(nav)
    sharpe = (
        annualized_return / annualized_volatility
        if annualized_volatility and not pd.isna(annualized_volatility)
        else float("nan")
    )
    max_drawdown = _max_drawdown(nav)

    pnl_pct = _trade_pnl_pct(trades)
    cost_paid = _total_cost_paid(trades)
    mean_nav = nav.mean()

    return {
        "total_return": total_return,
        "annualized_return": annualized_return,
        "annualized_volatility": annualized_volatility,
        "sharpe": sharpe,
        "max_drawdown": max_drawdown,
        "hit_rate": float((pnl_pct > 0).mean()) if len(pnl_pct) else 0.0,
        "average_trade_return": float(pnl_pct.mean()) if len(pnl_pct) else float("nan"),
        "median_trade_return": float(pnl_pct.median()) if len(pnl_pct) else float("nan"),
        "profit_factor": _profit_factor(pnl_pct),
        "average_holding_period": _average_holding_period(trades, calendar),
        "trade_count": int(len(trades)),
        "turnover": _safe_divide(_sum_numeric(trades, "notional_at_entry"), mean_nav),
        "cost_paid_total": cost_paid,
        "return_before_cost": total_return + _safe_divide(cost_paid, nav.iloc[0]) if len(nav) else float("nan"),
        "return_after_cost": total_return,
        "exposure_ratio": _exposure_ratio(equity_curve),
        "max_consecutive_losses": _max_consecutive_losses(trades, pnl_pct),
    }


def metrics_is_oos(
    equity_curve: pd.DataFrame,
    trades: pd.DataFrame,
    is_start: object,
    is_end: object,
    oos_start: object,
    oos_end: object,
    calendar: object,
) -> dict[str, dict[str, float | int]]:
    """Compute IS, OOS, and full-period metric blocks."""
    return {
        "is": compute_metrics(
            _slice_equity(equity_curve, is_start, is_end),
            _slice_trades(trades, is_start, is_end),
            calendar,
        ),
        "oos": compute_metrics(
            _slice_equity(equity_curve, oos_start, oos_end),
            _slice_trades(trades, oos_start, oos_end),
            calendar,
        ),
        "full": compute_metrics(equity_curve, trades, calendar),
    }


def _trade_pnl_pct(trades: pd.DataFrame) -> pd.Series:
    if trades.empty:
        return pd.Series(dtype="float64")

    entry = pd.to_numeric(trades["entry_price"], errors="coerce")
    exit_ = pd.to_numeric(trades["exit_price"], errors="coerce")
    costs = pd.to_numeric(trades["buy_cost"], errors="coerce") + pd.to_numeric(
        trades["sell_cost"], errors="coerce"
    )
    notional = pd.to_numeric(trades["notional_at_entry"], errors="coerce")
    return (exit_ / entry - 1.0) - (costs / notional)


def _total_return(nav: pd.Series) -> float:
    if nav.empty:
        return float("nan")
    return float(nav.iloc[-1] / nav.iloc[0] - 1.0)


def _annualized_return(total_return: float, periods: int) -> float:
    if periods == 0 or pd.isna(total_return):
        return float("nan")
    return float((1.0 + total_return) ** (252.0 / periods) - 1.0)


def _annualized_volatility(nav: pd.Series) -> float:
    daily_log_returns = np.log(nav / nav.shift(1)).dropna()
    if daily_log_returns.empty:
        return float("nan")
    return float(math.sqrt(252.0) * daily_log_returns.std())


def _max_drawdown(nav: pd.Series) -> float:
    if nav.empty:
        return float("nan")
    drawdown = nav / nav.cummax() - 1.0
    return float(drawdown.min())


def _profit_factor(pnl_pct: pd.Series) -> float:
    if pnl_pct.empty:
        return float("nan")
    positive = pnl_pct.loc[pnl_pct > 0].sum()
    negative = pnl_pct.loc[pnl_pct < 0].sum()
    if negative == 0:
        return float("inf")
    return float(positive / abs(negative))


def _average_holding_period(trades: pd.DataFrame, calendar: object | None) -> float:
    if trades.empty:
        return float("nan")
    if calendar is None:
        return float("nan")

    dates = getattr(calendar, "dates", calendar)
    if not isinstance(dates, Sequence):
        return float("nan")
    index_by_date = {pd.Timestamp(date).normalize(): index for index, date in enumerate(dates)}
    holding_periods = []
    for _, trade in trades.iterrows():
        entry_date = pd.Timestamp(trade["entry_date"]).normalize()
        exit_date = pd.Timestamp(trade["exit_date"]).normalize()
        if entry_date not in index_by_date or exit_date not in index_by_date:
            return float("nan")
        holding_periods.append(index_by_date[exit_date] - index_by_date[entry_date])
    return float(pd.Series(holding_periods, dtype="float64").mean())


def _max_consecutive_losses(trades: pd.DataFrame, pnl_pct: pd.Series) -> int:
    if trades.empty:
        return 0
    ordered = trades.assign(_pnl_pct=pnl_pct).sort_values(["entry_date", "exit_date"])
    longest = 0
    current = 0
    for pnl in ordered["_pnl_pct"]:
        if pd.isna(pnl):
            current = 0
        elif pnl <= 0:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return int(longest)


def _exposure_ratio(equity_curve: pd.DataFrame) -> float:
    if equity_curve.empty:
        return float("nan")
    net_value = pd.to_numeric(equity_curve["net_value"], errors="coerce")
    cash = pd.to_numeric(equity_curve["cash"], errors="coerce")
    exposure = (net_value - cash) / net_value
    return float(exposure.replace([np.inf, -np.inf], np.nan).mean())


def _total_cost_paid(trades: pd.DataFrame) -> float:
    return _sum_numeric(trades, "buy_cost") + _sum_numeric(trades, "sell_cost")


def _sum_numeric(data: pd.DataFrame, column: str) -> float:
    if data.empty:
        return 0.0
    return float(pd.to_numeric(data[column], errors="coerce").sum())


def _safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0 or pd.isna(denominator):
        return float("nan")
    return float(numerator / denominator)


def _slice_equity(equity_curve: pd.DataFrame, start: object, end: object) -> pd.DataFrame:
    _require_columns(equity_curve, ("date",), "equity_curve")
    dates = pd.to_datetime(equity_curve["date"], errors="raise")
    start_ts = pd.Timestamp(start).normalize()
    end_ts = pd.Timestamp(end).normalize()
    return equity_curve.loc[(dates >= start_ts) & (dates <= end_ts)].copy()


def _slice_trades(trades: pd.DataFrame, start: object, end: object) -> pd.DataFrame:
    _require_columns(trades, ("entry_date",), "trades")
    entry_dates = pd.to_datetime(trades["entry_date"], errors="raise")
    start_ts = pd.Timestamp(start).normalize()
    end_ts = pd.Timestamp(end).normalize()
    return trades.loc[(entry_dates >= start_ts) & (entry_dates <= end_ts)].copy()


def _require_columns(data: pd.DataFrame, columns: tuple[str, ...], name: str) -> None:
    missing = [column for column in columns if column not in data.columns]
    if missing:
        raise ValueError(f"{name} is missing required columns: {missing}")
