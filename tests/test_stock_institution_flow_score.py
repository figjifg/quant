from __future__ import annotations

import pandas as pd
import pytest

from src.features.stock_institution_flow_score import build_stock_institution_flow_scores


def test_stock_institution_flow_score_uses_rolling_institution_amounts_and_within_sector_zscore() -> None:
    signal_date = pd.Timestamp("2025-01-07")
    result = build_stock_institution_flow_scores(
        _stock_daily(),
        signal_dates=[signal_date],
        value_window=2,
        mcap_window=3,
    )
    by_ticker = result.set_index("ticker")

    a_raw = ((30.0 + 40.0) / (300.0 + 400.0) + (20.0 + 30.0 + 40.0) / 1000.0) / 2.0
    b_raw = ((10.0 + 10.0) / (200.0 + 200.0) + (10.0 + 10.0 + 10.0) / 1000.0) / 2.0
    mean = (a_raw + b_raw) / 2.0
    std = (((a_raw - mean) ** 2 + (b_raw - mean) ** 2) / 2.0) ** 0.5

    assert by_ticker.loc["000001", "institution_flow_20"] == pytest.approx((30.0 + 40.0) / (300.0 + 400.0))
    assert by_ticker.loc["000001", "institution_flow_60"] == pytest.approx((20.0 + 30.0 + 40.0) / 1000.0)
    assert by_ticker.loc["000001", "raw_stock_institution_flow_score"] == pytest.approx(a_raw)
    assert by_ticker.loc["000001", "stock_institution_flow_score"] == pytest.approx((a_raw - mean) / std)
    assert by_ticker.loc["000002", "stock_institution_flow_score"] == pytest.approx((b_raw - mean) / std)


def test_stock_institution_flow_score_keeps_missing_stock_flow_as_nan() -> None:
    daily = _stock_daily()
    daily.loc[
        daily["ticker"].eq("000002") & pd.to_datetime(daily["date"]).eq(pd.Timestamp("2025-01-06")),
        "institution_net_buy_amount",
    ] = pd.NA

    result = build_stock_institution_flow_scores(
        daily,
        signal_dates=[pd.Timestamp("2025-01-07")],
        value_window=2,
        mcap_window=3,
    )

    row = result.loc[result["ticker"].eq("000002")].iloc[0]
    assert pd.isna(row["raw_stock_institution_flow_score"])
    assert pd.isna(row["stock_institution_flow_score"])
    assert bool(row["eligible_for_score"]) is False


def test_stock_institution_flow_score_at_signal_date_is_unchanged_by_future_rows() -> None:
    signal_date = pd.Timestamp("2025-01-07")
    before = build_stock_institution_flow_scores(
        _stock_daily(),
        signal_dates=[signal_date],
        value_window=2,
        mcap_window=3,
    )

    daily = _stock_daily()
    daily.loc[pd.to_datetime(daily["date"]).gt(signal_date), "institution_net_buy_amount"] = 999999.0
    daily.loc[pd.to_datetime(daily["date"]).gt(signal_date), "traded_value"] = 1.0
    daily.loc[pd.to_datetime(daily["date"]).gt(signal_date), "market_cap"] = 1.0
    after = build_stock_institution_flow_scores(
        daily,
        signal_dates=[signal_date],
        value_window=2,
        mcap_window=3,
    )

    pd.testing.assert_series_equal(
        before.sort_values("ticker")["stock_institution_flow_score"].reset_index(drop=True),
        after.sort_values("ticker")["stock_institution_flow_score"].reset_index(drop=True),
    )


def _stock_daily() -> pd.DataFrame:
    dates = pd.date_range("2025-01-02", periods=6, freq="B")
    rows = []
    institution = {
        "000001": [10.0, 20.0, 30.0, 40.0, -999.0, -999.0],
        "000002": [10.0, 10.0, 10.0, 10.0, 999.0, 999.0],
        "000003": [5.0, 5.0, 5.0, 5.0, 0.0, 0.0],
        "000004": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    }
    traded = {
        "000001": [100.0, 200.0, 300.0, 400.0, 1.0, 1.0],
        "000002": [200.0, 200.0, 200.0, 200.0, 1.0, 1.0],
        "000003": [100.0, 100.0, 100.0, 100.0, 1.0, 1.0],
        "000004": [100.0, 100.0, 100.0, 100.0, 1.0, 1.0],
    }
    sectors = {"000001": "01", "000002": "01", "000003": "02", "000004": "02"}
    for ticker, values in institution.items():
        for date, institution_value, traded_value in zip(dates, values, traded[ticker], strict=True):
            rows.append(
                {
                    "date": date,
                    "ticker": ticker,
                    "sector_code": sectors[ticker],
                    "sector_name": f"Sector {sectors[ticker]}",
                    "market_cap": 1000.0,
                    "traded_value": traded_value,
                    "institution_net_buy_amount": institution_value,
                    "daily_return": 0.01,
                }
            )
    return pd.DataFrame(rows)
