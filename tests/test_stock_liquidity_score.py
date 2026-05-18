from __future__ import annotations

import pandas as pd
import pytest

from src.features.stock_liquidity_score import build_stock_liquidity_scores


def test_stock_liquidity_score_uses_rolling_liquidity_turnover_and_within_sector_zscore() -> None:
    signal_date = pd.Timestamp("2025-01-07")
    result = build_stock_liquidity_scores(
        _stock_daily(),
        signal_dates=[signal_date],
        short_window=2,
        long_window=4,
    )
    by_ticker = result.set_index("ticker")

    a_liquidity = ((300.0 + 500.0) / 2.0) / ((100.0 + 200.0 + 300.0 + 500.0) / 4.0)
    b_liquidity = ((100.0 + 100.0) / 2.0) / ((100.0 + 100.0 + 100.0 + 100.0) / 4.0)
    a_turnover = (((300.0 / 1000.0) + (500.0 / 1000.0)) / 2.0) / (
        ((100.0 / 1000.0) + (200.0 / 1000.0) + (300.0 / 1000.0) + (500.0 / 1000.0)) / 4.0
    )
    b_turnover = 1.0
    a_raw = (a_liquidity + a_turnover) / 2.0
    b_raw = (b_liquidity + b_turnover) / 2.0
    mean = (a_raw + b_raw) / 2.0
    std = (((a_raw - mean) ** 2 + (b_raw - mean) ** 2) / 2.0) ** 0.5

    assert by_ticker.loc["000001", "liquidity_change"] == pytest.approx(a_liquidity)
    assert by_ticker.loc["000001", "turnover_change"] == pytest.approx(a_turnover)
    assert by_ticker.loc["000001", "raw_stock_liquidity_score"] == pytest.approx(a_raw)
    assert by_ticker.loc["000001", "stock_liquidity_score"] == pytest.approx((a_raw - mean) / std)
    assert by_ticker.loc["000002", "stock_liquidity_score"] == pytest.approx((b_raw - mean) / std)


def test_stock_liquidity_score_keeps_invalid_denominator_as_nan() -> None:
    daily = _stock_daily()
    daily.loc[
        daily["ticker"].eq("000002") & pd.to_datetime(daily["date"]).eq(pd.Timestamp("2025-01-06")),
        "market_cap",
    ] = 0.0

    result = build_stock_liquidity_scores(
        daily,
        signal_dates=[pd.Timestamp("2025-01-07")],
        short_window=2,
        long_window=4,
    )

    row = result.loc[result["ticker"].eq("000002")].iloc[0]
    assert pd.isna(row["raw_stock_liquidity_score"])
    assert pd.isna(row["stock_liquidity_score"])
    assert bool(row["eligible_for_score"]) is False


def test_stock_liquidity_score_at_signal_date_is_unchanged_by_future_rows() -> None:
    signal_date = pd.Timestamp("2025-01-07")
    before = build_stock_liquidity_scores(
        _stock_daily(),
        signal_dates=[signal_date],
        short_window=2,
        long_window=4,
    )

    daily = _stock_daily()
    daily.loc[pd.to_datetime(daily["date"]).gt(signal_date), "traded_value"] = 999999.0
    daily.loc[pd.to_datetime(daily["date"]).gt(signal_date), "market_cap"] = 1.0
    after = build_stock_liquidity_scores(
        daily,
        signal_dates=[signal_date],
        short_window=2,
        long_window=4,
    )

    pd.testing.assert_series_equal(
        before.sort_values("ticker")["stock_liquidity_score"].reset_index(drop=True),
        after.sort_values("ticker")["stock_liquidity_score"].reset_index(drop=True),
    )


def _stock_daily() -> pd.DataFrame:
    dates = pd.date_range("2025-01-02", periods=6, freq="B")
    traded = {
        "000001": [100.0, 200.0, 300.0, 500.0, 1.0, 1.0],
        "000002": [100.0, 100.0, 100.0, 100.0, 1.0, 1.0],
        "000003": [100.0, 100.0, 100.0, 100.0, 1.0, 1.0],
        "000004": [100.0, 100.0, 100.0, 100.0, 1.0, 1.0],
    }
    sectors = {"000001": "01", "000002": "01", "000003": "02", "000004": "02"}
    rows = []
    for ticker, values in traded.items():
        for date, traded_value in zip(dates, values, strict=True):
            rows.append(
                {
                    "date": date,
                    "ticker": ticker,
                    "sector_code": sectors[ticker],
                    "sector_name": f"Sector {sectors[ticker]}",
                    "market_cap": 1000.0,
                    "traded_value": traded_value,
                    "daily_return": 0.01,
                }
            )
    return pd.DataFrame(rows)
