from __future__ import annotations

import pandas as pd
import pytest

from src.features.sector_breadth_score import build_sector_breadth_scores


def _stock_daily() -> pd.DataFrame:
    dates = pd.date_range("2025-01-02", periods=5, freq="B")
    rows = []
    specs = [
        ("000001", "01", "sector_01", 10.0, 0.02),
        ("000002", "01", "sector_01", 10.0, 0.01),
        ("000003", "01", "sector_01", -10.0, 0.03),
        ("000004", "02", "sector_02", 10.0, -0.01),
        ("000005", "02", "sector_02", -10.0, 0.01),
        ("000006", "02", "sector_02", -10.0, -0.01),
        ("000007", "03", "sector_03", 10.0, 0.02),
        ("000008", "03", "sector_03", 10.0, 0.02),
    ]
    for date in dates:
        for ticker, sector_code, sector_name, flow, daily_return in specs:
            rows.append(
                {
                    "date": date,
                    "ticker": ticker,
                    "sector_code": sector_code,
                    "sector_name": sector_name,
                    "market_cap": 1_000.0,
                    "foreign_net_buy_amount": flow,
                    "daily_return": daily_return,
                }
            )
    return pd.DataFrame(rows)


def _kospi_daily() -> pd.DataFrame:
    dates = pd.date_range("2025-01-02", periods=5, freq="B")
    return pd.DataFrame({"date": dates, "cap_weighted_return": [0.0] * len(dates)})


def test_breadth_score_counts_strict_positive_members_and_zscores() -> None:
    result = build_sector_breadth_scores(
        _stock_daily(),
        _kospi_daily(),
        signal_dates=[pd.Timestamp("2025-01-08")],
        window=2,
    )
    by_sector = result.set_index("sector_code")

    assert by_sector.loc["01", "n_stocks"] == 3
    assert by_sector.loc["01", "n_strict_positive"] == 2
    assert by_sector.loc["01", "sector_breadth_strict"] == pytest.approx(2.0 / 3.0)
    assert by_sector.loc["02", "n_strict_positive"] == 0
    assert by_sector.loc["02", "sector_breadth_strict"] == pytest.approx(0.0)
    assert by_sector.loc["01", "breadth_score"] == pytest.approx(1.0)
    assert by_sector.loc["02", "breadth_score"] == pytest.approx(-1.0)


def test_thin_sector_is_excluded_from_breadth_score() -> None:
    result = build_sector_breadth_scores(
        _stock_daily(),
        _kospi_daily(),
        signal_dates=[pd.Timestamp("2025-01-08")],
        window=2,
    )
    thin = result.loc[result["sector_code"].eq("03")].iloc[0]

    assert not bool(thin["eligible_for_score"])
    assert pd.isna(thin["sector_breadth_strict"])
    assert pd.isna(thin["breadth_score"])


def test_breadth_score_at_signal_date_is_unchanged_by_future_rows() -> None:
    stock = _stock_daily()
    kospi = _kospi_daily()
    signal_date = pd.Timestamp("2025-01-07")
    before = build_sector_breadth_scores(stock, kospi, signal_dates=[signal_date], window=2)

    mutated_stock = stock.copy()
    mutated_kospi = kospi.copy()
    mutated_stock.loc[pd.to_datetime(mutated_stock["date"]).gt(signal_date), "foreign_net_buy_amount"] = 999_000.0
    mutated_stock.loc[pd.to_datetime(mutated_stock["date"]).gt(signal_date), "daily_return"] = 999.0
    mutated_kospi.loc[pd.to_datetime(mutated_kospi["date"]).gt(signal_date), "cap_weighted_return"] = -0.99
    after = build_sector_breadth_scores(mutated_stock, mutated_kospi, signal_dates=[signal_date], window=2)

    pd.testing.assert_series_equal(
        before.sort_values("sector_code")["breadth_score"].reset_index(drop=True),
        after.sort_values("sector_code")["breadth_score"].reset_index(drop=True),
    )
