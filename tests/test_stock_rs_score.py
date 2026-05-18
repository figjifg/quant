from __future__ import annotations

import pandas as pd
import pytest

from src.features.stock_rs_score import build_stock_rs_scores


def test_stock_rs_score_uses_sector_relative_compounded_returns_and_within_sector_zscore() -> None:
    signal_date = pd.Timestamp("2025-01-07")
    result = build_stock_rs_scores(_stock_daily(), _sector_daily(), signal_dates=[signal_date], short_window=2, long_window=3)
    by_ticker = result.set_index("ticker")

    a_raw = _raw_score([0.03, 0.04], [0.02, 0.03, 0.04], [0.01, 0.01], [0.01, 0.01, 0.01])
    b_raw = _raw_score([0.01, 0.01], [0.01, 0.01, 0.01], [0.01, 0.01], [0.01, 0.01, 0.01])
    mean = (a_raw + b_raw) / 2.0
    std = (((a_raw - mean) ** 2 + (b_raw - mean) ** 2) / 2.0) ** 0.5

    assert by_ticker.loc["000001", "raw_stock_rs_score"] == pytest.approx(a_raw)
    assert by_ticker.loc["000001", "stock_rs_score"] == pytest.approx((a_raw - mean) / std)
    assert by_ticker.loc["000002", "stock_rs_score"] == pytest.approx((b_raw - mean) / std)


def test_stock_rs_score_at_signal_date_is_unchanged_by_future_rows() -> None:
    signal_date = pd.Timestamp("2025-01-07")
    before = build_stock_rs_scores(_stock_daily(), _sector_daily(), signal_dates=[signal_date], short_window=2, long_window=3)

    stocks = _stock_daily()
    sectors = _sector_daily()
    stocks.loc[pd.to_datetime(stocks["date"]).gt(signal_date), "daily_return"] = 99.0
    sectors.loc[pd.to_datetime(sectors["date"]).gt(signal_date), "cap_weighted_return"] = -99.0
    after = build_stock_rs_scores(stocks, sectors, signal_dates=[signal_date], short_window=2, long_window=3)

    pd.testing.assert_series_equal(
        before.sort_values("ticker")["stock_rs_score"].reset_index(drop=True),
        after.sort_values("ticker")["stock_rs_score"].reset_index(drop=True),
    )


def test_missing_sector_return_date_raises() -> None:
    sectors = _sector_daily().loc[lambda frame: frame["date"].ne(pd.Timestamp("2025-01-07"))]

    with pytest.raises(ValueError, match="sector_daily is missing"):
        build_stock_rs_scores(_stock_daily(), sectors, signal_dates=[pd.Timestamp("2025-01-07")], short_window=2, long_window=3)


def _raw_score(stock_2d: list[float], stock_3d: list[float], sector_2d: list[float], sector_3d: list[float]) -> float:
    return ((_compound(stock_2d) - _compound(sector_2d)) + (_compound(stock_3d) - _compound(sector_3d))) / 2.0


def _compound(values: list[float]) -> float:
    result = 1.0
    for value in values:
        result *= 1.0 + value
    return result - 1.0


def _stock_daily() -> pd.DataFrame:
    dates = pd.date_range("2025-01-02", periods=6, freq="B")
    rows = []
    returns = {
        "000001": [0.01, 0.02, 0.03, 0.04, -0.50, -0.50],
        "000002": [0.01, 0.01, 0.01, 0.01, 0.50, 0.50],
        "000003": [0.02, 0.02, 0.02, 0.02, 0.00, 0.00],
        "000004": [0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
    }
    sectors = {"000001": "01", "000002": "01", "000003": "02", "000004": "02"}
    for ticker, values in returns.items():
        for date, value in zip(dates, values, strict=True):
            rows.append(
                {
                    "date": date,
                    "ticker": ticker,
                    "sector_code": sectors[ticker],
                    "sector_name": f"Sector {sectors[ticker]}",
                    "daily_return": value,
                }
            )
    return pd.DataFrame(rows)


def _sector_daily() -> pd.DataFrame:
    dates = pd.date_range("2025-01-02", periods=6, freq="B")
    rows = []
    for date in dates:
        for sector_code, value in (("01", 0.01), ("02", 0.01)):
            rows.append(
                {
                    "date": date,
                    "sector_code": sector_code,
                    "sector_name": f"Sector {sector_code}",
                    "cap_weighted_return": value,
                }
            )
    return pd.DataFrame(rows)
