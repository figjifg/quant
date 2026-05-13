from __future__ import annotations

import pandas as pd

from src.backtest.calendar import derive_trading_calendar
from src.data.universe import build_execution_universe


def _synthetic_panel() -> pd.DataFrame:
    dates = pd.date_range("2025-01-02", periods=25, freq="B")
    rows = []
    for ticker in ["000010", "000020", "000030"]:
        ticker_dates = dates if ticker != "000030" else dates[-19:]
        for date in ticker_dates:
            rows.append(
                {
                    "날짜": date,
                    "종목코드": ticker,
                    "KRX종가": 100.0,
                    "거래대금추정": 6_000_000_000.0,
                    "수급금액추정여부": False,
                    "거래대금추정여부": False,
                    "동적유니버스포함": ticker != "000020",
                }
            )

    panel = pd.DataFrame(rows)
    panel.loc[
        (panel["종목코드"] == "000020") & (panel["날짜"] == dates[19]),
        "동적유니버스포함",
    ] = False
    panel.loc[
        (panel["종목코드"] == "000020") & (panel["날짜"] == dates[20]),
        "동적유니버스포함",
    ] = True
    return panel


def test_universe_uses_prior_trading_day_for_execution_date() -> None:
    panel = _synthetic_panel()
    calendar = derive_trading_calendar(panel)
    universe = build_execution_universe(panel, calendar)
    execution_date = pd.Timestamp("2025-01-30")

    tickers = set(universe.loc[universe["execution_date"] == execution_date, "종목코드"])

    assert "000010" in tickers
    assert "000020" not in tickers


def test_first_trading_day_and_fewer_than_20_prior_rows_are_ineligible() -> None:
    panel = _synthetic_panel()
    calendar = derive_trading_calendar(panel)
    universe = build_execution_universe(panel, calendar)

    assert calendar.dates[0] not in set(universe["execution_date"])
    assert "000030" not in set(universe["종목코드"])


def test_liquidity_filter_uses_last_20_rows_ending_at_prior_day() -> None:
    panel = _synthetic_panel()
    dates = pd.date_range("2025-01-02", periods=25, freq="B")
    panel.loc[
        (panel["종목코드"] == "000010") & (panel["날짜"].isin(dates[:20])),
        "거래대금추정",
    ] = 4_900_000_000.0
    panel.loc[
        (panel["종목코드"] == "000010") & (panel["날짜"] == dates[20]),
        "거래대금추정",
    ] = 6_000_000_000.0

    universe = build_execution_universe(panel, derive_trading_calendar(panel))
    execution_date = dates[20]

    tickers = set(universe.loc[universe["execution_date"] == execution_date, "종목코드"])

    assert "000010" not in tickers


def test_latest_prior_row_requires_non_null_krx_close() -> None:
    panel = _synthetic_panel()
    dates = pd.date_range("2025-01-02", periods=25, freq="B")
    panel.loc[
        (panel["종목코드"] == "000010") & (panel["날짜"] == dates[19]),
        "KRX종가",
    ] = pd.NA

    universe = build_execution_universe(panel, derive_trading_calendar(panel))
    execution_date = dates[20]

    tickers = set(universe.loc[universe["execution_date"] == execution_date, "종목코드"])

    assert "000010" not in tickers


def test_headline_excludes_estimated_signal_rows_but_diagnostic_includes_them() -> None:
    panel = _synthetic_panel()
    dates = pd.date_range("2025-01-02", periods=25, freq="B")
    panel.loc[
        (panel["종목코드"] == "000010") & (panel["날짜"] == dates[18]),
        "거래대금추정여부",
    ] = True
    calendar = derive_trading_calendar(panel)
    execution_date = dates[20]

    headline = build_execution_universe(panel, calendar, exclude_estimated_flag_rows=True)
    diagnostic = build_execution_universe(panel, calendar, exclude_estimated_flag_rows=False)

    headline_tickers = set(headline.loc[headline["execution_date"] == execution_date, "종목코드"])
    diagnostic_tickers = set(
        diagnostic.loc[diagnostic["execution_date"] == execution_date, "종목코드"]
    )

    assert "000010" not in headline_tickers
    assert "000010" in diagnostic_tickers


def test_headline_does_not_filter_on_수급금액추정여부() -> None:
    """수급금액추정여부 is universally True in the Kiwoom panel; not a meaningful gate."""
    panel = _synthetic_panel()
    dates = pd.date_range("2025-01-02", periods=25, freq="B")
    panel.loc[
        (panel["종목코드"] == "000010") & (panel["날짜"] == dates[18]),
        "수급금액추정여부",
    ] = True
    calendar = derive_trading_calendar(panel)
    execution_date = dates[20]

    headline = build_execution_universe(panel, calendar, exclude_estimated_flag_rows=True)
    headline_tickers = set(headline.loc[headline["execution_date"] == execution_date, "종목코드"])

    assert "000010" in headline_tickers
