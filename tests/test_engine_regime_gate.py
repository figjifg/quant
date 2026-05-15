from __future__ import annotations

import pandas as pd

from src.backtest.calendar import derive_trading_calendar
from src.backtest.costs import Costs
from src.backtest.engine import run_candidate_backtest


def _costs() -> Costs:
    return Costs(commission_bps=1.5, tax_bps_sell=20.0, slippage_bps=5.0)


def _panel(*, tickers: list[str] | None = None, periods: int = 8) -> pd.DataFrame:
    dates = pd.date_range("2025-01-02", periods=periods, freq="B")
    rows = []
    for ticker_index, ticker in enumerate(tickers or ["000001"], start=1):
        for date_index, date in enumerate(dates):
            rows.append(
                {
                    "날짜": date,
                    "종목코드": ticker,
                    "시가": 100.0 + ticker_index + date_index,
                    "KRX종가": 100.5 + ticker_index + date_index,
                }
            )
    return pd.DataFrame(rows)


def _candidates(calendar_dates: tuple[pd.Timestamp, ...], execution_indexes: list[int]) -> pd.DataFrame:
    rows = []
    for execution_index in execution_indexes:
        rows.append(
            {
                "execution_date": calendar_dates[execution_index],
                "signal_date": calendar_dates[execution_index - 1],
                "종목코드": "000001",
                "fnv_5": 0.1,
                "inv_5": 0.1,
                "combined_flow_5": 1.0,
            }
        )
    return pd.DataFrame(rows)


def test_regime_gate_dates_suppress_entries_on_off_signal_dates() -> None:
    panel = _panel(periods=6)
    calendar = derive_trading_calendar(panel)
    candidates = _candidates(calendar.dates, [1, 2])

    result = run_candidate_backtest(
        panel,
        calendar,
        candidates,
        _costs(),
        period_start=calendar.dates[0],
        period_end=calendar.dates[-1],
        holding=2,
        regime_gate_dates={calendar.dates[0]},
    )

    assert len(result.trades) == 1
    assert result.trades.iloc[0]["signal_date"] == calendar.dates[0]


def test_gate_off_flip_forces_exit_at_next_day_open() -> None:
    panel = _panel(periods=8)
    calendar = derive_trading_calendar(panel)
    candidates = _candidates(calendar.dates, [1])

    result = run_candidate_backtest(
        panel,
        calendar,
        candidates,
        _costs(),
        period_start=calendar.dates[0],
        period_end=calendar.dates[-1],
        holding=6,
        gate_exit_signal_dates={calendar.dates[2]},
    )

    trade = result.trades.iloc[0]
    assert trade["entry_date"] == calendar.dates[1]
    assert trade["exit_date"] == calendar.dates[3]
    assert trade["exit_price"] == 104.0
    assert trade["exit_reason"] == "gate_off"


def test_universe_exit_closes_name_that_leaves_signal_universe() -> None:
    panel = _panel(periods=8)
    calendar = derive_trading_calendar(panel)
    candidates = _candidates(calendar.dates, [1])

    result = run_candidate_backtest(
        panel,
        calendar,
        candidates,
        _costs(),
        period_start=calendar.dates[0],
        period_end=calendar.dates[-1],
        holding=6,
        universe_exit_signal_tickers={
            (calendar.dates[0], "000001"),
            (calendar.dates[1], "000001"),
        },
    )

    trade = result.trades.iloc[0]
    assert trade["entry_date"] == calendar.dates[1]
    assert trade["exit_date"] == calendar.dates[3]
    assert trade["exit_price"] == 104.0
    assert trade["exit_reason"] == "universe_exit"
