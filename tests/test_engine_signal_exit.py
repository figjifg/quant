from __future__ import annotations

import pandas as pd

from src.backtest.calendar import derive_trading_calendar
from src.backtest.costs import Costs
from src.backtest.engine import run_candidate_backtest


def _costs() -> Costs:
    return Costs(commission_bps=1.5, tax_bps_sell=20.0, slippage_bps=5.0)


def _panel(*, periods: int = 8, open_nan_index: int | None = None) -> pd.DataFrame:
    dates = pd.date_range("2025-01-02", periods=periods, freq="B")
    rows = []
    for index, date in enumerate(dates):
        open_price = 100.0 + index
        if open_nan_index is not None and index == open_nan_index:
            open_price = pd.NA
        rows.append(
            {
                "날짜": date,
                "종목코드": "000001",
                "시가": open_price,
                "KRX종가": 100.5 + index,
            }
        )
    return pd.DataFrame(rows)


def _candidates(dates: tuple[pd.Timestamp, ...], *, execution_index: int = 1) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "execution_date": dates[execution_index],
                "signal_date": dates[execution_index - 1],
                "종목코드": "000001",
                "fnv_5": 0.1,
                "inv_5": 0.1,
                "combined_flow_5": 1.0,
            }
        ]
    )


def _signal_exit_features(
    dates: tuple[pd.Timestamp, ...],
    *,
    reversal_index: int | None = None,
    nan_index: int | None = None,
) -> pd.DataFrame:
    rows = []
    for index, date in enumerate(dates):
        fnv_5 = 0.1
        inv_5 = 0.1
        if reversal_index is not None and index == reversal_index:
            inv_5 = 0.0
        if nan_index is not None and index == nan_index:
            fnv_5 = pd.NA
        rows.append({"날짜": date, "종목코드": "000001", "fnv_5": fnv_5, "inv_5": inv_5})
    return pd.DataFrame(rows)


def test_signal_reversal_triggers_exit_on_next_day_open() -> None:
    panel = _panel(periods=8)
    calendar = derive_trading_calendar(panel)

    result = run_candidate_backtest(
        panel,
        calendar,
        _candidates(calendar.dates),
        _costs(),
        period_start=calendar.dates[0],
        period_end=calendar.dates[-1],
        holding=2,
        signal_exit_features=_signal_exit_features(calendar.dates, reversal_index=3),
    )

    trade = result.trades.iloc[0]
    assert trade["entry_date"] == calendar.dates[1]
    assert trade["exit_date"] == calendar.dates[4]
    assert trade["exit_price"] == 104.0
    assert trade["exit_reason"] == "signal_reversal"


def test_positive_signal_holds_until_period_end_without_time_cap() -> None:
    panel = _panel(periods=8)
    calendar = derive_trading_calendar(panel)
    period_end = calendar.dates[6]

    result = run_candidate_backtest(
        panel,
        calendar,
        _candidates(calendar.dates),
        _costs(),
        period_start=calendar.dates[0],
        period_end=period_end,
        holding=2,
        signal_exit_features=_signal_exit_features(calendar.dates),
    )

    trade = result.trades.iloc[0]
    assert trade["exit_date"] == period_end
    assert trade["exit_price"] == 106.5
    assert trade["exit_reason"] == "period_end"


def test_nan_signal_during_hold_is_conservative_reversal() -> None:
    panel = _panel(periods=8)
    calendar = derive_trading_calendar(panel)

    result = run_candidate_backtest(
        panel,
        calendar,
        _candidates(calendar.dates),
        _costs(),
        period_start=calendar.dates[0],
        period_end=calendar.dates[-1],
        signal_exit_features=_signal_exit_features(calendar.dates, nan_index=2),
    )

    trade = result.trades.iloc[0]
    assert trade["exit_date"] == calendar.dates[3]
    assert trade["exit_reason"] == "signal_reversal"


def test_signal_exit_none_preserves_fixed_holding_behavior() -> None:
    panel = _panel(periods=8)
    calendar = derive_trading_calendar(panel)
    candidates = _candidates(calendar.dates)

    before = run_candidate_backtest(
        panel,
        calendar,
        candidates,
        _costs(),
        period_start=calendar.dates[0],
        period_end=calendar.dates[-1],
        holding=3,
    )
    after = run_candidate_backtest(
        panel,
        calendar,
        candidates,
        _costs(),
        period_start=calendar.dates[0],
        period_end=calendar.dates[-1],
        holding=3,
        signal_exit_features=None,
    )

    pd.testing.assert_frame_equal(after.trades, before.trades)
    pd.testing.assert_frame_equal(after.equity_curve, before.equity_curve)


def test_signal_reversal_fallback_when_next_day_open_is_nan() -> None:
    panel = _panel(periods=8, open_nan_index=4)
    calendar = derive_trading_calendar(panel)

    result = run_candidate_backtest(
        panel,
        calendar,
        _candidates(calendar.dates),
        _costs(),
        period_start=calendar.dates[0],
        period_end=calendar.dates[-1],
        signal_exit_features=_signal_exit_features(calendar.dates, reversal_index=3),
    )

    trade = result.trades.iloc[0]
    assert trade["exit_date"] == calendar.dates[5]
    assert trade["exit_price"] == 105.0
    assert trade["exit_reason"] == "signal_reversal_fallback"
