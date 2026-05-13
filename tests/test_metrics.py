from __future__ import annotations

import math

import pandas as pd
import pytest

from src.backtest.calendar import KRXTradingCalendar
from src.backtest.engine import TRADE_COLUMNS
from src.reporting.metrics import METRIC_KEYS, compute_metrics, metrics_is_oos


def _equity_curve(values: list[float], cash: list[float] | None = None) -> pd.DataFrame:
    dates = pd.date_range("2025-01-02", periods=len(values), freq="B")
    return pd.DataFrame(
        {
            "date": dates,
            "net_value": values,
            "cash": cash if cash is not None else values,
        }
    )


def _trades(pnl_prices: list[tuple[float, float]]) -> pd.DataFrame:
    dates = pd.date_range("2025-01-02", periods=len(pnl_prices) + 6, freq="B")
    rows = []
    for index, (entry_price, exit_price) in enumerate(pnl_prices):
        rows.append(
            {
                "entry_date": dates[index],
                "exit_date": dates[index + 5],
                "entry_price": entry_price,
                "exit_price": exit_price,
                "notional_at_entry": 100.0,
                "buy_cost": 0.0,
                "sell_cost": 0.0,
            }
        )
    return pd.DataFrame(rows, columns=TRADE_COLUMNS)


def test_total_return_zero_vol_sharpe_nan_and_max_drawdown() -> None:
    curve = _equity_curve([1.0, 1.0, 1.0])
    trades = _trades([])

    metrics = compute_metrics(curve, trades)

    assert set(metrics) == set(METRIC_KEYS)
    assert metrics["total_return"] == 0.0
    assert metrics["annualized_volatility"] == 0.0
    assert math.isnan(metrics["sharpe"])
    assert metrics["max_drawdown"] == 0.0


def test_drawdown_uses_running_peak() -> None:
    curve = _equity_curve([1.0, 1.2, 0.9, 1.1])
    trades = _trades([])

    metrics = compute_metrics(curve, trades)

    assert metrics["max_drawdown"] == -0.25


def test_single_trade_pnl_costs_hit_rate_average_and_profit_factor() -> None:
    curve = _equity_curve([1.0, 1.05])
    trades = pd.DataFrame(
        [
            {
                "entry_date": pd.Timestamp("2025-01-02"),
                "exit_date": pd.Timestamp("2025-01-09"),
                "entry_price": 100.0,
                "exit_price": 110.0,
                "notional_at_entry": 1_000.0,
                "buy_cost": 2.0,
                "sell_cost": 3.0,
            }
        ]
    )

    metrics = compute_metrics(curve, trades)

    expected = 0.10 - 5.0 / 1_000.0
    assert metrics["hit_rate"] == 1.0
    assert metrics["average_trade_return"] == pytest.approx(expected)
    assert metrics["median_trade_return"] == pytest.approx(expected)
    assert math.isinf(metrics["profit_factor"])
    assert metrics["cost_paid_total"] == 5.0


def test_max_consecutive_losses_counts_zero_as_loss_sorted_by_entry_date() -> None:
    curve = _equity_curve([1.0, 1.0])
    trades = pd.DataFrame(
        [
            {
                "entry_date": pd.Timestamp("2025-01-06"),
                "exit_date": pd.Timestamp("2025-01-13"),
                "entry_price": 100.0,
                "exit_price": 100.0,
                "notional_at_entry": 100.0,
                "buy_cost": 0.0,
                "sell_cost": 0.0,
            },
            {
                "entry_date": pd.Timestamp("2025-01-02"),
                "exit_date": pd.Timestamp("2025-01-09"),
                "entry_price": 100.0,
                "exit_price": 90.0,
                "notional_at_entry": 100.0,
                "buy_cost": 0.0,
                "sell_cost": 0.0,
            },
            {
                "entry_date": pd.Timestamp("2025-01-03"),
                "exit_date": pd.Timestamp("2025-01-10"),
                "entry_price": 100.0,
                "exit_price": 101.0,
                "notional_at_entry": 100.0,
                "buy_cost": 0.0,
                "sell_cost": 0.0,
            },
        ]
    )

    metrics = compute_metrics(curve, trades)

    assert metrics["max_consecutive_losses"] == 1


def test_exposure_ratio_and_calendar_holding_period() -> None:
    dates = pd.date_range("2025-01-02", periods=8, freq="B")
    curve = pd.DataFrame(
        {
            "date": dates[:3],
            "net_value": [1.0, 1.0, 1.0],
            "cash": [1.0, 0.4, 0.0],
        }
    )
    trades = pd.DataFrame(
        [
            {
                "entry_date": dates[0],
                "exit_date": dates[5],
                "entry_price": 100.0,
                "exit_price": 101.0,
                "notional_at_entry": 0.6,
                "buy_cost": 0.0,
                "sell_cost": 0.0,
            }
        ]
    )
    calendar = KRXTradingCalendar(tuple(dates))

    metrics = compute_metrics(curve, trades, calendar)

    assert metrics["exposure_ratio"] == 0.5333333333333333
    assert metrics["average_holding_period"] == 5.0


def test_metrics_is_oos_slices_equity_by_date_and_trades_by_entry_date() -> None:
    dates = pd.date_range("2025-01-02", periods=6, freq="B")
    curve = pd.DataFrame({"date": dates, "net_value": [1.0, 1.1, 1.2, 1.2, 1.1, 1.0], "cash": 1.0})
    trades = pd.DataFrame(
        [
            {
                "entry_date": dates[1],
                "exit_date": dates[3],
                "entry_price": 100.0,
                "exit_price": 101.0,
                "notional_at_entry": 100.0,
                "buy_cost": 0.0,
                "sell_cost": 0.0,
            },
            {
                "entry_date": dates[4],
                "exit_date": dates[5],
                "entry_price": 100.0,
                "exit_price": 99.0,
                "notional_at_entry": 100.0,
                "buy_cost": 0.0,
                "sell_cost": 0.0,
            },
        ]
    )

    metrics = metrics_is_oos(curve, trades, dates[0], dates[2], dates[3], dates[5], KRXTradingCalendar(tuple(dates)))

    assert metrics["is"]["trade_count"] == 1
    assert metrics["oos"]["trade_count"] == 1
    assert metrics["full"]["trade_count"] == 2
