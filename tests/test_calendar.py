from __future__ import annotations

import pandas as pd
import pytest

from src.backtest.calendar import KRXTradingCalendar, derive_trading_calendar


def _panel() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "날짜": pd.to_datetime(
                [
                    "2025-01-03",
                    "2025-01-03",
                    "2025-01-04",
                    "2025-01-07",
                    "2025-01-08",
                ]
            ),
            "종목코드": ["000010", "000020", "000010", "000010", "000010"],
            "KRX종가": [100.0, None, 101.0, 102.0, 103.0],
        }
    )


def test_calendar_uses_sorted_unique_dates_with_any_non_null_krx_close() -> None:
    calendar = derive_trading_calendar(_panel())

    assert calendar.dates == (
        pd.Timestamp("2025-01-03"),
        pd.Timestamp("2025-01-04"),
        pd.Timestamp("2025-01-07"),
        pd.Timestamp("2025-01-08"),
    )


def test_next_trading_day_skips_dates_absent_from_panel_calendar() -> None:
    calendar = KRXTradingCalendar(
        (
            pd.Timestamp("2025-01-03"),
            pd.Timestamp("2025-01-07"),
            pd.Timestamp("2025-01-08"),
        )
    )

    assert calendar.next_trading_day("2025-01-03") == pd.Timestamp("2025-01-07")
    assert calendar.next_trading_day("2025-01-04") == pd.Timestamp("2025-01-07")


def test_add_trading_days_counts_strictly_after_input_date() -> None:
    calendar = KRXTradingCalendar(
        (
            pd.Timestamp("2025-01-03"),
            pd.Timestamp("2025-01-07"),
            pd.Timestamp("2025-01-08"),
            pd.Timestamp("2025-01-09"),
        )
    )

    assert calendar.add_trading_days("2025-01-03", 1) == calendar.next_trading_day("2025-01-03")
    assert calendar.add_trading_days("2025-01-03", 3) == pd.Timestamp("2025-01-09")
    assert calendar.add_trading_days("2025-01-04", 2) == pd.Timestamp("2025-01-08")


def test_add_zero_trading_days_returns_input_only_for_trading_day() -> None:
    calendar = KRXTradingCalendar((pd.Timestamp("2025-01-03"), pd.Timestamp("2025-01-07")))

    assert calendar.add_trading_days("2025-01-03", 0) == pd.Timestamp("2025-01-03")
    with pytest.raises(ValueError, match="not a trading day"):
        calendar.add_trading_days("2025-01-04", 0)


def test_out_of_range_dates_raise() -> None:
    calendar = KRXTradingCalendar((pd.Timestamp("2025-01-03"), pd.Timestamp("2025-01-07")))

    with pytest.raises(ValueError, match="No trading day after"):
        calendar.next_trading_day("2025-01-07")
    with pytest.raises(ValueError, match="out of range"):
        calendar.add_trading_days("2025-01-03", 2)


def test_empty_calendar_raises() -> None:
    with pytest.raises(ValueError, match="cannot be empty"):
        KRXTradingCalendar(())
