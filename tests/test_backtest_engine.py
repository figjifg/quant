from __future__ import annotations

import pandas as pd

from src.backtest.calendar import derive_trading_calendar
from src.backtest.costs import Costs, sell_cost
from src.backtest.engine import run_headline_backtest


def _panel(
    *,
    tickers: list[str] | None = None,
    periods: int = 12,
    open_nan: tuple[str, int] | None = None,
    close_nan: tuple[str, int] | None = None,
) -> pd.DataFrame:
    dates = pd.date_range("2025-01-02", periods=periods, freq="B")
    rows = []
    for ticker_index, ticker in enumerate(tickers or ["000001", "000002", "000003"], start=1):
        for date_index, date in enumerate(dates):
            open_price = 100.0 + ticker_index + date_index
            close_price = open_price + 1.0
            if open_nan == (ticker, date_index):
                open_price = pd.NA
            if close_nan == (ticker, date_index):
                close_price = pd.NA
            rows.append(
                {
                    "날짜": date,
                    "종목코드": ticker,
                    "시가": open_price,
                    "KRX종가": close_price,
                }
            )
    return pd.DataFrame(rows)


def _features_and_universe(
    panel: pd.DataFrame,
    *,
    signals_by_execution_index: dict[int, list[str]] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    dates = tuple(sorted(panel["날짜"].unique()))
    rows = []
    selected = signals_by_execution_index or {1: sorted(panel["종목코드"].unique())}
    for execution_index, tickers in selected.items():
        execution_date = pd.Timestamp(dates[execution_index])
        signal_date = pd.Timestamp(dates[execution_index - 1])
        for rank, ticker in enumerate(tickers):
            rows.append(
                {
                    "execution_date": execution_date,
                    "signal_date": signal_date,
                    "종목코드": ticker,
                    "fnv_5": 0.10,
                    "inv_5": 0.20,
                    "combined_flow_5": 1_000.0 - rank,
                }
            )
    features = pd.DataFrame(rows)
    universe = features.loc[:, ["execution_date", "signal_date", "종목코드"]].copy()
    return features, universe


def _costs() -> Costs:
    return Costs(commission_bps=1.5, tax_bps_sell=20.0, slippage_bps=5.0)


def test_never_more_than_max_positions_simultaneous_positions() -> None:
    panel = _panel(tickers=[f"{index:06d}" for index in range(1, 9)], periods=12)
    calendar = derive_trading_calendar(panel)
    features, universe = _features_and_universe(
        panel,
        signals_by_execution_index={1: sorted(panel["종목코드"].unique())},
    )

    result = run_headline_backtest(
        panel,
        calendar,
        features,
        universe,
        _costs(),
        period_start=calendar.dates[0],
        period_end=calendar.dates[-1],
        max_positions=5,
        holding=5,
    )

    assert result.equity_curve["n_positions"].max() <= 5
    assert len(result.trades) == 5


def test_no_duplicate_entry_on_same_ticker_while_held() -> None:
    panel = _panel(tickers=["000001", "000002"], periods=12)
    calendar = derive_trading_calendar(panel)
    features, universe = _features_and_universe(
        panel,
        signals_by_execution_index={1: ["000001", "000002"], 2: ["000001"]},
    )

    result = run_headline_backtest(
        panel,
        calendar,
        features,
        universe,
        _costs(),
        period_start=calendar.dates[0],
        period_end=calendar.dates[8],
        max_positions=5,
        holding=5,
    )

    assert list(result.trades["종목코드"]).count("000001") == 1


def test_exit_cash_arithmetic_matches_sell_cost_formula() -> None:
    panel = _panel(tickers=["000001"], periods=8)
    calendar = derive_trading_calendar(panel)
    features, universe = _features_and_universe(panel, signals_by_execution_index={1: ["000001"]})
    costs = _costs()

    result = run_headline_backtest(
        panel,
        calendar,
        features,
        universe,
        costs,
        period_start=calendar.dates[0],
        period_end=calendar.dates[-1],
        max_positions=5,
        holding=5,
    )

    trade = result.trades.iloc[0]
    exit_notional = trade["shares"] * trade["exit_price"]
    expected_sell_cost = sell_cost(exit_notional, costs)
    cash_before_exit = (
        1.0
        - trade["notional_at_entry"]
        - trade["buy_cost"]
    )
    expected_cash_after_exit = cash_before_exit + exit_notional - expected_sell_cost
    exit_curve_row = result.equity_curve.loc[result.equity_curve["date"] == trade["exit_date"]].iloc[0]

    assert abs(trade["sell_cost"] - expected_sell_cost) < 1e-12
    assert abs(exit_curve_row["cash"] - expected_cash_after_exit) < 1e-12


def test_holding_period_exit_date_uses_calendar_add_trading_days() -> None:
    panel = _panel(tickers=["000001"], periods=10)
    calendar = derive_trading_calendar(panel)
    features, universe = _features_and_universe(panel, signals_by_execution_index={1: ["000001"]})

    result = run_headline_backtest(
        panel,
        calendar,
        features,
        universe,
        _costs(),
        period_start=calendar.dates[0],
        period_end=calendar.dates[-1],
        max_positions=5,
        holding=5,
    )

    trade = result.trades.iloc[0]
    assert trade["exit_date"] == calendar.add_trading_days(trade["entry_date"], 5)
    assert trade["exit_reason"] == "holding_period"


def test_missing_price_fallback_exits_on_next_non_null_close() -> None:
    panel = _panel(tickers=["000001", "000002"], periods=10, close_nan=("000001", 6))
    calendar = derive_trading_calendar(panel)
    features, universe = _features_and_universe(panel, signals_by_execution_index={1: ["000001"]})

    result = run_headline_backtest(
        panel,
        calendar,
        features,
        universe,
        _costs(),
        period_start=calendar.dates[0],
        period_end=calendar.dates[-1],
        max_positions=5,
        holding=5,
    )

    trade = result.trades.iloc[0]
    assert trade["exit_date"] == calendar.dates[7]
    assert trade["exit_reason"] == "missing_price_fallback"
    assert trade["exit_price"] == panel.loc[
        (panel["종목코드"] == "000001") & (panel["날짜"] == calendar.dates[7]),
        "KRX종가",
    ].iloc[0]


def test_nan_open_on_entry_date_skips_entry_without_trade_row() -> None:
    panel = _panel(tickers=["000001"], periods=10, open_nan=("000001", 1))
    calendar = derive_trading_calendar(panel)
    features, universe = _features_and_universe(panel, signals_by_execution_index={1: ["000001"]})

    result = run_headline_backtest(
        panel,
        calendar,
        features,
        universe,
        _costs(),
        period_start=calendar.dates[0],
        period_end=calendar.dates[-1],
        max_positions=5,
        holding=5,
    )

    assert result.trades.empty
    assert result.equity_curve["n_positions"].max() == 0


def test_period_end_force_exit_closes_all_remaining_slots_at_last_close() -> None:
    panel = _panel(tickers=["000001", "000002"], periods=8)
    calendar = derive_trading_calendar(panel)
    features, universe = _features_and_universe(
        panel,
        signals_by_execution_index={4: ["000001", "000002"]},
    )
    period_end = calendar.dates[6]

    result = run_headline_backtest(
        panel,
        calendar,
        features,
        universe,
        _costs(),
        period_start=calendar.dates[0],
        period_end=period_end,
        max_positions=5,
        holding=3,
    )

    assert set(result.trades["종목코드"]) == {"000001", "000002"}
    assert set(result.trades["exit_reason"]) == {"period_end"}
    assert set(result.trades["exit_date"]) == {period_end}
    assert result.equity_curve.iloc[-1]["n_positions"] == 0
