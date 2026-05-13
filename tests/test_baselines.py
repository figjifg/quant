from __future__ import annotations

import math

import pandas as pd

from src.backtest.calendar import derive_trading_calendar
from src.backtest.costs import Costs, buy_cost, sell_cost
from src.strategies.baselines import _rebalance_dates, run_baseline


def _costs() -> Costs:
    return Costs(commission_bps=1.5, tax_bps_sell=20.0, slippage_bps=5.0)


def _panel(tickers: list[str], periods: int = 10) -> pd.DataFrame:
    dates = pd.date_range("2025-01-02", periods=periods, freq="B")
    rows = []
    for ticker_index, ticker in enumerate(tickers, start=1):
        for date_index, date in enumerate(dates):
            rows.append(
                {
                    "날짜": date,
                    "종목코드": ticker,
                    "시가": 100.0 + ticker_index + date_index,
                    "KRX종가": 101.0 + ticker_index + date_index,
                }
            )
    return pd.DataFrame(rows)


def _universe(dates: list[pd.Timestamp], tickers: list[str]) -> pd.DataFrame:
    rows = []
    for execution_date in dates:
        for ticker in tickers:
            rows.append(
                {
                    "execution_date": execution_date,
                    "signal_date": execution_date,
                    "종목코드": ticker,
                }
            )
    return pd.DataFrame(rows)


def test_b0_cash_returns_flat_equity_curve() -> None:
    panel = _panel(["000001"], periods=6)
    calendar = derive_trading_calendar(panel)

    result = run_baseline(
        "B0_cash",
        panel,
        calendar,
        pd.DataFrame(),
        pd.DataFrame(),
        _costs(),
        calendar.dates[1],
        calendar.dates[4],
    )

    assert list(result.equity_curve["date"]) == list(calendar.dates[1:5])
    assert result.equity_curve["net_value"].tolist() == [1.0, 1.0, 1.0, 1.0]
    assert result.equity_curve["gross_value"].tolist() == [1.0, 1.0, 1.0, 1.0]
    assert result.trades.empty


def test_b1_enters_first_day_universe_and_final_nav_matches_prices_minus_costs() -> None:
    tickers = ["000001", "000002", "000003"]
    panel = _panel(tickers, periods=6)
    calendar = derive_trading_calendar(panel)
    universe = _universe([calendar.dates[0]], tickers)
    costs = _costs()

    result = run_baseline(
        "B1_buy_and_hold",
        panel,
        calendar,
        pd.DataFrame(),
        universe,
        costs,
        calendar.dates[0],
        calendar.dates[-1],
    )

    assert set(result.trades["종목코드"]) == set(tickers)
    assert set(result.trades["entry_date"]) == {calendar.dates[0]}

    expected_nav = 1.0
    entry_notional = 1.0 / len(tickers)
    for ticker in tickers:
        start_price = panel.loc[
            (panel["종목코드"] == ticker) & (panel["날짜"] == calendar.dates[0]),
            "시가",
        ].iloc[0]
        end_price = panel.loc[
            (panel["종목코드"] == ticker) & (panel["날짜"] == calendar.dates[-1]),
            "KRX종가",
        ].iloc[0]
        exit_notional = entry_notional * end_price / start_price
        expected_nav -= buy_cost(entry_notional, costs)
        expected_nav += exit_notional - entry_notional - sell_cost(exit_notional, costs)

    assert abs(result.equity_curve.iloc[-1]["net_value"] - expected_nav) < 1e-12


def test_b2_rebalance_dates_are_every_five_trading_days_from_period_start() -> None:
    panel = _panel(["000001", "000002"], periods=13)
    calendar = derive_trading_calendar(panel)
    period_dates = list(calendar.dates)

    result = run_baseline(
        "B2_universe_5d_rebalance",
        panel,
        calendar,
        pd.DataFrame(),
        _universe(period_dates, ["000001", "000002"]),
        _costs(),
        period_dates[0],
        period_dates[-1],
        holding=5,
    )

    expected_rebalance_dates = _rebalance_dates(period_dates, 5)
    assert len(expected_rebalance_dates) == math.ceil(len(period_dates) / 5)
    assert expected_rebalance_dates == [period_dates[0], period_dates[5], period_dates[10]]
    assert len(result.equity_curve) == len(period_dates)


def test_b3_uses_price_momentum_candidates_not_flow_candidates() -> None:
    panel = _panel(["FLOW01", "MOMO01"], periods=8)
    calendar = derive_trading_calendar(panel)
    execution_date = calendar.dates[1]
    signal_date = calendar.dates[0]
    universe = pd.DataFrame(
        [
            {
                "execution_date": execution_date,
                "signal_date": signal_date,
                "종목코드": ticker,
            }
            for ticker in ["FLOW01", "MOMO01"]
        ]
    )
    features = pd.DataFrame(
        [
            {
                "execution_date": execution_date,
                "signal_date": signal_date,
                "종목코드": "FLOW01",
                "fnv_5": 0.20,
                "inv_5": 0.20,
                "combined_flow_5": 0.40,
                "recent_return_5": -0.10,
            },
            {
                "execution_date": execution_date,
                "signal_date": signal_date,
                "종목코드": "MOMO01",
                "fnv_5": -0.20,
                "inv_5": -0.20,
                "combined_flow_5": -0.40,
                "recent_return_5": 0.10,
            },
        ]
    )

    result = run_baseline(
        "B3_price_momentum",
        panel,
        calendar,
        features,
        universe,
        _costs(),
        calendar.dates[0],
        calendar.dates[-1],
        max_positions=1,
        holding=2,
    )

    assert result.trades["종목코드"].tolist() == ["MOMO01"]
